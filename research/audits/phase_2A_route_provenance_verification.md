# Phase 2A: Historical Route Provenance Verification
**Project:** BLRMap Prototype (Smart Bengaluru Two-Wheeler Routing Engine)  
**Investigation Type:** Read-Only Provenance Audit & Runtime Timestamp Analysis  
**Audit Date:** 2026-11-07  
**Artifact Classification:** Empirical Verification & Research Integrity Record  

---

## Executive Summary & Classification Matrix

This audit evaluated the runtime provenance of the recovered MongoDB route snapshots against the five Strava GPX activities recorded between 2026-11-03 and 2026-11-06.

In accordance with strict research integrity standards, each journey was classified into one of three tiers:
- **Category A:** Contemporaneous route recommendation verified (database record bound to actual ride timestamp with session or execution proof).
- **Category B:** Historical route snapshot recovered, but contemporaneous display not verified (identical route geometry recovered in database, but timestamps post-date or precede the ride, or lack contemporaneous session linkage).
- **Category C:** Route provenance unresolved (recorded trajectory departs from all recovered database snapshots; generation provenance cannot be verified).

### Activity Classification Summary

| Activity | Ride Date & Time (IST) | Trajectory Direction | Matching Snapshot in MongoDB | Provenance Classification | Primary Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Day 1 Morning** | 2026-11-03<br>10:00:29 – 10:31:35 | Home → Office | `6aeb9507cb8bb18c0918511f`<br>(Clone: `6abbfb192bd55da62aa1a464`) | **Category B** | Route geometry recovered with 100% precision (381 pts, 11.23 km; mean dev 66.1 m). However, earliest Nov 3 DB record logged at 18:22 IST (~8 hrs after ride). No contemporaneous session logged. |
| **Day 1 Afternoon** | 2026-11-03<br>13:22:07 – 13:55:18 | Office → Home | *None* (Departs from DB route `6ae9d93bbe7ce3c2d71601d5`) | **Category C** | Trajectory follows CMH Road corridor (12.20 km). Diverges from recovered DB return route (`6ae9d93bbe7ce3c2d71601d5`) by 327.2 m mean dev. No CMH return route exists in MongoDB corpus. |
| **Day 2 Morning** | 2026-11-04<br>09:55:56 – 10:30:43 | Home → Office | `6aeb9507cb8bb18c0918511f`<br>(Clone: `6abbfb192bd55da62aa1a464`) | **Category B** | Route geometry recovered with 100% precision (381 pts, 11.23 km; mean dev 91.9 m). DB record created at 01:56 IST on Nov 5 (~15.5 hrs after ride). No contemporaneous session logged. |
| **Day 3 Morning** | 2026-11-06<br>09:24:46 – 09:53:08 | Home → Office | `6aeb9507cb8bb18c0918511f`<br>(Clone: `6abbfb192bd55da62aa1a464`) | **Category B** | Trajectory matches Day 1 Morning GPX within 3.5 m mean dev and DB snapshot within 65.7 m. Zero queries logged to MongoDB on Nov 6; contemporaneous display unverified. |
| **Day 3 Afternoon** | 2026-11-06<br>12:41:21 – 13:15:19 | Office → Home | *None* (Departs from DB route `6ae9d93bbe7ce3c2d71601d5`) | **Category C** | Trajectory matches Day 1 Afternoon within 5.2 m mean dev (CMH Road corridor). Does not match any recovered Office → Home snapshot in MongoDB. |

> [!IMPORTANT]
> **Key Finding:** No activity qualifies for Category A. While the Morning Dynamic route was recovered with 100% geometric precision from MongoDB Atlas (Category B), database insertion timestamps post-date the rides by 4.5 to 15.5 hours, and no contemporaneous session IDs were bound during navigation.

---

## 1. MongoDB Timestamp Verification

The four requested route documents were audited directly from MongoDB Atlas (`blrnav.journeys`).

### 1.1 Timestamp Audit Matrix

