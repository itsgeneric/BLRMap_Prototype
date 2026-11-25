"""
Paper 2, Phase 3: Experiment E consolidation (perpendicular-offset alternatives vs Yen K-shortest-path).
Input : stage_2b_full_ablation_results.json (original Experiment E data; read-only)
Output: tables (CSV) and one figure. No values are estimated; every number is computed from the JSON.
Corridors are identified by ID and distance class only (no names, no coordinates).
Definitions that cannot be recomputed from the JSON (geometry not stored) are flagged in PHASE3_NOTE.md.
"""
import json, re, sys, os, statistics as st
import numpy as np, pandas as pd

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
d = json.load(open(SRC))
YEN = d["metadata"]["yen_selected_corridors"]
rows = []
for cid, v in d["corridors"].items():
    info = v["corridor_info"]; E = v["experiments"]["Experiment_E"]
    cls, km = re.match(r"(\w+) \(([\d.]+) km\)", info["dist_cat"]).groups()
    e1 = E["E1_Perpendicular_Offset"]
    det = e1.get("detour_ratios", [])[1:]; ov = e1.get("overlap_ratios", [])[1:]   # index 0 is the primary route itself (1.0)
    rows.append(dict(corridor=cid, dist_class=cls, dist_km=float(km),
                     alternatives=e1["surviving_count"], candidates=e1["generated_count"],
                     any_alt=int(e1["surviving_count"] > 0), full_k3=int(e1["surviving_count"] == 3),
                     diversity_raw=e1["pairwise_diversity"],
                     diversity=(e1["pairwise_diversity"] if e1["surviving_count"] > 0 else np.nan),
                     runtime_s=round(e1["runtime_ms"]/1000, 2),
                     detour_mean=(round(np.mean(det), 4) if det else np.nan), detour_max=(max(det) if det else np.nan),
                     overlap_mean=(round(np.mean(ov), 4) if ov else np.nan), overlap_max=(max(ov) if ov else np.nan),
                     in_yen_subset=int(cid in YEN), exceptions_recorded=len(v["exceptions"])))
T = pd.DataFrame(rows)
T.drop(columns=["diversity_raw"]).to_csv(os.path.join(OUT, "expE_offset_corridor_table.csv"), index=False)

# ---------- offset summary (all 25, successful subset, by class) ----------
def summ(df, label):
    s = df[df.any_alt == 1]
    alts = [x for c in df.corridor for x in d["corridors"][c]["experiments"]["Experiment_E"]["E1_Perpendicular_Offset"].get("detour_ratios", [])[1:]]
    ovs = [x for c in df.corridor for x in d["corridors"][c]["experiments"]["Experiment_E"]["E1_Perpendicular_Offset"].get("overlap_ratios", [])[1:]]
    return dict(group=label, n_corridors=len(df), n_with_any_alt=int(df.any_alt.sum()),
        pct_any_alt=round(df.any_alt.mean()*100, 1), n_full_k3=int(df.full_k3.sum()), pct_full_k3=round(df.full_k3.mean()*100, 1),
        mean_alts_all=round(df.alternatives.mean(), 3), mean_alts_when_any=round(s.alternatives.mean(), 3) if len(s) else np.nan,
        diversity_mean_incl_zero_for_failures=round(df.diversity_raw.mean(), 4),
        diversity_mean_successful_only=round(s.diversity.mean(), 4) if len(s) else np.nan,
        diversity_median_successful_only=round(s.diversity.median(), 4) if len(s) else np.nan,
        n_alternatives_total=len(alts), detour_mean=round(float(np.mean(alts)), 4) if alts else np.nan, detour_max=max(alts) if alts else np.nan,
        overlap_mean=round(float(np.mean(ovs)), 4) if ovs else np.nan, overlap_max=max(ovs) if ovs else np.nan,
        runtime_median_s=round(df.runtime_s.median(), 2), runtime_mean_s=round(df.runtime_s.mean(), 2),
        runtime_min_s=df.runtime_s.min(), runtime_max_s=df.runtime_s.max())
