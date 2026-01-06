#!/usr/bin/env python3
"""
Inspect the schema of a large JSON file without loading it all into memory.
Uses ijson for streaming JSON parsing.
"""

import json
from collections import defaultdict

def get_schema_sample(filepath, max_items=3):
    """
    Stream through JSON and extract schema info:
    - Top-level keys
    - Array element structure (first few items)
    - Nested object shapes
    """
    
    # For OSM Overpass response, we know the general structure:
    # { "version": ..., "generator": ..., "elements": [...] }
    
    # Use a streaming approach - read in chunks
    with open(filepath, 'r') as f:
        # Read first chunk to get top-level structure
        chunk = f.read(1000)
        print("=" * 60)
        print("FIRST 1000 CHARS (structure preview):")
        print("=" * 60)
        print(chunk)
        print("\n")
    
    # Now try to parse incrementally using json.JSONDecoder
    with open(filepath, 'r') as f:
        content = f.read(50000)  # Read 50KB to get some elements
    
    # Find where "elements" array starts
    elements_start = content.find('"elements"')
    if elements_start == -1:
        print("Could not find 'elements' key")
        return
    
    print("=" * 60)
    print("TOP-LEVEL KEYS (before elements):")
    print("=" * 60)
    
    # Parse the header part
    header_end = content.find('[', elements_start)
    header = content[:header_end]
    
    # Extract key-value pairs before elements
    import re
    kv_pattern = r'"(\w+)":\s*([^,}]+)'
    matches = re.findall(kv_pattern, header)
    for key, val in matches:
        if key != 'elements':
            print(f"  {key}: {val.strip()[:50]}")
    
    print("\n")
    print("=" * 60)
    print(f"FIRST {max_items} ELEMENTS (schema detection):")
    print("=" * 60)
    
    # Find array content
    array_start = header_end + 1
    
    # Parse a few elements manually
    bracket_count = 0
    element_starts = []
    element_ends = []
    in_element = False
    
    for i, char in enumerate(content[array_start:], start=array_start):
        if char == '{':
            if bracket_count == 0:
                element_starts.append(i)
                in_element = True
            bracket_count += 1
        elif char == '}':
            bracket_count -= 1
            if bracket_count == 0 and in_element:
                element_ends.append(i + 1)
                in_element = False
                if len(element_ends) >= max_items:
                    break
    
    # Parse and display elements
    element_types = defaultdict(int)
    sample_elements = []
    
    for start, end in zip(element_starts, element_ends):
        try:
            elem_str = content[start:end]
            elem = json.loads(elem_str)
            sample_elements.append(elem)
            element_types[elem.get('type', 'unknown')] += 1
        except json.JSONDecodeError as e:
            print(f"  Parse error: {e}")
    
    for i, elem in enumerate(sample_elements):
        print(f"\n--- Element {i+1} ---")
        print(f"  Type: {elem.get('type')}")
        print(f"  Keys: {list(elem.keys())}")
        
        # Show structure without full data
        for key, val in elem.items():
            if isinstance(val, list):
                print(f"  {key}: list[{len(val)} items]")
                if val and isinstance(val[0], dict):
                    print(f"    First item keys: {list(val[0].keys())}")
                elif val:
                    print(f"    First item type: {type(val[0]).__name__} = {val[0]}")
            elif isinstance(val, dict):
                print(f"  {key}: dict with keys {list(val.keys())}")
            else:
                print(f"  {key}: {type(val).__name__} = {val}")


def count_elements(filepath):
    """Count total elements by streaming through the file"""
    print("\n")
    print("=" * 60)
    print("COUNTING TOTAL ELEMENTS (streaming):")
    print("=" * 60)
    
    count = 0
    type_counts = defaultdict(int)
    
    with open(filepath, 'r') as f:
        # Skip to elements array
        in_elements = False
        bracket_depth = 0
        current_type = None
        buffer = ""
        
        while True:
            chunk = f.read(100000)  # 100KB chunks
            if not chunk:
                break
            
            for char in chunk:
                if not in_elements:
                    buffer += char
                    if '"elements"' in buffer:
                        in_elements = True
                        buffer = ""
                    elif len(buffer) > 20:
                        buffer = buffer[-15:]
                else:
                    if char == '{':
                        if bracket_depth == 1:  # Starting a new element
                            count += 1
                            buffer = "{"
                        elif bracket_depth > 1:
                            buffer += char
                        bracket_depth += 1
                    elif char == '}':
                        bracket_depth -= 1
                        buffer += char
                        if bracket_depth == 1:  # Finished an element
                            # Try to extract type
                            if '"type"' in buffer:
                                import re
                                match = re.search(r'"type":\s*"(\w+)"', buffer)
                                if match:
                                    type_counts[match.group(1)] += 1
                            buffer = ""
                    elif char == '[':
                        if bracket_depth == 0:
                            bracket_depth = 1  # Start of elements array
                        else:
                            buffer += char
                    elif char == ']':
                        if bracket_depth == 1:
                            break  # End of elements array
                        else:
                            buffer += char
                    elif bracket_depth > 1:
                        buffer += char
    
    print(f"  Total elements: {count}")
    print(f"  By type:")
    for t, c in sorted(type_counts.items()):
        print(f"    {t}: {c}")
    
    return count, type_counts


if __name__ == '__main__':
    filepath = 'raw_shape_data.json'
    
    print("\n" + "#" * 60)
    print("# OSM OVERPASS RESPONSE SCHEMA INSPECTOR")
    print("#" * 60)
    
    get_schema_sample(filepath, max_items=5)
    count_elements(filepath)
