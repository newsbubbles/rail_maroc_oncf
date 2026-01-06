#!/usr/bin/env python3
"""
Generate GTFS shapes.txt from OSM rail data.

Strategy:
1. Filter to main passenger rail (exclude sidings, military, industrial)
2. Build a graph of connected track segments
3. For each GTFS route, find the path between its terminal stations
4. Output as shapes.txt
"""

import json
import csv
import math
from collections import defaultdict
from pathlib import Path

# Our GTFS routes - shape_id matches route_id from routes.txt
# Terminals use stop_id from stops.txt
ROUTES = {
    'AL_BORAQ_TNG_CASA': {
        'name': 'Al Boraq Tanger-Casa',
        'terminals': ['TANGER_BORAQ', 'CASA_VOYAGEURS'],
    },
    'AL_BORAQ_TNG_MKC': {
        'name': 'Al Boraq Tanger-Marrakech', 
        'terminals': ['TANGER_BORAQ', 'MARRAKECH'],
    },
    'AL_ATLAS_CASA_MKC': {
        'name': 'Al Atlas Casa-Marrakech', 
        'terminals': ['CASA_VOYAGEURS', 'MARRAKECH'],
    },
    'AL_ATLAS_CASA_FES': {
        'name': 'Al Atlas Casa-Fes',
        'terminals': ['CASA_VOYAGEURS', 'FES'],
    },
    'AL_ATLAS_CASA_OUJDA': {
        'name': 'Al Atlas Casa-Oujda',
        'terminals': ['CASA_VOYAGEURS', 'OUJDA'],
    },
    'AL_ATLAS_MKC_FES': {
        'name': 'Al Atlas Marrakech-Fes',
        'terminals': ['MARRAKECH', 'FES'],
    },
    'TNR_CASA_AIRPORT': {
        'name': 'TNR Casa-Airport',
        'terminals': ['CASA_VOYAGEURS', 'AIN_SEBAA'],
    },
    'TNR_CASA_SETTAT': {
        'name': 'TNR Casa-Settat',
        'terminals': ['CASA_VOYAGEURS', 'SETTAT'],
    },
    'TNR_KENITRA_CASA': {
        'name': 'TNR Kenitra-Casa',
        'terminals': ['KENITRA', 'CASA_VOYAGEURS'],
    },
}

# Station coordinates (from our stops.txt)
STATIONS = {}

