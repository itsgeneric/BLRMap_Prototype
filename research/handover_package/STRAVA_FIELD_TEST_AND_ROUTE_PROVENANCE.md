# Strava Field Tests and Route Provenance

## User's firsthand account — accept as working premise
The user personally states:
- All five Strava activities were rides following routes recommended by the user's own BLRMap project.
- Morning rides were Home → Office.
- Afternoon rides were Office → Home.
- On the afternoon commute, the user initially followed an earlier route drawn by the project. A rerouting event then occurred, and the project recommended the CMH Road / Indiranagar / Murphy Road corridor. The user followed that project-recommended route from then on.
- The same afternoon corridor was followed on 3 November and 6 November.
- The user does not want further Antigravity testing to prove the CMH recommendation. Accept this as firsthand user-confirmed history for planning and analysis, while noting the application did not preserve the original route telemetry.

## Nominal coordinates
Home: 13.009650938573566, 77.59550260525107  
Office: 12.986041215429744, 77.66777637520387

Morning: Home → Office.  
Afternoon: Office → Home.

## GPX files included
- `Day_1_Morning_Ride.gpx`
- `Day_1_Afternoon_Ride.gpx`
- `Day_2_Morning.gpx`
- `Day_3_Morning_RIde.gpx`
- `Day_3_afternoon.gpx`

## Screenshot files included
- `Day1_morning.png`
- `Day1_afternoon.png`
- `Day2_morning.png`
- `Day3_morning.png`
- `Day3_afternoon.png`

## Activity metadata from the audit
| Activity | IST time | Direction | GPX distance |
|---|---|---|---:|
| Day 1 Morning (Nov 3) | 10:00:29–10:31:35 | Home → Office | 11.840 km |
| Day 1 Afternoon (Nov 3) | 13:22:07–13:55:18 | Office → Home | 12.201 km |
| Day 2 Morning (Nov 4) | 09:55:56–10:30:43 | Home → Office | 12.191 km |
| Day 3 Morning (Nov 6) | 09:24:46–09:53:08 | Home → Office | 11.686 km |
| Day 3 Afternoon (Nov 6) | 12:41:21–13:15:19 | Office → Home | 12.287 km |

These are GPX point-to-point computed distances from the audit; Strava's displayed distance may differ. Elapsed times are derived from first/last GPS timestamps.

## GPS route consistency findings
- Day 1 Morning vs Day 3 Morning: mean mutual trajectory deviation 3.5 m (P90 6.2 m).
- Day 1 Afternoon vs Day 3 Afternoon: mean mutual trajectory deviation 5.2 m (P90 6.4 m).
- Morning trajectories closely match the recovered MongoDB morning route snapshot (11.23 km, 381 points):
  - Day 1 Morning mean deviation 66.1 m (P90 189.2 m).
  - Day 2 Morning mean deviation 91.9 m (P90 334.6 m).
  - Day 3 Morning mean deviation 65.7 m (P90 200.2 m).
- The morning route snapshot is MongoDB document `6aeb9507cb8bb18c0918511f`; it is 100% coordinate-identical to older document `6abbfb192bd55da62aa1a464`.
- Recovered afternoon engine snapshot `6ae9d93bbe7ce3c2d71601d5` is 11.62 km / 370 points, but follows a different northern corridor. The CMH Road Strava tracks diverge from it by about 327 m mean.
- User confirms the CMH Road corridor was recommended by the project after rerouting. It was followed consistently on Nov 3 and Nov 6. Treat as user-confirmed, but original route snapshot/session telemetry was not recovered.

## Phase 2A provenance audit classification (as database evidence only)
- Day 1 Morning: Category B — historical geometry recovered; contemporaneous display not verified.
- Day 1 Afternoon: Category C in the database-only audit because CMH route snapshot was not found.
- Day 2 Morning: Category B.
- Day 3 Morning: Category B.
- Day 3 Afternoon: Category C in the database-only audit because CMH route snapshot was not found.

Important: This database-evidence classification does not override the user's firsthand account. For future research, label afternoon route as **user-confirmed project recommendation; original application record unavailable**. Do not call it an external app route.

## Route audit findings
- MongoDB Atlas `blrnav.journeys` had 105 records for the Home ↔ Office corridor and 30 distinct route geometries.
- Morning baseline: `6aeb9507cb8bb18c0918511f`, 11.23 km, 381 points.
- Afternoon engine baseline: `6ae9d93bbe7ce3c2d71601d5`, 11.62 km, 370 points.
- The database timestamps were after the relevant rides; no contemporaneous session IDs were linked. No further investigation is authorised by the user.
- Historical routing reported state-expanded A*, road multipliers, bridge/flyover override 0.80, roundabout 0.95, turn penalties 25/8/0 m.
- The audit reported the heuristic changed from `h=d/0.8` to `h=0.8*d` on 4 Nov 2026 at 13:44:20 IST; both were reported to produce the same static route for the tested graph.

## Research treatment
The five rides are useful real-world observations of routes the user says were recommended by the project. They are not a controlled head-to-head comparison with Google Maps/Waze. Do not claim actual travel-time savings or superiority from these five observations alone.
