"""Step 5: interactive Plotly scatter_3d.

Both renderers (this and animate.py) draw a `Scene`:
  points  DataFrame: x, y, z, group, hover, size, kind ('paper' | 'talk' | 'author')
  labels  DataFrame: x, y, z, text, [short], group   (one permanent label per group, or top-N authors)
  edges   list of (label_index, label_index)          (thin lines between labels)
  groups  list of group names in colour order
  axes    optional (x, y, z) axis titles when the reducer produces meaningful axes
"""
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

REPO = Path(__file__).resolve().parents[2]
FONT_FILES = [REPO / "public/fonts/GeneralSans-Regular.otf", REPO / "public/fonts/GeneralSans-Medium.otf",
              REPO / "poster/build/fonts/MontaguSlab-Regular48.ttf", REPO / "poster/build/fonts/MontaguSlab-Light144.ttf"]

# Themes. `canvas` follows the HAI101 website / poster: linen ground, ink type, brick accents,
# label bars in ink with paper text, GeneralSans body + Montagu Slab display.
THEMES = {
    "canvas": dict(
        bg="#e6dfcd", ink="#1c1c1e", muted="#6f6a66", grid="#cabc9f", accent="#a5432a",
        label_bg="#1c1c1e", label_fg="#f1f0ef", edge="#f1f0ef",
        sans="GeneralSans, 'Helvetica Neue', Arial, sans-serif", slab="'Montagu Slab', Georgia, serif",
        # muted hues sampled around the key art: brick, moss, ochre, slate, plum, teal, rust, olive, navy, rose, sand, iron
        palette=["#a5432a", "#2e5b34", "#b98a2f", "#3f5f8a", "#6e3b5c", "#2f6f6a", "#c86a3a", "#6f7a2f",
                 "#2d3e63", "#b3686a", "#8c7349", "#4e4a52", "#9a948c"],
    ),
    "dark": dict(
        bg="#1a1917", ink="#f1f0ef", muted="#b9b4b0", grid="#3a3734", accent="#e2b54e",
        label_bg="#1a1917", label_fg="#f1f0ef", edge="#1a1917",
        sans="Georgia, serif", slab="Georgia, serif",
        palette=["#e5533d", "#3aa65a", "#f2c14e", "#4f8fe6", "#a875f0", "#2fc4c4", "#e55fc3",
                 "#ff8c2b", "#c6e03a", "#d9b38c", "#ff9e9e", "#8fcbff", "#9a948c"],
    ),
}
THEMES["light"] = dict(THEMES["dark"], bg="#ffffff", ink="#1a1917", muted="#6f6a66", grid="#e3e0d8",
                       label_bg="#ffffff", label_fg="#1a1917", edge="#ffffff")
NOISE_INDEX = -1  # last palette entry is the grey for unclustered


@dataclass
class Scene:
    points: pd.DataFrame
    labels: pd.DataFrame
    groups: list
    edges: list = field(default_factory=list)
    axes: tuple = None
    title: str = ""
    kicker: str = "Semantic map · HAI101"

    def color(self, group, theme="canvas"):
        pal = THEMES[theme]["palette"]
        if group in (-1, "unclustered"):
            return pal[NOISE_INDEX]
        return pal[self.groups.index(group) % (len(pal) - 1)]


def sqrt_sizes(counts, lo, hi):
    s = np.sqrt(np.asarray(counts, dtype=float))
    s = (s - s.min()) / (s.max() - s.min() or 1.0)
    return lo + s * (hi - lo)


