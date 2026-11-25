# Phase 2 methodology note: repeated real-world journeys between two fixed endpoints (Paper 2, RQ4)

Status: FROZEN with Phase 2 (see PHASE2_FREEZE_MANIFEST.md).
Scope: five rides over three days (Day 1 to Day 3, AM and PM) along the Point 1 to Point 2 corridor. Real-world observational data only. No Paper 1 evidence is used.
Anonymisation: endpoints are Point 1 and Point 2. Morning (AM) rides run Point 1 to Point 2; afternoon (PM) rides run Point 2 to Point 1. Calendar dates and clock times are not published. No place names, road names or absolute coordinates appear in any output.

## 1. Evidence labels
| Item | Label |
|---|---|
| Distance, elapsed time, stopped/moving time, speeds, repeat-ride consistency (this note) | Measured (from GPX) |
| Morning alignment with the recovered MongoDB route snapshot (66.1 / 91.9 / 65.7 m mean deviation for Day 1 / Day 2 / Day 3 AM) | Recovered historical snapshot; audit-reported, not recomputed here (geometry not in the handover package); contemporaneous display not verified |
| The afternoon route was recommended by the author's own project after a rerouting event and followed on Day 1 and Day 3 | User-confirmed; no original application record is available (no independently recovered record) |
| Cause of the Day 2 AM deviation (section 4) | Unknown (not investigated; no explanation is offered) |

The afternoon rides are compared with each other only, never with the different afternoon route stored in the database. The user-confirmed afternoon recommendation must not be described as an independently recovered application record.

## 2. Calculations
- **Parsing.** Track points (latitude, longitude, elevation, UTC time) are read from each Strava GPX.
- **Distance.** Sum of haversine distances between consecutive points (R = 6,371,008.8 m). This reproduces the GPX distances in the handover audit (11.840, 12.201, 12.191, 11.686, 12.287 km). Strava's displayed distance may differ and was not available.
- **Elapsed time.** Last minus first GPS timestamp. This is recorded elapsed time, not an ETA.
- **Moving and stopped time.** For each interval between points, speed = distance / time. An interval is "stopped" if speed < 0.5 m/s. Intervals longer than 5 s are treated as recording gaps: a gap with no net movement counts as stopped, and a gap with displacement counts as moving (signal loss while moving). Moving speed = distance of moving intervals / moving time.
- **Average speed.** Reported both as distance / elapsed time (includes stops) and as moving speed.
- **Repeat-route consistency.** Tracks are projected to local metres (equirectangular, origin at the data mean, never written out). For each point of track A, the distance to the nearest point on the polyline of track B is computed, and vice versa. Points whose nearest location is an end of the other polyline (track not covering that stretch) are excluded. The mean, median, P90 and maximum are taken over all remaining points in both directions (symmetric).

## 3. Results (measured)
| Ride | Distance (km) | Elapsed (min) | Moving (min) | Stopped (min) | Speed incl. stops (km/h) | Moving speed (km/h) | Stop events |
|---|---:|---:|---:|---:|---:|---:|---:|
| Day 1 AM | 11.84 | 31.1 | 29.1 | 2.1 | 22.8 | 24.4 | 23 |
| Day 2 AM | 12.19 | 34.8 | 29.9 | 4.9 | 21.0 | 24.4 | 26 |
| Day 3 AM | 11.69 | 28.4 | 27.0 | 1.4 | 24.7 | 25.9 | 13 |
| Day 1 PM | 12.20 | 33.2 | 29.7 | 3.5 | 22.1 | 24.6 | 23 |
| Day 3 PM | 12.29 | 34.0 | 27.8 | 6.1 | 21.7 | 26.4 | 21 |

