import asyncio
import logging
from pathlib import Path

import asyncio
import logging 
from src.config import (
    DISCORD_TOKEN,
    OSU_CLIENT_ID,
    OSU_CLIENT_SECRET,
    validate_config,
)

from src.components.database.connection import create_tables, engine
from src.components.database.repository import BeatmapRepository
from src.discord_bot.bot import create_bot
from src.components.osu.auth import OsuAuth
from src.components.osu.client import OsuClient
from src.components.tracker.monitor import BeatmapMonitor
from src.discord_bot.commands import register_commands
 
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "bot.log", encoding="utf-8"),
    ],
)


async def main() -> None:
    validate_config()

    await create_tables()

    osu_auth = OsuAuth(
        client_id=OSU_CLIENT_ID,
        client_secret=OSU_CLIENT_SECRET
    )
    osu_client = OsuClient(osu_auth)
    repository = BeatmapRepository()
    bot = create_bot()

    monitor = BeatmapMonitor(
        osu_client=osu_client,
        repository=repository,
        bot=bot,
    )

    tree = register_commands(bot, osu_client, monitor)

    monitor_task = None

    @bot.event
    async def on_ready():
        nonlocal monitor_task

        logging.info("Discord подключен: %s", bot.user)

        synced = await bot.tree.sync()
        logging.info(
            "Синхронизировано Slash-command: %s",
            len(synced)
        )

        if monitor_task is None:
            logging.warning("Запускаю мониторинг osu!")
            monitor_task = asyncio.create_task(monitor.run())

    try:
        await bot.start(DISCORD_TOKEN)

    finally:
        if monitor_task is not None:
            monitor_task.cancel()

            await asyncio.gather(
                monitor_task,
                return_exceptions=True
            )


        await bot.close()
        await osu_client.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())