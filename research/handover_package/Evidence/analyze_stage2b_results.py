"""
Phase 13.1 — Stage 2B Statistical Analysis and Artifact Generation.

Processes:
- stage_2b_full_ablation_results.json

Computes:
1. Comprehensive descriptive statistics for all experiments (A, B, C, D, E).
2. Paired Wilcoxon signed-rank tests using Pratt's method for zero differences
   alongside standard Wilcoxon zero-drop for sensitivity reporting.
3. Parametric paired t-tests and Cohen's d_z effect sizes with 95% CIs.
4. Non-parametric rank-biserial correlations (r_rb) and Hodges-Lehmann median
   difference estimators with 95% non-parametric CIs.
5. Holm-Bonferroni family-wise error rate corrections within approved comparison families:
   - Family A: A0 vs A1, A0 vs A2, A1 vs A2
   - Family B: B0 vs B1, B0 vs B2, B1 vs B2
   - Family C: C0 vs C2, C1 vs C2, C3 vs C2
   - Family D: D1 vs D4, D2 vs D4, D3 vs D4
   - Family E: E1 vs E2, E1 vs E3, E2 vs E3
6. Export CSV metric tables for Experiments A, B, C, D, E and Runtimes.
7. Publication-quality figures using matplotlib (PNGs saved in figures/).
8. Structured JSON summary: statistical_analysis_results.json.
"""

