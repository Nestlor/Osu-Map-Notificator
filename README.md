# osu! Map Notifier

A simple pet-project for self-purpose use that monitors osu! beatmapsets and sends notifications to configured Discord channels.
its mostly spaghetti code so dont expect much from it

invite URL - https://discord.com/oauth2/authorize?client_id=1558110914002288730&permissions=4503737066704192&integration_type=0&scope=bot+applications.commands

## Features

- Automatically monitors new and updated beatmapsets(with interval that you can change yourself).
- Sends notifications to configured Discord channels.
- Supports independent channel settings for each Discord server.
- Retrieves beatmapset information by ID.
- Supports manual map checks.
- Stores data and server settings in SQLite.
- Logs application events and errors.

## Commands

| Command | Description |
|---|---|
| `/beatmap <beatmapset_id>` | Get beatmapset information |
| `/setchannel <channel>` | Configure the notification channel |
| `!check [limit]` | Manually check beatmapsets |
| `!beatmap <beatmapset_id>` | Get beatmapset information |
| `!setchannel <channel>` | Configure the notification channel |

## Tech Stack

- Python
- discord.py
- osu! API v2
- httpx
- SQLAlchemy
- SQLite
- Alembic

## Installation

```bash
git clone <repository-url>
cd osu_map_notificator

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_discord_bot_token
OSU_CLIENT_ID=your_osu_client_id
OSU_CLIENT_SECRET=your_osu_client_secret
```

Apply database migrations and start the bot:

```bash
alembic upgrade head
python -m main
```

## Requirements

A Discord application and osu! API credentials are required. Configure the bot's permissions and synchronize its Slash commands before use.