S = [summ(T, "All 25 corridors")] + [summ(T[T.dist_class == c], f"{c} corridors") for c in ["Short", "Medium", "Long"]]
S = pd.DataFrame(S); S.to_csv(os.path.join(OUT, "expE_offset_summary.csv"), index=False)

# ---------- Yen comparison (5 corridors) ----------
Y = []
for cid in YEN:
    E = d["corridors"][cid]["experiments"]["Experiment_E"]; cls = T.set_index("corridor").loc[cid]
    e1, e2, e3 = E["E1_Perpendicular_Offset"], E["E2_Raw_Yen_KSP"], E["E3_Filtered_Yen_KSP"]
    for name, e, alts_key in (("E1 Offset", e1, "surviving_count"), ("E2 Raw Yen", e2, "surviving_alts"), ("E3 Filtered Yen", e3, "surviving_alts")):
        det = e.get("detour_ratios", [])[1:]; ov = e.get("overlap_ratios", [])[1:]
        Y.append(dict(corridor=cid, dist_class=cls.dist_class, dist_km=cls.dist_km, method=name,
                      alternatives=e[alts_key], candidates=e.get("generated_count", e.get("candidates_generated")),
                      rejected_overlap=e.get("rejected_overlap", np.nan),
                      diversity=e["pairwise_diversity"], runtime_s=round(e["runtime_ms"]/1000, 2),
                      detour_mean=round(float(np.mean(det)), 4) if det else np.nan,
                      overlap_mean=round(float(np.mean(ov)), 4) if ov else np.nan, overlap_max=max(ov) if ov else np.nan,
                      status=e.get("outcome_status", "n/a (offset)"), k3_achieved=int(e[alts_key] == 3)))
Y = pd.DataFrame(Y); Y.to_csv(os.path.join(OUT, "expE_yen_comparison_per_corridor.csv"), index=False)

G = []
for m, g in Y.groupby("method"):
    ok = g[g.alternatives > 0]
    matched = g[g.corridor.isin(Y[(Y.method == "E1 Offset") & (Y.alternatives > 0)].corridor) & g.corridor.isin(Y[(Y.method == "E3 Filtered Yen") & (Y.alternatives > 0)].corridor)]
    G.append(dict(method=m, n=len(g), corridors_with_any_alt=len(ok), k3_achieved=int(g.k3_achieved.sum()),
        mean_alts=round(g.alternatives.mean(), 2), runtime_mean_s=round(g.runtime_s.mean(), 2), runtime_median_s=round(g.runtime_s.median(), 2),
        diversity_mean_all5_zero_for_failures=round(g.diversity.mean(), 4),
        diversity_mean_corridors_with_alts=round(ok.diversity.mean(), 4),
        diversity_mean_matched_corridors=round(matched.diversity.mean(), 4), n_matched=len(matched),
        overlap_mean_alts=round(ok.overlap_mean.mean(), 4), overlap_max=g.overlap_max.max(),
        detour_mean_alts=round(ok.detour_mean.mean(), 4), candidates_total=int(g.candidates.sum()),
        rejected_overlap_total=(int(g.rejected_overlap.sum()) if m == "E3 Filtered Yen" else np.nan)))
G = pd.DataFrame(G); G.to_csv(os.path.join(OUT, "expE_yen_comparison_summary.csv"), index=False)

# runtime ratios per corridor (Yen / offset)
P = Y.pivot(index="corridor", columns="method", values="runtime_s")
R = pd.DataFrame({"E1_offset_s": P["E1 Offset"], "E2_raw_yen_s": P["E2 Raw Yen"], "E3_filtered_yen_s": P["E3 Filtered Yen"]})
R["E2_over_E1"] = (R.E2_raw_yen_s / R.E1_offset_s).round(2); R["E3_over_E1"] = (R.E3_filtered_yen_s / R.E1_offset_s).round(2)
R.to_csv(os.path.join(OUT, "expE_runtime_ratios.csv"))
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print(S.T.to_string()); print(); print(Y.drop(columns=["status"]).to_string()); print(); print(G.T.to_string()); print(); print(R.to_string())
print("ratio of means E2/E1:", round(R.E2_raw_yen_s.mean()/R.E1_offset_s.mean(), 2), " median per-corridor ratio:", R.E2_over_E1.median())

