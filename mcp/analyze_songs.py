#!/usr/bin/env python3
"""
Bulk Song Analysis Tool - Analyze a CSV of songs using ALL 10 Spotify MCP Tools
"""

import asyncio
import os
import sys
import json
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify credentials are loaded
if "SPOTIFY_CLIENT_ID" not in os.environ or "SPOTIFY_CLIENT_SECRET" not in os.environ:
    print("[ERROR] Missing Spotify credentials!")
    print("Please create a .env file with your Spotify credentials.")
    print("See .env.example for the template.")
    sys.exit(1)

# Import the server
sys.path.insert(0, os.path.dirname(__file__))
import music_server_updated_2025 as server
def load_songs_from_csv(filename):
    """Load songs from CSV file"""
    songs = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "song_name": row["song_name"],
                "artist_name": row.get("artist_name", "")
            })
    return songs

def get_songs_interactively():
    """Get songs from user input interactively"""
    songs = []
    print("\n" + "=" * 70)
    print("  INTERACTIVE SONG INPUT")
    print("=" * 70)
    print("\nEnter songs one by one. Type 'done' when finished.")
    print("Format: Song Name [by Artist Name] (artist is optional)")
    print("\nExamples:")
    print("  - Blinding Lights by The Weeknd")
    print("  - Bohemian Rhapsody")
    print("  - Shape of You by Ed Sheeran")

    count = 1
    while True:
        print(f"\n[Song {count}]")
        song_input = input("  Enter song (or 'done'): ").strip()

        if song_input.lower() == 'done':
            break

        if not song_input:
            continue

        # Parse input - check if it has " by " or " - " separator
        if " by " in song_input.lower():
            parts = song_input.split(" by ", 1)
            song_name = parts[0].strip()
            artist_name = parts[1].strip()
        elif " - " in song_input:
            parts = song_input.split(" - ", 1)
            song_name = parts[0].strip()
            artist_name = parts[1].strip()
        else:
            song_name = song_input
            artist_name = input("  Artist (optional, press Enter to skip): ").strip()

        songs.append({
            "song_name": song_name,
            "artist_name": artist_name
        })

        print(f"  ✓ Added: {song_name}" + (f" by {artist_name}" if artist_name else ""))
        count += 1

    return songs

def get_songs_from_paste():
    """Get songs from bulk paste input"""
    songs = []
    print("\n" + "=" * 70)
    print("  BULK PASTE MODE")
    print("=" * 70)
    print("\nPaste your list of songs (one per line), then press Ctrl+Z and Enter (Windows) or Ctrl+D (Mac/Linux)")
    print("\nSupported formats:")
    print("  - Song Name - Artist Name")
    print("  - Song Name by Artist Name")
    print("  - Just Song Name (artist optional)")
    print("\nPaste your songs below:")
    print("-" * 70)

    lines = []
    try:
        while True:
            line = input()
            if line.strip():
                lines.append(line.strip())
    except EOFError:
        pass

    print("-" * 70)

    # Parse all lines
    for line in lines:
        if not line:
            continue

        # Parse input - check if it has " - " or " by " separator
        if " - " in line:
            parts = line.split(" - ", 1)
            song_name = parts[0].strip()
            artist_name = parts[1].strip()
        elif " by " in line.lower():
            parts = line.split(" by ", 1)
            song_name = parts[0].strip()
            artist_name = parts[1].strip()
        else:
            song_name = line.strip()
            artist_name = ""

        songs.append({
            "song_name": song_name,
            "artist_name": artist_name
        })

    print(f"\n[OK] Parsed {len(songs)} songs from your paste")

    # Show preview
    if songs:
        print("\nPreview (first 10 songs):")
        for i, song in enumerate(songs[:10], 1):
            print(f"  {i}. {song['song_name']}" + (f" - {song['artist_name']}" if song['artist_name'] else ""))
        if len(songs) > 10:
            print(f"  ... and {len(songs) - 10} more")

    return songs

def print_separator():
    print("\n" + "=" * 70)