| Metric / Field | Document 1: `6aeb9507cb8bb18c0918511f` | Document 2: `6abbfb192bd55da62aa1a464` | Document 3: `6ae9d93bbe7ce3c2d71601d5` | Document 4: `6ada31685cc0b289ffd2f434` |
| :--- | :--- | :--- | :--- | :--- |
| **Direction** | Home → Office (Morning) | Home → Office (Morning) | Office → Home (Afternoon) | Office → Home (Afternoon) |
| **Mode & Strategy** | `dynamic` / `direct` | `dynamic` / `direct` | `dynamic` / `direct` | `dynamic` / `direct` |
| **Distance & Points** | `11.23 km` / 381 coordinates | `11.23 km` / 381 coordinates | `11.62 km` / 370 coordinates | `11.62 km` / 370 coordinates |
| **ObjectId Time (UTC)** | 2026-11-04 20:26:47.000 UTC | 2026-09-29 17:53:29.000 UTC | 2026-11-03 12:53:15.000 UTC | 2026-10-22 15:53:12.000 UTC |
| **ObjectId Time (IST)** | **2026-11-05 01:56:47.000 IST** | **2026-09-29 23:23:29.000 IST** | **2026-11-03 18:23:15.000 IST** | **2026-10-22 21:23:12.000 IST** |
| **`created_at` (UTC)** | 2026-11-04 20:26:47.971000 | 2026-09-29 17:53:29.557000 | 2026-11-03 12:53:15.235000 | 2026-10-22 15:53:12.141000 |
| **`created_at` (IST)** | **2026-11-05 01:56:47.971 IST** | **2026-09-29 23:23:29.557 IST** | **2026-11-03 18:23:15.235 IST** | **2026-10-22 21:23:12.141 IST** |
| **`updated_at`** | Identical to `created_at` | Identical to `created_at` | Identical to `created_at` | Identical to `created_at` |
| **`route.computed_at`**| Identical to `created_at` | Identical to `created_at` | Identical to `created_at` | Identical to `created_at` |
| **`requested_at`** | *Field not present in schema* | *Field not present in schema* | *Field not present in schema* | *Field not present in schema* |
| **`session_id`** | `None` | `None` | `None` | `None` |
| **`status`** | `"planned"` | `"planned"` | `"planned"` | `"planned"` |
| **`journey.started_at`**| `None` | `None` | `None` | `None` |
| **`journey.completed_at`**| `None` | `None` | `None` | `None` |
| **Congested Avoided**| 0 nodes | 0 nodes | 13 nodes | 4 nodes |

### 1.2 Nature of the Recorded Timestamps
Code inspection of [`api_server.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/api_server.py) (lines 140–152) and [`database/operations.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/database/operations.py) (lines 53–74) confirms the exact operational meaning of these timestamps:
1. **Timestamp Generation:** When the backend handles `GET /dynamic-route`, it executes `now = _now() = datetime.now(timezone.utc)`.
2. **Atomic Record Creation:** `created_at`, `updated_at`, and `route.computed_at` are stamped synchronously with this single `now` value during the `db["journeys"].insert_one()` call.
3. **No Subsequent Updates:** In all four documents, `updated_at == created_at`. No updates occurred after initial insertion.
4. **No Lifecycle Progression:** The lifecycle fields (`status: "navigating"`, `journey.started_at`, `session_id`) populated when a user taps "Start Navigation" in [`app/page.tsx`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/app/page.tsx) are absent (`None`).

---

## 2. Historical Recommendation Provenance

### 2.1 Absence of Contemporaneous Logging During Rides
Comparing the ride timestamps from Strava GPX metadata against MongoDB database logs reveals a systematic temporal dislocation:

```
2026-11-03 (Day 1)
  10:00 - 10:31 IST: Day 1 Morning Ride  ──────┐ [No contemporaneous MongoDB records]
  13:22 - 13:55 IST: Day 1 Afternoon Ride ─────┤
                                               ▼
                                  18:22 - 18:23 IST: 3 Route queries logged in MongoDB
                                  (6ae9d909be..., 6ae9d91cbe..., 6ae9d93bbe...)

2026-11-04 (Day 2)
  09:55 - 10:30 IST: Day 2 Morning Ride  ──────┐ [No contemporaneous MongoDB records]
                                               ▼
                                  01:56 - 01:58 IST (Nov 5): 4 Route queries logged in MongoDB
                                  (6aeb94fe..., 6aeb9507..., 6aeb9559..., 6aeb9572...)

2026-11-06 (Day 3)
  09:24 - 09:53 IST: Day 3 Morning Ride  ──────┐ [ZERO queries logged on Nov 6]
  12:41 - 13:15 IST: Day 3 Afternoon Ride ─────┘
```

### 2.2 Root-Cause Analysis for Missing Mobile Telemetry
Investigation of the frontend and network configuration revealed why mobile navigation sessions did not generate contemporaneous database updates during transit:
1. **Hardcoded Loopback Address:** In [`lib/api.ts`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/lib/api.ts) (line 5) and [`lib/tripTracker.ts`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/lib/tripTracker.ts) (line 3), the backend API base is hardcoded to:
   ```typescript
   const API_BASE = 'http://127.0.0.1:8000';
   ```
2. **Network Disconnection on Transit:** While the user is on the road riding a motorcycle, a mobile client cannot reach `http://127.0.0.1:8000` (which refers to the phone's internal loopback rather than the developer's laptop host).
3. **Silent Failure Mode:** In [`lib/tripTracker.ts`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/lib/tripTracker.ts) (line 69), `startTrip` catches network connection errors silently:
   ```typescript
   fetch(`${API_BASE}/journeys/${journeyId}/start`, ...).catch(err => {
     console.debug('[TripTracker] startTrip notice:', err);
   });
   ```
   Consequently, when navigation commenced on the road, lifecycle telemetry failed silently, leaving all database records in the `"planned"` status with `session_id: null`.

### 2.3 Earlier Generation and Exact Geometric Reuse
Coordinate-by-coordinate comparison confirms that the routes recorded on November 3 and November 4 are exact, bit-for-bit duplicates of routes generated weeks earlier:
- **Morning Dynamic Route (381 points, 11.23 km):**
  Document `6aeb9507cb8bb18c0918511f` (logged 2026-11-04 20:26 UTC) is **100% coordinate-identical** to document `6abbfb192bd55da62aa1a464` (generated on 2026-09-29 17:53 UTC).
- **Afternoon Dynamic Route (370 points, 11.62 km):**
  Document `6ae9d93bbe7ce3c2d71601d5` (logged 2026-11-03 12:53 UTC) is **100% coordinate-identical** to document `6ada31685cc0b289ffd2f434` (generated on 2026-10-22 15:53 UTC).

Because `two_wheeler_astar` is deterministic on static graph topology in the absence of edge congestion penalties, the identical route was computed and displayed repeatedly across multiple sessions.

---

## 3. Afternoon Route Discrepancy Investigation

### 3.1 The CMH Road Trajectory
Both afternoon Strava GPX activities (`Day_1_Afternoon_Ride.gpx` and `Day_3_afternoon.gpx`) followed an identical spatial path with an average mutual difference of only **5.2 meters** (90th percentile: 6.4 meters).

The recorded corridor follows:
```
Office: CAIR DRDO (Kaggadasapura Main Road)
  │ (Suranjandas Road / 1st Main Road)
  ▼
Indiranagar 80 Feet Road
  │
  ▼
Chinmaya Mission Hospital (CMH) Road  <-- Critical Divergence Sector
  │
  ▼
Indiranagar Double Road (100 Feet Road / CMH Junction)
  │
  ▼
Swamy Vivekananda Road / Murphy Road (Ulsoor)
  │
  ▼
St. John's Road / Assaye Road / Haines Road / Miller Road / Jayamahal Road
  │
  ▼
Home: J.C. Nagar (L K Legacy)
```

