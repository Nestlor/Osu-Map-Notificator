import asyncio
import logging

import discord
import httpx

from ..database.repository import BeatmapRepository
from discord_bot.embeds import build_beatmapset_embed
from ..osu.client import OsuClient
from config import CHECK_INTERVAL, DISCORD_CHANNEL_ID

logger = logging.getLogger(__name__)


class BeatmapMonitor:
    def __init__(self, osu_client: OsuClient, repository: BeatmapRepository, bot: discord.Client):
        self.osu_client = osu_client
        self.repository = repository
        self.bot = bot
        self.channel_id = DISCORD_CHANNEL_ID
        self.interval = CHECK_INTERVAL

        logger.info(
            "BeatmapMonitor инициализирован. Канал: %s, интервал: %s сек.",
            self.channel_id,
            self.interval,
        )

    async def publish_pending(self) -> None:
        logger.info("Начало отправки ожидающих сетов")

        channel = self.bot.get_channel(self.channel_id)

        if channel is None:
            logger.info("Канал не найден в кэше. Получаю канал через API")
            channel = await self.bot.fetch_channel(self.channel_id)

        pending = await self.repository.get_pending()

        logger.info("Ожидающих отправки сетов: %s", len(pending))

        for beatmapset in pending:
            try:
                data = await self.osu_client.get_beatmap(beatmapset.id)

                data["beatmaps"] = [
                    beatmap
                    for beatmap in data.get("beatmaps", [])
                    if beatmap.get("mode") == "osu"
                    or beatmap.get("mode_int") == 0
                ]

                if not data["beatmaps"]:
                    logger.info(
                        "Сет %s пропущен: нет карт osu!standard",
                        beatmapset.id,
                    )
                    await self.repository.mark_sent(beatmapset.id)
                    continue

                embed = build_beatmapset_embed(data)
                await channel.send(
                    content="New Map detected:",
                    embed=embed
                )

                await self.repository.mark_sent(beatmapset.id)

                logger.info(
                    "Отправлен сет %s: %s",
                    beatmapset.id,
                    data.get("title")
                )

            except (httpx.HTTPError, discord.HTTPException):
                logger.exception(
                    "Не удалось отправить сет %s",
                    beatmapset.id
                )

        logger.info("Отправка ожидающих сетов завершена")

    async def run(self) -> None:
        count = await self.repository.count()

        if count == 0:
            logger.warning("RUN: база пустая, запрашиваю сеты")

            existing = (
                await self.osu_client.get_ranked_and_qualified_beatmapsets()
            )

            logger.warning("RUN: получено сетов: %s", len(existing))

            for data in existing:
                await self.repository.add_if_new(
                    data,
                    notification_status="sent",
                )

        while True:
            try:
                logger.info("Начинаю очередную проверку osu!")

                beatmapsets = (
                    await self.osu_client.get_ranked_and_qualified_beatmapsets()
                )

                logger.info("Получено сетов от osu! API: %s", len(beatmapsets))

                for data in reversed(beatmapsets):
                    await self.repository.add_if_new(
                        data,
                        notification_status="pending",
                    )

                await self.publish_pending()

                logger.info(
                    "Проверка завершена. Следующая через %s сек.",
                    self.interval,
                )

            except Exception:
                logger.exception("Неожиданная ошибка мониторинга")

            await asyncio.sleep(self.interval)

    async def check_beatmapsets(self, limit: int = 10) -> int:
        logger.info("Запущена ручная проверка. Лимит: %s", limit)

        beatmapsets = (
            await self.osu_client.get_ranked_and_qualified_beatmapsets()
        )

        logger.info("Получено сетов для ручной проверки: %s", len(beatmapsets))

        standard_beatmapsets = []

        for beatmapset in beatmapsets:
            standard_maps = [
                beatmap
                for beatmap in beatmapset.get("beatmaps", [])
                if beatmap.get("mode") == "osu"
                or beatmap.get("mode_int") == 0
            ]

            if standard_maps:
                beatmapset["beatmaps"] = standard_maps
                standard_beatmapsets.append(beatmapset)

        selected = standard_beatmapsets[:limit]

        logger.info(
            "Сетов с osu!standard: %s. Выбрано для отправки: %s",
            len(standard_beatmapsets),
            len(selected),
        )

        channel = self.bot.get_channel(self.channel_id)

        if channel is None:
            logger.info("Получаю канал через API")
            channel = await self.bot.fetch_channel(self.channel_id)

        sent = 0

        for beatmapset in selected:
            try:
                data = await self.osu_client.get_beatmap(beatmapset["id"])

                data["beatmaps"] = [
                    beatmap
                    for beatmap in data.get("beatmaps", [])
                    if beatmap.get("mode") == "osu"
                    or beatmap.get("mode_int") == 0
                ]

                if not data["beatmaps"]:
                    logger.warning(
                        "Сет %s пропущен: нет сложностей osu!standard",
                        beatmapset["id"],
                    )
                    continue

                embed = build_beatmapset_embed(data)

                await channel.send(
                    content="🆕 New map detected:",
                    embed=embed,
                )

                sent += 1

                logger.info(
                    "Тестовый сет отправлен: %s — %s",
                    beatmapset["id"],
                    data.get("title"),
                )

            except (httpx.HTTPError, discord.HTTPException):
                logger.exception(
                    "Не удалось отправить сет %s",
                    beatmapset["id"],
                )

        logger.info("Ручная проверка завершена. Отправлено: %s", sent)

        return sent