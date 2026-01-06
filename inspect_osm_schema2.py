#!/usr/bin/env python3
"""
Inspect OSM Overpass response - handles the wrapped response format.
"""

import json
import re
from collections import defaultdict

def inspect_schema(filepath):
    print("\n" + "#" * 60)
    print("# OSM OVERPASS RESPONSE SCHEMA")
    print("#" * 60)
    
    with open(filepath, 'r') as f:
        # Load the wrapper
        wrapper = json.load(f)
    
    print("\n=== WRAPPER STRUCTURE ===")
    print(f"Keys: {list(wrapper.keys())}")
    print(f"status_code: {wrapper.get('status_code')}")
    
    # Parse the body (it's a JSON string)
    body = json.loads(wrapper['body'])
    
    print("\n=== BODY STRUCTURE ===")
    print(f"Keys: {list(body.keys())}")
    print(f"version: {body.get('version')}")
    print(f"generator: {body.get('generator')}")
    
    elements = body.get('elements', [])
    print(f"\nTotal elements: {len(elements)}")
    
    # Count by type
    type_counts = defaultdict(int)
    for elem in elements:
        type_counts[elem.get('type', 'unknown')] += 1
    
    print("\nBy type:")
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")
    
    # Sample elements
    print("\n=== SAMPLE ELEMENTS ===")
    for i, elem in enumerate(elements[:3]):
        print(f"\n--- Element {i+1} (type: {elem.get('type')}) ---")
        print(f"  id: {elem.get('id')}")
        print(f"  Keys: {list(elem.keys())}")
        
        if 'bounds' in elem:
            b = elem['bounds']
            print(f"  bounds: {b['minlat']:.4f},{b['minlon']:.4f} to {b['maxlat']:.4f},{b['maxlon']:.4f}")
        
        if 'nodes' in elem:
            nodes = elem['nodes']
            print(f"  nodes: list of {len(nodes)} node IDs")
            print(f"    first 3: {nodes[:3]}")
        
        if 'geometry' in elem:
            geom = elem['geometry']
            print(f"  geometry: list of {len(geom)} points")
            if geom:
                print(f"    first point: {geom[0]}")
                print(f"    last point: {geom[-1]}")
        
        if 'tags' in elem:
            tags = elem['tags']
            print(f"  tags: {len(tags)} tags")
            for k, v in list(tags.items())[:10]:
                print(f"    {k}: {v}")
    
    # Check what tags are available
    print("\n=== TAG ANALYSIS ===")
    all_tags = defaultdict(set)
    for elem in elements:
        for k, v in elem.get('tags', {}).items():
            all_tags[k].add(v)
    
    print(f"\nUnique tag keys: {len(all_tags)}")
    print("\nKey tags for rail identification:")
    for key in ['railway', 'name', 'ref', 'operator', 'service', 'usage', 'electrified', 'gauge']:
        if key in all_tags:
            vals = all_tags[key]
            if len(vals) <= 10:
                print(f"  {key}: {vals}")
            else:
                print(f"  {key}: {len(vals)} unique values")
    
    return body, elements


if __name__ == '__main__':
    body, elements = inspect_schema('raw_shape_data.json')
    
    # Save just the elements for easier processing
    print("\n=== SAVING UNWRAPPED DATA ===")
    with open('osm_elements.json', 'w') as f:
        json.dump(elements, f)
    print(f"Saved {len(elements)} elements to osm_elements.json")
