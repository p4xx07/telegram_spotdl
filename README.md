# Spotify Telegram Downloader Bot

A Telegram bot that listens for Spotify track links and downloads them using [SpotDL](https://spotdl.github.io/). Downloads are sent to a local folder and organized by artist/title.

## Features

- Detects Spotify track links in Telegram chats.
- Downloads tracks via `spotdl` (with YouTube fallback).
- Buffered progress messages sent to Telegram (avoids spamming the chat).
- Uses environment variables for credentials; secure and configurable.
- Works in Docker and Docker Compose for easy deployment.

## Requirements

- Docker & Docker Compose
- Telegram bot token
- Spotify Developer account credentials (Client ID & Secret)

## Environment Variables

Set in `docker-compose.yml`:

```
TELEGRAM_TOKEN="your_telegram_bot_token"
SPOTIFY_CLIENT_ID="your_spotify_client_id"
SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"
```

## Setup

1. Clone the repository:

```
git clone <repo_url>
cd <repo_folder>
```

2. Build the Docker image:

```
docker-compose build
```

3. Start the bot:

```
docker-compose up -d
```


4. Music downloads will appear in `./music`.

## Bot Usage

- Add the bot to your Telegram chat.
- Send a Spotify track link, for example:


```
https://open.spotify.com/track/xxxxxxxxxxxx
```

- The bot will buffer download progress and notify when complete.


## Notes

- The bot auto-generates a SpotDL config from the Spotify ENV variables.
- You can adjust buffering interval by changing `BUFFER_TIME` in `bot.py`.