async def tool_1_explicitness(songs):
    """TOOL 1: Analyze explicit content"""
    print("\n[RUNNING TOOL 1: analyze_explicitness]")
    result = await server.call_tool("analyze_explicitness", {"songs": songs})
    data = json.loads(result[0].text)

    print_separator()
    print("  EXPLICIT CONTENT ANALYSIS")
    print_separator()
    print(f"\nTotal Songs: {data['summary']['total_songs_analyzed']}")
    print(f"Explicit Songs: {data['summary']['explicit_songs_count']}")
    print(f"Clean Songs: {data['summary']['clean_songs_count']}")
    print(f"Explicit %: {data['summary']['explicit_percentage']}%")
    print(f"Rating: {data['summary']['rating']}")

    if data['explicit_songs']:
        print(f"\nALL EXPLICIT SONGS ({len(data['explicit_songs'])} total):")
        for i, song in enumerate(data['explicit_songs'], 1):
            artists = ", ".join(song['artists'])
            print(f"  {i}. {song['name']} by {artists}")

    if data.get('clean_songs'):
        print(f"\nALL CLEAN SONGS ({len(data['clean_songs'])} total):")
        for i, song in enumerate(data['clean_songs'], 1):
            artists = ", ".join(song['artists'])
            print(f"  {i}. {song['name']} by {artists}")

    print_separator()

async def tool_2_diversity(songs):
    """TOOL 2: Analyze collection diversity"""
    print("\n[RUNNING TOOL 2: analyze_collection_diversity]")
    result = await server.call_tool("analyze_collection_diversity", {"songs": songs})
    data = json.loads(result[0].text)

    print_separator()
    print("  DIVERSITY ANALYSIS")
    print_separator()
    print(f"\nDiversity Level: {data['summary']['diversity_level']}")
    print(f"\nARTIST DIVERSITY: {data['artist_diversity']['interpretation']}")
    print(f"  Unique Artists: {data['artist_diversity']['unique_artists']}")
    print(f"  Diversity Score: {data['artist_diversity']['diversity_score']}")
    print(f"\nGENRE DIVERSITY: {data['genre_diversity']['interpretation']}")
    print(f"  Unique Genres: {data['genre_diversity']['unique_genres']}")
    print(f"\nPOPULARITY: {data['popularity_distribution']['interpretation']}")
    print(f"  Average: {data['popularity_distribution']['average_popularity']}/100")

    # Show songs by popularity tier if available
    if data.get('popularity_distribution', {}).get('by_tier'):
        print("\n  Songs by Popularity Tier:")
        for tier, songs_list in data['popularity_distribution']['by_tier'].items():
            print(f"\n  {tier.upper()} ({len(songs_list)} songs):")
            for song in songs_list[:5]:  # Show first 5 from each tier
                artists = ", ".join(song['artists'])
                print(f"    - {song['name']} by {artists} (Popularity: {song['popularity']})")
            if len(songs_list) > 5:
                print(f"    ... and {len(songs_list) - 5} more")

    print(f"\nERA: {data['era_distribution']['interpretation']}")
    print(f"  {data['era_distribution']['earliest']} - {data['era_distribution']['latest']}")

    # Show songs by decade/era if available
    if data.get('era_distribution', {}).get('by_decade'):
        print("\n  Songs by Decade:")
        for decade, songs_list in sorted(data['era_distribution']['by_decade'].items(), reverse=True):
            print(f"\n  {decade} ({len(songs_list)} songs):")
            for song in songs_list[:5]:  # Show first 5 from each decade
                artists = ", ".join(song['artists'])
                release_year = song.get('release_year', 'Unknown')
                print(f"    - {song['name']} by {artists} ({release_year})")
            if len(songs_list) > 5:
                print(f"    ... and {len(songs_list) - 5} more")

    print_separator()

async def tool_3_genres(songs):
    """TOOL 3: Analyze genre distribution"""
    print("\n[RUNNING TOOL 3: analyze_genres_in_collection]")
    result = await server.call_tool("analyze_genres_in_collection", {"songs": songs})
    data = json.loads(result[0].text)

    print_separator()
    print("  GENRE ANALYSIS")
    print_separator()
    print(f"\nDominant Style: {data['summary']['dominant_style']}")
    print(f"Unique Genres: {data['summary']['unique_genres']}")
    print(f"Diversity: {data['summary']['genre_diversity']}")
    print("\nTOP 10 GENRES WITH EXAMPLE SONGS:")
    for i, genre in enumerate(data['top_genres'][:10], 1):
        print(f"\n  {i}. {genre['genre']} - {genre['count']} songs ({genre['percentage']}%)")

        # Show example songs for this genre if available
        if genre.get('songs'):
            print(f"     Example songs:")
            for song in genre['songs'][:5]:  # Show up to 5 example songs
                artists = ", ".join(song['artists'])
                print(f"       - {song['name']} by {artists}")
            if len(genre['songs']) > 5:
                print(f"       ... and {len(genre['songs']) - 5} more")
    print_separator()

