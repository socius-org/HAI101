"""Step 6: rotating-camera animation of a Scene with matplotlib 3D (MP4 via ffmpeg, GIF via pillow)."""
import itertools
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter  # noqa: E402

from .plot import FONT_FILES, THEMES  # noqa: E402

# Fonts shipped with the website / posters; fall back to matplotlib's defaults if missing.
for f in FONT_FILES:
    if f.exists():
        font_manager.fontManager.addfont(str(f))
_names = {f.name for f in font_manager.fontManager.ttflist}
SANS = "General Sans" if "General Sans" in _names else "DejaVu Sans"
SLAB = "Montagu Slab" if "Montagu Slab" in _names else "DejaVu Serif"


def ffmpeg_path():
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def draw_cube(ax, lo, hi, color, scale):
    """Thin wireframe box around the point cloud's bounding box: the traditional 3D-figure frame,
    without ticks. lo/hi are per-axis extents (already centred)."""
    corners = list(itertools.product(*[(l, h) for l, h in zip(lo, hi)]))
    for a in corners:
        for b in corners:
            if a < b and sum(x != y for x, y in zip(a, b)) == 1:
                ax.plot(*zip(a, b), color=color, lw=0.7 * scale, alpha=0.9, zorder=0)


def fit_axes(fig, ax, corners, elev, region=(0.06, 0.13, 0.94, 0.84)):
    """Scale and shift the 3D axes so the projected `corners` stay inside `region` (figure fractions:
    left, bottom, right, top) at every azimuth. mplot3d pads the cube heavily and the padding depends
    on the cloud's shape, so a fixed zoom either wastes space (flat clouds) or collides with the
    heading (cubic ones)."""
    from mpl_toolkits.mplot3d import proj3d

    fig.canvas.draw()
    to_fig = fig.transFigure.inverted()
    xs, ys = [], []
    for az in range(0, 360, 15):
        ax.view_init(elev=elev, azim=az)
        M = ax.get_proj()
        for c in corners:
            x2, y2, _ = proj3d.proj_transform(*c, M)
            fx, fy = to_fig.transform(ax.transData.transform((x2, y2)))
            xs.append(fx)
            ys.append(fy)
    bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
    l, b, w, h = ax.get_position().bounds
    c0 = (l + w / 2, b + h / 2)
    s = min((region[2] - region[0]) / (bx1 - bx0), (region[3] - region[1]) / (by1 - by0))
    # Scaling the axes about its centre scales the projection about the same point.
    pc = (c0[0] + s * ((bx0 + bx1) / 2 - c0[0]), c0[1] + s * ((by0 + by1) / 2 - c0[1]))
    rc = ((region[0] + region[2]) / 2, (region[1] + region[3]) / 2)
    nw, nh = w * s, h * s
    ax.set_position([c0[0] - nw / 2 + (rc[0] - pc[0]), c0[1] - nh / 2 + (rc[1] - pc[1]), nw, nh])


