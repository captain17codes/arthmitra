# ArthMitra — Maharashtra Geospatial Data Pipeline Report

Date executed: 27 Oct 2026
Pipeline version: 1.0.0
Target State: Maharashtra (Focus District: Pune, LGD Code: 490)

## Summary Statistics

| Metric | Count / Value | Target | Status |
|---|---|---|---|
| Total LGD Villages Processed | 10 | Baseline Seed | ✅ PASS |
| Census 2011 Match Rate | 100.0% (10/10) | ≥ 95.0% | ✅ PASS |
| OSM Coordinates Match Rate | 100.0% (10/10) | ≥ 90.0% | ✅ PASS |
| Precomputed Neighbours (≤ 10 km) | 2 pairs | Complete Graph | ✅ PASS |

## Sub-District Coverage (Talukas)
- Haveli (LGD: 4201)
- Purandar (LGD: 4202)
- Baramati (LGD: 4203)
- Shirur (LGD: 4204)
- Khed (LGD: 4205)

## Generated Output Files
- `villages.csv`: Demographics, coordinates, and Mission Antyodaya amenities.
- `village_neighbours.csv`: Precomputed inter-village geodesic distance table for distance-decay catchment calculation.
