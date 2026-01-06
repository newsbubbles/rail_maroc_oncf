# Rail Maroc - GTFS Implementation Plan

## Project Goal
Bring rail paths and functionality to map apps in Morocco by creating a GTFS feed for ONCF (Office National des Chemins de Fer).

---

## Phase 1 — Make the rail network "real" (OSM)

### Tools
- **Beginner**: OpenStreetMap iD editor (browser)
- **Power user**: JOSM (recommended if technical)

### Tags for Main Rail Lines
```
railway=rail
usage=main
gauge=1435          (standard gauge for ONCF)
electrified=yes     (most ONCF mainlines)
operator=ONCF
```

### Tags for Stations
```
railway=station
name=Casa-Voyageurs
operator=ONCF
network=ONCF
```

### Tags for Platforms
```
railway=platform
```

### Priority Routes (High Visibility)
1. Casablanca ↔ Rabat
2. Casa Voyageurs
3. Rabat Ville
4. Kenitra
5. Tangier (Al Boraq corridor)

---

## Phase 2 — Build a Minimal GTFS

### Required Files (Minimum Viable GTFS)
1. `agency.txt`
2. `stops.txt`
3. `routes.txt`
4. `trips.txt`
5. `stop_times.txt`
6. `calendar.txt`

### Data Sources
- ONCF official website: https://www.oncf.ma
- OpenStreetMap for coordinates
- Published timetables

### Validation Tools
- MobilityData GTFS Validator
- Google Transit Feed Validator

---

## Phase 3 — Submit to Google Transit

### Submission Process
- Google Transit Partner Program
- Frame as: "Pilot GTFS feed to demonstrate feasibility for Morocco rail"

### Key Framing Points
- International accessibility standard
- GTFS used by blind navigation tools
- Tourism, climate, inclusion benefits
- No operational secrets exposed
- "GTFS is a static public schedule format already visible on station boards"

---

## Phase 4 — Political Nudge (Optional)

### Messaging Strategy
- Avoid: "Google Maps doesn't show trains"
- Use: "International accessibility standard", "Tourism UX gap"

---

## Current Status
- [x] Phase 1: OSM mapping ✅ ALREADY DONE (by community)
- [x] Phase 2: GTFS data collection ✅ COMPLETE
- [ ] Phase 3: Google Transit submission (IN PROGRESS)

### Phase 2 Validation Results (2026-01-06)
- ✅ All required files present
- ✅ Agency validated (ONCF)
- ✅ 33 stops validated, all coordinates in Morocco bounds
- ✅ 9 routes validated (all Rail type)
- ✅ 3 service patterns (WEEKDAY, WEEKEND, DAILY)
- ✅ 60 trips validated, all references valid
- ✅ 240 stop_times validated, all times/sequences valid
- ✅ Feed info present
- 📦 `oncf_gtfs.zip` ready (4.5 KB)
- [ ] Phase 4: Stakeholder outreach

### Phase 2 Deliverables (Completed 2026-01-06)
- `gtfs/agency.txt` - ONCF agency definition
- `gtfs/stops.txt` - 33 stations with coordinates
- `gtfs/routes.txt` - 9 rail routes
- `gtfs/trips.txt` - 60 train trips
- `gtfs/stop_times.txt` - 240 stop time entries
- `gtfs/calendar.txt` - Service patterns
- `gtfs/feed_info.txt` - Feed metadata
