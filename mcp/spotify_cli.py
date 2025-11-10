#!/usr/bin/env python3
"""
Interactive Command-Line Interface for Spotify MCP Server
"""

import asyncio
import os
import sys
import json
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

def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 60)
    print("  SPOTIFY MCP SERVER - COMMAND LINE INTERFACE")
    print("=" * 60)
    print()

def print_help():
    """Print help menu"""
    print("\nAvailable Commands:")
    print("-" * 60)
    print("  help                    - Show this help menu")
    print("  list                    - List all available tools")
    print("  search <query>          - Search for tracks")
    print("  profile                 - Get your Spotify profile")
    print("  top-tracks              - Get your top tracks")
    print("  top-artists             - Get your top artists")
    print("  artist <artist_id>      - Get artist information")
    print("  playlist <playlist_id>  - Analyze a playlist")
    print("  quit / exit             - Exit the program")
    print("-" * 60)
    print()

async def handle_command(command_line):
    """Handle user commands"""
    parts = command_line.strip().split(maxsplit=1)
    if not parts:
        return True

    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    try:
        if cmd in ["quit", "exit"]:
            print("\nGoodbye!")
            return False

        elif cmd == "help":
            print_help()

        elif cmd == "list":
            tools = await server.list_tools()
            print("\n" + "=" * 60)
            print(f"  AVAILABLE TOOLS ({len(tools)} total)")
            print("=" * 60)
            for i, tool in enumerate(tools, 1):
                print(f"\n{i}. {tool.name}")
                print(f"   {tool.description}")
            print("\n" + "=" * 60)

        elif cmd == "search":
            if not args:
                print("[ERROR] Please provide a search query. Example: search Taylor Swift")
                return True

            print(f"\nSearching for: {args}...")
            result = await server.call_tool("search_tracks", {"query": args, "limit": 5})
            data = json.loads(result[0].text)

            print("\n" + "=" * 60)
            print(f"  SEARCH RESULTS FOR: {args}")
            print("=" * 60)
            for i, track in enumerate(data, 1):
                artists = ", ".join(track["artists"])
                print(f"\n{i}. {track['name']}")
                print(f"   Artist(s): {artists}")
                print(f"   Album: {track['album']}")
                print(f"   Popularity: {track['popularity']}/100")
                print(f"   Spotify URL: {track['external_url']}")
            print("\n" + "=" * 60)

        elif cmd == "profile":
            print("\nFetching your Spotify profile...")
            resource_data = await server.read_resource("music://user/profile")
            data = json.loads(resource_data)

            print("\n" + "=" * 60)
            print("  YOUR SPOTIFY PROFILE")
            print("=" * 60)
            print(f"\nDisplay Name: {data.get('display_name', 'N/A')}")
            print(f"Email: {data.get('email', 'N/A')}")
            print(f"Country: {data.get('country', 'N/A')}")
            print(f"Followers: {data.get('followers', {}).get('total', 0)}")
            print(f"Product: {data.get('product', 'N/A')}")
            print(f"Profile URL: {data.get('external_urls', {}).get('spotify', 'N/A')}")
            print("\n" + "=" * 60)

        elif cmd == "top-tracks":
            print("\nFetching your top tracks...")
            resource_data = await server.read_resource("music://user/top-tracks")
            data = json.loads(resource_data)

            print("\n" + "=" * 60)
            print("  YOUR TOP 20 TRACKS")
            print("=" * 60)
            for i, track in enumerate(data.get("items", []), 1):
                artists = ", ".join([a["name"] for a in track["artists"]])
                print(f"\n{i}. {track['name']}")
                print(f"   Artist(s): {artists}")
                print(f"   Album: {track['album']['name']}")
                print(f"   Popularity: {track['popularity']}/100")
            print("\n" + "=" * 60)

        elif cmd == "top-artists":
            print("\nFetching your top artists...")
            resource_data = await server.read_resource("music://user/top-artists")
            data = json.loads(resource_data)

            print("\n" + "=" * 60)
            print("  YOUR TOP 20 ARTISTS")
            print("=" * 60)
            for i, artist in enumerate(data.get("items", []), 1):
                genres = ", ".join(artist.get("genres", []))[:50]
                print(f"\n{i}. {artist['name']}")
                print(f"   Genres: {genres if genres else 'N/A'}")
                print(f"   Popularity: {artist['popularity']}/100")
                print(f"   Followers: {artist['followers']['total']:,}")
            print("\n" + "=" * 60)

        elif cmd == "artist":
            if not args:
                print("[ERROR] Please provide an artist ID. Example: artist 06HL4z0CvFAxyc27GXpf02")
                return True

            print(f"\nFetching artist info for ID: {args}...")
            result = await server.call_tool("get_artist_info", {"artist_id": args})
            data = json.loads(result[0].text)

            print("\n" + "=" * 60)
            print(f"  ARTIST: {data['name']}")
            print("=" * 60)
            print(f"\nGenres: {', '.join(data['genres']) if data['genres'] else 'N/A'}")
            print(f"Popularity: {data['popularity']}/100")
            print(f"Followers: {data['followers']:,}")
            print(f"Spotify URL: {data['external_url']}")

            print("\nTop Tracks:")
            for i, track in enumerate(data['top_tracks'], 1):
                print(f"  {i}. {track['name']} (Popularity: {track['popularity']}/100)")
            print("\n" + "=" * 60)

        elif cmd == "playlist":
            if not args:
                print("[ERROR] Please provide a playlist ID. Example: playlist 37i9dQZF1DXcBWIGoYBM5M")
                return True

            print(f"\nAnalyzing playlist ID: {args}...")
            result = await server.call_tool("analyze_playlist", {"playlist_id": args})
            data = json.loads(result[0].text)

            print("\n" + "=" * 60)
            print(f"  PLAYLIST: {data['name']}")
            print("=" * 60)
            print(f"\nDescription: {data['description']}")
            print(f"Owner: {data['owner']}")
            print(f"Total Tracks: {data['total_tracks']}")
            print(f"Followers: {data['followers']}")
            print(f"\nStatistics:")
            print(f"  Average Popularity: {data['stats']['average_popularity']}/100")
            print(f"  Explicit Songs: {data['stats']['explicit_songs']} ({data['stats']['explicit_percentage']}%)")
            print(f"\nSpotify URL: {data['external_url']}")
            print("\n" + "=" * 60)

        else:
            print(f"[ERROR] Unknown command: {cmd}")
            print("Type 'help' to see available commands")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    return True

async def main():
    """Main interactive loop"""
    print_banner()
    print("Welcome! This CLI lets you interact with your Spotify account.")
    print("Type 'help' to see available commands, 'quit' to exit.")

    # Test connection
    try:
        tools = await server.list_tools()
        print(f"\n[OK] Connected to MCP server ({len(tools)} tools available)")
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to MCP server: {e}")
        return

    # Interactive loop
    while True:
        try:
            command = input("\nspotify> ").strip()
            if not command:
                continue

            should_continue = await handle_command(command)
            if not should_continue:
                break

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break

if __name__ == "__main__":
    asyncio.run(main())
