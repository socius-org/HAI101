# Semantic map of the HAI101 speakers

Maps the speakers' published abstracts into 3D and renders an interactive Plotly map plus a
rotating-camera animation.

```
python fetch_openalex.py     # 1. speakers' abstracts from OpenAlex -> data/abstracts.csv
python main.py               # 2. embed, reduce, plot, animate -> output/
```

Two levels:

- **`--level abstract` (default).** Every paper is a point coloured by speaker (their 80 most recent,
  `--max-papers`), each speaker's HAI101 talk (pulled from `../src/data.js`) is a square, and the
  speaker's name sits on their medoid paper. Thin lines join each speaker to their nearest neighbour
  in embedding space (`--edges`). No clustering step: the speakers are the groups, and the picture
  shows how wide each one's work spreads and where the talk sits in it.
- **`--level author`.** The original brief: one point per speaker (mean of their abstracts, sized by
  paper count), HDBSCAN clusters with c-TF-IDF keywords. With 12 speakers this is sparse and
  seed-sensitive; it is kept for comparison.

`--reducer axes` replaces UMAP with three interpretable axes scored against anchor sentences
(human minds vs artificial systems; language/LLMs vs perception/decisions/agents; theory/philosophy
vs empirical/benchmarks; see `AXES` in `src/reduce.py`).

## How it works

1. **Fetch** (`fetch_openalex.py`): each speaker in `src/data.js` is mapped to an OpenAlex author
   profile (by name + institution, or pinned by id where names are ambiguous) and every work with an
   abstract of 200+ characters is written to `data/abstracts.csv` (`authors`, `abstract`, `title`,
   `year`, `coauthors`, `openalex_id`). The chosen profiles are listed in `data/authors_resolved.csv`;
   check that file if a speaker looks out of place.
2. **Load** (`src/load.py`): drops empty abstracts, strips "Abstract:" prefixes and copyright lines,
   normalises author names, explodes multi-author cells (`;` or `,`) to one row per (author, abstract)
   and prints the 20 most frequent names so near-duplicates can be spotted. Names are never merged
   automatically.
3. **Embed** (`src/embed.py`): sentence-transformers, `allenai/specter2_base` by default (CLS pooling,
   as SPECTER expects), falling back to `all-mpnet-base-v2`. Each unique abstract is encoded once and
   cached in `cache/embeddings.npy` + `cache/embeddings.json` keyed by a SHA-1 of the text.
4. **Author vectors** (`src/reduce.py`): mean of the author's abstract embeddings, L2-normalised;
   authors with fewer than `--min-papers` abstracts are dropped.
5. **Reduce**: UMAP to 3D (cosine, `n_neighbors` 15 clamped to n-1, `min_dist` 0.1, seed 42), or PCA /
   t-SNE. Clustering runs HDBSCAN on the high-dimensional author vectors (or on a 10D UMAP when there
   are 30+ authors), never on the 3D coordinates. Each cluster gets 5 c-TF-IDF keywords.
6. **Plot** (`src/plot.py`): `output/author_map_3d.html`, coloured by cluster, marker size ~ sqrt(papers),
   hover shows name, paper count and cluster keywords, permanent labels for the top `--label-top`.
7. **Animate** (`src/animate.py`): matplotlib orbit, azimuth 0-360 in 2-degree steps at 20 degrees
   elevation, 30 fps, 1080x1080 MP4 (ffmpeg on PATH or the one bundled with `imageio-ffmpeg`), and a
   600 px / 15 fps GIF. Stills at azimuth 0, 90 and 180 are saved as `frame_az*.png`.

## Options (`python main.py --help`)

| option | default | meaning |
|---|---|---|
| `--data` | `data/abstracts.csv` | CSV or JSON with `authors` + `abstract` columns, or a folder of `.txt` (first line = authors) |
| `--model` | `allenai/specter2_base` | sentence-transformers model |
| `--level` | `abstract` | `abstract` (paper points, talk squares) or `author` (one point per speaker) |
| `--talks` | `../src/data.js` | where to read the HAI101 talk abstracts (`''` to skip) |
| `--min-papers` | 2 | drop authors with fewer abstracts |
| `--max-papers` | 80 | keep each author's N most recent abstracts (0 = all) |
| `--edges` | 1 | abstract level: lines from each speaker to their k nearest speakers (0 = none) |
| `--reducer` | `umap` | `umap`, `pca`, `tsne` or `axes` |
| `--n-neighbors`, `--min-dist` | 15, 0.1 | UMAP parameters |
| `--no-cluster` | off | skip HDBSCAN; colour by a `field` column if present |
| `--min-cluster-size` | 2 (<30 authors) / 5 | HDBSCAN parameter |
| `--label-top` | 25 | number of authors with permanent labels |
| `--theme` | `dark` | `dark` or `light` |
| `--title` | HAI101 title | plot/animation title |
| `--seed` | 42 | seed for numpy, torch, UMAP, t-SNE |
| `--no-animation` | off | plot only |
| `--from-coords` | off | re-render from `output/author_coords.csv` without recomputing embeddings |
| `--out-dir`, `--cache-dir` | `output`, `cache` | locations |

## Outputs

- `output/author_map_3d.html`: interactive map (self-contained, open in a browser)
- `output/author_rotation.mp4`, `output/author_rotation.gif`: rotating view
- `output/abstract_coords.csv` + `output/label_coords.csv`: every point (paper or talk) and label with x/y/z
- `output/author_coords.csv`, `output/cluster_keywords.csv`: author-level outputs (`--level author`)
- `output/frame_az000.png`, `frame_az090.png`, `frame_az180.png`: stills for checking labels

## Install

```
pip install -r requirements.txt
```

`sentence-transformers` pulls in PyTorch (~1 GB). The first run downloads the embedding model.

## Notes on the data

- Abstracts come from OpenAlex, so only works it indexes with an abstract are included. Co-authored
  papers count toward the speaker only (`authors` holds the speaker's name; co-authors are kept in a
  separate column and are not exploded).
- OpenAlex sometimes splits one person over several profiles or merges namesakes into one. Pinned ids
  and the Penn-only filter for Helen Jin handle the cases found so far; see `SPEAKERS` in
  `fetch_openalex.py`.
