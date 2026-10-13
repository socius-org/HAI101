"""Steps 3-4: author vectors, 3D reduction, optional clustering with keyword labels."""
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.manifold import TSNE


def author_vectors(df, emb, min_papers=2, center=True):
    """Mean of each author's abstract embeddings, L2-normalized. df rows align with emb rows.
    center: subtract the corpus mean first. Scientific-text encoders put every abstract in a narrow
    cone (pairwise cosine ~0.95 for anything), so without this the author means are all near-identical
    and neither UMAP nor HDBSCAN has much to work with."""
    mu = emb.mean(axis=0) if center else 0.0
    groups = df.groupby("author").indices
    names, vecs, counts = [], [], []
    for name, idx in sorted(groups.items()):
        if len(idx) < min_papers:
            continue
        v = (emb[idx] - mu).mean(axis=0)
        names.append(name)
        vecs.append(v / (np.linalg.norm(v) or 1.0))
        counts.append(len(idx))
    dropped = len(groups) - len(names)
    print(f"[authors] {len(names)} authors kept with >= {min_papers} abstracts, {dropped} dropped")
    if not names:
        raise SystemExit("no authors left after --min-papers filter")
    return pd.DataFrame({"author": names, "papers": counts}), np.stack(vecs)


def center_normalize(emb):
    """Subtract the corpus mean and re-normalise rows; see author_vectors for why."""
    Z = emb - emb.mean(axis=0)
    return Z / np.maximum(np.linalg.norm(Z, axis=1, keepdims=True), 1e-9)


# Interpretable axes for --reducer axes: each axis is scored as cos(e, positive) - cos(e, negative).
AXES = {
    "human minds <-> artificial systems": (
        "Studies of human minds: perception, cognition and behaviour, with psychology experiments on people.",
        "Engineering of artificial systems: algorithms, neural network architectures, training and optimisation.",
    ),
    "language & LLMs <-> perception, decisions & agents": (
        "Language, text, large language models and natural language processing.",
        "Perception, decision-making, reinforcement learning, agents and control.",
    ),
    "theory & philosophy <-> empirical & benchmarks": (
        "Philosophy, theory and conceptual analysis of science, mind and explanation.",
        "Empirical results, datasets, benchmarks and experiments with measured performance.",
    ),
}


def axes_projection(emb, model, axes=AXES):
    """Project embeddings onto anchor-defined axes. emb rows must be unit vectors from `model`."""
    anchors = model.encode([s for pair in axes.values() for s in pair], normalize_embeddings=True)
    pos, neg = anchors[0::2], anchors[1::2]
    return emb @ pos.T - emb @ neg.T


def reduce_3d(X, reducer="umap", seed=42, n_neighbors=15, min_dist=0.1):
    n = len(X)
    if reducer == "pca":
        return PCA(n_components=3, random_state=seed).fit_transform(X)
    if reducer == "tsne":
        perplexity = min(30, max(2, (n - 1) // 3))
        return TSNE(n_components=3, metric="cosine", perplexity=perplexity, init="pca",
                    random_state=seed).fit_transform(X)
    if reducer == "umap":
        import umap

        k = min(n_neighbors, n - 1)  # UMAP needs n_neighbors < n_samples
        if k < n_neighbors:
            print(f"[reduce] only {n} points: n_neighbors {n_neighbors} -> {k}")
        return umap.UMAP(n_components=3, metric="cosine", n_neighbors=k, min_dist=min_dist,
                         random_state=seed).fit_transform(X)
    raise ValueError(f"unknown reducer {reducer}")


def cluster(X, seed=42, min_cluster_size=None):
    """HDBSCAN on the normalized high-dim vectors (small n) or a 10D UMAP of them (large n).
    Never on the 3D plot coordinates. Returns labels; -1 = noise."""
    import hdbscan

    n = len(X)
    min_cluster_size = min_cluster_size or (2 if n < 30 else 5)
    if n >= 30:
        import umap

        k = min(15, n - 1)
        Z = umap.UMAP(n_components=10, metric="cosine", n_neighbors=k, min_dist=0.0,
                      random_state=seed).fit_transform(X)
        space = "10D UMAP"
    else:
        Z = X  # rows are unit vectors, so euclidean distance orders like cosine distance
        space = f"{X.shape[1]}D embedding"
    labels = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=1).fit_predict(Z)
    n_clusters = len(set(labels) - {-1})
    print(f"[cluster] HDBSCAN on {space}, min_cluster_size={min_cluster_size}: "
          f"{n_clusters} clusters, {(labels == -1).sum()} unclustered")
    if n_clusters == 0 and n >= 4:
        # Density-based clustering has nothing to grip on a handful of points; fall back to
        # agglomerative (cosine, average linkage) with k picked by silhouette.
        from sklearn.cluster import AgglomerativeClustering
        from sklearn.metrics import silhouette_score

        best = None
        for k in range(2, min(6, n - 1) + 1):
            lab = AgglomerativeClustering(n_clusters=k, metric="cosine", linkage="average").fit_predict(X)
            score = silhouette_score(X, lab, metric="cosine")
            if best is None or score > best[0]:
                best = (score, k, lab)
        score, k, labels = best
        print(f"[cluster] fallback: agglomerative (cosine, average) k={k}, silhouette={score:.2f}")
    return labels


def cluster_keywords(df, authors, labels, top_k=5, min_df=3):
    """c-TF-IDF (as in BERTopic): term frequency within the cluster's pooled abstracts, weighted by
    log(1 + A / tf_total) where A is the average cluster length. The vocabulary is fitted on the
    individual abstracts with min_df so a term must occur in several papers to be a label."""
    cl = dict(zip(authors["author"], labels))
    abstracts = df["abstract"].drop_duplicates()
    vec = CountVectorizer(stop_words="english", ngram_range=(1, 2), min_df=min_df,
                          token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z-]{2,}\b")
    vec.fit(abstracts)
    terms = np.array(vec.get_feature_names_out())

    docs, ids = [], []
    for c in sorted(set(labels)):
        members = [a for a, l in cl.items() if l == c]
        docs.append(" ".join(df.loc[df["author"].isin(members), "abstract"].drop_duplicates()))
        ids.append(c)
    counts = vec.transform(docs).toarray().astype(float)
    tf = counts / np.maximum(counts.sum(axis=1, keepdims=True), 1)
    avg_len = counts.sum() / len(docs)
    idf = np.log1p(avg_len / np.maximum(counts.sum(axis=0), 1))
    M = tf * idf
    rows = []
    for c, row in zip(ids, M):
        top = terms[np.argsort(row)[::-1][:top_k]]
        members = [a for a, l in cl.items() if l == c]
        rows.append({"cluster": c, "label": "unclustered" if c == -1 else ", ".join(top[:3]),
                     "keywords": ", ".join(top), "n_authors": len(members), "authors": "; ".join(members)})
    return pd.DataFrame(rows)