import sys
import os
import json
import math
import itertools
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import pandas as pd
import scipy.stats as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CURR_DIR = os.path.abspath(os.path.dirname(__file__))
RESULTS_JSON = os.path.join(CURR_DIR, "stage_2b_full_ablation_results.json")
FIG_DIR = os.path.join(CURR_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def calc_descriptive_stats(values: List[float]) -> Dict[str, Any]:
    """Calculate n, mean, std, median, min, max, iqr, q25, q75."""
    arr = np.array(values, dtype=float)
    n = len(arr)
    if n == 0:
        return {"n": 0, "mean": None, "std": None, "median": None, "min": None, "max": None, "iqr": None}
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    median = float(np.median(arr))
    min_v = float(np.min(arr))
    max_v = float(np.max(arr))
    q25 = float(np.percentile(arr, 25))
    q75 = float(np.percentile(arr, 75))
    iqr = float(q75 - q25)
    return {
        "n": n,
        "mean": round(mean, 4),
        "std": round(std, 4),
        "median": round(median, 4),
        "min": round(min_v, 4),
        "max": round(max_v, 4),
        "q25": round(q25, 4),
        "q75": round(q75, 4),
        "iqr": round(iqr, 4),
    }


def calc_cohens_dz(x: np.ndarray, y: np.ndarray) -> Tuple[float, Tuple[float, float]]:
    """Paired Cohen's d_z and 95% confidence interval."""
    d = x - y
    n = len(d)
    mean_d = float(np.mean(d))
    s_d = float(np.std(d, ddof=1)) if n > 1 else 0.0
    if s_d == 0.0 or n < 2:
        return 0.0, (0.0, 0.0)
    dz = mean_d / s_d
    # 95% CI on mean_d, scaled by s_d
    t_crit = float(st.t.ppf(0.975, df=n - 1))
    se_d = s_d / math.sqrt(n)
    ci_lower = (mean_d - t_crit * se_d) / s_d
    ci_upper = (mean_d + t_crit * se_d) / s_d
    return round(dz, 4), (round(ci_lower, 4), round(ci_upper, 4))


def calc_rank_biserial(x: np.ndarray, y: np.ndarray) -> float:
    """Matched-pairs rank-biserial correlation r_rb = (W+ - W-) / (W+ + W-)."""
    d = x - y
    non_zero = d[d != 0]
    if len(non_zero) == 0:
        return 0.0
    abs_d = np.abs(non_zero)
    ranks = st.rankdata(abs_d)
    w_plus = float(np.sum(ranks[non_zero > 0]))
    w_minus = float(np.sum(ranks[non_zero < 0]))
    total_w = w_plus + w_minus
    if total_w == 0.0:
        return 0.0
    return round((w_plus - w_minus) / total_w, 4)


def calc_hodges_lehmann(x: np.ndarray, y: np.ndarray) -> Tuple[float, Tuple[float, float]]:
    """Hodges-Lehmann median difference estimator and non-parametric 95% CI."""
    d = x - y
    n = len(d)
    if n == 0:
        return 0.0, (0.0, 0.0)
    # Walsh averages (d_i + d_j) / 2 for i <= j
    walsh = []
    for i in range(n):
        for j in range(i, n):
            walsh.append((d[i] + d[j]) / 2.0)
    walsh.sort()
    hl_estimate = float(np.median(walsh))
    m = len(walsh)
    # Normal approximation for critical rank of Wilcoxon distribution at alpha=0.05
    mean_w = n * (n + 1) / 4.0
    se_w = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
    k = int(round(mean_w - 1.96 * se_w))
    k = max(0, min(k, m // 2))
    ci_lower = float(walsh[k])
    ci_upper = float(walsh[m - 1 - k])
    return round(hl_estimate, 4), (round(ci_lower, 4), round(ci_upper, 4))


def perform_paired_test(x: List[float], y: List[float], name_x: str, name_y: str, metric_name: str, family: str) -> Dict[str, Any]:
    """Execute complete paired test battery between x and y."""
    arr_x = np.array(x, dtype=float)
    arr_y = np.array(y, dtype=float)
    diff = arr_x - arr_y
    n = len(diff)
    zeros_count = int(np.sum(diff == 0.0))

    # Wilcoxon signed-rank test (Pratt's method: primary)
    try:
        if np.all(diff == 0.0):
            w_pratt_stat, w_pratt_p = 0.0, 1.0
        else:
            res_pratt = st.wilcoxon(arr_x, arr_y, zero_method="pratt")
            w_pratt_stat = float(res_pratt.statistic)
            w_pratt_p = float(res_pratt.pvalue)
    except Exception as exc:
        w_pratt_stat, w_pratt_p = None, None

    # Wilcoxon signed-rank test (Wilcox zero-drop: sensitivity)
    try:
        if np.all(diff == 0.0) or len(diff[diff != 0]) < 1:
            w_wilcox_stat, w_wilcox_p = 0.0, 1.0
        else:
            res_wilcox = st.wilcoxon(arr_x, arr_y, zero_method="wilcox")
            w_wilcox_stat = float(res_wilcox.statistic)
            w_wilcox_p = float(res_wilcox.pvalue)
    except Exception as exc:
        w_wilcox_stat, w_wilcox_p = None, None

    # Paired t-test
    try:
        if np.all(diff == 0.0):
            t_stat, t_p = 0.0, 1.0
        else:
            res_t = st.ttest_rel(arr_x, arr_y)
            t_stat = float(res_t.statistic)
            t_p = float(res_t.pvalue)
    except Exception:
        t_stat, t_p = None, None

    dz, dz_ci = calc_cohens_dz(arr_x, arr_y)
    r_rb = calc_rank_biserial(arr_x, arr_y)
    hl, hl_ci = calc_hodges_lehmann(arr_x, arr_y)

    mean_diff = float(np.mean(diff))
    median_diff = float(np.median(diff))

    return {
        "family": family,
        "metric": metric_name,
        "comparison": f"{name_x} vs {name_y}",
        "treatment": name_x,
        "control": name_y,
        "n": n,
        "zero_differences": zeros_count,
        "mean_diff": round(mean_diff, 4),
        "median_diff": round(median_diff, 4),
        "wilcoxon_pratt_stat": round(w_pratt_stat, 4) if w_pratt_stat is not None else None,
        "p_raw_pratt": round(w_pratt_p, 6) if w_pratt_p is not None else None,
        "wilcoxon_wilcox_stat": round(w_wilcox_stat, 4) if w_wilcox_stat is not None else None,
        "p_raw_wilcox": round(w_wilcox_p, 6) if w_wilcox_p is not None else None,
        "t_stat": round(t_stat, 4) if t_stat is not None else None,
        "t_pvalue": round(t_p, 6) if t_p is not None else None,
        "cohens_dz": dz,
        "cohens_dz_95ci": dz_ci,
        "rank_biserial_r": r_rb,
        "hodges_lehmann": hl,
        "hodges_lehmann_95ci": hl_ci,
        "p_adjusted_holm": None,
        "significant_005": None,
    }


def apply_holm_bonferroni(tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply Holm-Bonferroni step-down correction to a family of tests."""
    # Filter valid p-values
    valid_indices = [i for i, t in enumerate(tests) if t.get("p_raw_pratt") is not None]
    if not valid_indices:
        return tests

    # Sort valid tests by p_raw_pratt ascending
    sorted_pairs = sorted(
        [(tests[i]["p_raw_pratt"], i) for i in valid_indices],
        key=lambda pair: pair[0]
    )

    m = len(sorted_pairs)
    adj_p_values = {}
    running_max = 0.0

    for rank, (p_raw, orig_idx) in enumerate(sorted_pairs):
        multiplier = m - rank
        adj_p = min(1.0, p_raw * multiplier)
        running_max = max(running_max, adj_p)
        adj_p_values[orig_idx] = min(1.0, running_max)

    for i in valid_indices:
        adj_p = round(adj_p_values[i], 6)
        tests[i]["p_adjusted_holm"] = adj_p
        tests[i]["significant_005"] = bool(adj_p < 0.05)

    return tests


def generate_visualizations(df_a, df_b, df_c, df_d, df_e):
    """Generate publication-quality ablation charts."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8

    # 1. Figure 1: Exp A Trade-off: Runtime vs State Expansions vs Turns
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), dpi=300)
    cfgs = ["A0_Turn_Aware", "A1_Turn_Unaware_StateExpanded", "A2_Turn_Unaware_NodeLevel"]
    labels = ["A0: Turn-Aware\n(State-Expanded)", "A1: Turn-Unaware\n(State-Expanded)", "A2: Turn-Unaware\n(Node-Level)"]
    colors = ["#2b5c8f", "#d95f02", "#7570b3"]

    # Runtime boxplot
    rt_data = [df_a[df_a["config"] == c]["runtime_ms"] for c in cfgs]
    bp0 = axes[0].boxplot(rt_data, tick_labels=labels, patch_artist=True, medianprops=dict(color="black", linewidth=1.5))
    for patch, col in zip(bp0["boxes"], colors):
        patch.set_facecolor(col)
        patch.set_alpha(0.7)
    axes[0].set_title("(a) Computational Runtime (ms)", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Runtime [milliseconds]")

    # State expansions
    exp_data = [df_a[df_a["config"] == c]["expanded_states"] for c in cfgs]
    bp1 = axes[1].boxplot(exp_data, tick_labels=labels, patch_artist=True, medianprops=dict(color="black", linewidth=1.5))
    for patch, col in zip(bp1["boxes"], colors):
        patch.set_facecolor(col)
        patch.set_alpha(0.7)
    axes[1].set_title("(b) Search State Expansions", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Expanded States Count")

    # Sharp Turns
    turns_data = [df_a[df_a["config"] == c]["sharp_turns"] for c in cfgs]
    bp2 = axes[2].boxplot(turns_data, tick_labels=labels, patch_artist=True, medianprops=dict(color="black", linewidth=1.5))
    for patch, col in zip(bp2["boxes"], colors):
        patch.set_facecolor(col)
        patch.set_alpha(0.7)
    axes[2].set_title("(c) Sharp Turns Count (>= 60°)", fontsize=11, fontweight="bold")
    axes[2].set_ylabel("Sharp Turn Count")

    plt.tight_layout()
    fig1_path = os.path.join(FIG_DIR, "fig1_exp_a_tradeoffs.png")
    plt.savefig(fig1_path, dpi=300)
    plt.close()

    # 2. Figure 2: Exp B Road-Class Composition Shift
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    b_cfgs = ["B0_Production_2W", "B1_Neutral_Road_Class", "B2_Physical_Distance_Ref"]
    b_labels = ["B0: Production 2W\n(1.5 Main / 0.9 Inner)", "B1: Road Neutrality\n(1.0 Neutral Weights)", "B2: Physical Shortest\n(Distance Only)"]
    art_means = [df_b[df_b["config"] == c]["arterial_pct"].mean() for c in b_cfgs]
    res_means = [df_b[df_b["config"] == c]["residential_pct"].mean() for c in b_cfgs]
    col_means = [df_b[df_b["config"] == c]["collector_pct"].mean() for c in b_cfgs]
    svc_means = [df_b[df_b["config"] == c]["service_pct"].mean() for c in b_cfgs]

    x = np.arange(len(b_labels))
    width = 0.55
    p1 = ax.bar(x, art_means, width, label="Arterial (Motorway/Trunk/Primary/Secondary)", color="#e41a1c", alpha=0.85)
    p2 = ax.bar(x, col_means, width, bottom=art_means, label="Collector (Tertiary)", color="#377eb8", alpha=0.85)
    p3 = ax.bar(x, res_means, width, bottom=np.array(art_means) + np.array(col_means), label="Residential (Living/Unclassified)", color="#4daf4a", alpha=0.85)
    p4 = ax.bar(x, svc_means, width, bottom=np.array(art_means) + np.array(col_means) + np.array(res_means), label="Service", color="#984ea3", alpha=0.85)

    ax.set_ylabel("Mean Exposure Share of Total Route Distance [%]", fontsize=10, fontweight="bold")
    ax.set_title("Experiment B: Road-Class Exposure Shift Across Routing Paradigms (N=25)", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(b_labels)
    ax.set_ylim(0, 105)
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    plt.tight_layout()
    fig2_path = os.path.join(FIG_DIR, "fig2_exp_b_road_classes.png")
    plt.savefig(fig2_path, dpi=300)
    plt.close()

    # 3. Figure 3: Exp C Turn-Penalty Sensitivity Curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=300)
    c_cfgs = ["C0_Zero_Turn_Penalties", "C1_Low_Turn_Penalties", "C2_Baseline_Turn_Penalties", "C3_High_Turn_Penalties"]
    c_labels = ["C0 (0/0)", "C1 (12/4)", "C2 Baseline (25/8)", "C3 High (50/16)"]
    c_sharp_means = [df_c[df_c["config"] == c]["sharp_turns"].mean() for c in c_cfgs]
    c_sharp_std = [df_c[df_c["config"] == c]["sharp_turns"].std() for c in c_cfgs]
    c_tot_means = [df_c[df_c["config"] == c]["total_turns"].mean() for c in c_cfgs]
    c_tot_std = [df_c[df_c["config"] == c]["total_turns"].std() for c in c_cfgs]

    ax1.plot(c_labels, c_sharp_means, marker="o", color="#d95f02", linewidth=2, markersize=8, label="Sharp Turns (>= 60°)")
    ax1.plot(c_labels, c_tot_means, marker="s", color="#7570b3", linewidth=2, markersize=8, label="Total Turns (Sharp + Mod)")
    ax1.set_title("(a) Maneuver Frequency Sensitivity", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Mean Turns per Corridor Count")
    ax1.set_xlabel("Penalty Configuration (Sharp / Moderate)")
    ax1.legend(frameon=True)

    c_dist_means = [df_c[df_c["config"] == c]["distance_km"].mean() for c in c_cfgs]
    c_rt_means = [df_c[df_c["config"] == c]["runtime_ms"].mean() for c in c_cfgs]
    ax2.plot(c_labels, c_dist_means, marker="^", color="#1b9e77", linewidth=2, markersize=8, label="Physical Distance (km)")
    ax2.set_title("(b) Route Distance Response", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Mean Physical Distance [km]")
    ax2.set_xlabel("Penalty Configuration (Sharp / Moderate)")
    ax2.legend(frameon=True)

    plt.tight_layout()
    fig3_path = os.path.join(FIG_DIR, "fig3_exp_c_sensitivity.png")
    plt.savefig(fig3_path, dpi=300)
    plt.close()

    # 4. Figure 4: Exp E Alternative Routing Comparison (Offset vs Yen)
    df_e_selected = df_e[df_e["runtime_ms"].notnull() & (df_e["runtime_ms"] > 0)]
    if not df_e_selected.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=300)
        e_cfgs = ["E1_Perpendicular_Offset", "E2_Raw_Yen_KSP", "E3_Filtered_Yen_KSP"]
        e_labels = [
            "E1: Offset (N=25)\n(Heuristic)",
            "E2: Raw Yen (N=5)\n(Exact Spur)",
            "E3: Filtered Yen (N=5)\n(70% Pruned)",
        ]
        colors_e = ["#1b9e77", "#d95f02", "#7570b3"]

        # Runtime comparison (log scale)
        e_runtimes_s = [df_e_selected[df_e_selected["config"] == c]["runtime_ms"] / 1000.0 for c in e_cfgs]
        bp_e = ax1.boxplot(e_runtimes_s, tick_labels=e_labels, patch_artist=True, medianprops=dict(color="black", linewidth=1.5))
        for patch, col in zip(bp_e["boxes"], colors_e):
            patch.set_facecolor(col)
            patch.set_alpha(0.7)
        ax1.set_yscale("log")
        ax1.set_title("(a) Computational Runtime (Seconds, Log Scale)", fontsize=11, fontweight="bold")
        ax1.set_ylabel("Runtime [seconds, log10]")

        # Diversity comparison
        e_div = [df_e_selected[df_e_selected["config"] == c]["pairwise_diversity"] for c in e_cfgs]
        bp_div = ax2.boxplot(e_div, tick_labels=e_labels, patch_artist=True, medianprops=dict(color="black", linewidth=1.5))
        for patch, col in zip(bp_div["boxes"], colors_e):
            patch.set_facecolor(col)
            patch.set_alpha(0.7)
        ax2.set_title("(b) Pairwise Route Diversity (1 - Jaccard)", fontsize=11, fontweight="bold")
        ax2.set_ylabel("Diversity Index [0.0 - 1.0]")
        ax2.set_ylim(-0.05, 1.05)

        plt.tight_layout()
        fig4_path = os.path.join(FIG_DIR, "fig4_exp_e_alternatives.png")
        plt.savefig(fig4_path, dpi=300)
        plt.close()


def main():
    print("=" * 80)
    print("PHASE 13.1 — STAGE 2B STATISTICAL ANALYSIS & DELIVERABLE GENERATION")
    print("=" * 80)

    if not os.path.exists(RESULTS_JSON):
        print(f"[ERROR] Results file not found: {RESULTS_JSON}")
        sys.exit(1)

    with open(RESULTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    corridors = data.get("corridors", {})
    print(f"Loaded results for {len(corridors)} corridors.")

    # -------------------------------------------------------------------------
    # 1. Tabulate Per-Experiment Metrics into DataFrames
    # -------------------------------------------------------------------------
    rows_a = []
    rows_b = []
    rows_c = []
    rows_d = []
    rows_e = []
    rows_runtime = []

    for c_id, c_data in corridors.items():
        c_info = c_data["corridor_info"]
        exps = c_data["experiments"]

        # Exp A
        if "Experiment_A" in exps:
            for cfg in ["A0_Turn_Aware", "A1_Turn_Unaware_StateExpanded", "A2_Turn_Unaware_NodeLevel"]:
                m = exps["Experiment_A"][cfg]
                rows_a.append({
                    "corridor_id": c_id,
                    "corridor_name": c_info["name"],
                    "dist_cat": c_info["dist_cat"],
                    "config": cfg,
                    "runtime_ms": m["runtime_ms"],
                    "expanded_states": m["expanded_states"],
                    "distance_km": m["distance_km"],
                    "impedance_cost": m["impedance_cost"],
                    "sharp_turns": m["turns"]["sharp_turns"],
                    "moderate_turns": m["turns"]["moderate_turns"],
                    "total_turns": m["turns"]["total_turns"],
                })
                rows_runtime.append({
                    "corridor_id": c_id,
                    "experiment": "Exp_A",
                    "config": cfg,
                    "median_runtime_ms": m["runtime_ms"],
                    "raw_runtimes_ms": str(m["raw_runtimes_ms"]),
                })

        # Exp B
        if "Experiment_B" in exps:
            for cfg in ["B0_Production_2W", "B1_Neutral_Road_Class", "B2_Physical_Distance_Ref"]:
                m = exps["Experiment_B"][cfg]
                macro = m["road_classes"]["macro_pct"]
                rows_b.append({
                    "corridor_id": c_id,
                    "corridor_name": c_info["name"],
                    "dist_cat": c_info["dist_cat"],
                    "config": cfg,
                    "runtime_ms": m["runtime_ms"],
                    "distance_km": m["distance_km"],
                    "impedance_cost": m["impedance_cost"],
                    "arterial_pct": macro["arterial_pct"],
                    "collector_pct": macro["collector_pct"],
                    "residential_pct": macro["residential_pct"],
                    "service_pct": macro["service_pct"],
                })
                rows_runtime.append({
                    "corridor_id": c_id,
                    "experiment": "Exp_B",
                    "config": cfg,
                    "median_runtime_ms": m["runtime_ms"],
                    "raw_runtimes_ms": str(m["raw_runtimes_ms"]),
                })

        # Exp C
        if "Experiment_C" in exps:
            for cfg in ["C0_Zero_Turn_Penalties", "C1_Low_Turn_Penalties", "C2_Baseline_Turn_Penalties", "C3_High_Turn_Penalties"]:
                m = exps["Experiment_C"][cfg]
                rows_c.append({
                    "corridor_id": c_id,
                    "corridor_name": c_info["name"],
                    "dist_cat": c_info["dist_cat"],
                    "config": cfg,
                    "runtime_ms": m["runtime_ms"],
                    "distance_km": m["distance_km"],
                    "impedance_cost": m["impedance_cost"],
                    "sharp_turns": m["turns"]["sharp_turns"],
                    "moderate_turns": m["turns"]["moderate_turns"],
                    "total_turns": m["turns"]["total_turns"],
                })
                rows_runtime.append({
                    "corridor_id": c_id,
                    "experiment": "Exp_C",
                    "config": cfg,
                    "median_runtime_ms": m["runtime_ms"],
                    "raw_runtimes_ms": str(m["raw_runtimes_ms"]),
                })

        # Exp D
        if "Experiment_D" in exps:
            for cfg in ["D1_Bridge_Off_Roundabout_Off", "D2_Bridge_On_Roundabout_Off", "D3_Bridge_Off_Roundabout_On", "D4_Bridge_On_Roundabout_On"]:
                m = exps["Experiment_D"][cfg]
                rows_d.append({
                    "corridor_id": c_id,
                    "corridor_name": c_info["name"],
                    "dist_cat": c_info["dist_cat"],
                    "config": cfg,
                    "runtime_ms": m["runtime_ms"],
                    "distance_km": m["distance_km"],
                    "impedance_cost": m["impedance_cost"],
                    "bridge_length_m": m["bridge"]["bridge_length_m"],
                    "bridge_pct": m["bridge"]["bridge_pct"],
                    "roundabout_length_m": m["roundabout"]["roundabout_length_m"],
                    "roundabout_pct": m["roundabout"]["roundabout_pct"],
                })
                rows_runtime.append({
                    "corridor_id": c_id,
                    "experiment": "Exp_D",
                    "config": cfg,
                    "median_runtime_ms": m["runtime_ms"],
                    "raw_runtimes_ms": str(m["raw_runtimes_ms"]),
                })

        # Exp E
        if "Experiment_E" in exps:
            # E1
            e1 = exps["Experiment_E"]["E1_Perpendicular_Offset"]
            rows_e.append({
                "corridor_id": c_id,
                "corridor_name": c_info["name"],
                "dist_cat": c_info["dist_cat"],
                "config": "E1_Perpendicular_Offset",
                "is_yen_selected": c_data["is_yen_selected"],
                "outcome_status": "SUCCESS_OFFSET",
                "runtime_ms": e1["runtime_ms"],
                "surviving_count": e1["surviving_count"],
                "generated_count": e1["generated_count"],
                "pairwise_diversity": e1["pairwise_diversity"],
                "detour_ratios": str(e1.get("detour_ratios", [])),
                "overlap_ratios": str(e1.get("overlap_ratios", [])),
            })
            rows_runtime.append({
                "corridor_id": c_id,
                "experiment": "Exp_E1",
                "config": "E1_Perpendicular_Offset",
                "median_runtime_ms": e1["runtime_ms"],
                "raw_runtimes_ms": str(e1["raw_runtimes_ms"]),
            })

            # E2 & E3
            if c_data["is_yen_selected"]:
                e2 = exps["Experiment_E"]["E2_Raw_Yen_KSP"]
                rows_e.append({
                    "corridor_id": c_id,
                    "corridor_name": c_info["name"],
                    "dist_cat": c_info["dist_cat"],
                    "config": "E2_Raw_Yen_KSP",
                    "is_yen_selected": True,
                    "outcome_status": e2["outcome_status"],
                    "runtime_ms": e2["runtime_ms"],
                    "surviving_count": e2["surviving_alts"],
                    "generated_count": e2["candidates_generated"],
                    "pairwise_diversity": e2["pairwise_diversity"],
                    "detour_ratios": str(e2.get("detour_ratios", [])),
                    "overlap_ratios": str(e2.get("overlap_ratios", [])),
                })
                rows_runtime.append({
                    "corridor_id": c_id,
                    "experiment": "Exp_E2",
                    "config": "E2_Raw_Yen_KSP",
                    "median_runtime_ms": e2["runtime_ms"],
                    "raw_runtimes_ms": str(e2["raw_runtimes_ms"]),
                })

                e3 = exps["Experiment_E"]["E3_Filtered_Yen_KSP"]
                rows_e.append({
                    "corridor_id": c_id,
                    "corridor_name": c_info["name"],
                    "dist_cat": c_info["dist_cat"],
                    "config": "E3_Filtered_Yen_KSP",
                    "is_yen_selected": True,
                    "outcome_status": e3["outcome_status"],
                    "runtime_ms": e3["runtime_ms"],
                    "surviving_count": e3["surviving_alts"],
                    "generated_count": e3["candidates_generated"],
                    "pairwise_diversity": e3["pairwise_diversity"],
                    "detour_ratios": str(e3.get("detour_ratios", [])),
                    "overlap_ratios": str(e3.get("overlap_ratios", [])),
                })
                rows_runtime.append({
                    "corridor_id": c_id,
                    "experiment": "Exp_E3",
                    "config": "E3_Filtered_Yen_KSP",
                    "median_runtime_ms": e3["runtime_ms"],
                    "raw_runtimes_ms": str(e3["raw_runtimes_ms"]),
                })

    df_a = pd.DataFrame(rows_a)
    df_b = pd.DataFrame(rows_b)
    df_c = pd.DataFrame(rows_c)
    df_d = pd.DataFrame(rows_d)
    df_e = pd.DataFrame(rows_e)
    df_rt = pd.DataFrame(rows_runtime)

    # Save CSVs
    df_a.to_csv(os.path.join(CURR_DIR, "exp_a_corridor_metrics.csv"), index=False)
    df_b.to_csv(os.path.join(CURR_DIR, "exp_b_corridor_metrics.csv"), index=False)
    df_c.to_csv(os.path.join(CURR_DIR, "exp_c_corridor_metrics.csv"), index=False)
    df_d.to_csv(os.path.join(CURR_DIR, "exp_d_corridor_metrics.csv"), index=False)
    df_e.to_csv(os.path.join(CURR_DIR, "exp_e_corridor_metrics.csv"), index=False)
    df_rt.to_csv(os.path.join(CURR_DIR, "runtime_comparisons.csv"), index=False)
    print("[OK] Saved CSV metric tables for Experiments A, B, C, D, E and Runtimes.")

    # -------------------------------------------------------------------------
    # 2. Descriptive Statistics Summary per Configuration
    # -------------------------------------------------------------------------
    desc_stats = {"Experiment_A": {}, "Experiment_B": {}, "Experiment_C": {}, "Experiment_D": {}, "Experiment_E": {}}

    for cfg in ["A0_Turn_Aware", "A1_Turn_Unaware_StateExpanded", "A2_Turn_Unaware_NodeLevel"]:
        sub = df_a[df_a["config"] == cfg]
        desc_stats["Experiment_A"][cfg] = {
            "runtime_ms": calc_descriptive_stats(sub["runtime_ms"].tolist()),
            "expanded_states": calc_descriptive_stats(sub["expanded_states"].tolist()),
            "distance_km": calc_descriptive_stats(sub["distance_km"].tolist()),
            "impedance_cost": calc_descriptive_stats(sub["impedance_cost"].tolist()),
            "sharp_turns": calc_descriptive_stats(sub["sharp_turns"].tolist()),
            "total_turns": calc_descriptive_stats(sub["total_turns"].tolist()),
        }

    for cfg in ["B0_Production_2W", "B1_Neutral_Road_Class", "B2_Physical_Distance_Ref"]:
        sub = df_b[df_b["config"] == cfg]
        desc_stats["Experiment_B"][cfg] = {
            "runtime_ms": calc_descriptive_stats(sub["runtime_ms"].tolist()),
            "distance_km": calc_descriptive_stats(sub["distance_km"].tolist()),
            "impedance_cost": calc_descriptive_stats(sub["impedance_cost"].tolist()),
            "arterial_pct": calc_descriptive_stats(sub["arterial_pct"].tolist()),
            "collector_pct": calc_descriptive_stats(sub["collector_pct"].tolist()),
            "residential_pct": calc_descriptive_stats(sub["residential_pct"].tolist()),
            "service_pct": calc_descriptive_stats(sub["service_pct"].tolist()),
        }

    for cfg in ["C0_Zero_Turn_Penalties", "C1_Low_Turn_Penalties", "C2_Baseline_Turn_Penalties", "C3_High_Turn_Penalties"]:
        sub = df_c[df_c["config"] == cfg]
        desc_stats["Experiment_C"][cfg] = {
            "runtime_ms": calc_descriptive_stats(sub["runtime_ms"].tolist()),
            "distance_km": calc_descriptive_stats(sub["distance_km"].tolist()),
            "impedance_cost": calc_descriptive_stats(sub["impedance_cost"].tolist()),
            "sharp_turns": calc_descriptive_stats(sub["sharp_turns"].tolist()),
            "total_turns": calc_descriptive_stats(sub["total_turns"].tolist()),
        }

    for cfg in ["D1_Bridge_Off_Roundabout_Off", "D2_Bridge_On_Roundabout_Off", "D3_Bridge_Off_Roundabout_On", "D4_Bridge_On_Roundabout_On"]:
        sub = df_d[df_d["config"] == cfg]
        desc_stats["Experiment_D"][cfg] = {
            "runtime_ms": calc_descriptive_stats(sub["runtime_ms"].tolist()),
            "distance_km": calc_descriptive_stats(sub["distance_km"].tolist()),
            "impedance_cost": calc_descriptive_stats(sub["impedance_cost"].tolist()),
            "bridge_length_m": calc_descriptive_stats(sub["bridge_length_m"].tolist()),
            "bridge_pct": calc_descriptive_stats(sub["bridge_pct"].tolist()),
            "roundabout_length_m": calc_descriptive_stats(sub["roundabout_length_m"].tolist()),
            "roundabout_pct": calc_descriptive_stats(sub["roundabout_pct"].tolist()),
        }

    for cfg in ["E1_Perpendicular_Offset", "E2_Raw_Yen_KSP", "E3_Filtered_Yen_KSP"]:
        sub = df_e[df_e["config"] == cfg]
        desc_stats["Experiment_E"][cfg] = {
            "runtime_ms": calc_descriptive_stats(sub["runtime_ms"].dropna().tolist()),
            "surviving_count": calc_descriptive_stats(sub["surviving_count"].dropna().tolist()),
            "pairwise_diversity": calc_descriptive_stats(sub["pairwise_diversity"].dropna().tolist()),
        }

    # -------------------------------------------------------------------------
    # 3. Paired Statistical Hypothesis Testing across Families
    # -------------------------------------------------------------------------
    statistical_tests = []

    # Family A: Turn Awareness & State Expansion
    # Comparisons: A0 vs A1, A0 vs A2, A1 vs A2
    fam_a_tests = []
    piv_a_rt = df_a.pivot(index="corridor_id", columns="config", values="runtime_ms")
    piv_a_exp = df_a.pivot(index="corridor_id", columns="config", values="expanded_states")
    piv_a_sharp = df_a.pivot(index="corridor_id", columns="config", values="sharp_turns")
    piv_a_tot = df_a.pivot(index="corridor_id", columns="config", values="total_turns")
    piv_a_dist = df_a.pivot(index="corridor_id", columns="config", values="distance_km")

    # Primary hypothesis tests on sharp turns and runtime
    fam_a_tests.append(perform_paired_test(piv_a_sharp["A0_Turn_Aware"], piv_a_sharp["A1_Turn_Unaware_StateExpanded"], "A0", "A1", "sharp_turns", "Family_A_Turns"))
    fam_a_tests.append(perform_paired_test(piv_a_sharp["A0_Turn_Aware"], piv_a_sharp["A2_Turn_Unaware_NodeLevel"], "A0", "A2", "sharp_turns", "Family_A_Turns"))
    fam_a_tests.append(perform_paired_test(piv_a_sharp["A1_Turn_Unaware_StateExpanded"], piv_a_sharp["A2_Turn_Unaware_NodeLevel"], "A1", "A2", "sharp_turns", "Family_A_Turns"))
    apply_holm_bonferroni(fam_a_tests)
    statistical_tests.extend(fam_a_tests)

    fam_a_rt_tests = []
    fam_a_rt_tests.append(perform_paired_test(piv_a_rt["A0_Turn_Aware"], piv_a_rt["A1_Turn_Unaware_StateExpanded"], "A0", "A1", "runtime_ms", "Family_A_Runtime"))
    fam_a_rt_tests.append(perform_paired_test(piv_a_rt["A0_Turn_Aware"], piv_a_rt["A2_Turn_Unaware_NodeLevel"], "A0", "A2", "runtime_ms", "Family_A_Runtime"))
    fam_a_rt_tests.append(perform_paired_test(piv_a_rt["A1_Turn_Unaware_StateExpanded"], piv_a_rt["A2_Turn_Unaware_NodeLevel"], "A1", "A2", "runtime_ms", "Family_A_Runtime"))
    apply_holm_bonferroni(fam_a_rt_tests)
    statistical_tests.extend(fam_a_rt_tests)

    fam_a_exp_tests = []
    fam_a_exp_tests.append(perform_paired_test(piv_a_exp["A0_Turn_Aware"], piv_a_exp["A1_Turn_Unaware_StateExpanded"], "A0", "A1", "expanded_states", "Family_A_Expansions"))
    fam_a_exp_tests.append(perform_paired_test(piv_a_exp["A0_Turn_Aware"], piv_a_exp["A2_Turn_Unaware_NodeLevel"], "A0", "A2", "expanded_states", "Family_A_Expansions"))
    fam_a_exp_tests.append(perform_paired_test(piv_a_exp["A1_Turn_Unaware_StateExpanded"], piv_a_exp["A2_Turn_Unaware_NodeLevel"], "A1", "A2", "expanded_states", "Family_A_Expansions"))
    apply_holm_bonferroni(fam_a_exp_tests)
    statistical_tests.extend(fam_a_exp_tests)

    # Family B: Road Impedance
    # Comparisons: B0 vs B1, B0 vs B2, B1 vs B2
    piv_b_art = df_b.pivot(index="corridor_id", columns="config", values="arterial_pct")
    piv_b_res = df_b.pivot(index="corridor_id", columns="config", values="residential_pct")
    piv_b_dist = df_b.pivot(index="corridor_id", columns="config", values="distance_km")

    fam_b_art = []
    fam_b_art.append(perform_paired_test(piv_b_art["B0_Production_2W"], piv_b_art["B1_Neutral_Road_Class"], "B0", "B1", "arterial_pct", "Family_B_Arterial"))
    fam_b_art.append(perform_paired_test(piv_b_art["B0_Production_2W"], piv_b_art["B2_Physical_Distance_Ref"], "B0", "B2", "arterial_pct", "Family_B_Arterial"))
    fam_b_art.append(perform_paired_test(piv_b_art["B1_Neutral_Road_Class"], piv_b_art["B2_Physical_Distance_Ref"], "B1", "B2", "arterial_pct", "Family_B_Arterial"))
    apply_holm_bonferroni(fam_b_art)
    statistical_tests.extend(fam_b_art)

    fam_b_res = []
    fam_b_res.append(perform_paired_test(piv_b_res["B0_Production_2W"], piv_b_res["B1_Neutral_Road_Class"], "B0", "B1", "residential_pct", "Family_B_Residential"))
    fam_b_res.append(perform_paired_test(piv_b_res["B0_Production_2W"], piv_b_res["B2_Physical_Distance_Ref"], "B0", "B2", "residential_pct", "Family_B_Residential"))
    fam_b_res.append(perform_paired_test(piv_b_res["B1_Neutral_Road_Class"], piv_b_res["B2_Physical_Distance_Ref"], "B1", "B2", "residential_pct", "Family_B_Residential"))
    apply_holm_bonferroni(fam_b_res)
    statistical_tests.extend(fam_b_res)

    fam_b_dist = []
    fam_b_dist.append(perform_paired_test(piv_b_dist["B0_Production_2W"], piv_b_dist["B1_Neutral_Road_Class"], "B0", "B1", "distance_km", "Family_B_Distance"))
    fam_b_dist.append(perform_paired_test(piv_b_dist["B0_Production_2W"], piv_b_dist["B2_Physical_Distance_Ref"], "B0", "B2", "distance_km", "Family_B_Distance"))
    fam_b_dist.append(perform_paired_test(piv_b_dist["B1_Neutral_Road_Class"], piv_b_dist["B2_Physical_Distance_Ref"], "B1", "B2", "distance_km", "Family_B_Distance"))
    apply_holm_bonferroni(fam_b_dist)
    statistical_tests.extend(fam_b_dist)

    # Family C: Turn Penalty Sensitivity (Treatments vs Baseline C2)
    # Comparisons: C0 vs C2, C1 vs C2, C3 vs C2
    piv_c_sharp = df_c.pivot(index="corridor_id", columns="config", values="sharp_turns")
    piv_c_tot = df_c.pivot(index="corridor_id", columns="config", values="total_turns")

    fam_c_sharp = []
    fam_c_sharp.append(perform_paired_test(piv_c_sharp["C0_Zero_Turn_Penalties"], piv_c_sharp["C2_Baseline_Turn_Penalties"], "C0", "C2", "sharp_turns", "Family_C_SharpTurns"))
    fam_c_sharp.append(perform_paired_test(piv_c_sharp["C1_Low_Turn_Penalties"], piv_c_sharp["C2_Baseline_Turn_Penalties"], "C1", "C2", "sharp_turns", "Family_C_SharpTurns"))
    fam_c_sharp.append(perform_paired_test(piv_c_sharp["C3_High_Turn_Penalties"], piv_c_sharp["C2_Baseline_Turn_Penalties"], "C3", "C2", "sharp_turns", "Family_C_SharpTurns"))
    apply_holm_bonferroni(fam_c_sharp)
    statistical_tests.extend(fam_c_sharp)

    fam_c_tot = []
    fam_c_tot.append(perform_paired_test(piv_c_tot["C0_Zero_Turn_Penalties"], piv_c_tot["C2_Baseline_Turn_Penalties"], "C0", "C2", "total_turns", "Family_C_TotalTurns"))
    fam_c_tot.append(perform_paired_test(piv_c_tot["C1_Low_Turn_Penalties"], piv_c_tot["C2_Baseline_Turn_Penalties"], "C1", "C2", "total_turns", "Family_C_TotalTurns"))
    fam_c_tot.append(perform_paired_test(piv_c_tot["C3_High_Turn_Penalties"], piv_c_tot["C2_Baseline_Turn_Penalties"], "C3", "C2", "total_turns", "Family_C_TotalTurns"))
    apply_holm_bonferroni(fam_c_tot)
    statistical_tests.extend(fam_c_tot)

    # Family D: Bridge & Roundabout 2x2 Factorial (Treatments vs Control D4)
    # Comparisons: D1 vs D4, D2 vs D4, D3 vs D4
    piv_d_brg = df_d.pivot(index="corridor_id", columns="config", values="bridge_length_m")
    piv_d_rbt = df_d.pivot(index="corridor_id", columns="config", values="roundabout_length_m")
    piv_d_cost = df_d.pivot(index="corridor_id", columns="config", values="impedance_cost")

    fam_d_cost = []
    fam_d_cost.append(perform_paired_test(piv_d_cost["D1_Bridge_Off_Roundabout_Off"], piv_d_cost["D4_Bridge_On_Roundabout_On"], "D1", "D4", "impedance_cost", "Family_D_Cost"))
    fam_d_cost.append(perform_paired_test(piv_d_cost["D2_Bridge_On_Roundabout_Off"], piv_d_cost["D4_Bridge_On_Roundabout_On"], "D2", "D4", "impedance_cost", "Family_D_Cost"))
    fam_d_cost.append(perform_paired_test(piv_d_cost["D3_Bridge_Off_Roundabout_On"], piv_d_cost["D4_Bridge_On_Roundabout_On"], "D3", "D4", "impedance_cost", "Family_D_Cost"))
    apply_holm_bonferroni(fam_d_cost)
    statistical_tests.extend(fam_d_cost)

    # Family E: Alternative Routing (on 5 selected Yen corridors)
    # Comparisons: E1 vs E2, E1 vs E3, E2 vs E3
    df_e_yen = df_e[df_e["is_yen_selected"] == True]
    piv_e_rt = df_e_yen.pivot(index="corridor_id", columns="config", values="runtime_ms")
    piv_e_div = df_e_yen.pivot(index="corridor_id", columns="config", values="pairwise_diversity")

    fam_e_rt = []
    fam_e_rt.append(perform_paired_test(piv_e_rt["E1_Perpendicular_Offset"], piv_e_rt["E2_Raw_Yen_KSP"], "E1", "E2", "runtime_ms", "Family_E_Runtime"))
    fam_e_rt.append(perform_paired_test(piv_e_rt["E1_Perpendicular_Offset"], piv_e_rt["E3_Filtered_Yen_KSP"], "E1", "E3", "runtime_ms", "Family_E_Runtime"))
    fam_e_rt.append(perform_paired_test(piv_e_rt["E2_Raw_Yen_KSP"], piv_e_rt["E3_Filtered_Yen_KSP"], "E2", "E3", "runtime_ms", "Family_E_Runtime"))
    apply_holm_bonferroni(fam_e_rt)
    statistical_tests.extend(fam_e_rt)

    fam_e_div = []
    fam_e_div.append(perform_paired_test(piv_e_div["E1_Perpendicular_Offset"], piv_e_div["E2_Raw_Yen_KSP"], "E1", "E2", "pairwise_diversity", "Family_E_Diversity"))
    fam_e_div.append(perform_paired_test(piv_e_div["E1_Perpendicular_Offset"], piv_e_div["E3_Filtered_Yen_KSP"], "E1", "E3", "pairwise_diversity", "Family_E_Diversity"))
    fam_e_div.append(perform_paired_test(piv_e_div["E2_Raw_Yen_KSP"], piv_e_div["E3_Filtered_Yen_KSP"], "E2", "E3", "pairwise_diversity", "Family_E_Diversity"))
    apply_holm_bonferroni(fam_e_div)
    statistical_tests.extend(fam_e_div)

    # Convert statistical tests to DataFrame and save CSV
    df_stat = pd.DataFrame(statistical_tests)
    df_stat.to_csv(os.path.join(CURR_DIR, "statistical_test_results.csv"), index=False)
    print(f"[OK] Computed {len(statistical_tests)} paired statistical tests across {len(set(t['family'] for t in statistical_tests))} families.")

    # -------------------------------------------------------------------------
    # 4. Generate Visualizations
    # -------------------------------------------------------------------------
    print("Generating figures...")
    generate_visualizations(df_a, df_b, df_c, df_d, df_e)
    print("[OK] Visualizations generated in figures/ directory.")

    # -------------------------------------------------------------------------
    # 5. Save Complete Statistical Summary JSON
    # -------------------------------------------------------------------------
    final_output = {
        "metadata": data.get("metadata", {}),
        "descriptive_statistics": desc_stats,
        "statistical_tests": statistical_tests,
    }
    with open(os.path.join(CURR_DIR, "statistical_analysis_results.json"), "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2)
    print("[OK] Statistical analysis results saved to statistical_analysis_results.json.")
    print("=" * 80)


if __name__ == "__main__":
    main()