async def tool_4_top_artists(songs):
    """TOOL 4: Get top artists from collection"""
    print("\n[RUNNING TOOL 4: get_top_artists_from_collection]")
    result = await server.call_tool("get_top_artists_from_collection", {"songs": songs, "top_n": 10})
    data = json.loads(result[0].text)

    print_separator()
    print("  TOP ARTISTS")
    print_separator()
    print(f"\nUnique Artists: {data['summary']['unique_artists']}")
    print(f"Distribution: {data['distribution_type']}")
    print("\nTOP 10 ARTISTS WITH THEIR SONGS:")
    for i, artist in enumerate(data['top_artists'], 1):
        print(f"\n  {i}. {artist['artist']} - {artist['song_count']} songs ({artist['percentage']}%)")

        # Show all songs for this artist if available
        if artist.get('songs'):
            print(f"     Songs:")
            for song in artist['songs']:
                print(f"       - {song['name']}")
    print_separator()

async def tool_5_create_playlist(songs, playlist_name):
    """TOOL 5: Create playlist"""
    print(f"\n[RUNNING TOOL 5: create_playlist - '{playlist_name}']")
    result = await server.call_tool("create_playlist", {
        "playlist_name": playlist_name,
        "songs": songs,
        "description": "Created with Spotify MCP Server",
        "public": False
    })
    data = json.loads(result[0].text)

    print_separator()
    print("  PLAYLIST CREATED")
    print_separator()
    print(f"\nPlaylist: {data['playlist']['name']}")
    print(f"URL: {data['playlist']['url']}")
    print(f"Songs Added: {data['summary']['songs_added']}/{data['summary']['total_requested']}")
    if data['summary']['not_found'] > 0:
        print(f"Not Found: {data['summary']['not_found']}")
    print_separator()

async def tool_6_balanced_playlist(songs, criteria, playlist_name=None):
    """TOOL 6: Generate balanced playlist"""
    print(f"\n[RUNNING TOOL 6: generate_balanced_playlist - Balance by {criteria}]")

    # Build arguments
    args = {
        "songs": songs,
        "target_size": 20,
        "balance_criteria": criteria
    }

    # Add playlist name if provided (this will create it on Spotify)
    if playlist_name:
        args["playlist_name"] = playlist_name
        print(f"Will create playlist on Spotify: '{playlist_name}'")

    result = await server.call_tool("generate_balanced_playlist", args)
    data = json.loads(result[0].text)

    print_separator()
    print(f"  BALANCED PLAYLIST (by {criteria})")
    print_separator()
    print(f"\nSource Songs: {data['summary']['source_songs']}")
    print(f"Selected Songs: {data['summary']['selected_songs']}")
    print("\nBALANCED SELECTION:")
    for i, song in enumerate(data['balanced_selection'][:10], 1):
        artists = ", ".join(song['artists'])
        print(f"  {i}. {song['name']} by {artists}")
    if len(data['balanced_selection']) > 10:
        print(f"  ... and {len(data['balanced_selection']) - 10} more")

    # Show playlist creation info if it was created
    if "playlist_created" in data:
        print("\n[SUCCESS] PLAYLIST CREATED ON SPOTIFY!")
        print(f"  Name: {data['playlist_created']['name']}")
        print(f"  URL: {data['playlist_created']['url']}")
        print(f"  ID: {data['playlist_created']['id']}")

    print_separator()