### 3.2 Corpus-Wide Search for CMH Return Routes
A spatial query was executed across all 105 Home $\leftrightarrow$ Office documents in MongoDB Atlas, searching for any route polyline passing within 150 meters of the CMH Road / Indiranagar corridor (`12.9782, 77.6410`):
- **Matches Found:** Exactly 6 documents passed near CMH Road.
- **Directional Analysis:** **All 6 matching documents were Morning (Home → Office) routes** generated on 2026-09-29 and 2026-10-26 when morning traffic on Old Madras Road forced a southern diversion.
- **Office → Home Matches:** **ZERO**. Not a single Office → Home journey document in MongoDB follows the CMH Road corridor. All 10 Office → Home documents in the database returned either via Baiyappanahalli/Wheeler Road (11.62 km dynamic route) or Kensington/Murphy Road (10.99 km shortest route).

### 3.3 Examination of Frontend Alternative Route Logic
To assess whether the user was shown an alternative route option on screen:
1. **No Lateral Offset Alternatives in Mobile Frontend:**
   Inspection of [`components/Navigation/ModeSelector.tsx`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/components/Navigation/ModeSelector.tsx), [`components/Navigation/BottomActionBar.tsx`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/components/Navigation/BottomActionBar.tsx), and [`app/page.tsx`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/app/page.tsx) confirms that Perpendicular Lateral Offset candidate splitting (`build_split_route_candidates`) is **not invoked** in the Next.js production frontend. It exists solely in offline ablation evaluation scripts.
2. **"Fastest (Compare)" Dual-Route Display:**
   When the user selects the `"fastest"` mode in `ModeSelector.tsx`, the frontend calls `fetchBothRoutes()` in [`lib/api.ts`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/lib/api.ts), fetching `/route` (shortest) and `/dynamic-route` (dynamic) simultaneously. As confirmed by [`out/_next/static/chunks/829-b6ccace5c12fe177.js`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/out/_next/static/chunks/829-b6ccace5c12fe177.js), the alternative path rendered in `GoogleMapContainer.tsx` is simply the other route (e.g. shortest path if dynamic is primary).
3. **Topological Mismatch:**
   Neither the shortest route (`10.99 km`) nor the dynamic route (`11.62 km`) traversed CMH Road.

### 3.4 Divergence Finding & Classification
Because no project route snapshot in MongoDB Atlas records the CMH Road return path, and no frontend mechanism exists to generate it within the production codebase:
- The CMH Road afternoon trajectory cannot be traced to any saved project route.
- It is classified strictly as **Category C (Route provenance unresolved)**.

---

## 4. Heuristic Versioning and Runtime Verification

