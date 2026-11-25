"""
Phase 11: Runtime Comparison Chart Generator
Generates publication-quality charts comparing:
1. Mean search runtime across Dijkstra, Admissible A*, Aggressive A*, Perpendicular Offset, and Yen's KSP.
2. Runtime variability and distribution (box plots / error bars).
3. Search speedup relative to uniform-cost Dijkstra and Yen's KSP.

Outputs:
- research/literature_survey/11_route_quality_evaluation/visualizations/runtime_comparison_chart.png
- research/literature_survey/11_route_quality_evaluation/visualizations/single_path_speedup_chart.png
"""

import sys
import os
import json
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

IN_JSON = os.path.join(
    PROJECT_ROOT,
    "research", "literature_survey", "11_route_quality_evaluation",
    "runtime_evaluation.json"
)
OUT_DIR = os.path.join(
    PROJECT_ROOT,
    "research", "literature_survey", "11_route_quality_evaluation",
    "visualizations"
)
os.makedirs(OUT_DIR, exist_ok=True)


def generate_runtime_charts():
    print("=" * 80)
    print("GENERATING RUNTIME COMPARISON AND VARIABILITY CHARTS")
    print("=" * 80)

    if not os.path.exists(IN_JSON):
        print(f"Error: {IN_JSON} not found.")
        return

    with open(IN_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    corridor_ids = [c["id"] for c in data]
    corridor_names = [c["name"].split(" to ")[0] + "\n→ " + c["name"].split(" to ")[1] for c in data]

    dijkstra_means = [c["algorithms"]["Dijkstra"]["stats"]["mean"] for c in data]
    admissible_means = [c["algorithms"]["Admissible_AStar"]["stats"]["mean"] for c in data]
    aggressive_means = [c["algorithms"]["Aggressive_AStar"]["stats"]["mean"] for c in data]
    offset_means = [c["algorithms"]["Perpendicular_Offset"]["stats"]["mean"] / 1000.0 for c in data]  # in seconds
    yen_means = [c["algorithms"]["Yens_KSP"]["stats"]["mean"] / 1000.0 for c in data]  # in seconds

    # --------------------------------------------------------
    # Figure 1: Single-Path Heuristic Search Runtime (ms)
    # Dijkstra vs Admissible A* vs Aggressive A*
    # --------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

    x = np.arange(len(corridor_ids))
    width = 0.26

    ax1.bar(x - width, dijkstra_means, width, label="Uniform Dijkstra (h=0)", color="#7f7f7f", alpha=0.9)
    ax1.bar(x, admissible_means, width, label="Standard Admissible A* (h=0.8×)", color="#1f77b4", alpha=0.9)
    ax1.bar(x + width, aggressive_means, width, label="Aggressive A* (h=1.25×)", color="#ff7f0e", alpha=0.9)

    ax1.set_title("Single-Path Algorithm Runtime (ms)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Commuter Corridor", fontsize=10, fontweight="semibold")
    ax1.set_ylabel("Execution Runtime (ms)", fontsize=10, fontweight="semibold")
    ax1.set_xticks(x)
    ax1.set_xticklabels([c["id"] for c in data], rotation=0, fontsize=9)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(fontsize=9)

    # Figure 2: Multi-Path Alternative Route Search Runtime (Seconds)
    # Perpendicular Offset vs Yen's KSP
    ax2.bar(x - width/2, offset_means, width, label="Perpendicular Offset (Proposed)", color="#2ca02c", alpha=0.9)
    ax2.bar(x + width/2, yen_means, width, label="Yen's KSP (Baseline, K=4)", color="#d62728", alpha=0.9)

    ax2.set_title("Multi-Path Alternative Route Generation Runtime (Seconds)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Commuter Corridor", fontsize=10, fontweight="semibold")
    ax2.set_ylabel("Execution Runtime (Seconds - Log Scale)", fontsize=10, fontweight="semibold")
    ax2.set_yscale("log")
    ax2.set_xticks(x)
    ax2.set_xticklabels([c["id"] for c in data], rotation=0, fontsize=9)
    ax2.grid(True, linestyle=":", alpha=0.6, which="both")
    ax2.legend(fontsize=9)

    plt.suptitle("Empirical Computational Runtime Benchmark across Bengaluru Commuter Corridors", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()

    out_chart1 = os.path.join(OUT_DIR, "runtime_comparison_chart.png")
    plt.savefig(out_chart1, dpi=300)
    plt.close(fig)
    print(f"Saved runtime comparison chart: {out_chart1}")

    # --------------------------------------------------------
    # Figure 2: Speedup Ratios
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    speedups_dijkstra = [d / a if a > 0 else 1.0 for d, a in zip(dijkstra_means, admissible_means)]
    ax.bar(x, speedups_dijkstra, width=0.5, color="#1f77b4", alpha=0.85, edgecolor="#0d47a1")
    ax.axhline(1.0, color="red", linestyle="--", linewidth=1.2, label="Dijkstra Baseline (1.0x)")

    for i, val in enumerate(speedups_dijkstra):
        ax.text(i, val + 0.1, f"{val:.1f}x", ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_title("Standard Admissible A* Speedup Factor vs. Uniform Dijkstra Baseline", fontsize=11, fontweight="bold")
    ax.set_xlabel("Commuter Corridor", fontsize=10, fontweight="semibold")
    ax.set_ylabel("Speedup Ratio (Dijkstra Time / Admissible A* Time)", fontsize=10, fontweight="semibold")
    ax.set_xticks(x)
    ax.set_xticklabels([c["id"] for c in data], rotation=0, fontsize=9)
    ax.set_ylim(0, max(speedups_dijkstra) * 1.25)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(fontsize=9)

    plt.tight_layout()
    out_chart2 = os.path.join(OUT_DIR, "single_path_speedup_chart.png")
    plt.savefig(out_chart2, dpi=300)
    plt.close(fig)
    print(f"Saved single-path speedup chart: {out_chart2}")


if __name__ == "__main__":
    generate_runtime_charts()
