"""3D semantic map of the HAI101 speakers from their abstracts, plus a rotating animation.

    python main.py                          # abstract-level map: every paper a point, talks as squares
    python main.py --level author           # one point per author, HDBSCAN clusters (original spec)
    python main.py --reducer axes           # interpretable anchor axes instead of UMAP
    python main.py --from-coords            # re-render plot + animation from output/*_coords.csv
"""
import argparse
import os
import random
from pathlib import Path

import numpy as np
import pandas as pd

from src.animate import animate
from src.embed import DEFAULT_MODEL, embed_abstracts, load_model
from src.load import load_and_explode
from src.plot import Scene, plot_scene, sqrt_sizes, write_html
from src.reduce import (AXES, author_vectors, axes_projection, center_normalize, cluster,
                        cluster_keywords, reduce_3d)
from src.talks import load_talks


def seed_everything(seed):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
    except ImportError:
        pass


def centroid_edges(vectors, k=2):
    """k nearest neighbours between label vectors (cosine on centred space), as index pairs."""
    S = vectors @ vectors.T
    np.fill_diagonal(S, -np.inf)
    edges = set()
    for i in range(len(S)):
        for j in np.argsort(S[i])[::-1][:k]:
            edges.add((min(i, j), max(i, j)))
    return sorted(edges)


def abstract_scene(df, emb, talks, args, embed):
    """Every paper a point coloured by speaker; the HAI101 talk a square; label at each speaker's centroid."""
    Z = center_normalize(emb)
    speakers = list(dict.fromkeys(df["author"]))  # keep input order (= website order)
    talk_rows = talks[talks["speaker_id"].isin(df["speaker_id"].unique())] if "speaker_id" in df else talks.iloc[0:0]
    name_of = dict(zip(df["speaker_id"], df["author"]))
    talk_text = [t.abstract or t.title for t in talk_rows.itertuples()]
    if talk_text:
        T, _ = embed(talk_text)
        T = (T - emb.mean(axis=0))
        T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-9)
        Z_all = np.vstack([Z, T])
    else:
        Z_all = Z

    if args.reducer == "axes":
        xyz = axes_projection(np.vstack([emb, embed(talk_text)[0]]) if talk_text else emb, load_model(args.model))
        axes = tuple(AXES)
    else:
        xyz = reduce_3d(Z_all, args.reducer, args.seed, args.n_neighbors, args.min_dist)
        axes = None

    n = len(df)
    pts = pd.DataFrame({
        "x": xyz[:n, 0], "y": xyz[:n, 1], "z": xyz[:n, 2], "group": df["author"].to_numpy(), "kind": "paper",
        "size": 4.0, "title": df["title"].to_numpy() if "title" in df else "", "year": df.get("year", ""),
    })
    pts["hover"] = [f"<b>{g}</b><br>{y} · {str(t)[:90]}" for g, y, t in zip(pts["group"], pts["year"], pts["title"])]
    if talk_text:
        tp = pd.DataFrame({
            "x": xyz[n:, 0], "y": xyz[n:, 1], "z": xyz[n:, 2],
            "group": [name_of[s] for s in talk_rows["speaker_id"]], "kind": "talk", "size": 9.0,
            "title": talk_rows["title"].to_numpy(), "year": "HAI101",
        })
        tp["hover"] = [f"<b>HAI101 talk · {g}</b><br>{t}" + ("" if a else "<br><i>(title only, no abstract yet)</i>")
                       for g, t, a in zip(tp["group"], tp["title"], talk_rows["has_abstract"])]
        pts = pd.concat([pts, tp], ignore_index=True)

    # Label at the medoid paper (least total distance to the speaker's other papers): unlike the mean,
    # it stays inside the main clump when a speaker's work splits into two.
    def medoid(P):
        D = np.linalg.norm(P[:, None] - P[None], axis=2)
        return P[D.sum(axis=1).argmin()]

    cent_xyz = np.stack([medoid(xyz[:n][(df["author"] == s).to_numpy()]) for s in speakers])
    labels = pd.DataFrame({"x": cent_xyz[:, 0], "y": cent_xyz[:, 1], "z": cent_xyz[:, 2],
                           "text": speakers, "short": [s.split()[-1] for s in speakers], "group": speakers})
    cent_vec = np.stack([Z[(df["author"] == s).to_numpy()].mean(axis=0) for s in speakers])
    cent_vec /= np.linalg.norm(cent_vec, axis=1, keepdims=True)
    edges = centroid_edges(cent_vec, args.edges) if args.edges else []
    return Scene(points=pts, labels=labels, groups=speakers, edges=edges, axes=axes, title=args.title)