### 4.1 Git Repository and Commit State
- **HEAD Commit:** `afd989feec7ff550525ef89d78bb5dc8ca0d130f`
- **Commit Author:** CompsciiNikhil
- **Commit Timestamp:** `2026-10-27 22:40:30 +0530`
- **Commit Message:** *"Reroute from current GPS position instead of original origin"*
- **Status of Working Tree:** The working tree contains uncommitted modifications to [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py), [`core/config.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/core/config.py), [`routing/graph_manager.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/graph_manager.py), and [`api_server.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/api_server.py).

### 4.2 Verification of Source Modification Timestamps
Operating system file metadata on [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) was verified:
- **Filesystem Modification Timestamp:** `2026-11-04 13:44:20.427577 IST`
- **Nature of Change:** Introduction of `heuristic_mode="admissible"` with scaling:
  ```python
  # Legacy (Active at commit afd989f until 2026-11-04 13:44:20 IST):
  def heuristic(node):
      return haversine_m(...) / MIN_PENALTY_FLOOR  # 1.25 * haversine

  # Corrected (Active after 2026-11-04 13:44:20 IST):
  def heuristic(node):
      if heuristic_mode == "aggressive":
          return h_dist / MIN_PENALTY_FLOOR
      elif heuristic_mode == "admissible":
          return h_dist * MIN_PENALTY_FLOOR       # 0.80 * haversine
  ```

### 4.3 Activity-to-Configuration Mapping

| Journey Activity | Execution Time (IST) | Codebase Heuristic State | Active Runtime Configuration |
| :--- | :--- | :--- | :--- |
| **Day 1 Morning** | 2026-11-03 10:00:29 – 10:31:35 | Prior to modification | Legacy Aggressive Heuristic ($1.25 \cdot d$) |
| **Day 1 Afternoon** | 2026-11-03 13:22:07 – 13:55:18 | Prior to modification | Legacy Aggressive Heuristic ($1.25 \cdot d$) |
| **Day 2 Morning** | 2026-11-04 09:55:56 – 10:30:43 | Prior to modification | Legacy Aggressive Heuristic ($1.25 \cdot d$) |
| *[Source Modification]* | *2026-11-04 13:44:20 IST* | *Modified on disk* | *Transition from Aggressive to Admissible* |
| **Day 3 Morning** | 2026-11-06 09:24:46 – 09:53:08 | Post modification | Corrected Admissible Heuristic ($0.80 \cdot d$) |
| **Day 3 Afternoon** | 2026-11-06 12:41:21 – 13:15:19 | Post modification | Corrected Admissible Heuristic ($0.80 \cdot d$) |

### 4.4 Empirical Proof of Algorithmic Invariance
To establish whether this heuristic transition altered the generated path, an empirical evaluation was executed using the production graph network [`bengaluru_graph.pkl`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/bengaluru_graph.pkl):

```
Home Node: 10094964481  ────────►  Office Node: 10088394354

1. Under Aggressive Heuristic (Legacy Day 1 / Day 2):
   • Route Node Sequence: [10094964481, ..., 10088394354] (183 nodes)
   • Polyline Coordinates: 381 coordinates, 11.230 km
2. Under Admissible Heuristic (Corrected Day 3):
   • Route Node Sequence: [10094964481, ..., 10088394354] (183 nodes)
   • Polyline Coordinates: 381 coordinates, 11.230 km

Sequence Identity Check:
• route_agg == route_adm:       TRUE (100% Identical Node Sequence)
• coords_agg == coords_adm:     TRUE (100% Identical Coordinate Polyline)
• coords_agg == MongoDB Record: TRUE (Matches 6aeb9507cb8bb18c0918511f)
```

**Conclusion on Heuristic Versioning:**
On this specific commute corridor, the state-expanded search space is topologically constrained such that the optimal trade-off knee is invariant to the heuristic mode. Both the legacy aggressive heuristic and the corrected admissible heuristic generate the exact identical 11.230 km, 183-node, 381-coordinate route.

This mathematical equivalence directly explains why the Day 1 Morning ride (under the aggressive heuristic) and the Day 3 Morning ride (under the admissible heuristic) followed an identical spatial path with only **3.5 meters** average difference.

---

## 5. Audit Conclusions & Summary

1. **Morning Route Provenance (Category B):**
   The route geometry followed on Day 1, Day 2, and Day 3 mornings was recovered from MongoDB Atlas with 100% precision (`11.23 km`, 381 points). However, because database insertion timestamps post-date the rides by several hours and mobile session logging was disabled by loopback connection limits, contemporaneous display on the device cannot be verified through database logs alone.
2. **Afternoon Route Provenance (Category C):**
   Both afternoon rides followed an identical corridor through CMH Road and Murphy Road (5.2 m mutual deviation). This corridor does not exist in any recovered Office $\to$ Home document in MongoDB, and its provenance within the project cannot be verified.
3. **Heuristic Impact:**
   The heuristic transition from aggressive ($1.25\cdot d$) to admissible ($0.80\cdot d$) on 2026-11-04 at 13:44:20 IST was verified from filesystem metadata and git diffs, but had zero effect on the route geometry on this corridor due to topological invariance.