async def tool_11_compare_to_taste(songs):
    """TOOL 11: Compare to My Taste"""
    print("\n[RUNNING TOOL 11: compare_to_my_taste]")
    result = await server.call_tool("compare_to_my_taste", {"songs": songs})
    data = json.loads(result[0].text)

    print_separator()
    print("  COMPARE TO YOUR TASTE")
    print_separator()
    print(f"\nAlignment: {data['summary']['alignment']}")
    print(f"Match Percentage: {data['summary']['match_percentage']}%")
    print(f"Total Analyzed: {data['summary']['total_analyzed']}")

    print(f"\nMATCHES:")
    print(f"  Favorite Tracks Found: {data['matches']['favorite_tracks_count']}")
    if data['matches']['favorite_tracks']:
        print("  Examples:")
        for track in data['matches']['favorite_tracks']:
            print(f"    - {track['name']} by {', '.join(track['artists'])}")

    print(f"\n  Favorite Artists Found: {data['matches']['favorite_artists_count']}")
    if data['matches']['favorite_artists']:
        print("  Examples:")
        for track in data['matches']['favorite_artists'][:3]:
            print(f"    - {track['name']} by {', '.join(track['artists'])}")

    print(f"\nOVERLAPS:")
    print(f"  Artists: {data['overlaps']['artist_overlap']}")
    print(f"  Genres: {data['overlaps']['genre_overlap']}")

    if data['insights']['new_genres_in_collection']:
        print(f"\nNEW GENRES TO EXPLORE:")
        for genre in data['insights']['new_genres_in_collection']:
            print(f"  - {genre}")

    if data['insights']['songs_to_explore']:
        print(f"\nSONGS OUTSIDE YOUR USUAL TASTE:")
        for song in data['insights']['songs_to_explore']:
            print(f"  - {song['name']} by {', '.join(song['artists'])}")

    print_separator()

async def tool_12_find_missing(songs):
    """TOOL 12: Find What's Missing"""
    print("\n[RUNNING TOOL 12: find_whats_missing]")
    result = await server.call_tool("find_whats_missing", {"songs": songs})
    data = json.loads(result[0].text)

    print_separator()
    print("  FIND WHAT'S MISSING FROM YOUR LIBRARY")
    print_separator()
    print(f"\nTotal Checked: {data['summary']['total_songs_checked']}")
    print(f"Already Saved: {data['summary']['already_saved']}")
    print(f"Missing: {data['summary']['missing_from_library']} ({data['summary']['missing_percentage']}%)")

    if data['missing_songs']:
        print(f"\nSONGS NOT IN YOUR LIBRARY:")
        for i, song in enumerate(data['missing_songs'][:10], 1):
            artists = ", ".join(song['artists'])
            print(f"  {i}. {song['name']} by {artists}")
            print(f"     Popularity: {song['popularity']}/100")
            print(f"     URL: {song['url']}")
        if len(data['missing_songs']) > 10:
            print(f"  ... and {len(data['missing_songs']) - 10} more")

    if data['already_saved_songs']:
        print(f"\nALREADY IN YOUR LIBRARY ({len(data['already_saved_songs'])} songs):")
        for song in data['already_saved_songs'][:5]:
            print(f"  - {song['name']} by {', '.join(song['artists'])}")

    print_separator()

async def run_all_analyses(songs):
    """Run all 6 collection-based tools"""
    print("\n" + "=" * 70)
    print("  RUNNING ALL COLLECTION ANALYSES")
    print("=" * 70)

    await tool_1_explicitness(songs)
    await tool_2_diversity(songs)
    await tool_3_genres(songs)
    await tool_4_top_artists(songs)

