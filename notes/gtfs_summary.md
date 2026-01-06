# GTFS Feed Summary - Rail Maroc

## Feed Statistics

| File | Records | Description |
|------|---------|-------------|
| `agency.txt` | 1 | ONCF agency definition |
| `stops.txt` | 33 | Train stations across Morocco |
| `routes.txt` | 9 | Rail routes (Al Boraq, Al Atlas, TNR) |
| `calendar.txt` | 3 | Service patterns (weekday, weekend, daily) |
| `trips.txt` | 60 | Individual train trips |
| `stop_times.txt` | 240 | Stop time entries |
| `feed_info.txt` | 1 | Feed metadata |

## Routes Included

### High-Speed (Al Boraq)
1. **AL_BORAQ_TNG_CASA** - Tanger ↔ Casablanca (~2h10)
   - 15 southbound + 6 northbound trips daily
   - Stops: Tanger-Ville, Kénitra, Rabat-Agdal, Casa-Voyageurs

### Inter-City (Al Atlas)
2. **AL_ATLAS_CASA_MKC** - Casablanca ↔ Marrakech (~2h)
   - 11 trips each direction daily
   - Direct service

3. **AL_ATLAS_CASA_FES** - Casablanca ↔ Fès (~3h30)
   - 4 trips each direction daily
   - Stops: Casa-Voyageurs, Rabat-Agdal, Meknès, Fès

4. **AL_ATLAS_TNG_FES** - Tanger ↔ Fès (Direct, ~4h13)
   - 4 trips daily
   - Stops: Tanger-Ville, Sidi Kacem, Meknès, Fès

### Suburban (TNR)
5. **TNR_CASA_KENITRA** - Casa-Port ↔ Kénitra (~1h45)
   - 6 sample trips (actual service is every 10-20 min)
   - 11 stops along Atlantic corridor

### Additional Routes (Defined but minimal trips)
6. **AL_BORAQ_TNG_MKC** - Tanger ↔ Marrakech (through service)
7. **AL_ATLAS_CASA_OUJDA** - Casablanca ↔ Oujda (Eastern line)
8. **AL_ATLAS_CASA_JADIDA** - Casablanca ↔ El Jadida
9. **AL_ATLAS_NADOR_CASA** - Nador ↔ Casablanca

## Stations Coverage

### Major Hubs
- **Casablanca**: Casa-Voyageurs, Casa-Port, Casa-Oasis
- **Rabat**: Rabat-Agdal, Rabat-Ville
- **Tangier**: Tanger-Ville, Tanger Al Boraq
- **Marrakech**: Single main station
- **Fès**: Single main station

### Regional Stations
- Kénitra, Meknès, Oujda, Taza, Settat, El Jadida, Safi, Nador

### Suburban Stations (TNR Line)
- Ain Sebaâ, Mohammedia, Bouznika, Skhirat, Témara, Salé, Salé-Tabriquet

## Data Quality Notes

### ✅ Verified Data
- Station coordinates from OpenStreetMap/Wikipedia
- Al Boraq timetables from official ONCF PDF (Spring 2024)
- Route structure from seat61.com and moroccotrains.com

### ⚠️ Approximate Data
- Casablanca-Marrakech times (based on 2-hour journey time)
- Some intermediate stop times estimated
- TNR frequency simplified (actual is much higher)

### 📝 To Improve
- Add more TNR trips (currently shows 6, actual is 50+/day)
- Add Oujda/Nador line trips
- Add El Jadida/Safi branch trips
- Add overnight train services
- Verify all coordinates on-ground

## Validation

To validate this feed:
```bash
# Using MobilityData GTFS Validator
java -jar gtfs-validator.jar -i gtfs/ -o validation_report/

# Or Google's transitfeed
feedvalidator.py gtfs/
```

## Next Steps

1. **Validate** - Run through GTFS validator
2. **Expand** - Add more trips for all routes
3. **Submit** - Google Transit Partner Program
4. **OSM** - Ensure rail geometry is complete in OpenStreetMap
