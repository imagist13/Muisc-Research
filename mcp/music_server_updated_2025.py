#!/usr/bin/env python3
"""
Music MCP Server - Updated for 2025 Spotify API Changes
AI @Princeton Workshop - October 31, 2025

This MCP server connects Claude to Spotify, allowing natural language
music queries, playlist analysis, and song recommendations.

WHAT CHANGED IN 2025:
- audio-features endpoint now requires track IDs instead of URIs
- Updated authentication flow
- Improved error handling for batch requests
"""

import os
import json
import logging
from typing import Any, Sequence
from datetime import datetime
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

# Load environment variables from .env file
load_dotenv()
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("music-server")

# Initialize Spotify clients
_spotify_client_oauth = None
_spotify_client_cc = None

def get_spotify_client(require_user_auth=False):
    """
    Initialize and return authenticated Spotify client (lazy initialization).
    
    Args:
        require_user_auth: If True, uses OAuth (requires user authorization).
                          If False, uses Client Credentials (no user auth needed).
    """
    global _spotify_client_oauth, _spotify_client_cc
    
    # Check if environment variables exist
    if "SPOTIFY_CLIENT_ID" not in os.environ or "SPOTIFY_CLIENT_SECRET" not in os.environ:
        raise RuntimeError(
            "Spotify credentials not found. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables."
        )
    
    if require_user_auth:
        # Use OAuth for user-specific operations
        if _spotify_client_oauth is None:
            scope = "user-library-read user-top-read playlist-read-private playlist-modify-public playlist-modify-private"
            _spotify_client_oauth = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=os.environ["SPOTIFY_CLIENT_ID"],
                client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
                redirect_uri="http://127.0.0.1:8888/callback",
                scope=scope
            ))
        return _spotify_client_oauth
    else:
        # Use Client Credentials for public operations (search, recommendations, etc.)
        if _spotify_client_cc is None:
            _spotify_client_cc = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=os.environ["SPOTIFY_CLIENT_ID"],
                client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]
            ))
        return _spotify_client_cc

# Initialize MCP server
app = Server("music-server")
# Note: sp is now lazily initialized via get_spotify_client() when needed