def author_scene(df, emb, args):
    """Original spec: one point per author, sized by paper count, coloured by HDBSCAN cluster."""
    authors, X = author_vectors(df, emb, args.min_papers)
    xyz = reduce_3d(X, args.reducer, args.seed, args.n_neighbors, args.min_dist)
    if args.no_cluster:
        labels, group_label = np.zeros(len(authors), int), {0: "all authors"}
        kw = None
    else:
        labels = cluster(X, args.seed, args.min_cluster_size)
        kw = cluster_keywords(df, authors, labels)
        group_label = dict(zip(kw["cluster"], kw["label"]))
    pts = authors.assign(x=xyz[:, 0], y=xyz[:, 1], z=xyz[:, 2], kind="author",
                         group=[group_label[l] for l in labels], cluster=labels,
                         size=sqrt_sizes(authors["papers"], 8, 28))
    pts["hover"] = [f"<b>{a}</b><br>{p} abstracts<br>{g}" for a, p, g in zip(pts["author"], pts["papers"], pts["group"])]
    top = pts.sort_values("papers", ascending=False).head(args.label_top)
    lab = pd.DataFrame({"x": top["x"], "y": top["y"], "z": top["z"], "text": top["author"], "group": top["group"]})
    groups = [group_label[c] for c in sorted(set(labels)) if c != -1] + (["unclustered"] if -1 in labels else [])
    return Scene(points=pts, labels=lab.reset_index(drop=True), groups=groups, title=args.title), kw


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default="data/abstracts.csv", help="CSV/JSON with 'authors' and 'abstract' columns, or a folder of .txt")
    ap.add_argument("--talks", default="../src/data.js", help="website data.js to pull the HAI101 talk abstracts from ('' to skip)")
    ap.add_argument("--level", choices=["abstract", "author"], default="abstract", help="one point per paper (default) or per author")
    ap.add_argument("--out-dir", default="output")
    ap.add_argument("--cache-dir", default="cache")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="sentence-transformers model (falls back to all-mpnet-base-v2)")
    ap.add_argument("--min-papers", type=int, default=2, help="drop authors with fewer abstracts")
    ap.add_argument("--max-papers", type=int, default=80, help="keep at most this many (most recent) abstracts per author; 0 = all")
    ap.add_argument("--reducer", choices=["umap", "pca", "tsne", "axes"], default="umap")
    ap.add_argument("--n-neighbors", type=int, default=15, help="UMAP n_neighbors (clamped to n-1)")
    ap.add_argument("--min-dist", type=float, default=0.1, help="UMAP min_dist")
    ap.add_argument("--edges", type=int, default=1, help="abstract level: link each speaker centroid to its k nearest (0 = none)")
    ap.add_argument("--no-cluster", action="store_true", help="author level: skip HDBSCAN")
    ap.add_argument("--min-cluster-size", type=int, default=None, help="HDBSCAN min_cluster_size (default 2 if <30 authors, else 5)")
    ap.add_argument("--label-top", type=int, default=25, help="author level: permanent labels for the top N authors")
    ap.add_argument("--theme", choices=["canvas", "dark", "light"], default="canvas", help="canvas = HAI101 website style")
    ap.add_argument("--title", default="Where the speakers' work sits")
    ap.add_argument("--kicker", default="Semantic map · HAI101", help="small uppercase line above the title")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--hide-talks", action="store_true", help="abstract level: leave the HAI101 talk squares out of the plot (layout unchanged)")
    ap.add_argument("--web", action="store_true", help="animation without heading/legend/note and with bigger label bars, for embedding in the site")
    ap.add_argument("--no-animation", action="store_true")
    ap.add_argument("--px", type=int, default=1080, help="animation frame size in pixels (square); marker and label sizes scale with it")
    ap.add_argument("--from-coords", action="store_true", help="skip embedding/reduction; redraw from the saved coords")
    args = ap.parse_args()

    seed_everything(args.seed)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written, summary = [], {}
    coords_path = out / ("author_coords.csv" if args.level == "author" else "abstract_coords.csv")
    labels_path = out / "label_coords.csv"

    if args.from_coords:
        pts, lab = pd.read_csv(coords_path), pd.read_csv(labels_path)
        groups = list(dict.fromkeys(lab["group"])) if args.level == "abstract" else list(dict.fromkeys(pts["group"]))
        scene = Scene(points=pts, labels=lab, groups=groups, title=args.title)
        print(f"[coords] {len(pts)} points from {coords_path}")
    else:
        df, _ = load_and_explode(args.data)
        if args.max_papers and "year" in df:
            # Prolific authors would otherwise dominate the layout; keep their most recent work.
            before = len(df)
            df = (df.assign(_y=pd.to_numeric(df["year"], errors="coerce").fillna(0))
                    .sort_values("_y", ascending=False).groupby("author").head(args.max_papers)
                    .drop(columns="_y").sort_index().reset_index(drop=True))
            print(f"[load] --max-papers {args.max_papers}: {before} -> {len(df)} pairs")
        uniq = df["abstract"].drop_duplicates().tolist()
        emb_uniq, model_used = embed_abstracts(uniq, args.model, args.cache_dir)
        row_of = {a: i for i, a in enumerate(uniq)}
        emb = emb_uniq[[row_of[a] for a in df["abstract"]]]
        summary.update(abstracts=len(uniq), pairs=len(df), model=model_used, reducer=args.reducer)

        if args.level == "abstract":
            talks = load_talks(args.talks) if args.talks else pd.DataFrame(columns=["speaker_id"])
            scene = abstract_scene(df, emb, talks, args, lambda t: embed_abstracts(t, model_used, args.cache_dir))
            summary.update(speakers=len(scene.groups), talks=int((scene.points["kind"] == "talk").sum()))
        else:
            scene, kw = author_scene(df, emb, args)
            if kw is not None:
                kw_path = out / "cluster_keywords.csv"
                kw.to_csv(kw_path, index=False)
                written.append(kw_path)
                summary["clusters"] = int((kw["cluster"] != -1).sum())
                print("[keywords]")
                for _, r in kw.iterrows():
                    print(f"       {r['cluster']:>3}  ({r['n_authors']} authors)  {r['keywords']}")
        scene.points.to_csv(coords_path, index=False)
        scene.labels.to_csv(labels_path, index=False)
        written += [coords_path, labels_path]

    if args.hide_talks:
        scene.points = scene.points[scene.points["kind"] != "talk"].reset_index(drop=True)

    html = out / "author_map_3d.html"
    scene.kicker = args.kicker
    write_html(plot_scene(scene, args.theme), html, args.theme, cdn=args.web)
    written.append(html)
    if not args.no_animation:
        written += animate(scene, out, args.theme, px=args.px, web=args.web)

    print("\n== summary ==")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("  files:")
    for p in written:
        print(f"    {p}  ({Path(p).stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
