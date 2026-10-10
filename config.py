import os 

from dotenv import load_dotenv

load_dotenv()

OSU_CLIENT_ID = os.getenv("OSU_CLIENT_ID")
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))

DATABASE_URL = str(os.getenv("DATABASE_URL"))

def validate_config() -> None:
    required ={
        "OSU_CLIENT_ID": OSU_CLIENT_ID,
        "OSU_CLIENT_SECRET": OSU_CLIENT_SECRET,
        "DISCORD_TOKEN": DISCORD_TOKEN
    }

    missing = [
        name for name, value in required.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            f"Не заданы переменные окружения: {', '.join(missing)}"
        )