def _sp(require_user_auth=False):
    """Helper function to get Spotify client (lazy initialization)."""
    return get_spotify_client(require_user_auth=require_user_auth)


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available music-related resources."""
    return [
        Resource(
            uri=AnyUrl("music://user/profile"),
            name="User Profile",
            mimeType="application/json",
            description="Current user's Spotify profile information"
        ),
        Resource(
            uri=AnyUrl("music://user/top-tracks"),
            name="Top Tracks",
            mimeType="application/json",
            description="User's most played tracks"
        ),
        Resource(
            uri=AnyUrl("music://user/top-artists"),
            name="Top Artists",
            mimeType="application/json",
            description="User's most listened to artists"
        )
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read and return music resource data."""
    uri_str = str(uri)
    
    if uri_str == "music://user/profile":
        # Requires user auth
        profile = _sp(require_user_auth=True).current_user()
        return json.dumps(profile, indent=2)
    
    elif uri_str == "music://user/top-tracks":
        # Requires user auth
        tracks = _sp(require_user_auth=True).current_user_top_tracks(limit=20, time_range="medium_term")
        return json.dumps(tracks, indent=2)
    
    elif uri_str == "music://user/top-artists":
        # Requires user auth
        artists = _sp(require_user_auth=True).current_user_top_artists(limit=20, time_range="medium_term")
        return json.dumps(artists, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available music analysis tools."""
    return [
        Tool(
            name="search_tracks",
            description="Search for tracks on Spotify by name, artist, or keywords",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (song name, artist, keywords)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to return (1-50)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_recommendations",
            description="Get song recommendations based on seed tracks, artists, or genres. Provide song names, artist names, or genres and get personalized recommendations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "seed_tracks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "song_name": {"type": "string"},
                                "artist_name": {"type": "string"}
                            },
                            "required": ["song_name"]
                        },
                        "description": "Up to 5 songs to base recommendations on (provide song name and optionally artist name)"
                    },
                    "seed_artists": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Up to 5 artist names to base recommendations on"
                    },
                    "seed_genres": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Up to 5 genre names (e.g., 'pop', 'rock', 'hip-hop', 'electronic')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of recommendations (1-100)",
                        "default": 20
                    }
                }
            }
        ),
        Tool(
            name="analyze_playlist",
            description="Analyze a Spotify playlist to get insights about its musical characteristics",
            inputSchema={
                "type": "object",
                "properties": {
                    "playlist_id": {
                        "type": "string",
                        "description": "Spotify playlist ID"
                    }
                },
                "required": ["playlist_id"]
            }
        ),
        Tool(
            name="get_artist_info",
            description="Get detailed information about an artist including genres, popularity, and top tracks",
            inputSchema={
                "type": "object",
                "properties": {
                    "artist_id": {
                        "type": "string",
                        "description": "Spotify artist ID"
                    }
                },
                "required": ["artist_id"]
            }
        ),
        Tool(
            name="analyze_explicitness",
            description="Analyze explicit content in a collection of songs - find out how many songs have explicit lyrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "songs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "song_name": {"type": "string"},
                                "artist_name": {"type": "string"}
                            },
                            "required": ["song_name"]
                        },
                        "description": "List of songs to check for explicit content"
                    }
                },
                "required": ["songs"]
            }
        ),
        Tool(
            name="analyze_collection_diversity",
            description="Analyze diversity in a music collection - unique artists, genre spread, era distribution, popularity range",
            inputSchema={
                "type": "object",
                "properties": {
                    "songs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "song_name": {"type": "string"},
                                "artist_name": {"type": "string"}
                            },
                            "required": ["song_name"]
                        },
                        "description": "List of songs to analyze for diversity"
                    }
                },
                "required": ["songs"]
            }
        ),
        Tool(
            name="get_top_artists_from_collection",
            description="Find the most frequent artists in a song collection and their contribution percentage",
            inputSchema={
                "type": "object",
                "properties": {
                    "songs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "song_name": {"type": "string"},
                                "artist_name": {"type": "string"}
                            },
                            "required": ["song_name"]
                        },
                        "description": "List of songs to analyze"
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of top artists to return",
                        "default": 10
                    }
                },
                "required": ["songs"]
            }
        ),
        Tool(
            name="analyze_genres_in_collection",
            description="Analyze genre distribution in a music collection - find dominant genres, genre diversity, and trends",
            inputSchema={
                "type": "object",
                "properties": {
                    "songs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "song_name": {"type": "string"},
                                "artist_name": {"type": "string"}
                            },
                            "required": ["song_name"]
                        },
                        "description": "List of songs to analyze for genres"
                    }
                },
                "required": ["songs"]
            }
        ),
        Tool(
            name="create_playlist",
            description="Create a new Spotify playlist from a collection of songs",
            inputSchema={
                "type": "object",
                "properties": {
                    "playlist_name": {
                        "type": "string",
                        "description": "Name for the new playlist"
                    },
                    "songs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "song_name": {"type": "string"},
                                "artist_name": {"type": "string"}
                            },
                            "required": ["song_name"]
                        },
                        "description": "List of songs to add to the playlist"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the playlist"
                    },
                    "public": {
                        "type": "boolean",
                        "description": "Whether the playlist should be public (default: false)",
                        "default": False
                    }
                },
                "required": ["playlist_name", "songs"]
            }
        ),
        Tool(
            name="generate_balanced_playlist",
            description="Create a balanced playlist from a song collection based on genre, artist, and era distribution",
            inputSchema={
                "type": "object",
                "properties": {
                    "songs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "song_name": {"type": "string"},
                                "artist_name": {"type": "string"}
                            },
                            "required": ["song_name"]
                        },
                        "description": "Source collection of songs to balance from"
                    },
                    "target_size": {
                        "type": "integer",
                        "description": "Target number of songs for the balanced playlist (default: 30)",
                        "default": 30
                    },
                    "balance_criteria": {
                        "type": "string",
                        "description": "What to balance by: 'genre', 'artist', or 'era' (default: 'genre')",
                        "default": "genre"
                    },
                    "playlist_name": {
                        "type": "string",
                        "description": "Name for the new balanced playlist (optional - if provided, creates the playlist)"
                    }
                },
                "required": ["songs"]
            }
        ),
        Tool(
            name="compare_to_my_taste",
            description="Compare a song collection to your actual Spotify listening history - find overlaps, differences, and get personalized insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "songs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "song_name": {"type": "string"},
                                "artist_name": {"type": "string"}
                            },
                            "required": ["song_name"]
                        },
                        "description": "List of songs to compare to your taste"
                    }
                },
                "required": ["songs"]
            }
        ),
        Tool(
            name="find_whats_missing",
            description="Check which songs from a collection are NOT in your Spotify library - find songs you haven't saved yet",
            inputSchema={
                "type": "object",
                "properties": {
                    "songs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "song_name": {"type": "string"},
                                "artist_name": {"type": "string"}
                            },
                            "required": ["song_name"]
                        },
                        "description": "List of songs to check against your library"
                    }
                },
                "required": ["songs"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Execute music analysis tools."""
    
    try:
        if name == "search_tracks":
            query = arguments["query"]
            limit = arguments.get("limit", 10)
            
            # Search doesn't require user auth - use Client Credentials
            results = _sp(require_user_auth=False).search(q=query, type="track", limit=limit)
            tracks = results["tracks"]["items"]
            
            formatted_results = []
            for track in tracks:
                formatted_results.append({
                    "name": track["name"],
                    "artists": [artist["name"] for artist in track["artists"]],
                    "album": track["album"]["name"],
                    "id": track["id"],
                    "uri": track["uri"],
                    "popularity": track["popularity"],
                    "preview_url": track.get("preview_url"),
                    "external_url": track["external_urls"]["spotify"]
                })
            
            return [TextContent(
                type="text",
                text=json.dumps(formatted_results, indent=2)
            )]

        elif name == "get_recommendations":
            seed_tracks_input = arguments.get("seed_tracks", [])
            seed_artists_input = arguments.get("seed_artists", [])
            seed_genres = arguments.get("seed_genres", [])
            limit = arguments.get("limit", 20)

            # Look up track IDs from song names
            track_ids = []
            track_lookup_errors = []
            for track_data in seed_tracks_input[:5]:
                song_name = track_data["song_name"]
                artist_name = track_data.get("artist_name", "")

                query = song_name
                if artist_name:
                    query += f" artist:{artist_name}"

                # Search doesn't require user auth
                search_results = _sp(require_user_auth=False).search(q=query, type="track", limit=1)
                tracks = search_results["tracks"]["items"]

                if tracks:
                    track_ids.append(tracks[0]["id"])
                else:
                    track_lookup_errors.append(f"Track not found: {query}")

            # Look up artist IDs from artist names
            artist_ids = []
            artist_lookup_errors = []
            for artist_name in seed_artists_input[:5]:
                # Search doesn't require user auth
                search_results = _sp(require_user_auth=False).search(q=f"artist:{artist_name}", type="artist", limit=1)
                artists = search_results["artists"]["items"]

                if artists:
                    artist_ids.append(artists[0]["id"])
                else:
                    artist_lookup_errors.append(f"Artist not found: {artist_name}")

            # Ensure we have at least one seed
            if not track_ids and not artist_ids and not seed_genres:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "At least one seed (track, artist, or genre) is required",
                        "track_lookup_errors": track_lookup_errors if track_lookup_errors else None,
                        "artist_lookup_errors": artist_lookup_errors if artist_lookup_errors else None
                    }, indent=2)
                )]

            # Get recommendations - doesn't require user auth
            recommendations = _sp(require_user_auth=False).recommendations(
                seed_tracks=track_ids[:5] if track_ids else None,
                seed_artists=artist_ids[:5] if artist_ids else None,
                seed_genres=seed_genres[:5] if seed_genres else None,
                limit=limit
            )

            formatted_recs = []
            for track in recommendations["tracks"]:
                formatted_recs.append({
                    "name": track["name"],
                    "artists": [artist["name"] for artist in track["artists"]],
                    "album": track["album"]["name"],
                    "id": track["id"],
                    "uri": track["uri"],
                    "popularity": track["popularity"],
                    "external_url": track["external_urls"]["spotify"]
                })

            result = {
                "recommendations": formatted_recs,
                "seeds_used": {
                    "tracks": len(track_ids),
                    "artists": len(artist_ids),
                    "genres": len(seed_genres) if seed_genres else 0
                }
            }

            # Include any lookup errors if they occurred
            if track_lookup_errors or artist_lookup_errors:
                result["lookup_warnings"] = {
                    "track_errors": track_lookup_errors if track_lookup_errors else None,
                    "artist_errors": artist_lookup_errors if artist_lookup_errors else None
                }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "analyze_playlist":
            playlist_id = arguments["playlist_id"]

            # Get playlist details - may require user auth if private
            playlist = _sp(require_user_auth=True).playlist(playlist_id)
            tracks = playlist["tracks"]["items"]

            # Collect track info
            track_info = []
            total_popularity = 0
            explicit_count = 0

            for item in tracks:
                if item["track"]:
                    track = item["track"]
                    track_info.append({
                        "name": track["name"],
                        "artists": [a["name"] for a in track["artists"]],
                        "popularity": track["popularity"],
                        "explicit": track["explicit"]
                    })
                    total_popularity += track["popularity"]
                    if track["explicit"]:
                        explicit_count += 1

            analysis = {
                "name": playlist["name"],
                "description": playlist["description"],
                "owner": playlist["owner"]["display_name"],
                "total_tracks": playlist["tracks"]["total"],
                "followers": playlist["followers"]["total"],
                "stats": {
                    "average_popularity": round(total_popularity / len(track_info), 1) if track_info else 0,
                    "explicit_songs": explicit_count,
                    "explicit_percentage": round((explicit_count / len(track_info) * 100), 1) if track_info else 0
                },
                "external_url": playlist["external_urls"]["spotify"]
            }

            return [TextContent(
                type="text",
                text=json.dumps(analysis, indent=2)
            )]
        
        elif name == "get_artist_info":
            artist_id = arguments["artist_id"]
            
            # Get artist details - doesn't require user auth
            artist = _sp(require_user_auth=False).artist(artist_id)
            
            # Get top tracks - doesn't require user auth
            top_tracks = _sp(require_user_auth=False).artist_top_tracks(artist_id)
            
            info = {
                "name": artist["name"],
                "genres": artist["genres"],
                "popularity": artist["popularity"],
                "followers": artist["followers"]["total"],
                "top_tracks": [
                    {
                        "name": track["name"],
                        "album": track["album"]["name"],
                        "popularity": track["popularity"],
                        "id": track["id"]
                    }
                    for track in top_tracks["tracks"][:10]
                ],
                "external_url": artist["external_urls"]["spotify"]
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(info, indent=2)
            )]

        elif name == "analyze_explicitness":
            songs = arguments["songs"]
            
            explicit_songs = []
            clean_songs = []
            errors = []
            
            for song_data in songs:
                song_name = song_data["song_name"]
                artist_name = song_data.get("artist_name", "")
                
                # Build search query
                query = song_name
                if artist_name:
                    query += f" artist:{artist_name}"
                
                # Search for the song - doesn't require user auth
                search_results = _sp(require_user_auth=False).search(q=query, type="track", limit=1)
                tracks = search_results["tracks"]["items"]
                
                if not tracks:
                    errors.append(f"Not found: {query}")
                    continue
                
                track = tracks[0]
                
                song_info = {
                    "name": track["name"],
                    "artists": [a["name"] for a in track["artists"]],
                    "explicit": track["explicit"],
                    "popularity": track["popularity"]
                }
                
                if track["explicit"]:
                    explicit_songs.append(song_info)
                else:
                    clean_songs.append(song_info)
            
            total_songs = len(explicit_songs) + len(clean_songs)
            explicit_percentage = (len(explicit_songs) / total_songs * 100) if total_songs > 0 else 0
            
            result = {
                "summary": {
                    "total_songs_analyzed": total_songs,
                    "explicit_songs_count": len(explicit_songs),
                    "clean_songs_count": len(clean_songs),
                    "explicit_percentage": round(explicit_percentage, 1),
                    "rating": "Family-Friendly" if explicit_percentage == 0 else 
                              "Mostly Clean" if explicit_percentage < 25 else
                              "Mixed Content" if explicit_percentage < 50 else
                              "Mostly Explicit" if explicit_percentage < 75 else
                              "Explicit",
                    "errors": errors if errors else None
                },
                "explicit_songs": explicit_songs,
                "clean_songs": clean_songs
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "analyze_collection_diversity":
            songs = arguments["songs"]
            
            all_artists = []
            all_genres = set()
            popularities = []
            release_years = []
            track_info = []
            errors = []
            
            for song_data in songs:
                song_name = song_data["song_name"]
                artist_name = song_data.get("artist_name", "")
                
                # Build search query
                query = song_name
                if artist_name:
                    query += f" artist:{artist_name}"
                
                # Search for the song - doesn't require user auth
                search_results = _sp(require_user_auth=False).search(q=query, type="track", limit=1)
                tracks = search_results["tracks"]["items"]
                
                if not tracks:
                    errors.append(f"Not found: {query}")
                    continue
                
                track = tracks[0]
                
                # Collect artist names
                for artist in track["artists"]:
                    all_artists.append(artist["name"])
                    
                    # Get artist genres - doesn't require user auth
                    try:
                        artist_info = _sp(require_user_auth=False).artist(artist["id"])
                        all_genres.update(artist_info["genres"])
                    except:
                        pass
                
                # Collect popularity
                popularities.append(track["popularity"])
                
                # Get release year
                release_date = track["album"]["release_date"]
                year = None
                if release_date:
                    year = int(release_date.split("-")[0])
                    release_years.append(year)
                
                track_info.append({
                    "name": track["name"],
                    "artists": [a["name"] for a in track["artists"]],
                    "popularity": track["popularity"],
                    "release_year": year
                })
            
            # Calculate diversity metrics
            unique_artists = len(set(all_artists))
            total_artists = len(all_artists)
            artist_diversity = unique_artists / total_artists if total_artists > 0 else 0
            
            unique_genres = len(all_genres)
            
            popularity_range = max(popularities) - min(popularities) if popularities else 0
            avg_popularity = sum(popularities) / len(popularities) if popularities else 0
            
            year_range = max(release_years) - min(release_years) if release_years else 0
            
            # Determine diversity level
            if artist_diversity > 0.8 and unique_genres > 10:
                diversity_level = "Very Diverse"
            elif artist_diversity > 0.6 and unique_genres > 5:
                diversity_level = "Diverse"
            elif artist_diversity > 0.4:
                diversity_level = "Moderately Diverse"
            else:
                diversity_level = "Low Diversity"
            
            result = {
                "summary": {
                    "diversity_level": diversity_level,
                    "total_songs": len(track_info),
                    "errors": errors if errors else None
                },
                "artist_diversity": {
                    "unique_artists": unique_artists,
                    "total_artist_appearances": total_artists,
                    "diversity_score": round(artist_diversity, 3),
                    "interpretation": "High" if artist_diversity > 0.7 else 
                                    "Medium" if artist_diversity > 0.4 else "Low"
                },
                "genre_diversity": {
                    "unique_genres": unique_genres,
                    "genres": sorted(list(all_genres)),
                    "interpretation": "Very Diverse" if unique_genres > 10 else
                                    "Diverse" if unique_genres > 5 else
                                    "Limited" if unique_genres > 2 else
                                    "Very Limited"
                },
                "popularity_distribution": {
                    "average_popularity": round(avg_popularity, 1),
                    "range": popularity_range,
                    "interpretation": "Mainstream" if avg_popularity > 70 else
                                    "Popular" if avg_popularity > 50 else
                                    "Mixed" if avg_popularity > 30 else
                                    "Underground/Niche"
                },
                "era_distribution": {
                    "year_range": year_range,
                    "earliest": min(release_years) if release_years else None,
                    "latest": max(release_years) if release_years else None,
                    "interpretation": "Multi-era" if year_range > 20 else
                                    "Modern" if (min(release_years) > 2010 if release_years else False) else
                                    "Recent-focused"
                },
                "tracks": track_info
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_top_artists_from_collection":
            songs = arguments["songs"]
            top_n = arguments.get("top_n", 10)
            
            artist_count = {}
            artist_songs = {}
            errors = []
            
            for song_data in songs:
                song_name = song_data["song_name"]
                artist_name = song_data.get("artist_name", "")
                
                # Build search query
                query = song_name
                if artist_name:
                    query += f" artist:{artist_name}"
                
                # Search for the song - doesn't require user auth
                search_results = _sp(require_user_auth=False).search(q=query, type="track", limit=1)
                tracks = search_results["tracks"]["items"]
                
                if not tracks:
                    errors.append(f"Not found: {query}")
                    continue
                
                track = tracks[0]
                
                # Count each artist
                for artist in track["artists"]:
                    artist_name = artist["name"]
                    artist_count[artist_name] = artist_count.get(artist_name, 0) + 1
                    
                    if artist_name not in artist_songs:
                        artist_songs[artist_name] = []
                    artist_songs[artist_name].append(track["name"])
            
            # Sort by frequency
            sorted_artists = sorted(
                artist_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n]
            
            total_songs = sum(artist_count.values())
            
            top_artists = []
            for artist_name, count in sorted_artists:
                percentage = (count / total_songs * 100) if total_songs > 0 else 0
                top_artists.append({
                    "artist": artist_name,
                    "song_count": count,
                    "percentage": round(percentage, 1),
                    "songs": artist_songs[artist_name]
                })
            
            result = {
                "summary": {
                    "total_songs_analyzed": len(songs) - len(errors),
                    "unique_artists": len(artist_count),
                    "top_artist": sorted_artists[0][0] if sorted_artists else None,
                    "errors": errors if errors else None
                },
                "top_artists": top_artists,
                "distribution_type": "Focused" if top_artists and top_artists[0]["percentage"] > 40 else
                                   "Balanced" if len(set(artist_count.values())) > len(artist_count) * 0.5 else
                                   "Varied"
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "analyze_genres_in_collection":
            songs = arguments["songs"]
            
            genre_count = {}
            artist_genres_map = {}
            track_info = []
            errors = []
            
            for song_data in songs:
                song_name = song_data["song_name"]
                artist_name = song_data.get("artist_name", "")
                
                # Build search query
                query = song_name
                if artist_name:
                    query += f" artist:{artist_name}"
                
                # Search for the song - doesn't require user auth
                search_results = _sp(require_user_auth=False).search(q=query, type="track", limit=1)
                tracks = search_results["tracks"]["items"]
                
                if not tracks:
                    errors.append(f"Not found: {query}")
                    continue
                
                track = tracks[0]
                track_genres = []
                
                # Get genres from all artists - doesn't require user auth
                for artist in track["artists"]:
                    artist_name_key = artist["name"]
                    
                    # Cache artist info to avoid duplicate API calls
                    if artist_name_key not in artist_genres_map:
                        try:
                            artist_info = _sp(require_user_auth=False).artist(artist["id"])
                            artist_genres_map[artist_name_key] = artist_info["genres"]
                        except:
                            artist_genres_map[artist_name_key] = []
                    
                    artist_genres = artist_genres_map[artist_name_key]
                    track_genres.extend(artist_genres)
                    
                    # Count genres
                    for genre in artist_genres:
                        genre_count[genre] = genre_count.get(genre, 0) + 1
                
                track_info.append({
                    "name": track["name"],
                    "artists": [a["name"] for a in track["artists"]],
                    "genres": list(set(track_genres)) if track_genres else ["Unknown"]
                })
            
            # Sort genres by frequency
            sorted_genres = sorted(
                genre_count.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Calculate genre diversity
            total_genre_tags = sum(genre_count.values())
            unique_genres = len(genre_count)
            
            # Top genres with percentages
            top_genres = []
            for genre, count in sorted_genres[:15]:
                percentage = (count / total_genre_tags * 100) if total_genre_tags > 0 else 0
                top_genres.append({
                    "genre": genre,
                    "count": count,
                    "percentage": round(percentage, 1)
                })
            
            # Determine dominant style
            if sorted_genres:
                top_genre = sorted_genres[0][0]
                if "pop" in top_genre:
                    dominant_style = "Pop-oriented"
                elif "rock" in top_genre:
                    dominant_style = "Rock-focused"
                elif "hip hop" in top_genre or "rap" in top_genre:
                    dominant_style = "Hip-Hop/Rap"
                elif "electronic" in top_genre or "edm" in top_genre:
                    dominant_style = "Electronic"
                elif "indie" in top_genre or "alternative" in top_genre:
                    dominant_style = "Indie/Alternative"
                elif "r&b" in top_genre or "soul" in top_genre:
                    dominant_style = "R&B/Soul"
                elif "country" in top_genre:
                    dominant_style = "Country"
                elif "jazz" in top_genre:
                    dominant_style = "Jazz"
                elif "classical" in top_genre:
                    dominant_style = "Classical"
                else:
                    dominant_style = top_genre.title()
            else:
                dominant_style = "Unknown"
            
            result = {
                "summary": {
                    "total_songs_analyzed": len(track_info),
                    "unique_genres": unique_genres,
                    "dominant_style": dominant_style,
                    "genre_diversity": "Very Diverse" if unique_genres > 20 else
                                     "Diverse" if unique_genres > 10 else
                                     "Moderately Diverse" if unique_genres > 5 else
                                     "Limited",
                    "errors": errors if errors else None
                },
                "top_genres": top_genres,
                "genre_distribution": {
                    "total_genre_tags": total_genre_tags,
                    "average_genres_per_song": round(total_genre_tags / len(track_info), 1) if track_info else 0
                },
                "tracks_with_genres": track_info
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "create_playlist":
            playlist_name = arguments["playlist_name"]
            songs = arguments["songs"]
            description = arguments.get("description", "")
            public = arguments.get("public", False)

            # Get current user ID - requires user auth
            user = _sp(require_user_auth=True).current_user()
            user_id = user["id"]

            # Create the playlist - requires user auth
            playlist = _sp(require_user_auth=True).user_playlist_create(
                user=user_id,
                name=playlist_name,
                public=public,
                description=description
            )

            # Search and collect track URIs
            track_uris = []
            found_songs = []
            not_found = []

            for song_data in songs:
                song_name = song_data["song_name"]
                artist_name = song_data.get("artist_name", "")

                # Build search query
                query = song_name
                if artist_name:
                    query += f" artist:{artist_name}"

                # Search for the song - doesn't require user auth
                search_results = _sp(require_user_auth=False).search(q=query, type="track", limit=1)
                tracks = search_results["tracks"]["items"]

                if tracks:
                    track = tracks[0]
                    track_uris.append(track["uri"])
                    found_songs.append({
                        "name": track["name"],
                        "artists": [a["name"] for a in track["artists"]]
                    })
                else:
                    not_found.append(query)

                # Add tracks to playlist in batches of 100 (Spotify limit) - requires user auth
                for i in range(0, len(track_uris), 100):
                    batch = track_uris[i:i+100]
                    _sp(require_user_auth=True).playlist_add_items(playlist["id"], batch)

            result = {
                "success": True,
                "playlist": {
                    "id": playlist["id"],
                    "name": playlist["name"],
                    "url": playlist["external_urls"]["spotify"],
                    "public": public
                },
                "summary": {
                    "total_requested": len(songs),
                    "songs_added": len(track_uris),
                    "not_found": len(not_found)
                },
                "added_songs": found_songs,
                "not_found_queries": not_found if not_found else None
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "generate_balanced_playlist":
            songs = arguments["songs"]
            target_size = arguments.get("target_size", 30)
            balance_criteria = arguments.get("balance_criteria", "genre")
            playlist_name = arguments.get("playlist_name")

            # First, analyze the collection to understand distribution
            track_data = []
            errors = []

            for song_data in songs:
                song_name = song_data["song_name"]
                artist_name = song_data.get("artist_name", "")

                query = song_name
                if artist_name:
                    query += f" artist:{artist_name}"

                # Search doesn't require user auth
                search_results = _sp(require_user_auth=False).search(q=query, type="track", limit=1)
                tracks = search_results["tracks"]["items"]

                if not tracks:
                    errors.append(f"Not found: {query}")
                    continue

                track = tracks[0]

                # Get artist info for genres - doesn't require user auth
                genres = []
                for artist in track["artists"]:
                    try:
                        artist_info = _sp(require_user_auth=False).artist(artist["id"])
                        genres.extend(artist_info["genres"])
                    except:
                        pass

                # Get release year
                release_date = track["album"]["release_date"]
                year = int(release_date.split("-")[0]) if release_date else None

                track_data.append({
                    "track": track,
                    "genres": list(set(genres)),
                    "year": year,
                    "artists": [a["name"] for a in track["artists"]]
                })

            # Balance based on criteria
            selected_tracks = []

            if balance_criteria == "genre":
                # Group by genre
                genre_groups = {}
                for item in track_data:
                    for genre in item["genres"] if item["genres"] else ["Unknown"]:
                        if genre not in genre_groups:
                            genre_groups[genre] = []
                        genre_groups[genre].append(item)

                # Select evenly from each genre
                import random
                genres_list = list(genre_groups.keys())
                random.shuffle(genres_list)

                idx = 0
                while len(selected_tracks) < min(target_size, len(track_data)):
                    genre = genres_list[idx % len(genres_list)]
                    if genre_groups[genre]:
                        item = genre_groups[genre].pop(0)
                        if item not in selected_tracks:
                            selected_tracks.append(item)
                    idx += 1

            elif balance_criteria == "artist":
                # Ensure diversity of artists
                artist_count = {}
                import random
                shuffled = track_data.copy()
                random.shuffle(shuffled)

                for item in shuffled:
                    if len(selected_tracks) >= target_size:
                        break
                    artist_key = tuple(sorted(item["artists"]))
                    if artist_count.get(artist_key, 0) < 2:  # Max 2 per artist
                        selected_tracks.append(item)
                        artist_count[artist_key] = artist_count.get(artist_key, 0) + 1

            elif balance_criteria == "era":
                # Balance by decade
                decade_groups = {}
                for item in track_data:
                    if item["year"]:
                        decade = (item["year"] // 10) * 10
                        if decade not in decade_groups:
                            decade_groups[decade] = []
                        decade_groups[decade].append(item)

                import random
                decades_list = sorted(decade_groups.keys())

                idx = 0
                while len(selected_tracks) < min(target_size, len(track_data)):
                    if not decades_list:
                        break
                    decade = decades_list[idx % len(decades_list)]
                    if decade_groups[decade]:
                        item = decade_groups[decade].pop(0)
                        selected_tracks.append(item)
                    idx += 1

            # Prepare result
            balanced_songs = []
            for item in selected_tracks:
                track = item["track"]
                balanced_songs.append({
                    "name": track["name"],
                    "artists": [a["name"] for a in track["artists"]],
                    "genres": item["genres"],
                    "year": item["year"],
                    "id": track["id"],
                    "uri": track["uri"]
                })

            result = {
                "summary": {
                    "balance_criteria": balance_criteria,
                    "source_songs": len(track_data),
                    "selected_songs": len(selected_tracks),
                    "target_size": target_size
                },
                "balanced_selection": balanced_songs
            }

            # Create playlist if name provided - requires user auth
            if playlist_name:
                user = _sp(require_user_auth=True).current_user()
                playlist = _sp(require_user_auth=True).user_playlist_create(
                    user=user["id"],
                    name=playlist_name,
                    public=False,
                    description=f"Balanced by {balance_criteria}"
                )

                track_uris = [item["track"]["uri"] for item in selected_tracks]
                for i in range(0, len(track_uris), 100):
                    batch = track_uris[i:i+100]
                    _sp(require_user_auth=True).playlist_add_items(playlist["id"], batch)

                result["playlist_created"] = {
                    "id": playlist["id"],
                    "name": playlist["name"],
                    "url": playlist["external_urls"]["spotify"]
                }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "compare_to_my_taste":
            songs = arguments["songs"]

            # Get user's top tracks and artists - requires user auth
            top_tracks = _sp(require_user_auth=True).current_user_top_tracks(limit=50, time_range="medium_term")
            top_artists = _sp(require_user_auth=True).current_user_top_artists(limit=50, time_range="medium_term")

            # Extract user's favorite artists and genres
            user_artists = set([artist["name"].lower() for artist in top_artists["items"]])
            user_genres = set()
            for artist in top_artists["items"]:
                user_genres.update(artist["genres"])

            # Extract user's top track names for matching
            user_tracks = set([track["name"].lower() for track in top_tracks["items"]])

            # Analyze the input collection
            matching_tracks = []
            matching_artists = []
            non_matching_tracks = []
            collection_artists = set()
            collection_genres = set()
            errors = []

            for song_data in songs:
                song_name = song_data["song_name"]
                artist_name = song_data.get("artist_name", "")

                # Build search query
                query = song_name
                if artist_name:
                    query += f" artist:{artist_name}"

                # Search for the song - doesn't require user auth
                search_results = _sp(require_user_auth=False).search(q=query, type="track", limit=1)
                tracks = search_results["tracks"]["items"]

                if not tracks:
                    errors.append(f"Not found: {query}")
                    continue

                track = tracks[0]
                track_artists = [a["name"] for a in track["artists"]]

                # Check if track is in user's top tracks
                is_favorite_track = track["name"].lower() in user_tracks

                # Check if artist is in user's top artists
                is_favorite_artist = any(a.lower() in user_artists for a in track_artists)

                # Get genres for this track - doesn't require user auth
                track_genres = []
                for artist in track["artists"]:
                    try:
                        artist_info = _sp(require_user_auth=False).artist(artist["id"])
                        track_genres.extend(artist_info["genres"])
                    except:
                        pass

                collection_genres.update(track_genres)
                for artist in track_artists:
                    collection_artists.add(artist.lower())

                song_info = {
                    "name": track["name"],
                    "artists": track_artists,
                    "is_favorite_track": is_favorite_track,
                    "is_favorite_artist": is_favorite_artist,
                    "genres": list(set(track_genres))
                }

                if is_favorite_track or is_favorite_artist:
                    if is_favorite_track:
                        matching_tracks.append(song_info)
                    if is_favorite_artist:
                        matching_artists.append(song_info)
                else:
                    non_matching_tracks.append(song_info)

            # Calculate overlaps
            artist_overlap = len(collection_artists.intersection(user_artists))
            genre_overlap = len(collection_genres.intersection(user_genres))

            # Determine taste alignment
            total_analyzed = len(matching_tracks) + len(matching_artists) + len(non_matching_tracks)
            match_percentage = ((len(matching_tracks) + len(matching_artists)) / total_analyzed * 100) if total_analyzed > 0 else 0

            if match_percentage > 50:
                alignment = "Strong Match - This collection aligns well with your taste!"
            elif match_percentage > 25:
                alignment = "Moderate Match - Some overlap with your preferences"
            else:
                alignment = "Low Match - This collection explores different territory"

            # Find missing genres from user's taste
            missing_genres = list(user_genres - collection_genres)[:5]
            new_genres = list(collection_genres - user_genres)[:5]

            result = {
                "summary": {
                    "alignment": alignment,
                    "match_percentage": round(match_percentage, 1),
                    "total_analyzed": total_analyzed,
                    "errors": errors if errors else None
                },
                "matches": {
                    "favorite_tracks_count": len(matching_tracks),
                    "favorite_artists_count": len(matching_artists),
                    "favorite_tracks": matching_tracks[:5],
                    "favorite_artists": matching_artists[:5]
                },
                "overlaps": {
                    "artist_overlap": f"{artist_overlap} artists",
                    "genre_overlap": f"{genre_overlap} genres"
                },
                "insights": {
                    "missing_from_your_taste": missing_genres,
                    "new_genres_in_collection": new_genres,
                    "songs_to_explore": [
                        {"name": t["name"], "artists": t["artists"]}
                        for t in non_matching_tracks[:5]
                    ]
                }
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "find_whats_missing":
            songs = arguments["songs"]

            # Get ALL user's saved tracks (may require pagination) - requires user auth
            saved_tracks_set = set()
            offset = 0
            limit = 50

            while True:
                saved = _sp(require_user_auth=True).current_user_saved_tracks(limit=limit, offset=offset)
                if not saved["items"]:
                    break

                for item in saved["items"]:
                    track = item["track"]
                    # Create a unique identifier for the track
                    saved_tracks_set.add(track["id"])

                offset += limit
                if len(saved["items"]) < limit:
                    break  # No more tracks

            # Check which songs from the collection are missing
            missing_songs = []
            already_saved = []
            errors = []

            for song_data in songs:
                song_name = song_data["song_name"]
                artist_name = song_data.get("artist_name", "")

                # Build search query
                query = song_name
                if artist_name:
                    query += f" artist:{artist_name}"

                # Search for the song - doesn't require user auth
                search_results = _sp(require_user_auth=False).search(q=query, type="track", limit=1)
                tracks = search_results["tracks"]["items"]

                if not tracks:
                    errors.append(f"Not found: {query}")
                    continue

                track = tracks[0]

                song_info = {
                    "name": track["name"],
                    "artists": [a["name"] for a in track["artists"]],
                    "id": track["id"],
                    "uri": track["uri"],
                    "url": track["external_urls"]["spotify"],
                    "popularity": track["popularity"]
                }

                # Check if it's in user's saved tracks
                if track["id"] in saved_tracks_set:
                    already_saved.append(song_info)
                else:
                    missing_songs.append(song_info)

            result = {
                "summary": {
                    "total_songs_checked": len(songs) - len(errors),
                    "missing_from_library": len(missing_songs),
                    "already_saved": len(already_saved),
                    "missing_percentage": round((len(missing_songs) / (len(missing_songs) + len(already_saved)) * 100), 1) if (len(missing_songs) + len(already_saved)) > 0 else 0,
                    "errors": errors if errors else None
                },
                "missing_songs": missing_songs,
                "already_saved_songs": already_saved
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
