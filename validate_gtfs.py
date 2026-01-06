#!/usr/bin/env python3
"""GTFS Validation Script for Rail Maroc"""

import os
import sys
from pathlib import Path

# Check required files
REQUIRED_FILES = [
    'agency.txt',
    'stops.txt', 
    'routes.txt',
    'trips.txt',
    'stop_times.txt',
    'calendar.txt'
]

OPTIONAL_FILES = [
    'feed_info.txt',
    'shapes.txt',
    'calendar_dates.txt',
    'frequencies.txt',
    'transfers.txt'
]

def check_file_exists(gtfs_dir, filename):
    """Check if file exists and return line count"""
    filepath = gtfs_dir / filename
    if filepath.exists():
        with open(filepath, 'r') as f:
            lines = f.readlines()
        return True, len(lines) - 1  # subtract header
    return False, 0

def validate_csv_structure(gtfs_dir, filename):
    """Validate CSV has consistent column count"""
    filepath = gtfs_dir / filename
    if not filepath.exists():
        return None, "File not found"
    
    errors = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        return None, "Empty file"
    
    header = lines[0].strip().split(',')
    header_count = len(header)
    
    for i, line in enumerate(lines[1:], start=2):
        if line.strip():  # skip empty lines
            cols = line.strip().split(',')
            if len(cols) != header_count:
                errors.append(f"Line {i}: Expected {header_count} columns, got {len(cols)}")
    
    return header, errors if errors else None

def validate_references(gtfs_dir):
    """Check referential integrity between files"""
    errors = []
    
    # Load IDs from each file
    def load_ids(filename, id_column):
        filepath = gtfs_dir / filename
        if not filepath.exists():
            return set()
        ids = set()
        with open(filepath, 'r') as f:
            lines = f.readlines()
        if not lines:
            return set()
        header = lines[0].strip().split(',')
        if id_column not in header:
            return set()
        idx = header.index(id_column)
        for line in lines[1:]:
            if line.strip():
                cols = line.strip().split(',')
                if len(cols) > idx:
                    ids.add(cols[idx])
        return ids
    
    # Load all IDs
    agency_ids = load_ids('agency.txt', 'agency_id')
    stop_ids = load_ids('stops.txt', 'stop_id')
    route_ids = load_ids('routes.txt', 'route_id')
    trip_ids = load_ids('trips.txt', 'trip_id')
    service_ids = load_ids('calendar.txt', 'service_id')
    
    # Check routes reference valid agencies
    with open(gtfs_dir / 'routes.txt', 'r') as f:
        lines = f.readlines()
    header = lines[0].strip().split(',')
    if 'agency_id' in header:
        idx = header.index('agency_id')
        for i, line in enumerate(lines[1:], start=2):
            if line.strip():
                cols = line.strip().split(',')
                if len(cols) > idx and cols[idx] not in agency_ids:
                    errors.append(f"routes.txt line {i}: Unknown agency_id '{cols[idx]}'")
    
    # Check trips reference valid routes and services
    with open(gtfs_dir / 'trips.txt', 'r') as f:
        lines = f.readlines()
    header = lines[0].strip().split(',')
    route_idx = header.index('route_id') if 'route_id' in header else -1
    service_idx = header.index('service_id') if 'service_id' in header else -1
    
    for i, line in enumerate(lines[1:], start=2):
        if line.strip():
            cols = line.strip().split(',')
            if route_idx >= 0 and len(cols) > route_idx:
                if cols[route_idx] not in route_ids:
                    errors.append(f"trips.txt line {i}: Unknown route_id '{cols[route_idx]}'")
            if service_idx >= 0 and len(cols) > service_idx:
                if cols[service_idx] not in service_ids:
                    errors.append(f"trips.txt line {i}: Unknown service_id '{cols[service_idx]}'")
    
    # Check stop_times reference valid trips and stops
    with open(gtfs_dir / 'stop_times.txt', 'r') as f:
        lines = f.readlines()
    header = lines[0].strip().split(',')
    trip_idx = header.index('trip_id') if 'trip_id' in header else -1
    stop_idx = header.index('stop_id') if 'stop_id' in header else -1
    
    for i, line in enumerate(lines[1:], start=2):
        if line.strip():
            cols = line.strip().split(',')
            if trip_idx >= 0 and len(cols) > trip_idx:
                if cols[trip_idx] not in trip_ids:
                    errors.append(f"stop_times.txt line {i}: Unknown trip_id '{cols[trip_idx]}'")
            if stop_idx >= 0 and len(cols) > stop_idx:
                if cols[stop_idx] not in stop_ids:
                    errors.append(f"stop_times.txt line {i}: Unknown stop_id '{cols[stop_idx]}'")
    
    return errors

def validate_coordinates(gtfs_dir):
    """Validate stop coordinates are reasonable for Morocco"""
    errors = []
    # Morocco bounding box (approximate)
    MIN_LAT, MAX_LAT = 27.0, 36.0
    MIN_LON, MAX_LON = -13.0, -1.0
    
    with open(gtfs_dir / 'stops.txt', 'r') as f:
        lines = f.readlines()
    
    header = lines[0].strip().split(',')
    lat_idx = header.index('stop_lat') if 'stop_lat' in header else -1
    lon_idx = header.index('stop_lon') if 'stop_lon' in header else -1
    name_idx = header.index('stop_name') if 'stop_name' in header else -1
    
    for i, line in enumerate(lines[1:], start=2):
        if line.strip():
            cols = line.strip().split(',')
            try:
                lat = float(cols[lat_idx])
                lon = float(cols[lon_idx])
                name = cols[name_idx] if name_idx >= 0 else f"line {i}"
                
                if not (MIN_LAT <= lat <= MAX_LAT):
                    errors.append(f"stops.txt: {name} latitude {lat} outside Morocco bounds")
                if not (MIN_LON <= lon <= MAX_LON):
                    errors.append(f"stops.txt: {name} longitude {lon} outside Morocco bounds")
            except (ValueError, IndexError) as e:
                errors.append(f"stops.txt line {i}: Invalid coordinates - {e}")
    
    return errors