# ---------- figure ----------
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5, "legend.fontsize": 7,
                     "xtick.labelsize": 7.5, "ytick.labelsize": 7.5})
fig, axs = plt.subplots(1, 3, figsize=(7.16, 3.0), constrained_layout=True)
# (a) alternatives per corridor, stacked by class
ax = axs[0]; cnts = pd.crosstab(T.alternatives, T.dist_class).reindex(index=[0, 1, 2, 3], columns=["Short", "Medium", "Long"], fill_value=0)
bot = np.zeros(4); cl = {"Short": "#c6dbef", "Medium": "#6baed6", "Long": "#08519c"}
for c in ["Short", "Medium", "Long"]:
    ax.bar(cnts.index, cnts[c], bottom=bot, color=cl[c], label=c, width=0.65, edgecolor="white", lw=0.5); bot += cnts[c].values
for x, t in zip(cnts.index, bot): ax.text(x, t + 0.25, f"{int(t)}", ha="center", fontsize=7.5)
ax.set_xticks([0, 1, 2, 3]); ax.set_xlabel("Alternatives returned"); ax.set_ylabel("Corridors (of 25)"); ax.set_ylim(0, 17)
ax.set_title("(a) Offset: alternatives", loc="left"); ax.legend(title="Distance class", title_fontsize=7, frameon=False, loc="upper left")
# (b) diversity per Yen corridor
ids = list(YEN); lab = [c.replace("OD_", "C") for c in ids]
mk = {"E1 Offset": ("o", "#08519c"), "E2 Raw Yen": ("s", "#969696"), "E3 Filtered Yen": ("^", "#d95f0e")}
ax = axs[1]
for m, (mkr, col) in mk.items():
    g = Y[Y.method == m].set_index("corridor").loc[ids]
    xs = np.arange(len(ids)) + {"E1 Offset": -0.18, "E2 Raw Yen": 0, "E3 Filtered Yen": 0.18}[m]
    ax.scatter(xs, g.diversity, marker=mkr, color=col, s=24, label=m, zorder=3, edgecolor="white", lw=0.4)
    for x, y, a in zip(xs, g.diversity, g.alternatives):
        if a == 0: ax.scatter([x], [y], marker="x", color="k", s=30, zorder=4)
ax.set_xticks(range(len(ids))); ax.set_xticklabels(lab); ax.set_ylim(-0.04, 0.78); ax.set_xlabel("Corridor (Yen subset)"); ax.set_ylabel("Pairwise diversity (1 - Jaccard)")
ax.set_title("(b) Diversity (x = none returned)", loc="left"); ax.grid(alpha=0.25, lw=0.4)
# (c) runtime per corridor, log scale
ax = axs[2]; w = 0.26
for k, (m, (mkr, col)) in enumerate(mk.items()):
    g = Y[Y.method == m].set_index("corridor").loc[ids]
    ax.bar(np.arange(len(ids)) + (k-1)*w, g.runtime_s, width=w, color=col, label=m, edgecolor="white", lw=0.4)
ax.set_yscale("log"); ax.set_xticks(range(len(ids))); ax.set_xticklabels(lab); ax.set_xlabel("Corridor (Yen subset)"); ax.set_ylabel("Median runtime (s, log scale)")
ax.set_title("(c) Runtime per corridor", loc="left"); ax.grid(axis="y", alpha=0.25, lw=0.4)
from matplotlib.lines import Line2D
hs = [Line2D([0], [0], marker=mkr, color="w", markerfacecolor=col, markersize=7, label=m) for m, (mkr, col) in mk.items()]
fig.legend(handles=hs, loc="outside lower center", ncol=3, frameon=False, fontsize=7.5)
fig.savefig(os.path.join(OUT, "fig_expE_phase3.png"), dpi=300); fig.savefig(os.path.join(OUT, "fig_expE_phase3.pdf"))
print("figure ok")
