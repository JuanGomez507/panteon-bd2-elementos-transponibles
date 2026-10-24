"""Sección 4.5: visualizaciones a partir de datos leídos desde MongoDB.

Paleta: formula categórica/secuencial validada (ver dataviz skill,
references/palette.md) — azul/naranja/aqua para categorías (reinos), rampa de
un solo tono (azul) para magnitudes (heatmap).
"""
import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["panteon"]
sequences = db["sequences"]
species = db["species"]

# --- paleta validada (dataviz skill) ---------------------------------------
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
CAT = {"Animalia": "#2a78d6", "Plantae": "#eb6834", "Fungi": "#1baf7a"}
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

KINGDOMS = ["Animalia", "Plantae", "Fungi"]
DINUCLEOTIDES = [a + b for a in "ACGT" for b in "ACGT"]

# Ruta absoluta (relativa a este archivo), para que funcione igual desde un
# script ejecutado en la raiz del proyecto o desde un notebook en notebooks/.
FIG_DIR = str(Path(__file__).resolve().parent.parent / "docs" / "article" / "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def _style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK_SECONDARY, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.xaxis.label.set_color(INK_PRIMARY)
    ax.yaxis.label.set_color(INK_PRIMARY)


def fig1_composition_by_kingdom(out_path=f"{FIG_DIR}/fig1_composicion_por_reino.png"):
    """Composición de TEs por reino: barras agrupadas, cantidad por orden en cada reino."""
    rows = list(sequences.aggregate([
        {"$lookup": {"from": "species", "localField": "species_id", "foreignField": "_id", "as": "sp"}},
        {"$unwind": "$sp"},
        {"$group": {"_id": {"kingdom": "$sp.kingdom", "order": "$te_order"}, "n": {"$sum": 1}}},
    ]))
    orders = sorted({r["_id"]["order"] for r in rows})
    data = {k: {o: 0 for o in orders} for k in KINGDOMS}
    for r in rows:
        data[r["_id"]["kingdom"]][r["_id"]["order"]] = r["n"]

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    x = range(len(orders))
    width = 0.26
    for i, kingdom in enumerate(KINGDOMS):
        offsets = [xi + (i - 1) * width for xi in x]
        values = [data[kingdom][o] for o in orders]
        ax.bar(offsets, values, width=width, color=CAT[kingdom], label=kingdom, zorder=3)

    ax.set_xticks(list(x))
    ax.set_xticklabels(orders, rotation=40, ha="right")
    ax.set_ylabel("Cantidad de TEs")
    ax.set_title("Composición de elementos transponibles por orden y reino", color=INK_PRIMARY, loc="left", fontsize=12, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    _style_axes(ax)
    ax.legend(frameon=False, labelcolor=INK_SECONDARY, loc="upper right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def fig2_length_boxplot_by_order(out_path=f"{FIG_DIR}/fig2_longitud_por_orden.png"):
    """Boxplot de longitud por orden de TE, con cuartiles calculados en MongoDB ($percentile)."""
    rows = list(sequences.aggregate([
        {"$group": {
            "_id": "$te_order",
            "p": {"$percentile": {"input": "$length", "p": [0.05, 0.25, 0.5, 0.75, 0.95], "method": "approximate"}},
            "min": {"$min": "$length"}, "max": {"$max": "$length"}, "n": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ]))
    stats = []
    labels = []
    for r in rows:
        p05, p25, med, p75, p95 = r["p"]
        stats.append({
            "label": r["_id"], "whislo": p05, "q1": p25, "med": med, "q3": p75, "whishi": p95,
            "fliers": [],
        })
        labels.append(r["_id"])

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    bp = ax.bxp(stats, showfliers=False, patch_artist=True, widths=0.5)
    for box in bp["boxes"]:
        box.set_facecolor(SEQ_BLUE[3])
        box.set_edgecolor(INK_PRIMARY)
        box.set_linewidth(0.8)
    for part in ("whiskers", "caps", "medians"):
        for line in bp[part]:
            line.set_color(INK_PRIMARY)
            line.set_linewidth(1.0)

    ax.set_xticklabels(labels, rotation=40, ha="right")
    ax.set_ylabel("Longitud (nt)")
    ax.set_title("Distribución de la longitud de los TEs por orden (P5–P95)", color=INK_PRIMARY, loc="left", fontsize=12, fontweight="bold")
    _style_axes(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def fig3_gc_by_kingdom(out_path=f"{FIG_DIR}/fig3_gc_por_reino.png"):
    """Comparación del contenido GC entre reinos (boxplot con cuartiles de MongoDB)."""
    rows = list(sequences.aggregate([
        {"$lookup": {"from": "species", "localField": "species_id", "foreignField": "_id", "as": "sp"}},
        {"$unwind": "$sp"},
        {"$group": {
            "_id": "$sp.kingdom",
            "p": {"$percentile": {"input": "$gc_content", "p": [0.05, 0.25, 0.5, 0.75, 0.95], "method": "approximate"}},
        }},
    ]))
    by_kingdom = {r["_id"]: r["p"] for r in rows}

    stats = []
    for k in KINGDOMS:
        p05, p25, med, p75, p95 = by_kingdom[k]
        stats.append({"label": k, "whislo": p05, "q1": p25, "med": med, "q3": p75, "whishi": p95, "fliers": []})

    fig, ax = plt.subplots(figsize=(6, 5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    bp = ax.bxp(stats, showfliers=False, patch_artist=True, widths=0.4)
    for box, kingdom in zip(bp["boxes"], KINGDOMS):
        box.set_facecolor(CAT[kingdom])
        box.set_edgecolor(INK_PRIMARY)
        box.set_linewidth(0.8)
    for part in ("whiskers", "caps", "medians"):
        for line in bp[part]:
            line.set_color(INK_PRIMARY)
            line.set_linewidth(1.0)

    ax.set_ylabel("Contenido GC (%)")
    ax.set_title("Contenido GC por reino (P5–P95)", color=INK_PRIMARY, loc="left", fontsize=12, fontweight="bold")
    _style_axes(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def fig4_heatmap_dinucleotide_by_order(out_path=f"{FIG_DIR}/fig4_heatmap_kmers2.png"):
    """Heatmap: frecuencia relativa promedio de los 16 2-mers, por orden de TE."""
    group_stage = {"_id": "$te_order"}
    for d in DINUCLEOTIDES:
        group_stage[d] = {"$avg": {"$divide": [{"$ifNull": [f"$kmers.k2.{d}", 0]}, {"$subtract": ["$length", 1]}]}}
    rows = list(sequences.aggregate([{"$group": group_stage}, {"$sort": {"_id": 1}}]))

    orders = [r["_id"] for r in rows]
    matrix = [[r[d] for d in DINUCLEOTIDES] for r in rows]

    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("seq_blue", SEQ_BLUE)

    fig, ax = plt.subplots(figsize=(11, 5.5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    im = ax.imshow(np.array(matrix), cmap=cmap, aspect="auto")

    ax.set_xticks(range(len(DINUCLEOTIDES)))
    ax.set_xticklabels(DINUCLEOTIDES, fontsize=8)
    ax.set_yticks(range(len(orders)))
    ax.set_yticklabels(orders, fontsize=9)
    ax.set_title("Frecuencia relativa promedio de 2-mers por orden de TE", color=INK_PRIMARY, loc="left", fontsize=12, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.ax.tick_params(colors=INK_SECONDARY, labelsize=8)
    cbar.set_label("Frecuencia relativa", color=INK_SECONDARY, fontsize=9)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    os.makedirs(FIG_DIR, exist_ok=True)
    print(fig1_composition_by_kingdom())
    print(fig2_length_boxplot_by_order())
    print(fig3_gc_by_kingdom())
    print(fig4_heatmap_dinucleotide_by_order())