def validate_times(gtfs_dir):
    """Validate time format in stop_times.txt"""
    errors = []
    
    with open(gtfs_dir / 'stop_times.txt', 'r') as f:
        lines = f.readlines()
    
    header = lines[0].strip().split(',')
    arr_idx = header.index('arrival_time') if 'arrival_time' in header else -1
    dep_idx = header.index('departure_time') if 'departure_time' in header else -1
    
    def validate_time_format(time_str):
        """Validate HH:MM:SS format (allows >24 hours for overnight)"""
        parts = time_str.split(':')
        if len(parts) != 3:
            return False
        try:
            h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
            return h >= 0 and 0 <= m < 60 and 0 <= s < 60
        except ValueError:
            return False
    
    for i, line in enumerate(lines[1:], start=2):
        if line.strip():
            cols = line.strip().split(',')
            if arr_idx >= 0 and len(cols) > arr_idx:
                if not validate_time_format(cols[arr_idx]):
                    errors.append(f"stop_times.txt line {i}: Invalid arrival_time '{cols[arr_idx]}'")
            if dep_idx >= 0 and len(cols) > dep_idx:
                if not validate_time_format(cols[dep_idx]):
                    errors.append(f"stop_times.txt line {i}: Invalid departure_time '{cols[dep_idx]}'")
    
    return errors

def main():
    gtfs_dir = Path('gtfs')
    
    print("="*60)
    print("GTFS VALIDATION REPORT - Rail Maroc")
    print("="*60)
    
    all_errors = []
    all_warnings = []
    
    # 1. Check required files
    print("\n[1] REQUIRED FILES CHECK")
    print("-"*40)
    for filename in REQUIRED_FILES:
        exists, count = check_file_exists(gtfs_dir, filename)
        if exists:
            print(f"  ✅ {filename}: {count} records")
        else:
            print(f"  ❌ {filename}: MISSING")
            all_errors.append(f"Missing required file: {filename}")
    
    # 2. Check optional files
    print("\n[2] OPTIONAL FILES CHECK")
    print("-"*40)
    for filename in OPTIONAL_FILES:
        exists, count = check_file_exists(gtfs_dir, filename)
        if exists:
            print(f"  ✅ {filename}: {count} records")
        else:
            print(f"  ⚪ {filename}: not present (optional)")
    
    # 3. Validate CSV structure
    print("\n[3] CSV STRUCTURE VALIDATION")
    print("-"*40)
    for filename in REQUIRED_FILES + OPTIONAL_FILES:
        if (gtfs_dir / filename).exists():
            header, errors = validate_csv_structure(gtfs_dir, filename)
            if errors:
                print(f"  ❌ {filename}: {len(errors)} structural errors")
                all_errors.extend(errors)
            else:
                print(f"  ✅ {filename}: Valid structure ({len(header)} columns)")
    
    # 4. Referential integrity
    print("\n[4] REFERENTIAL INTEGRITY")
    print("-"*40)
    ref_errors = validate_references(gtfs_dir)
    if ref_errors:
        print(f"  ❌ {len(ref_errors)} reference errors found")
        for err in ref_errors[:10]:  # Show first 10
            print(f"     - {err}")
        if len(ref_errors) > 10:
            print(f"     ... and {len(ref_errors) - 10} more")
        all_errors.extend(ref_errors)
    else:
        print("  ✅ All references valid")
    
    # 5. Coordinate validation
    print("\n[5] COORDINATE VALIDATION (Morocco bounds)")
    print("-"*40)
    coord_errors = validate_coordinates(gtfs_dir)
    if coord_errors:
        print(f"  ❌ {len(coord_errors)} coordinate errors")
        for err in coord_errors:
            print(f"     - {err}")
        all_errors.extend(coord_errors)
    else:
        print("  ✅ All coordinates within Morocco bounds")
    
    # 6. Time format validation
    print("\n[6] TIME FORMAT VALIDATION")
    print("-"*40)
    time_errors = validate_times(gtfs_dir)
    if time_errors:
        print(f"  ❌ {len(time_errors)} time format errors")
        for err in time_errors[:10]:
            print(f"     - {err}")
        if len(time_errors) > 10:
            print(f"     ... and {len(time_errors) - 10} more")
        all_errors.extend(time_errors)
    else:
        print("  ✅ All times in valid HH:MM:SS format")
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    if all_errors:
        print(f"\n❌ VALIDATION FAILED: {len(all_errors)} errors found")
        print("\nErrors must be fixed before submission.")
        return 1
    else:
        print("\n✅ VALIDATION PASSED")
        print("\nFeed is ready for submission!")
        print("\nNext steps:")
        print("  1. zip -r oncf_gtfs.zip gtfs/")
        print("  2. Upload to GitHub or hosting service")
        print("  3. Submit to Mobility Database")
        return 0

if __name__ == '__main__':
    sys.exit(main())
