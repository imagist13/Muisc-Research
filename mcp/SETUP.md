# 🛠️ Setup Guide

Complete step-by-step instructions for setting up your MCP music server.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Spotify Configuration](#spotify-configuration)
4. [Claude Desktop Configuration](#claude-desktop-configuration)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, make sure you have:

### Required Software

- **Python 3.10 or higher**
  - Check: `python --version` or `python3 --version`
  - Download: [python.org/downloads](https://python.org/downloads)

- **pip** (Python package manager)
  - Usually comes with Python
  - Check: `pip --version` or `pip3 --version`

- **Claude Desktop**
  - Download: [claude.ai/download](https://claude.ai/download)
  - Make sure it's installed and you can open it

### Recommended (but optional)

- **Git** - for cloning the repository
- **Code editor** - VS Code, PyCharm, or any text editor
- **Terminal familiarity** - basic command line skills

---

## Installation

### Step 1: Get the Code

**Option A: Clone with Git (recommended)**

```bash
git clone <your-repo-url>
cd workshop-music-mcp
```

**Option B: Download ZIP**

1. Download the ZIP from GitHub
2. Extract it
3. Open terminal in that folder

### Step 2: Install Python Dependencies

```bash
# Make sure you're in the project directory
pip install -r requirements.txt

# Or if you need to use pip3:
pip3 install -r requirements.txt
```

This installs:
- `spotipy` - Spotify API client
- `mcp` - Model Context Protocol SDK
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

**Expected output:**
```
Successfully installed spotipy-2.23.0 mcp-1.0.0 pydantic-2.5.0 python-dotenv-1.0.0
```

---

## Spotify Configuration

### Step 1: Create a Spotify Developer Account

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account (free is fine!)
3. If prompted, accept the terms of service

### Step 2: Create an App

1. Click **"Create app"** button
2. Fill in the form:
   - **App name**: `MCP Music Server` (or any name you like)
   - **App description**: `MCP server for Claude`
   - **Redirect URI**: `http://localhost:8888/callback` ⚠️ **Important!**
   - **Web API**: ✅ Check this box
3. Click **"Save"**

### Step 3: Get Your Credentials

1. You'll see your new app in the dashboard
2. Click on it to open
3. Click **"Settings"** button
4. You'll see:
   - **Client ID** - A long string of letters/numbers
   - **Client Secret** - Click "View client secret" to reveal it

**⚠️ Keep these secret!** Don't share them or commit them to git.

### Step 4: Create .env File

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file
# On macOS/Linux: nano .env
# On Windows: notepad .env
# Or use any text editor
```

Paste your credentials:

```env
SPOTIFY_CLIENT_ID=your_actual_client_id_here
SPOTIFY_CLIENT_SECRET=your_actual_client_secret_here
```

**Example** (not real credentials):
```env
SPOTIFY_CLIENT_ID=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
SPOTIFY_CLIENT_SECRET=z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4
```

Save and close the file.

---

## Claude Desktop Configuration

### Step 1: Find Your Config File

The config file location depends on your operating system:

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Get the Absolute Path to Your Script

You need the **full path** to `music_server_updated_2025.py`.

**macOS/Linux:**
```bash
# Navigate to your project directory, then:
echo "$(pwd)/music_server_updated_2025.py"
```

**Windows (PowerShell):**
```powershell
cd path\to\workshop-music-mcp
Write-Output "$PWD\music_server_updated_2025.py"
```

**Windows (Command Prompt):**
```cmd
cd path\to\workshop-music-mcp
echo %cd%\music_server_updated_2025.py
```

Copy this path - you'll need it in the next step!

### Step 3: Edit the Config File

Open `claude_desktop_config.json` in a text editor.

**If the file is empty or doesn't exist**, create it with this content:

```json
{
  "mcpServers": {
    "music": {
      "command": "python",
      "args": [
        "/absolute/path/to/music_server_updated_2025.py"
      ],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret_here"
      }
    }
  }
}
```

**If the file already has other servers**, add the music server to the existing `mcpServers` object:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "music": {
      "command": "python",
      "args": [
        "/absolute/path/to/music_server_updated_2025.py"
      ],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret_here"
      }
    }
  }
}
```

**⚠️ Important:**
- Replace `/absolute/path/to/` with your actual path from Step 2
- Replace `your_client_id_here` and `your_client_secret_here` with your Spotify credentials
- On Windows, use double backslashes: `C:\\Users\\YourName\\...`
- Make sure the JSON is valid (no trailing commas, matching braces)

**Example (macOS):**
```json
{
  "mcpServers": {
    "music": {
      "command": "python3",
      "args": [
        "/Users/jane/projects/workshop-music-mcp/music_server_updated_2025.py"
      ],
      "env": {
        "SPOTIFY_CLIENT_ID": "a1b2c3d4e5f6g7h8",
        "SPOTIFY_CLIENT_SECRET": "z9y8x7w6v5u4t3s2"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

**This is crucial!** Claude Desktop only reads the config on startup.

1. Quit Claude Desktop completely (Cmd+Q on Mac, or close from system tray)
2. Wait a few seconds
3. Open Claude Desktop again

---

## Testing

### Step 1: Verify Connection

Open a new chat in Claude and type:

```
Can you search for songs by Taylor Swift?
```

If everything is set up correctly, Claude will:
1. Use the `search_tracks` tool
2. Connect to Spotify
3. Return a list of Taylor Swift songs

### Step 2: Test Other Features

Try these commands:

**Search:**
```
Find me some upbeat electronic music
```

**Recommendations:**
```
I love the song "Mr. Brightside" by The Killers. 
Can you recommend similar songs?
```

**Audio Analysis:**
```
What are the audio features of "Bohemian Rhapsody" by Queen?
```

### Step 3: Check for Errors

If Claude says it can't use the music tools:
- Make sure you restarted Claude Desktop
- Check that the path in the config is absolute (starts with `/` or `C:\`)
- Verify your Spotify credentials are correct

---

## Troubleshooting

### Common Issues

**"Claude doesn't see the music tools"**

1. Check that Claude Desktop was restarted after config changes
2. Verify the config file path is correct for your OS
3. Make sure the JSON syntax is valid (use [jsonlint.com](https://jsonlint.com/))
4. Check that the path to the Python script is absolute, not relative

**"ModuleNotFoundError: No module named 'spotipy'"**

```bash
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

**"Can't connect to Spotify"**

1. Check your `.env` file has the correct credentials
2. Verify you added the redirect URI `http://localhost:8888/callback` in Spotify dashboard
3. Make sure there are no extra spaces in your credentials

**"Invalid redirect URI"**

The redirect URI in your Spotify app settings must **exactly** match:
```
http://localhost:8888/callback
```
- No trailing slash
- Lowercase "http"
- Port 8888

**Python command not found**

Try `python3` instead of `python` in the config:
```json
"command": "python3"
```

### Still Having Issues?

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more detailed help, or:

1. Check the Claude Desktop logs
2. Ask in the AI@Princeton Discord
3. Open an issue on GitHub

---

## Next Steps

✅ **Server is working!** Now what?

- Try all the example queries in [README.md](README.md)
- Read [WORKSHOP_GUIDE.md](WORKSHOP_GUIDE.md) to learn how it works
- Build your own tools using [CONTRIBUTING.md](CONTRIBUTING.md)
- Join the 48-hour challenge!

---

**Questions?** Reach out during the workshop or on Discord!
