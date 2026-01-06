#!/usr/bin/env python3
"""
Comprehensive GTFS Validator for Rail Maroc
Based on GTFS Reference Specification
https://gtfs.org/schedule/reference/
"""

import csv
import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class GTFSValidator:
    def __init__(self, gtfs_dir):
        self.gtfs_dir = Path(gtfs_dir)
        self.errors = []
        self.warnings = []
        self.info = []
        self.data = {}
        
    def add_error(self, file, msg):
        self.errors.append(f"ERROR [{file}]: {msg}")
        
    def add_warning(self, file, msg):
        self.warnings.append(f"WARNING [{file}]: {msg}")
        
    def add_info(self, file, msg):
        self.info.append(f"INFO [{file}]: {msg}")
    
    def load_csv(self, filename):
        """Load a CSV file and return list of dicts"""
        filepath = self.gtfs_dir / filename
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def validate_required_files(self):
        """Check all required GTFS files exist"""
        required = ['agency.txt', 'stops.txt', 'routes.txt', 'trips.txt', 'stop_times.txt']
        conditionally_required = ['calendar.txt', 'calendar_dates.txt']  # At least one
        
        print("\n" + "="*60)
        print("REQUIRED FILES")
        print("="*60)
        
        for f in required:
            if (self.gtfs_dir / f).exists():
                data = self.load_csv(f)
                self.data[f] = data
                print(f"  ✅ {f} ({len(data)} records)")
            else:
                self.add_error(f, "Required file missing")
                print(f"  ❌ {f} MISSING")
        
        # Check conditional requirement
        has_calendar = (self.gtfs_dir / 'calendar.txt').exists()
        has_calendar_dates = (self.gtfs_dir / 'calendar_dates.txt').exists()
        
        if not has_calendar and not has_calendar_dates:
            self.add_error('calendar', "Either calendar.txt or calendar_dates.txt is required")
            print(f"  ❌ Neither calendar.txt nor calendar_dates.txt present")
        else:
            if has_calendar:
                data = self.load_csv('calendar.txt')
                self.data['calendar.txt'] = data
                print(f"  ✅ calendar.txt ({len(data)} records)")
            if has_calendar_dates:
                data = self.load_csv('calendar_dates.txt')
                self.data['calendar_dates.txt'] = data
                print(f"  ✅ calendar_dates.txt ({len(data)} records)")
    
    def validate_agency(self):
        """Validate agency.txt"""
        print("\n" + "="*60)
        print("AGENCY VALIDATION")
        print("="*60)
        
        data = self.data.get('agency.txt')
        if not data:
            return
        
        required_fields = ['agency_name', 'agency_url', 'agency_timezone']
        
        for i, row in enumerate(data, 1):
            for field in required_fields:
                if field not in row or not row[field].strip():
                    self.add_error('agency.txt', f"Row {i}: Missing required field '{field}'")
            
            # Validate URL format
            if 'agency_url' in row and row['agency_url']:
                if not row['agency_url'].startswith(('http://', 'https://')):
                    self.add_warning('agency.txt', f"Row {i}: agency_url should start with http:// or https://")
            
            # Validate timezone
            if 'agency_timezone' in row:
                tz = row['agency_timezone']
                # Basic check - should be like "Africa/Casablanca"
                if '/' not in tz:
                    self.add_warning('agency.txt', f"Row {i}: agency_timezone '{tz}' may be invalid")
        
        print(f"  ✅ {len(data)} agency(ies) validated")
        for row in data:
            print(f"     - {row.get('agency_name', 'Unknown')}")
    
    def validate_stops(self):
        """Validate stops.txt"""
        print("\n" + "="*60)
        print("STOPS VALIDATION")
        print("="*60)
        
        data = self.data.get('stops.txt')
        if not data:
            return
        
        required_fields = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
        stop_ids = set()
        
        # Morocco bounding box
        MIN_LAT, MAX_LAT = 27.0, 36.0
        MIN_LON, MAX_LON = -13.0, -1.0
        
        coord_issues = 0
        
        for i, row in enumerate(data, 1):
            # Check required fields
            for field in required_fields:
                if field not in row or not row[field].strip():
                    self.add_error('stops.txt', f"Row {i}: Missing required field '{field}'")
            
            # Check for duplicate stop_ids
            stop_id = row.get('stop_id', '')
            if stop_id in stop_ids:
                self.add_error('stops.txt', f"Row {i}: Duplicate stop_id '{stop_id}'")
            stop_ids.add(stop_id)
            
            # Validate coordinates
            try:
                lat = float(row.get('stop_lat', 0))
                lon = float(row.get('stop_lon', 0))
                
                if not (MIN_LAT <= lat <= MAX_LAT):
                    self.add_warning('stops.txt', f"Row {i}: stop_lat {lat} outside Morocco bounds")
                    coord_issues += 1
                if not (MIN_LON <= lon <= MAX_LON):
                    self.add_warning('stops.txt', f"Row {i}: stop_lon {lon} outside Morocco bounds")
                    coord_issues += 1
                    
            except ValueError:
                self.add_error('stops.txt', f"Row {i}: Invalid coordinate values")
        
        self.data['stop_ids'] = stop_ids
        print(f"  ✅ {len(data)} stops validated")
        print(f"     - Unique stop IDs: {len(stop_ids)}")
        if coord_issues == 0:
            print(f"     - All coordinates within Morocco bounds")
        else:
            print(f"     - {coord_issues} coordinate warnings")
    
    def validate_routes(self):
        """Validate routes.txt"""
        print("\n" + "="*60)
        print("ROUTES VALIDATION")
        print("="*60)
        
        data = self.data.get('routes.txt')
        if not data:
            return
        
        required_fields = ['route_id', 'route_type']
        route_ids = set()
        
        # Valid route types
        valid_route_types = {
            '0': 'Tram/Light Rail',
            '1': 'Subway/Metro', 
            '2': 'Rail',
            '3': 'Bus',
            '4': 'Ferry',
            '5': 'Cable Tram',
            '6': 'Aerial Lift',
            '7': 'Funicular',
            '11': 'Trolleybus',
            '12': 'Monorail'
        }
        
        route_type_counts = defaultdict(int)
        
        for i, row in enumerate(data, 1):
            # Check required fields
            for field in required_fields:
                if field not in row or not row[field].strip():
                    self.add_error('routes.txt', f"Row {i}: Missing required field '{field}'")
            
            # Check for duplicate route_ids
            route_id = row.get('route_id', '')
            if route_id in route_ids:
                self.add_error('routes.txt', f"Row {i}: Duplicate route_id '{route_id}'")
            route_ids.add(route_id)
            
            # Validate route_type
            route_type = row.get('route_type', '')
            if route_type not in valid_route_types:
                self.add_warning('routes.txt', f"Row {i}: Unknown route_type '{route_type}'")
            else:
                route_type_counts[valid_route_types[route_type]] += 1
            
            # Check route has either short_name or long_name
            short_name = row.get('route_short_name', '').strip()
            long_name = row.get('route_long_name', '').strip()
            if not short_name and not long_name:
                self.add_error('routes.txt', f"Row {i}: Either route_short_name or route_long_name required")
        
        self.data['route_ids'] = route_ids
        print(f"  ✅ {len(data)} routes validated")
        for rtype, count in route_type_counts.items():
            print(f"     - {rtype}: {count}")
    
    def validate_trips(self):
        """Validate trips.txt"""
        print("\n" + "="*60)
        print("TRIPS VALIDATION")
        print("="*60)
        
        data = self.data.get('trips.txt')
        if not data:
            return
        
        required_fields = ['route_id', 'service_id', 'trip_id']
        trip_ids = set()
        route_ids = self.data.get('route_ids', set())
        service_ids = self.data.get('service_ids', set())
        
        # Collect service_ids from calendar if not already done
        if not service_ids:
            calendar = self.data.get('calendar.txt', [])
            service_ids = {row['service_id'] for row in calendar if 'service_id' in row}
            self.data['service_ids'] = service_ids
        
        orphan_routes = set()
        orphan_services = set()
        
        for i, row in enumerate(data, 1):
            # Check required fields
            for field in required_fields:
                if field not in row or not row[field].strip():
                    self.add_error('trips.txt', f"Row {i}: Missing required field '{field}'")
            
            # Check for duplicate trip_ids
            trip_id = row.get('trip_id', '')
            if trip_id in trip_ids:
                self.add_error('trips.txt', f"Row {i}: Duplicate trip_id '{trip_id}'")
            trip_ids.add(trip_id)
            
            # Check route_id references
            route_id = row.get('route_id', '')
            if route_id and route_ids and route_id not in route_ids:
                orphan_routes.add(route_id)
            
            # Check service_id references
            service_id = row.get('service_id', '')
            if service_id and service_ids and service_id not in service_ids:
                orphan_services.add(service_id)
        
        self.data['trip_ids'] = trip_ids
        
        if orphan_routes:
            for r in orphan_routes:
                self.add_error('trips.txt', f"References unknown route_id '{r}'")
        if orphan_services:
            for s in orphan_services:
                self.add_error('trips.txt', f"References unknown service_id '{s}'")
        
        print(f"  ✅ {len(data)} trips validated")
        print(f"     - Unique trip IDs: {len(trip_ids)}")
        if not orphan_routes and not orphan_services:
            print(f"     - All references valid")
    
    def validate_stop_times(self):
        """Validate stop_times.txt"""
        print("\n" + "="*60)
        print("STOP_TIMES VALIDATION")
        print("="*60)
        
        data = self.data.get('stop_times.txt')
        if not data:
            return
        
        required_fields = ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence']
        trip_ids = self.data.get('trip_ids', set())
        stop_ids = self.data.get('stop_ids', set())
        
        time_pattern = re.compile(r'^\d{1,2}:\d{2}:\d{2}$')
        
        orphan_trips = set()
        orphan_stops = set()
        time_errors = 0
        sequence_issues = 0
        
        # Group by trip to check sequences
        trips_stops = defaultdict(list)
        
        for i, row in enumerate(data, 1):
            # Check required fields
            for field in required_fields:
                if field not in row or not row[field].strip():
                    self.add_error('stop_times.txt', f"Row {i}: Missing required field '{field}'")
            
            # Validate time format (HH:MM:SS, allows >24 for overnight)
            for time_field in ['arrival_time', 'departure_time']:
                time_val = row.get(time_field, '')
                if time_val and not time_pattern.match(time_val):
                    self.add_error('stop_times.txt', f"Row {i}: Invalid {time_field} format '{time_val}'")
                    time_errors += 1
                elif time_val:
                    parts = time_val.split(':')
                    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
                    if m >= 60 or s >= 60:
                        self.add_error('stop_times.txt', f"Row {i}: Invalid {time_field} '{time_val}'")
                        time_errors += 1
            
            # Check references
            trip_id = row.get('trip_id', '')
            if trip_id and trip_ids and trip_id not in trip_ids:
                orphan_trips.add(trip_id)
            
            stop_id = row.get('stop_id', '')
            if stop_id and stop_ids and stop_id not in stop_ids:
                orphan_stops.add(stop_id)
            
            # Collect for sequence validation
            try:
                seq = int(row.get('stop_sequence', 0))
                trips_stops[trip_id].append((seq, i))
            except ValueError:
                self.add_error('stop_times.txt', f"Row {i}: Invalid stop_sequence")
        
        # Check sequences are monotonically increasing per trip
        for trip_id, stops in trips_stops.items():
            stops.sort(key=lambda x: x[0])
            prev_seq = -1
            for seq, row_num in stops:
                if seq <= prev_seq:
                    self.add_warning('stop_times.txt', f"Trip {trip_id}: Non-increasing stop_sequence at row {row_num}")
                    sequence_issues += 1
                prev_seq = seq
        
        if orphan_trips:
            for t in list(orphan_trips)[:5]:
                self.add_error('stop_times.txt', f"References unknown trip_id '{t}'")
            if len(orphan_trips) > 5:
                self.add_error('stop_times.txt', f"... and {len(orphan_trips) - 5} more orphan trip references")
        
        if orphan_stops:
            for s in list(orphan_stops)[:5]:
                self.add_error('stop_times.txt', f"References unknown stop_id '{s}'")
            if len(orphan_stops) > 5:
                self.add_error('stop_times.txt', f"... and {len(orphan_stops) - 5} more orphan stop references")
        
        print(f"  ✅ {len(data)} stop_times validated")
        print(f"     - Covering {len(trips_stops)} trips")
        if time_errors == 0:
            print(f"     - All times in valid HH:MM:SS format")
        if sequence_issues == 0:
            print(f"     - All sequences valid")
        if not orphan_trips and not orphan_stops:
            print(f"     - All references valid")
    
    def validate_calendar(self):
        """Validate calendar.txt"""
        print("\n" + "="*60)
        print("CALENDAR VALIDATION")
        print("="*60)
        
        data = self.data.get('calendar.txt')
        if not data:
            print("  ⚪ calendar.txt not present (using calendar_dates.txt)")
            return
        
        required_fields = ['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 
                          'friday', 'saturday', 'sunday', 'start_date', 'end_date']
        
        service_ids = set()
        date_pattern = re.compile(r'^\d{8}$')  # YYYYMMDD
        
        for i, row in enumerate(data, 1):
            # Check required fields
            for field in required_fields:
                if field not in row or not row[field].strip():
                    self.add_error('calendar.txt', f"Row {i}: Missing required field '{field}'")
            
            service_id = row.get('service_id', '')
            service_ids.add(service_id)
            
            # Validate day fields (0 or 1)
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                val = row.get(day, '')
                if val not in ('0', '1'):
                    self.add_error('calendar.txt', f"Row {i}: {day} must be 0 or 1, got '{val}'")
            
            # Validate date format
            for date_field in ['start_date', 'end_date']:
                date_val = row.get(date_field, '')
                if date_val and not date_pattern.match(date_val):
                    self.add_error('calendar.txt', f"Row {i}: {date_field} must be YYYYMMDD format")
            
            # Check end_date >= start_date
            start = row.get('start_date', '')
            end = row.get('end_date', '')
            if start and end and end < start:
                self.add_warning('calendar.txt', f"Row {i}: end_date before start_date")
        
        self.data['service_ids'] = service_ids
        print(f"  ✅ {len(data)} service patterns validated")
        for row in data:
            days = []
            for d in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                if row.get(d) == '1':
                    days.append(d[:3].capitalize())
            print(f"     - {row.get('service_id')}: {', '.join(days)}")
    
    def validate_shapes(self):
        """Validate shapes.txt (optional but recommended)"""
        print("\n" + "="*60)
        print("SHAPES VALIDATION")
        print("="*60)
        
        filepath = self.gtfs_dir / 'shapes.txt'
        if not filepath.exists():
            self.add_info('shapes.txt', "Optional file not present - routes will show as straight lines")
            print("  ⚪ shapes.txt not present (optional)")
            return
        
        data = self.load_csv('shapes.txt')
        self.data['shapes.txt'] = data
        
        required_fields = ['shape_id', 'shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence']
        shape_ids = set()
        shape_points = defaultdict(int)
        
        for i, row in enumerate(data, 1):
            for field in required_fields:
                if field not in row or not row[field].strip():
                    self.add_error('shapes.txt', f"Row {i}: Missing required field '{field}'")
            
            shape_id = row.get('shape_id', '')
            shape_ids.add(shape_id)
            shape_points[shape_id] += 1
            
            # Validate coordinates
            try:
                lat = float(row.get('shape_pt_lat', 0))
                lon = float(row.get('shape_pt_lon', 0))
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    self.add_error('shapes.txt', f"Row {i}: Invalid coordinates")
            except ValueError:
                self.add_error('shapes.txt', f"Row {i}: Non-numeric coordinates")
        
        self.data['shape_ids'] = shape_ids
        
        # Check that trips reference valid shapes
        trips = self.data.get('trips.txt', [])
        trip_shape_ids = {t.get('shape_id', '') for t in trips if t.get('shape_id')}
        orphan_shapes = trip_shape_ids - shape_ids
        if orphan_shapes:
            for s in orphan_shapes:
                self.add_error('shapes.txt', f"Trip references unknown shape_id '{s}'")
        
        print(f"  ✅ {len(data)} shape points validated")
        print(f"     - {len(shape_ids)} unique shapes")
        for sid, count in sorted(shape_points.items()):
            print(f"       {sid}: {count} points")
    
    def validate_feed_info(self):
        """Validate feed_info.txt (optional but recommended)"""
        print("\n" + "="*60)
        print("FEED_INFO VALIDATION")
        print("="*60)
        
        filepath = self.gtfs_dir / 'feed_info.txt'
        if not filepath.exists():
            self.add_info('feed_info.txt', "Optional file not present")
            print("  ⚪ feed_info.txt not present (optional)")
            return
        
        data = self.load_csv('feed_info.txt')
        self.data['feed_info.txt'] = data
        
        required_fields = ['feed_publisher_name', 'feed_publisher_url', 'feed_lang']
        
        for i, row in enumerate(data, 1):
            for field in required_fields:
                if field not in row or not row[field].strip():
                    self.add_warning('feed_info.txt', f"Row {i}: Missing recommended field '{field}'")
        
        if data:
            row = data[0]
            print(f"  ✅ Feed info present")
            print(f"     - Publisher: {row.get('feed_publisher_name', 'N/A')}")
            print(f"     - Language: {row.get('feed_lang', 'N/A')}")
            print(f"     - Version: {row.get('feed_version', 'N/A')}")
    
    def run_validation(self):
        """Run all validations"""
        print("\n" + "#"*60)
        print("# GTFS VALIDATION REPORT - Rail Maroc")
        print("# MobilityData GTFS Spec Compliant")
        print("#"*60)
        
        self.validate_required_files()
        self.validate_agency()
        self.validate_stops()
        self.validate_routes()
        self.validate_calendar()  # Must come before trips
        self.validate_trips()
        self.validate_stop_times()
        self.validate_shapes()
        self.validate_feed_info()
        
        # Summary
        print("\n" + "#"*60)
        print("# VALIDATION SUMMARY")
        print("#"*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for err in self.errors[:20]:
                print(f"   {err}")
            if len(self.errors) > 20:
                print(f"   ... and {len(self.errors) - 20} more errors")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warn in self.warnings[:10]:
                print(f"   {warn}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more warnings")
        
        print("\n" + "="*60)
        if self.errors:
            print(f"❌ VALIDATION FAILED: {len(self.errors)} errors, {len(self.warnings)} warnings")
            print("\nFix errors before submitting to Google Transit.")
            return False
        elif self.warnings:
            print(f"✅ VALIDATION PASSED WITH WARNINGS: {len(self.warnings)} warnings")
            print("\nFeed is acceptable but consider fixing warnings.")
            return True
        else:
            print("✅ VALIDATION PASSED - No errors or warnings!")
            print("\nFeed is ready for submission!")
            return True


if __name__ == '__main__':
    validator = GTFSValidator('gtfs')
    success = validator.run_validation()
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Create zip file:
   cd gtfs && zip -r ../oncf_gtfs.zip *.txt && cd ..

2. Host publicly (GitHub, S3, etc.)

3. Validate with official tool:
   https://gtfs-validator.mobilitydata.org/

4. Submit to Mobility Database:
   https://database.mobilitydata.org/add-a-feed

5. Contact ONCF with your validated feed
""")
    
    exit(0 if success else 1)