def load_stations():
    """Load station coordinates from stops.txt (keyed by stop_id)"""
    with open('gtfs/stops.txt', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            STATIONS[row['stop_id']] = {
                'lat': float(row['stop_lat']),
                'lon': float(row['stop_lon']),
                'name': row['stop_name']
            }
    print(f"Loaded {len(STATIONS)} stations")

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km"""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def load_osm_data():
    """Load and filter OSM rail segments"""
    with open('osm_elements.json', 'r') as f:
        elements = json.load(f)
    
    print(f"\nLoaded {len(elements)} OSM way elements")
    
    # Filter to main passenger rail
    filtered = []
    excluded_usage = {'military', 'industrial'}
    excluded_service = {'yard', 'siding', 'spur', 'crossover'}
    
    usage_counts = defaultdict(int)
    service_counts = defaultdict(int)
    
    for elem in elements:
        tags = elem.get('tags', {})
        usage = tags.get('usage', 'unknown')
        service = tags.get('service', '')
        
        usage_counts[usage] += 1
        if service:
            service_counts[service] += 1
        
        # Include main lines and branches, exclude service tracks
        if usage not in excluded_usage and service not in excluded_service:
            if 'geometry' in elem and len(elem['geometry']) > 0:
                filtered.append(elem)
    
    print(f"\nUsage distribution:")
    for u, c in sorted(usage_counts.items(), key=lambda x: -x[1]):
        print(f"  {u}: {c}")
    
    print(f"\nService distribution (excluded):")
    for s, c in sorted(service_counts.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c}")
    
    print(f"\nFiltered to {len(filtered)} main passenger rail segments")
    return filtered

def build_track_graph(segments):
    """
    Build a graph where:
    - Nodes are track segment endpoints (rounded coordinates)
    - Edges are the track segments with their geometry
    """
    
    def coord_key(lat, lon, precision=4):
        """Round coordinates to create joinable keys"""
        return (round(lat, precision), round(lon, precision))
    
    # Graph: coord_key -> list of (other_coord_key, segment_id, geometry)
    graph = defaultdict(list)
    segment_geoms = {}  # segment_id -> full geometry
    
    for seg in segments:
        seg_id = seg['id']
        geom = seg['geometry']
        
        if len(geom) < 2:
            continue
        
        start = coord_key(geom[0]['lat'], geom[0]['lon'])
        end = coord_key(geom[-1]['lat'], geom[-1]['lon'])
        
        segment_geoms[seg_id] = geom
        
        # Bidirectional edges
        graph[start].append((end, seg_id, False))  # False = forward direction
        graph[end].append((start, seg_id, True))   # True = reverse direction
    
    print(f"\nBuilt graph with {len(graph)} nodes and {len(segment_geoms)} segments")
    return graph, segment_geoms

def find_nearest_node(graph, lat, lon, max_dist_km=10):
    """Find the graph node nearest to a given coordinate"""
    best_node = None
    best_dist = float('inf')
    
    for node in graph.keys():
        dist = haversine(lat, lon, node[0], node[1])
        if dist < best_dist:
            best_dist = dist
            best_node = node
    
    if best_dist > max_dist_km:
        return None, best_dist
    return best_node, best_dist

def find_path_bfs(graph, segment_geoms, start_node, end_node, max_segments=500):
    """
    BFS to find path between two nodes.
    Returns list of (segment_id, reversed) tuples.
    """
    from collections import deque
    
    if start_node == end_node:
        return []
    
    # BFS
    queue = deque([(start_node, [])])  # (current_node, path_so_far)
    visited = {start_node}
    
    while queue:
        current, path = queue.popleft()
        
        if len(path) > max_segments:
            continue
        
        for next_node, seg_id, reversed_dir in graph.get(current, []):
            if next_node in visited:
                continue
            
            new_path = path + [(seg_id, reversed_dir)]
            
            if next_node == end_node:
                return new_path
            
            visited.add(next_node)
            queue.append((next_node, new_path))
    
    return None  # No path found

def path_to_coordinates(path, segment_geoms):
    """Convert a path of segments to a list of coordinates"""
    coords = []
    
    for seg_id, reversed_dir in path:
        geom = segment_geoms[seg_id]
        points = [(p['lat'], p['lon']) for p in geom]
        
        if reversed_dir:
            points = points[::-1]
        
        # Avoid duplicating junction points
        if coords and points:
            if coords[-1] == points[0]:
                points = points[1:]
        
        coords.extend(points)
    
    return coords

def generate_shapes():
    """Main function to generate shapes.txt"""
    
    load_stations()
    segments = load_osm_data()
    graph, segment_geoms = build_track_graph(segments)
    
    shapes = []  # List of (shape_id, coords)
    
    print("\n" + "="*60)
    print("GENERATING ROUTE SHAPES")
    print("="*60)
    
    for route_id, route_info in ROUTES.items():
        print(f"\n--- {route_info['name']} ---")
        
        terminals = route_info['terminals']
        start_station = STATIONS.get(terminals[0])
        end_station = STATIONS.get(terminals[1])
        
        if not start_station or not end_station:
            print(f"  ERROR: Station not found")
            continue
        
        # Find nearest graph nodes
        start_node, start_dist = find_nearest_node(
            graph, start_station['lat'], start_station['lon']
        )
        end_node, end_dist = find_nearest_node(
            graph, end_station['lat'], end_station['lon']
        )
        
        print(f"  Start: {terminals[0]} -> node {start_node} ({start_dist:.2f} km)")
        print(f"  End: {terminals[1]} -> node {end_node} ({end_dist:.2f} km)")
        
        if not start_node or not end_node:
            print(f"  ERROR: Could not find graph nodes near stations")
            continue
        
        # Find path
        path = find_path_bfs(graph, segment_geoms, start_node, end_node)
        
        if not path:
            print(f"  ERROR: No path found between stations")
            continue
        
        coords = path_to_coordinates(path, segment_geoms)
        print(f"  Found path: {len(path)} segments, {len(coords)} points")
        
        # Calculate total distance
        total_dist = 0
        for i in range(1, len(coords)):
            total_dist += haversine(coords[i-1][0], coords[i-1][1], 
                                   coords[i][0], coords[i][1])
        print(f"  Total distance: {total_dist:.1f} km")
        
        shapes.append((route_id, coords))
    
    # Write shapes.txt
    print("\n" + "="*60)
    print("WRITING shapes.txt")
    print("="*60)
    
    with open('gtfs/shapes.txt', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['shape_id', 'shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence', 'shape_dist_traveled'])
        
        for shape_id, coords in shapes:
            dist_traveled = 0
            for i, (lat, lon) in enumerate(coords):
                if i > 0:
                    dist_traveled += haversine(
                        coords[i-1][0], coords[i-1][1], lat, lon
                    ) * 1000  # Convert to meters
                
                writer.writerow([shape_id, f"{lat:.6f}", f"{lon:.6f}", i+1, f"{dist_traveled:.1f}"])
    
    print(f"\nWrote {sum(len(c) for _, c in shapes)} shape points for {len(shapes)} routes")
    
    # Also need to update trips.txt with shape_id
    print("\n" + "="*60)
    print("UPDATING trips.txt with shape_id")
    print("="*60)
    
    # Read existing trips
    with open('gtfs/trips.txt', 'r') as f:
        reader = csv.DictReader(f)
        trips = list(reader)
        fieldnames = reader.fieldnames
    
    # Add shape_id column if not present
    if 'shape_id' not in fieldnames:
        fieldnames = list(fieldnames) + ['shape_id']
    
    # Map route_id to shape_id
    route_to_shape = {route_id: route_id for route_id in ROUTES.keys()}
    
    # Update trips
    for trip in trips:
        route_id = trip['route_id']
        trip['shape_id'] = route_to_shape.get(route_id, '')
    
    # Write updated trips
    with open('gtfs/trips.txt', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trips)
    
    print(f"Updated {len(trips)} trips with shape_id")
    
    return shapes


if __name__ == '__main__':
    shapes = generate_shapes()
