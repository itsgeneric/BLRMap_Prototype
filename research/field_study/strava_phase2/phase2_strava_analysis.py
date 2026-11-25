"""
Paper 2, Phase 2: Strava GPX analysis (five rides over three days).
Inputs : the five GPX files from the handover package (read-only).
Outputs: strava_points_supplement_anonymised.csv (arbitrary-origin metres, elapsed seconds only, first/last 500 m removed),
         strava_ride_summary.csv, strava_consistency.csv, strava_sensitivity.csv,
         fig_strava_phase2.png / .pdf (privacy-trimmed).
Endpoints are referred to only as Point 1 and Point 2. No place names or absolute coordinates are written out.
No external data, no MongoDB. Pure measurement from GPX.
"""
import re, math, datetime as dt, sys, os
import numpy as np, pandas as pd

SRC = sys.argv[1]            # folder holding the GPX files
OUT = sys.argv[2]            # output folder
os.makedirs(OUT, exist_ok=True)

RIDES = [  # id, file, direction, label
    ("D1_AM", "Day_1_Morning_Ride.gpx",   "Point 1 -> Point 2", "Day 1 AM"),
    ("D1_PM", "Day_1_Afternoon_Ride.gpx", "Point 2 -> Point 1", "Day 1 PM"),
    ("D2_AM", "Day_2_Morning.gpx",        "Point 1 -> Point 2", "Day 2 AM"),
    ("D3_AM", "Day_3_Morning_RIde.gpx",   "Point 1 -> Point 2", "Day 3 AM"),
    ("D3_PM", "Day_3_afternoon.gpx",      "Point 2 -> Point 1", "Day 3 PM"),
]
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
R = 6371008.8

def read_gpx(path):
    t = open(path, encoding="utf-8").read()
    rows = re.findall(r'<trkpt lat="([\d.\-]+)" lon="([\d.\-]+)">(.*?)</trkpt>', t, re.S)
    out = []
    for la, lo, body in rows:
        tm = re.search(r"<time>(.*?)</time>", body).group(1)
        el = re.search(r"<ele>(.*?)</ele>", body)
        out.append((float(la), float(lo), float(el.group(1)) if el else np.nan,
                    dt.datetime.fromisoformat(tm.replace("Z", "+00:00"))))
    return out

