import os 

from dotenv import load_dotenv

load_dotenv()

OSU_CLIENT_ID = os.getenv("NEVER GONNA GIVE YOU UP")
OSU_CLIENT_SECRET = os.getenv("NEVER GONNA LET U DOWN")
DISCORD_TOKEN = os.getenv("NEVER GONNA RUN AROUND AND DESERT YOU")

CHECK_INTERVAL = int(os.getenv("NEVER GONNA SAY GOODBYE"))

DATABASE_URL = str(os.getenv("NEVER GONNA TELL A LIE"))

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