def plot_scene(scene, theme="canvas"):
    T = THEMES[theme]
    pts, lab = scene.points, scene.labels
    fig = go.Figure()

    for g in scene.groups:
        col = scene.color(g, theme)
        papers = pts[(pts["group"] == g) & (pts["kind"] != "talk")]
        if len(papers):
            fig.add_trace(go.Scatter3d(
                x=papers["x"], y=papers["y"], z=papers["z"], mode="markers", name=str(g), legendgroup=str(g),
                marker=dict(size=papers["size"], color=col, opacity=0.85, line=dict(width=0.5, color=T["edge"])),
                text=papers["hover"], hovertemplate="%{text}<extra></extra>",
            ))
        talks = pts[(pts["group"] == g) & (pts["kind"] == "talk")]
        if len(talks):
            fig.add_trace(go.Scatter3d(
                x=talks["x"], y=talks["y"], z=talks["z"], mode="markers", name=f"{g} (HAI101 talk)",
                legendgroup=str(g), showlegend=False,
                marker=dict(size=talks["size"], color=col, symbol="square", opacity=1,
                            line=dict(width=2, color=T["ink"])),
                text=talks["hover"], hovertemplate="%{text}<extra></extra>",
            ))

    for (i, j) in scene.edges:
        a, b = lab.iloc[i], lab.iloc[j]
        fig.add_trace(go.Scatter3d(x=[a.x, b.x], y=[a.y, b.y], z=[a.z, b.z], mode="lines",
                                   line=dict(color=T["muted"], width=1.5), opacity=0.5,
                                   hoverinfo="skip", showlegend=False))
    if len(lab):
        fig.add_trace(go.Scatter3d(
            x=lab["x"], y=lab["y"], z=lab["z"], mode="text", text=lab["text"], textposition="top center",
            textfont=dict(size=13, color=T["ink"], family=T["sans"]),
            hoverinfo="skip", showlegend=False,
        ))

    def axis(title):
        return dict(title=dict(text=title or "", font=dict(size=11, color=T["muted"])), showticklabels=False,
                    showgrid=True, zeroline=False, gridcolor=T["grid"], gridwidth=1,
                    backgroundcolor=T["bg"], showbackground=True, showline=True, linecolor=T["grid"])

    ax = scene.axes or ("", "", "")
    fig.update_layout(
        title=dict(text=f"<span style='font-size:11px;letter-spacing:0.12em;color:{T['accent']};font-family:{T['sans']}'>"
                        f"{scene.kicker.upper()}</span><br><span style='font-family:{T['slab']};font-size:26px'>{scene.title}</span>",
                   x=0.03, y=0.96, yanchor="top", font=dict(color=T["ink"])),
        paper_bgcolor=T["bg"], font=dict(color=T["ink"], family=T["sans"]),
        scene=dict(xaxis=axis(ax[0]), yaxis=axis(ax[1]), zaxis=axis(ax[2]), aspectmode="data",
                   camera=dict(eye=dict(x=1.5, y=1.5, z=0.8))),
        legend=dict(title=dict(text="Speakers · click to toggle", font=dict(size=12)), itemsizing="constant",
                    bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
        hoverlabel=dict(bgcolor=T["label_bg"], font=dict(color=T["label_fg"], family=T["sans"], size=12),
                        bordercolor=T["label_bg"]),
        margin=dict(l=0, r=0, t=90, b=0),
    )
    return fig


def write_html(fig, path, theme="canvas", cdn=False):
    """Plotly HTML. cdn=True loads plotly.js from its CDN (file ~0.3 MB instead of ~4.8 MB) and the
    site's GeneralSans from ../fonts/, for serving from the website's public/ folder."""
    html = fig.to_html(include_plotlyjs="cdn" if cdn else True, full_html=True)
    if theme == "canvas":
        head = ('<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
                '<title>HAI101 · Semantic map</title>'
                '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/'
                'css2?family=Montagu+Slab:opsz,wght@16..144,400&display=swap" rel="stylesheet">')
        if cdn:
            head += ("<style>@font-face{font-family:'GeneralSans';src:url('../fonts/GeneralSans-Regular.otf') format('opentype');"
                     "font-weight:400}@font-face{font-family:'GeneralSans';src:url('../fonts/GeneralSans-Medium.otf') "
                     "format('opentype');font-weight:500}html,body{margin:0;height:100%;background:#e6dfcd}"
                     ".plotly-graph-div{height:100vh!important}</style>")
        html = html.replace("<head>", "<head>" + head, 1)
    Path(path).write_text(html, encoding="utf-8")
