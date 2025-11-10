#!/usr/bin/env python3
"""
Simple CSV to JSON converter for MCP tools

Usage:
    python csv_to_json.py song_list.csv
    python csv_to_json.py song_list.csv --output my_songs.json
"""

import csv
import json
import sys

def csv_to_json(csv_file, output_file=None):
    """Convert CSV to JSON format for MCP tools."""
    songs = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "song_name": row["song_name"].strip(),
                "artist_name": row["artist_name"].strip()
            })

    # Print summary
    print(f"[OK] Loaded {len(songs)} songs from {csv_file}")

    # Create output
    output = {"songs": songs}

    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved to {output_file}")

    # Print formatted output for copy-paste
    print("\n" + "="*60)
    print("COPY THIS FOR MCP INSPECTOR:")
    print("="*60)
    print(json.dumps(output, ensure_ascii=False))
    print("="*60)

    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python csv_to_json.py <input.csv> [--output <output.json>]")
        sys.exit(1)

    csv_file = sys.argv[1]
    output_file = None

    if "--output" in sys.argv:
        output_file = sys.argv[sys.argv.index("--output") + 1]

    csv_to_json(csv_file, output_file)
