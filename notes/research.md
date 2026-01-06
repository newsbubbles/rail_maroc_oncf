# Rail Maroc - Research Notes

## Data Sources
- ONCF Official: https://www.oncf.ma
- ONCF Voyages (tickets): https://www.oncf-voyages.ma
- Seat61 (comprehensive guide): https://www.seat61.com/train-travel-in-morocco.htm
- MoroccoTrains: https://www.moroccotrains.com
- Wikipedia: Railway stations in Morocco

## Train Types
1. **Al Boraq** - High-speed (320 km/h), TGV-based double-deck trains
2. **Al Atlas** - Classic inter-city trains, air-conditioned
3. **TNR (Train Navette Rapide)** - Suburban/commuter double-deck shuttles

## Main Routes

### Route 1: Al Boraq High-Speed (Tangier - Casablanca)
- **Stations**: Tanger-Ville → Kénitra → Rabat-Agdal → Casa-Voyageurs
- **Journey Time**: ~2h10
- **Frequency**: 15+ departures daily each direction
- **Departures from Tangier**: 06:00, 07:00, 08:00, 09:00, 10:00, 11:00, 12:00, 13:00, 14:00, 15:00, 16:00, 17:00, 18:00, 19:00, 21:00

### Route 2: Al Boraq/Atlas (Casablanca - Marrakech)
- **Stations**: Casa-Voyageurs → Settat → Marrakech
- **Journey Time**: ~2h00
- **Frequency**: 11+ departures daily each direction
- **Departures from Casa**: 07:00, 08:00, 09:00, 10:00, 11:00, 14:00, 15:00, 16:00, 17:00, 18:00, 19:00

### Route 3: Al Atlas (Casablanca - Fes - Oujda)
- **Stations**: Casa-Voyageurs → Rabat → Meknes → Fes → Taza → Oujda
- **Journey Time**: ~10h (full route)
- **Frequency**: Several daily

### Route 4: TNR Suburban (Casablanca - Rabat - Kenitra)
- **Stations**: Casa-Port → Ain Sebaa → Mohammedia → Bouznika → Skhirat → Témara → Rabat-Agdal → Rabat-Ville → Salé → Salé-Tabriquet → Kénitra
- **Frequency**: Every 10-20 minutes peak hours

## Station Coordinates (Verified)

| Station | Latitude | Longitude | City |
|---------|----------|-----------|------|
| Tanger-Ville | 35.7643 | -5.8340 | Tangier |
| Tanger Al Boraq | 35.7385 | -5.8145 | Tangier |
| Kénitra | 34.2610 | -6.5802 | Kénitra |
| Rabat-Agdal | 34.0078 | -6.8517 | Rabat |
| Rabat-Ville | 34.0212 | -6.8395 | Rabat |
| Salé | 34.0530 | -6.7490 | Salé |
| Casa-Voyageurs | 33.5979 | -7.6191 | Casablanca |
| Casa-Port | 33.6065 | -7.6280 | Casablanca |
| Casa-Oasis | 33.5692 | -7.6495 | Casablanca |
| Mohammedia | 33.6867 | -7.3833 | Mohammedia |
| Settat | 32.9955 | -7.6174 | Settat |
| Marrakech | 31.6295 | -8.0153 | Marrakech |
| Fes | 33.9789 | -4.9935 | Fes |
| Meknes | 33.8849 | -5.5389 | Meknes |
| Oujda | 34.6805 | -1.9110 | Oujda |
| Taza | 34.2167 | -4.0167 | Taza |
| El Jadida | 33.2316 | -8.5147 | El Jadida |
| Safi | 32.2994 | -9.2379 | Safi |
| Nador | 35.1681 | -2.9343 | Nador |

## Additional Suburban Stations (TNR Line)

| Station | Latitude | Longitude |
|---------|----------|-----------|
| Ain Sebaa | 33.6167 | -7.5500 |
| Bouznika | 33.7833 | -7.1667 |
| Skhirat | 33.8500 | -7.0333 |
| Témara | 33.9167 | -6.9167 |
| Salé-Tabriquet | 34.0400 | -6.7700 |

## Fares (Reference)
- **Al Boraq 2nd Class**: 89-224 MAD
- **Al Boraq 1st Class**: 129-292 MAD
- **Overnight couchette**: ~375 MAD shared, 399-670 MAD private

## GTFS Route Types
- `route_type=2` = Rail (intercity/long-distance)
- `route_type=1` = Subway/Metro (not applicable)
- `route_type=0` = Tram/Light Rail (not applicable)
