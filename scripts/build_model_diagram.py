"""Genera un diagrama estático del modelo de datos (para el artículo en PDF,
donde no se puede renderizar Mermaid)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

INK = "#0b0b0b"
SECOND = "#52514e"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
SURFACE = "#fcfcfb"
GRID = "#e1e0d9"

FIG_DIR = Path(__file__).resolve().parent.parent / "docs" / "article" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def box(ax, xy, w, h, color, title, lines):
    x, y = xy
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.04",
                           linewidth=1.4, edgecolor=color, facecolor="white", zorder=3)
    ax.add_patch(rect)
    header = FancyBboxPatch((x, y + h - 0.42), w, 0.42, boxstyle="round,pad=0.02,rounding_size=0.04",
                             linewidth=0, facecolor=color, zorder=4)
    ax.add_patch(header)
    ax.text(x + w / 2, y + h - 0.21, title, ha="center", va="center", fontsize=11,
             fontweight="bold", color="white", zorder=5)
    for i, line in enumerate(lines):
        ax.text(x + 0.12, y + h - 0.62 - i * 0.26, line, ha="left", va="center",
                 fontsize=8.3, color=INK, zorder=5, family="monospace")


fig, ax = plt.subplots(figsize=(10, 5.6), facecolor=SURFACE)
ax.set_facecolor(SURFACE)
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.6)
ax.axis("off")

box(ax, (0.4, 2.0), 3.0, 3.1, BLUE, "species  (~2790)", [
    "_id  ObjectId",
    "species_name*  str",
    "match_key  str",
    "kingdom  str",
    "phylum  str",
    "taxo_class / taxo_order",
    "family  str",
    "source / source2 / notes",
])

box(ax, (4.1, 0.9), 3.6, 4.2, ORANGE, "sequences  (~239,946)", [
    "_id  ObjectId",
    "original_id*  str",
    "te_class / te_order",
    "te_superfamily  str",
    "species_id  -> species._id",
    "species_name  str (denorm.)",
    "sequence  str [ACGTN]",
    "length / gc_content / n_pct",
    "kmers.k1 ... kmers.k6",
    "  {kmer_str: conteo}",
])

box(ax, (8.3, 2.0), 3.0, 1.4, AQUA, "kmer_profiles_alt", [
    "sequence_id -> sequences._id",
    "kmers  (solo exp. 4.4)",
])
ax.set_xlim(0, 11.5)

arrow1 = FancyArrowPatch((3.4, 3.5), (4.1, 3.0), arrowstyle="-|>", mutation_scale=16,
                          linewidth=1.4, color=SECOND, zorder=2,
                          connectionstyle="arc3,rad=-0.15")
ax.add_patch(arrow1)
ax.text(3.68, 3.75, "species_id\n(N:1)", fontsize=7.5, color=SECOND, ha="center")

arrow2 = FancyArrowPatch((7.7, 3.5), (8.3, 3.1), arrowstyle="<|-", mutation_scale=16,
                          linewidth=1.4, color=SECOND, zorder=2, linestyle="--")
ax.add_patch(arrow2)
ax.text(7.75, 4.0, "sequence_id\n(1:1, benchmark)", fontsize=7.5, color=SECOND, ha="center")

ax.text(0.4, 0.3, "* campo con índice único    ->  referencia (ObjectId)    - - >  solo para el experimento de la sección 4.4",
        fontsize=8, color=SECOND, ha="left")

fig.tight_layout()
out_path = str(FIG_DIR / "fig0_modelo_datos.png")
fig.savefig(out_path, dpi=150)
plt.close(fig)
print(out_path)