def contrast_text(hex_bg, T):
    """Ink on light bars (ochre, sand), paper on dark ones."""
    r, g, b = (int(hex_bg[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return T["ink"] if 0.299 * r + 0.587 * g + 0.114 * b > 0.5 else T["label_fg"]


def build_figure(scene, theme, px, dpi=100, web=False):
    """web=True: no heading, legend or note, bigger label bars; for embedding at a small size where
    the page supplies the caption and the bars are the only identification."""
    T = THEMES[theme]
    canvas = theme == "canvas"
    pts, lab = scene.points, scene.labels
    scale = px / 1080  # keep marker and font sizes proportional when rendering the small GIF

    fig = plt.figure(figsize=(px / dpi, px / dpi), dpi=dpi, facecolor=T["bg"])
    ax = fig.add_subplot(111, projection="3d", facecolor=T["bg"])
    # Respect our zorder (box < papers < talks < labels) instead of mplot3d's depth sort, so label
    # bars are never hidden behind points.
    ax.computed_zorder = False
    # Centre the cloud and fix equal limits so the orbit is smooth and nothing jumps between frames.
    xyz = pts[["x", "y", "z"]].to_numpy()
    centre = (xyz.max(0) + xyz.min(0)) / 2
    half = (xyz.max(0) - xyz.min(0)).max() / 2 * 1.08 or 1.0
    pad = (xyz.max(0) - xyz.min(0)) * 0.06
    box_lo, box_hi = xyz.min(0) - centre - pad, xyz.max(0) - centre + pad
    if canvas:
        draw_cube(ax, box_lo, box_hi, T["grid"], scale)

    for g in scene.groups:
        col = scene.color(g, theme)
        papers = pts[(pts["group"] == g) & (pts["kind"] != "talk")]
        if len(papers):
            p = papers[["x", "y", "z"]].to_numpy() - centre
            # size is in Plotly pixels (diameter); matplotlib wants point area, and author-level
            # markers (8-28 px) need a gentler factor than the 4 px paper dots.
            is_paper = papers["kind"].eq("paper").all()
            factor = (3.0 if web else 2.2) if is_paper else 1.1
            ax.scatter(p[:, 0], p[:, 1], p[:, 2], s=(papers["size"] * factor * scale) ** 2, c=col,
                       alpha=0.85 if canvas else (0.55 if is_paper else 0.9),
                       edgecolors=T["edge"] if canvas else "none", linewidths=0.4 * scale, depthshade=False)
        talks = pts[(pts["group"] == g) & (pts["kind"] == "talk")]
        if len(talks):
            t = talks[["x", "y", "z"]].to_numpy() - centre
            ax.scatter(t[:, 0], t[:, 1], t[:, 2], s=(talks["size"] * 1.9 * scale) ** 2, c=col, marker="s",
                       edgecolors=T["ink"], linewidths=0.7 * scale, depthshade=False, zorder=5)

    for (i, j) in scene.edges:
        a, b = lab.iloc[i][["x", "y", "z"]].to_numpy() - centre, lab.iloc[j][["x", "y", "z"]].to_numpy() - centre
        ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color=T["muted"], lw=0.8 * scale, alpha=0.45)
    text_col = "short" if "short" in lab else "text"
    for _, r in lab.iterrows():
        x, y, z = r[["x", "y", "z"]].to_numpy() - centre
        if canvas:  # poster-style label bar in the speaker's colour, text in ink or paper for contrast
            bg = scene.color(r["group"], theme)
            ax.text(x, y, z + half * 0.035, r[text_col], fontsize=(15 if web else 8.5) * scale,
                    color=contrast_text(bg, T), ha="center", va="bottom", family=SANS, weight=500, zorder=10,
                    bbox=dict(boxstyle="square,pad=0.35", facecolor=bg, edgecolor=T["ink"], linewidth=0.5 * scale))
        else:
            ax.text(x, y, z + half * 0.03, r[text_col], fontsize=9 * scale, color=T["ink"], ha="center",
                    va="bottom", family="serif", zorder=10,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor=T["bg"], edgecolor="none", alpha=0.7))

    for lim in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
        lim(-half, half)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    # Zoom so the points (plus headroom for labels) fill the space between heading and legend. The box
    # lines may run a little past that at the widest azimuths, which is fine.
    label_room = (xyz.max(0) - xyz.min(0)).max() * 0.07
    lo, hi = xyz.min(0) - centre, xyz.max(0) - centre + [0, 0, label_room]
    corners = list(itertools.product(*[(l, h) for l, h in zip(lo, hi)]))
    fit_axes(fig, ax, corners, elev=20, region=(0.02, 0.03, 0.98, 0.96) if web else (0.03, 0.12, 0.97, 0.86))
    if web:
        return fig, ax

    # Heading block, left-aligned like a website section: brick kicker, slab title.
    if canvas:
        fig.text(0.05, 0.945, scene.kicker.upper(), color=T["accent"], fontsize=7.5 * scale, family=SANS,
                 weight=500, ha="left", va="top")
        fig.text(0.05, 0.915, scene.title, color=T["ink"], fontsize=17 * scale, family=SLAB, ha="left", va="top",
                 wrap=True)
    else:
        fig.suptitle(scene.title, color=T["ink"], fontsize=11 * scale, family="serif", y=0.965)

    has_talks = pts["kind"].eq("talk").any()
    if scene.axes:
        note = "axes: " + "  ·  ".join(scene.axes)
    elif pts["kind"].eq("paper").any():
        note = "dots: papers (most recent per speaker)   ·   " + ("squares: HAI101 talks   ·   " if has_talks else "")             + "labels: speaker's medoid paper"
    else:
        note = ""
    if note:
        fig.text(0.95, 0.04, note, color=T["muted"], fontsize=7 * scale, ha="right", family=SANS if canvas else "serif")
    # Figure-level legend: the axes are oversized for zoom, so an axes legend would sit off-canvas.
    handles = [plt.Line2D([], [], marker="s" if canvas else "o", ls="", color=scene.color(g, theme),
                          markersize=6.5 * scale, label=str(g)) for g in scene.groups]
    leg = fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.045, 0.035), frameon=False,
                     fontsize=7.5 * scale, labelcolor=T["ink"], ncol=2 if len(scene.groups) > 8 else 1,
                     handletextpad=0.4, columnspacing=1.2, labelspacing=0.55,
                     prop=dict(family=SANS if canvas else "serif", size=7.5 * scale))
    for t in leg.get_texts():
        t.set_color(T["ink"])
    return fig, ax