async def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("  SPOTIFY SONG COLLECTION ANALYZER - ALL 12 TOOLS")
    print("=" * 70)

    # Ask user for input method
    print("\nHow would you like to provide songs?")
    print("  1. Load from CSV file (recommended for large lists)")
    print("  2. Enter songs manually (one by one)")
    print("  3. Paste a list of songs (bulk paste)")

    choice = input("\nSelect option (1, 2, or 3): ").strip()

    songs = []

    if choice == "2":
        # Interactive mode
        songs = get_songs_interactively()
        if not songs:
            print("\n[ERROR] No songs entered!")
            return
        print(f"\n[OK] Loaded {len(songs)} songs")
    elif choice == "3":
        # Bulk paste mode
        songs = get_songs_from_paste()
        if not songs:
            print("\n[ERROR] No songs entered!")
            return
    else:
        # CSV mode (default)
        csv_file = "song_list_template.csv"
        if len(sys.argv) > 1:
            csv_file = sys.argv[1]
        else:
            # Ask for CSV filename
            custom_file = input(f"\nEnter CSV filename (or press Enter for '{csv_file}'): ").strip()
            if custom_file:
                csv_file = custom_file

        if not os.path.exists(csv_file):
            print(f"\n[ERROR] CSV file not found: {csv_file}")
            print("\nUsage: python analyze_songs.py [csv_file]")
            print("Default: song_list_template.csv")
            return

        # Load songs
        print(f"\n[OK] Loading songs from: {csv_file}")
        songs = load_songs_from_csv(csv_file)
        print(f"[OK] Loaded {len(songs)} songs")

    # Show menu
    print("\nCOLLECTION ANALYSIS TOOLS (require song list):")
    print("  1. Analyze Explicitness")
    print("  2. Analyze Diversity")
    print("  3. Analyze Genres")
    print("  4. Get Top Artists")
    print("  5. Create Playlist")
    print("  6. Generate Balanced Playlist")
    print("  7. Compare to My Taste (MCP ONLY!)")
    print("  8. Find What's Missing from My Library (MCP ONLY!)")
    print("  9. Run ALL Analyses (1-4)")
    print("\nOTHER TOOLS (no song list needed):")
    print("  10. Search Tracks")
    print("  11. Get Recommendations")
    print("  12. Get Artist Info")
    print("  13. Analyze Playlist")
    print("  0. Exit")

    choice = input("\nSelect option (0-13): ").strip()

    if choice == "1":
        await tool_1_explicitness(songs)
    elif choice == "2":
        await tool_2_diversity(songs)
    elif choice == "3":
        await tool_3_genres(songs)
    elif choice == "4":
        await tool_4_top_artists(songs)
    elif choice == "5":
        name = input("Enter playlist name: ").strip() or "My Collection"
        await tool_5_create_playlist(songs, name)
    elif choice == "6":
        print("\nBalance by: genre, artist, or era?")
        criteria = input("Enter criteria: ").strip() or "genre"
        create = input("Create this playlist on Spotify? (yes/no): ").strip().lower()
        playlist_name = None
        if create in ["yes", "y"]:
            playlist_name = input("Enter playlist name: ").strip() or f"Balanced by {criteria.title()}"
        await tool_6_balanced_playlist(songs, criteria, playlist_name)
    elif choice == "7":
        await tool_11_compare_to_taste(songs)
    elif choice == "8":
        await tool_12_find_missing(songs)
    elif choice == "9":
        await run_all_analyses(songs)
    elif choice == "10":
        query = input("Search for: ").strip()
        if query:
            result = await server.call_tool("search_tracks", {"query": query, "limit": 5})
            data = json.loads(result[0].text)
            print_separator()
            print(f"  SEARCH RESULTS: {query}")
            print_separator()
            for i, track in enumerate(data, 1):
                print(f"\n{i}. {track['name']} by {', '.join(track['artists'])}")
                print(f"   Popularity: {track['popularity']}/100")
            print_separator()
    elif choice == "11":
        print("\nNeed at least one seed (track ID, artist ID, or genre)")
        seed = input("Enter seed track ID or genre: ").strip()
        if seed:
            # Check if it's a genre or ID
            if len(seed) < 10:  # Probably a genre
                result = await server.call_tool("get_recommendations", {"seed_genres": [seed], "limit": 10})
            else:
                result = await server.call_tool("get_recommendations", {"seed_tracks": [seed], "limit": 10})
            data = json.loads(result[0].text)
            print_separator()
            print("  RECOMMENDATIONS")
            print_separator()
            for i, track in enumerate(data, 1):
                print(f"{i}. {track['name']} by {', '.join(track['artists'])}")
            print_separator()
    elif choice == "12":
        artist_id = input("Enter artist ID: ").strip()
        if artist_id:
            result = await server.call_tool("get_artist_info", {"artist_id": artist_id})
            data = json.loads(result[0].text)
            print_separator()
            print(f"  ARTIST: {data['name']}")
            print_separator()
            print(f"\nGenres: {', '.join(data['genres'][:5])}")
            print(f"Popularity: {data['popularity']}/100")
            print(f"Followers: {data['followers']:,}")
            print("\nTop Tracks:")
            for i, track in enumerate(data['top_tracks'][:5], 1):
                print(f"  {i}. {track['name']}")
            print_separator()
    elif choice == "13":
        playlist_id = input("Enter playlist ID: ").strip()
        if playlist_id:
            result = await server.call_tool("analyze_playlist", {"playlist_id": playlist_id})
            data = json.loads(result[0].text)
            print_separator()
            print(f"  PLAYLIST: {data['name']}")
            print_separator()
            print(f"\nOwner: {data['owner']}")
            print(f"Tracks: {data['total_tracks']}")
            print(f"Avg Popularity: {data['stats']['average_popularity']}/100")
            print(f"Explicit: {data['stats']['explicit_percentage']}%")
            print_separator()
    elif choice == "0":
        print("\nGoodbye!")
    else:
        print("\n[ERROR] Invalid option")

if __name__ == "__main__":
    asyncio.run(main())