def hav(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2)
    dp, dl = p2 - p1, np.radians(lo2 - lo1)
    h = np.sin(dp/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2*R*np.arcsin(np.sqrt(h))

# ---------- per-point dataset ----------
frames = {}
for rid, f, direction, label in RIDES:
    p = read_gpx(os.path.join(SRC, f))
    d = pd.DataFrame(p, columns=["lat", "lon", "ele_m", "t_utc"])
    d["ride_id"] = rid
    d["t_ist"] = d["t_utc"].dt.tz_convert(IST)
    d["elapsed_s"] = (d["t_utc"] - d["t_utc"].iloc[0]).dt.total_seconds()
    d["dt_s"] = d["elapsed_s"].diff()
    d["step_m"] = np.r_[np.nan, hav(d.lat.values[:-1], d.lon.values[:-1], d.lat.values[1:], d.lon.values[1:])]
    d["speed_ms"] = d["step_m"] / d["dt_s"]
    d["cum_m"] = d["step_m"].fillna(0).cumsum()
    frames[rid] = d

# ---------- time classification (threshold-based, with sensitivity) ----------
GAP_S = 5.0   # intervals longer than this are treated as recording gaps, not 1 Hz samples
def classify(d, v_thr):
    x = d.iloc[1:]
    gap = x.dt_s > GAP_S
    slow = x.speed_ms < v_thr
    stop_sampled = (~gap) & slow            # 1 Hz samples, slow/stationary
    stop_gap = gap & slow                   # gap with no net movement (likely pause/stationary)
    move_gap = gap & ~slow                  # gap while displacement occurred (signal loss while moving)
    return dict(
        stopped_s=float(x.dt_s[stop_sampled | stop_gap].sum()),
        stopped_sampled_s=float(x.dt_s[stop_sampled].sum()),
        stopped_gap_s=float(x.dt_s[stop_gap].sum()),
        moving_s=float(x.dt_s[~(stop_sampled | stop_gap)].sum()),
        gap_moving_s=float(x.dt_s[move_gap].sum()),
        moving_m=float(x.step_m[~(stop_sampled | stop_gap)].sum()),
        n_stop_events=int(((stop_sampled | stop_gap).astype(int).diff().fillna(0) == 1).sum()),
    )

summ, sens = [], []
for rid, f, direction, label in RIDES:
    d = frames[rid]
    dist = d.step_m.sum(); el = d.elapsed_s.iloc[-1]
    c = classify(d, 0.5)
    spd = d.speed_ms[(d.dt_s <= GAP_S)]
    summ.append(dict(
        ride_id=rid, label=label, direction=direction,
        n_points=len(d), median_sample_interval_s=float(d.dt_s.median()),
        n_gaps_gt5s=int((d.dt_s > GAP_S).sum()), max_gap_s=float(d.dt_s.max()),
        distance_km=round(dist/1000, 3),
        elapsed_min=round(el/60, 2),
        stopped_min=round(c["stopped_s"]/60, 2),
        moving_min=round(c["moving_s"]/60, 2),
        avg_speed_elapsed_kmh=round(dist/el*3.6, 1),
        avg_speed_moving_kmh=round(c["moving_m"]/c["moving_s"]*3.6, 1),
        median_sampled_speed_kmh=round(float(spd.median())*3.6, 1),
        stop_events=c["n_stop_events"],
        gap_while_moving_s=round(c["gap_moving_s"], 0)))
    for v in (0.3, 0.5, 1.0):
        cc = classify(d, v)
        sens.append(dict(ride_id=rid, v_thr_ms=v, stopped_min=round(cc["stopped_s"]/60, 2),
                         moving_min=round(cc["moving_s"]/60, 2),
                         avg_speed_moving_kmh=round(cc["moving_m"]/cc["moving_s"]*3.6, 1)))
summ = pd.DataFrame(summ); sens = pd.DataFrame(sens)

# ---------- trajectory consistency (symmetric cross-track, overlap-only) ----------
LAT0 = float(np.mean([d.lat.mean() for d in frames.values()])); LON0 = float(np.mean([d.lon.mean() for d in frames.values()]))  # projection origin = data mean; never written out
def xy(d):
    x = (d.lon.values - LON0) * 111320.0 * math.cos(math.radians(LAT0))
    y = (d.lat.values - LAT0) * 110574.0
    return np.c_[x, y]
XY = {k: xy(v) for k, v in frames.items()}

def cross_track(P, Q):
    """distance from each point of P to polyline Q; returns (dist, clamped_to_Q_endpoint_flag)."""
    A, B = Q[:-1], Q[1:]
    AB = B - A
    L2 = (AB**2).sum(1); L2[L2 == 0] = 1e-9
    dmin = np.full(len(P), np.inf); endflag = np.zeros(len(P), bool)
    for i in range(0, len(P), 400):
        p = P[i:i+400][:, None, :]
        t = ((p - A) * AB).sum(2) / L2
        tc = np.clip(t, 0, 1)
        proj = A + tc[..., None] * AB
        dd = np.sqrt(((p - proj)**2).sum(2))
        j = dd.argmin(1); r = np.arange(len(j))
        dmin[i:i+400] = dd[r, j]
        endflag[i:i+400] = ((j == 0) & (t[r, j] <= 0)) | ((j == len(A)-1) & (t[r, j] >= 1))
    return dmin, endflag

def mutual(a, b):
    out = {}
    ds = []
    for P, Q, nm in ((XY[a], XY[b], "a_to_b"), (XY[b], XY[a], "b_to_a")):
        dd, ef = cross_track(P, Q)
        out[f"excluded_{nm}"] = int(ef.sum()); out[f"n_{nm}"] = len(P)
        ds.append(dd[~ef])
    allv = np.concatenate(ds)
    out.update(mean_m=round(float(allv.mean()), 1), median_m=round(float(np.median(allv)), 1),
               p90_m=round(float(np.percentile(allv, 90)), 1), max_m=round(float(allv.max()), 1),
               pct_within_15m=round(float((allv <= 15).mean()*100), 1))
    return out

pairs = [("D1_AM", "D3_AM", "Morning repeat (Day 1 vs Day 3)"),
         ("D1_AM", "D2_AM", "Morning (Day 1 vs Day 2)"),
         ("D2_AM", "D3_AM", "Morning (Day 2 vs Day 3)"),
         ("D1_PM", "D3_PM", "Afternoon repeat (Day 1 vs Day 3)"),
         ("D1_AM", "D1_PM", "Control: morning vs afternoon, Day 1 (different corridors)")]
cons = []
for a, b, nm in pairs:
    r = mutual(a, b); r.update(pair=f"{a} vs {b}", description=nm); cons.append(r)
cons = pd.DataFrame(cons)[["pair", "description", "mean_m", "median_m", "p90_m", "max_m", "pct_within_15m",
                           "n_a_to_b", "excluded_a_to_b", "n_b_to_a", "excluded_b_to_a"]]

# ---------- write tables ----------
TRIM = 500.0   # metres removed from each end of every published track
allp = np.vstack(list(XY.values())); ox, oy = allp.min(0) - 300.0     # arbitrary origin, not written out
sup = []
for rid, d in frames.items():
    m = ((d.cum_m > TRIM) & (d.cum_m < d.cum_m.iloc[-1] - TRIM)).values
    P = XY[rid] - [ox, oy]
    sup.append(pd.DataFrame({"ride_id": rid, "elapsed_s": d.elapsed_s[m].round(1), "x_m": P[m, 0].round(1), "y_m": P[m, 1].round(1),
                             "step_m": d.step_m[m].round(2), "speed_ms": d.speed_ms[m].round(3)}))
pd.concat(sup).to_csv(os.path.join(OUT, "strava_points_supplement_anonymised.csv"), index=False)
summ.to_csv(os.path.join(OUT, "strava_ride_summary.csv"), index=False)
cons.to_csv(os.path.join(OUT, "strava_consistency.csv"), index=False)
sens.to_csv(os.path.join(OUT, "strava_sensitivity.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print(summ.T.to_string()); print(); print(cons.to_string()); print(); print(sens.to_string())

# ---------- figure (privacy-trimmed, no map tiles, no absolute coordinates) ----------
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
TRIM = 500.0   # metres removed from each end of every plotted track
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.labelsize": 8,
                     "axes.titlesize": 8.5, "legend.fontsize": 7, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5})
fig = plt.figure(figsize=(7.16, 3.1), constrained_layout=True)
gs = fig.add_gridspec(1, 2, width_ratios=[1.45, 1])
ax = fig.add_subplot(gs[0]); bx = fig.add_subplot(gs[1])

allxy = []
style = {"D1_AM": dict(c="#9ecae1", lw=4.0, ls="-", z=2),  "D3_AM": dict(c="#08519c", lw=1.2, ls="-", z=4),
         "D2_AM": dict(c="#6baed6", lw=1.2, ls=(0, (3, 2)), z=3),
         "D1_PM": dict(c="#fdbb84", lw=4.0, ls="-", z=2),  "D3_PM": dict(c="#b30000", lw=1.2, ls="-", z=4)}
names = {"D1_AM": "Day 1 AM", "D2_AM": "Day 2 AM", "D3_AM": "Day 3 AM", "D1_PM": "Day 1 PM", "D3_PM": "Day 3 PM"}
for rid in ["D1_AM", "D2_AM", "D3_AM", "D1_PM", "D3_PM"]:
    d = frames[rid]; m = (d.cum_m > TRIM) & (d.cum_m < d.cum_m.iloc[-1] - TRIM)
    P = XY[rid][m.values]; allxy.append(P)
allxy = np.vstack(allxy); x0, y0 = allxy[:, 0].min() - 300, allxy[:, 1].min() - 300
for rid in ["D1_AM", "D2_AM", "D3_AM", "D1_PM", "D3_PM"]:
    d = frames[rid]; m = ((d.cum_m > TRIM) & (d.cum_m < d.cum_m.iloc[-1] - TRIM)).values
    P = (XY[rid][m] - [x0, y0]) / 1000
    s = style[rid]; ax.plot(P[:, 0], P[:, 1], color=s["c"], lw=s["lw"], ls=s["ls"], zorder=s["z"], label=names[rid],
                            solid_capstyle="round")
ax.set_aspect("equal"); ax.set_xlabel("East (km, arbitrary origin)"); ax.set_ylabel("North (km, arbitrary origin)")
ax.set_title("(a) GPS trajectories (first and last 500 m omitted)", loc="left")
ax.grid(alpha=0.25, lw=0.4); ax.legend(loc="upper right", frameon=True, framealpha=0.95, ncol=1, borderpad=0.4)

order = ["D1_AM", "D2_AM", "D3_AM", "D1_PM", "D3_PM"]
s2 = summ.set_index("ride_id")
mov = [s2.loc[r, "moving_min"] for r in order]; stp = [s2.loc[r, "stopped_min"] for r in order]
cols = ["#08519c", "#08519c", "#08519c", "#b30000", "#b30000"]
yy = np.arange(len(order))[::-1]
bx.barh(yy, mov, color=cols, height=0.6, label="Moving")
bx.barh(yy, stp, left=mov, color="#bdbdbd", height=0.6, hatch="///", edgecolor="white", lw=0, label="Stopped / paused")
for y, m_, s_, r in zip(yy, mov, stp, order):
    bx.text(m_ + s_ + 0.5, y, f"{m_+s_:.1f} min  ({s2.loc[r,'distance_km']:.1f} km)", va="center", fontsize=7)
bx.set_yticks(yy); bx.set_yticklabels([names[r] for r in order]); bx.set_xlim(0, 56)
bx.set_xlabel("Recorded elapsed time (min)"); bx.set_title("(b) Elapsed time split", loc="left")
bx.grid(axis="x", alpha=0.25, lw=0.4); bx.legend(loc="upper center", bbox_to_anchor=(0.45, -0.20), ncol=2, frameon=False)
fig.savefig(os.path.join(OUT, "fig_strava_phase2.png"), dpi=300); fig.savefig(os.path.join(OUT, "fig_strava_phase2.pdf"))
print("figure ok")
