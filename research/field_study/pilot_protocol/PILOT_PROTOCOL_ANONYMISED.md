# Pilot external comparison protocol (Paper 2), anonymised

Status: FROZEN with Phase 2. Descriptive pilot, not a benchmark.
Pairs are labelled Pair A to Pair D. No place names, addresses, road names, coordinates, dates or clock times are published. The private key linking pair labels to real locations is held only in the author's private archive.

## Platforms and settings
| Platform | Setting | Route used |
|---|---|---|
| Project | Dynamic tab (live-traffic mode); returns one route by design (the Shortest Path tab returns two) | The single route returned |
| Google Maps (web) | Motorcycle tab, "Leave now" | Top-ranked route |
| Waze (web) | Motorcycle vehicle type (user-confirmed; the setting is not visible in the screenshots), "Leave now" | Route marked best |

## Collection
- Four origin-destination pairs, none of them among the 25 Experiment E corridors.
- For each pair the three platforms were queried within about 10 minutes of each other, in a single weekday evening window (inferred from file timestamps and Waze arrival clocks; not independently logged).
- Recorded: top-route distance, predicted ETA, number of alternatives shown (Google and Waze), toll flag. Values were transcribed from screenshots.

## Not recorded and not claimed
Actual travel time, turn counts, road-class exposure (manual tracing was judged too time-consuming), alternative-route quality, any ranking of platforms, any superiority claim.

## Evidence labels
| Item | Label |
|---|---|
| Distances and ETAs of top routes, alternative counts | Measured (transcribed from screenshots) |
| Waze motorcycle vehicle type | User-confirmed |
| Collection window | Unverified (inferred) |
| Project engine version on the collection day | Unverified |

## Limitations to state
1. n = 4 pairs, one window, one day.
2. Each platform's ETA comes from its own model. The project's live-traffic mode uses Google Routes data, so the project and Google are not independent.
3. Destinations were typed as place names and geocoded separately by each platform; some origins were coordinates and some were named places.
4. No rides were taken on these routes. Predicted ETAs must never be compared with measured elapsed times.
5. Project routes are one route per pair by design, so alternative counts are not compared.

## Results table
See pilot_pairs_anonymised.csv.