| Comparison | Mean (m) | P90 (m) | Max (m) | Points within 15 m |
|---|---:|---:|---:|---:|
| Morning, Day 1 vs Day 3 | 3.4 | 6.2 | 50.9 | 98.1% |
| Afternoon, Day 1 vs Day 3 | 2.9 | 6.2 | 18.6 | 99.8% |
| Morning, Day 2 vs Day 1 or Day 3 | about 59 | about 215 | 443 | about 67% |
| Control: morning vs afternoon, Day 1 | 377 | 1,096 | 1,463 | 30.7% |

## 4. Findings
1. The Day 1 and Day 3 morning rides follow the same path.
2. The Day 1 and Day 3 afternoon rides follow the same path.
3. **The Day 2 morning ride is an observed deviation from the Day 1 and Day 3 morning path, with unknown cause.** It lies more than 30 m from that path over about 0 to 1.3 km, about 7.7 to 8.7 km (mean about 220 m, max about 360 m), and about 10.3 to 11.1 km along the ride. The median deviation is 4 m, so the remainder is shared. No explanation is proposed.
4. The control comparison (377 m mean) shows that the metric separates different routes.

Agreement with the handover audit: morning Day 1 vs Day 3 is 3.4 m mean / 6.2 m P90 here against 3.5 / 6.2 in the audit. For the afternoon repeat, with no exclusion this analysis gives 3.9 m mean / 6.3 m P90 / 150.2 m max against 5.2 / 6.4 / 149.7. The maximum and P90 reproduce. The mean differs by about 1 m, probably from a different definition or sampling. Excluding the 43 non-overlapping end points gives 2.9 m mean and 18.6 m max.

## 5. Sensitivity to the stopped-speed threshold (include in methodology or supplement)
Stopped / moving minutes and moving speed (km/h) when an interval counts as stopped below 0.3, 0.5 (reported) and 1.0 m/s:

| Ride | 0.3 m/s | 0.5 m/s (reported) | 1.0 m/s |
|---|---|---|---|
| Day 1 AM | 1.53 / 29.57 / 24.0 | 2.05 / 29.05 / 24.4 | 2.93 / 28.17 / 25.1 |
| Day 2 AM | 3.93 / 30.85 / 23.7 | 4.93 / 29.85 / 24.4 | 6.27 / 28.52 / 25.4 |
| Day 3 AM | 1.15 / 27.22 / 25.7 | 1.35 / 27.02 / 25.9 | 1.70 / 26.67 / 26.2 |
| Day 1 PM | 2.88 / 30.30 / 24.1 | 3.47 / 29.72 / 24.6 | 4.22 / 28.97 / 25.1 |
| Day 3 PM | 5.40 / 28.57 / 25.8 | 6.13 / 27.83 / 26.4 | 6.85 / 27.12 / 27.0 |

Stopped time changes by about 0.5 to 2.3 min per ride across the range, and moving speed by about 0.5 to 1.7 km/h. The ride ordering by stopped time is unchanged, but absolute stopped time depends on the threshold.

## 6. Limitations
- n = 5 rides, one rider, 3 days. Descriptive only. No statistics.
- Raw distances are not like-for-like. Recording started and stopped at different places (the Day 1 and Day 3 morning rides began roughly 0.3 km after Point 1).
- GPS jitter adds a little distance while stopped.
- Strava's own "moving time" uses its own algorithm and was not available, so it is not claimed to match.
- Elapsed times (28.4 to 34.8 min) reflect traffic, signals and rider behaviour. They do not show that one route is faster, and must not be compared with Google or Waze ETAs.
- The files are labelled "cycling" by Strava. The paper must state the vehicle actually used.

## 7. Anonymisation and data custody
- The figure and the supplementary point file use metres from an arbitrary origin, with the first and last 500 m of every ride removed, and elapsed seconds only (no dates or clock times). Distances, elapsed times and speeds are unchanged.
- Summary statistics are computed from the complete tracks. Only the published geometry is trimmed.
- The original GPX files and all raw measurements stay in the author's private research archive. They were read, never modified (checksums verified), and must never be published. The anonymised point file is a separate derived dataset.
