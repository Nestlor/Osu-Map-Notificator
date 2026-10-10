import asyncio
import logging

import discord
import httpx

from components.database.repository import BeatmapRepository
from discord_bot.embeds import build_beatmapset_embed
from components.osu.client import OsuClient
from config import CHECK_INTERVAL

logger = logging.getLogger(__name__)


class BeatmapMonitor:
    def __init__(self, osu_client: OsuClient, repository: BeatmapRepository, bot: discord.Client):
        self.osu_client = osu_client
        self.repository = repository
        self.bot = bot
        self.interval = CHECK_INTERVAL

        logger.info(
            "BeatmapMonitor инициализирован, интервал: %s сек.",
            self.interval,
        )

    async def publish_pending(self) -> None:
        logger.info("Начало отправки ожидающих сетов")

        guild_settings = await self.repository.get_all_guild_settings()
        pending = await self.repository.get_pending()

        logger.info("Настроено каналов: %s", len(guild_settings))
        logger.info("Ожидающих отправки сетов: %s", len(pending))

        if not guild_settings:
            logger.warning("Нет настроенных каналов для уведомлений")
            return

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

                for settings in guild_settings:
                    try:
                        channel = self.bot.get_channel(settings.channel_id)

                        if channel is None:
                            channel = await self.bot.fetch_channel(
                                settings.channel_id
                            )

                        await channel.send(
                            content="New map detected",
                            embed=embed
                        )

                        logger.info(
                            "Сет %s отправлен в канал %s",
                            beatmapset.id,
                            settings.channel_id,
                        )
                    except (httpx.HTTPError, discord.HTTPException):
                        logger.exception(
                            "Не удалось отправить сет %s в канал %s",
                            beatmapset.id,
                            settings.channel_id
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



    async def check_beatmapsets(self, guild_id: int, limit: int = 10, ) -> int:
        limit = max(1, min(limit, 15))

        logger.info(
            "Запущена ручная проверка для сервера %s. Лимит: %s",
            guild_id,
            limit,
        )

        settings = await self.repository.get_guild_settings(guild_id)

        if settings is None or settings.channel_id is None:
            logger.warning(
                "Для сервера %s не настроен канал уведомлений",
                guild_id,
            )
            return 0

        try:
            channel = self.bot.get_channel(settings.channel_id)

            if channel is None:
                channel = await self.bot.fetch_channel(
                    settings.channel_id
                )
        except discord.HTTPException:
            logger.exception(
                "Не удалось получить канал %s",
                settings.channel_id,
            )
            return 0

        beatmapsets = (
            await self.osu_client.get_ranked_and_qualified_beatmapsets()
        )

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
            "Сетов osu!standard: %s. Выбрано: %s",
            len(standard_beatmapsets),
            len(selected),
        )

        sent = 0

        for beatmapset in selected:
            try:
                data = await self.osu_client.get_beatmap(
                    beatmapset["id"]
                )

                data["beatmaps"] = [
                    beatmap
                    for beatmap in data.get("beatmaps", [])
                    if beatmap.get("mode") == "osu"
                    or beatmap.get("mode_int") == 0
                ]

                if not data["beatmaps"]:
                    continue

                embed = build_beatmapset_embed(data)

                await channel.send(
                    content="New test map detected",
                    embed=embed,
                )

                sent += 1

                logger.info(
                    "Тестовый сет %s отправлен в канал %s: %s",
                    beatmapset["id"],
                    settings.channel_id,
                    data.get("title"),
                )

            except (httpx.HTTPError, discord.HTTPException):
                logger.exception(
                    "Не удалось отправить сет %s",
                    beatmapset["id"],
                )

        logger.info(
            "Ручная проверка для сервера %s завершена. Отправлено: %s",
            guild_id,
            sent,
        )

        return sent