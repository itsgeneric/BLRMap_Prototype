"""
Generate placeholder figures for Paper 2 that cannot be compiled from LaTeX in this environment.

Figures generated:
  - figures/fig0_framework_arch.pdf / .png  : System architecture block diagram
  - figures/fig_pilot_casestudy.pdf / .png  : Composite of one pilot pair screenshots

Run from: Paper_2_Full_Latex/
"""

import os
import sys

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Figure 0: System architecture block diagram
# ---------------------------------------------------------------------------

def make_arch_figure():
    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # Helper: draw a rounded rectangle with centred text
    def box(x, y, w, h, text, fc="#d4e6f1", ec="#2874a6", fontsize=7, bold=False):
        rect = FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.08",
            facecolor=fc, edgecolor=ec, linewidth=1.0, zorder=2
        )
        ax.add_patch(rect)
        weight = "bold" if bold else "normal"
        ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
                weight=weight, wrap=True, zorder=3)

    # Arrow helper
    def arr(x0, y0, x1, y1):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="->", color="#555555", lw=0.8),
                    zorder=1)

    # Nodes
    box(5.0, 4.5, 3.0, 0.65, "OSMnx Bengaluru Network\n(308K nodes, 744K raw edges)",
        fc="#fdfefe", ec="#888888", fontsize=6.5)
    box(5.0, 3.6, 2.6, 0.55, "Graph Manager\n(load, pre-process, snap)", fontsize=7)
    box(2.5, 2.5, 2.2, 0.55, "Shortest Mode\nA* (admissible h)", fc="#d5f5e3", ec="#1e8449", fontsize=7)
    box(7.5, 2.5, 2.2, 0.55, "Dynamic Mode\nA* + live traffic", fc="#fdebd0", ec="#ca6f1e", fontsize=7)
    box(5.0, 1.55, 2.4, 0.55, "Alternative Generator\n(Perpendicular Offset, K=3)", fc="#e8daef", ec="#7d3c98", fontsize=7)
    box(7.5, 1.55, 2.2, 0.55, "Google Routes API\n(congestion + ETA)", fc="#fdfefe", ec="#888888", fontsize=6.5)
    box(7.5, 0.60, 2.2, 0.55, "MongoDB\nSnapshot Store", fc="#fdfefe", ec="#888888", fontsize=6.5)

    # Edges
    arr(5.0, 4.17, 5.0, 3.88)
    arr(3.85, 3.60, 2.5, 2.78)
    arr(6.15, 3.60, 7.5, 2.78)
    arr(5.0, 3.33, 5.0, 1.83)
    arr(7.5, 2.22, 7.5, 1.83)
    arr(7.5, 2.78, 7.5, 1.83)
    arr(7.5, 1.28, 7.5, 0.88)

    ax.set_title("Fig. 1 — Framework Architecture (schematic)", fontsize=8, pad=4)
    fig.tight_layout(pad=0.3)

    out_png = os.path.join(FIGURES_DIR, "fig0_framework_arch.png")
    out_pdf = os.path.join(FIGURES_DIR, "fig0_framework_arch.pdf")
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_png}")
    print(f"Saved: {out_pdf}")


# ---------------------------------------------------------------------------
# Figure: Pilot case study composite (one pair, three platforms)
# ---------------------------------------------------------------------------

PILOT_IMAGES = {
    "Project (Dynamic)": r"C:\Users\comps\Desktop\Final Year Project\BLRMap_Prototype\comparision_images\routes\ags layout - bnmit\blrnav.png",
    "Google Maps\n(motorcycle tab)": r"C:\Users\comps\Desktop\Final Year Project\BLRMap_Prototype\comparision_images\routes\ags layout - bnmit\gmaps.png",
    "Waze\n(motorcycle type)": r"C:\Users\comps\Desktop\Final Year Project\BLRMap_Prototype\comparision_images\routes\ags layout - bnmit\waze.png",
}


def make_pilot_figure():
    """
    Compose three screenshots side-by-side.
    NOTE: The raw screenshots contain visible place names, map tiles, and third-party imagery.
    The figure is included for academic illustration; the author must confirm
    permissions and anonymisation requirements before journal submission.
    """
    images = {}
    for label, path in PILOT_IMAGES.items():
        try:
            import matplotlib.image as mpimg
            images[label] = mpimg.imread(path)
        except Exception as e:
            print(f"  Warning: cannot load {path}: {e}")

    if not images:
        print("  No pilot images loaded; skipping pilot figure.")
        return

    n = len(images)
    fig, axes = plt.subplots(1, n, figsize=(6.5, 3.5))
    if n == 1:
        axes = [axes]

    for ax, (label, img) in zip(axes, images.items()):
        ax.imshow(img)
        ax.set_title(label, fontsize=7, pad=3)
        ax.axis("off")

    fig.suptitle(
        "Pilot Pair B (Short, $<$5 km) — representative screenshots\n"
        "Screenshots contain third-party map tiles and place names; "
        "exact endpoints not disclosed.",
        fontsize=6.5, y=0.02
    )
    fig.tight_layout(rect=[0, 0.08, 1, 1])

    out_png = os.path.join(FIGURES_DIR, "fig_pilot_casestudy.png")
    out_pdf = os.path.join(FIGURES_DIR, "fig_pilot_casestudy.pdf")
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_png}")
    print(f"Saved: {out_pdf}")


if __name__ == "__main__":
    if not HAS_MPL:
        print("matplotlib not available; cannot generate figures.")
        sys.exit(1)

    print("Generating architecture figure...")
    make_arch_figure()

    print("Generating pilot case study figure...")
    make_pilot_figure()

    print("Done.")
