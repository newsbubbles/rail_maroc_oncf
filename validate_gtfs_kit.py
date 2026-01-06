#!/usr/bin/env python3
"""GTFS Validation using gtfs-kit library"""

import gtfs_kit as gk
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("GTFS-KIT VALIDATION - Rail Maroc")
print("="*60)

# First, let's zip the GTFS folder
import zipfile
import os

gtfs_dir = Path('gtfs')
zip_path = Path('oncf_gtfs.zip')

print("\n[1] Creating GTFS zip file...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in gtfs_dir.glob('*.txt'):
        zipf.write(file, file.name)
        print(f"  Added: {file.name}")

print(f"\n  Created: {zip_path} ({zip_path.stat().st_size / 1024:.1f} KB)")

# Load and validate with gtfs-kit
print("\n[2] Loading feed with gtfs-kit...")
try:
    feed = gk.read_feed(str(zip_path), dist_units='km')
    print("  ✅ Feed loaded successfully")
except Exception as e:
    print(f"  ❌ Failed to load feed: {e}")
    exit(1)

# Basic stats
print("\n[3] FEED STATISTICS")
print("-"*40)
print(f"  Agencies: {len(feed.agency)}")
print(f"  Stops: {len(feed.stops)}")
print(f"  Routes: {len(feed.routes)}")
print(f"  Trips: {len(feed.trips)}")
print(f"  Stop times: {len(feed.stop_times)}")
print(f"  Calendar entries: {len(feed.calendar) if feed.calendar is not None else 0}")

# Validate
print("\n[4] RUNNING GTFS-KIT VALIDATION...")
print("-"*40)
try:
    problems = gk.validators.validate(feed)
    
    if problems.empty:
        print("  ✅ No validation problems found!")
    else:
        print(f"  Found {len(problems)} issues:")
        print()
        # Group by type
        for ptype in problems['type'].unique():
            subset = problems[problems['type'] == ptype]
            print(f"  [{ptype}] {len(subset)} issues")
            for _, row in subset.head(5).iterrows():
                print(f"    - {row['message']}")
            if len(subset) > 5:
                print(f"    ... and {len(subset) - 5} more")
            print()
except Exception as e:
    print(f"  Validation error: {e}")

# Check route types
print("\n[5] ROUTE TYPES")
print("-"*40)
route_types = {0: 'Tram', 1: 'Subway', 2: 'Rail', 3: 'Bus', 4: 'Ferry', 5: 'Cable', 6: 'Gondola', 7: 'Funicular'}
for rt in feed.routes['route_type'].unique():
    count = len(feed.routes[feed.routes['route_type'] == rt])
    print(f"  {route_types.get(rt, f'Unknown ({rt})')}: {count} routes")

# Check service dates
print("\n[6] SERVICE CALENDAR")
print("-"*40)
if feed.calendar is not None:
    for _, row in feed.calendar.iterrows():
        days = []
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            if row[day] == 1:
                days.append(day[:3].capitalize())
        print(f"  {row['service_id']}: {', '.join(days)}")
        print(f"    Valid: {row['start_date']} to {row['end_date']}")

print("\n" + "="*60)
print("✅ VALIDATION COMPLETE")
print("="*60)
print(f"\nGTFS zip ready: {zip_path.absolute()}")