def animate(scene, out_dir, theme="canvas", step=2, elev=20, fps=30, px=1080, gif_px=600, gif_fps=15,
            frames_png=(0, 90, 180), web=False):
    """Writes author_rotation.mp4 (if ffmpeg is available), author_rotation.gif and still frames at
    the azimuths in frames_png."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    azimuths = list(range(0, 360, step))

    fig, ax = build_figure(scene, theme, px, web=web)
    for az in frames_png:
        ax.view_init(elev=elev, azim=az)
        p = out_dir / f"frame_az{az:03d}.png"
        fig.savefig(p, dpi=fig.dpi, facecolor=fig.get_facecolor())
        written.append(p)

    def turn(i):
        ax.view_init(elev=elev, azim=azimuths[i])
        return ()

    ff = ffmpeg_path()
    if ff:
        matplotlib.rcParams["animation.ffmpeg_path"] = ff
        anim = FuncAnimation(fig, turn, frames=len(azimuths), interval=1000 / fps, blit=False)
        mp4 = out_dir / "author_rotation.mp4"
        anim.save(mp4, writer=FFMpegWriter(fps=fps, bitrate=5000, extra_args=["-pix_fmt", "yuv420p"]),
                  dpi=fig.dpi, savefig_kwargs={"facecolor": fig.get_facecolor()})
        written.append(mp4)
        print(f"[animate] {mp4} ({len(azimuths)} frames @ {fps} fps, {px}px)")
    else:
        print("[animate] no ffmpeg found (install ffmpeg or `pip install imageio-ffmpeg`): GIF only")
    plt.close(fig)

    # GIF: smaller canvas, every other frame, so the file stays a few MB.
    fig, ax = build_figure(scene, theme, gif_px, web=web)
    gif_az = azimuths[:: max(1, round(fps / gif_fps))]

    def turn_gif(i):
        ax.view_init(elev=elev, azim=gif_az[i])
        return ()

    anim = FuncAnimation(fig, turn_gif, frames=len(gif_az), interval=1000 / gif_fps, blit=False)
    gif = out_dir / "author_rotation.gif"
    anim.save(gif, writer=PillowWriter(fps=gif_fps), dpi=fig.dpi, savefig_kwargs={"facecolor": fig.get_facecolor()})
    plt.close(fig)
    written.append(gif)
    print(f"[animate] {gif} ({len(gif_az)} frames @ {gif_fps} fps, {gif_px}px)")
    return written
