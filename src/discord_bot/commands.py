from discord.ext import commands
import logging
from .embeds import build_beatmapset_embed


def register_commands(bot: commands.Bot, osu_client, monitor) -> None:

    @bot.command(name="beatmap")
    async def beatmap(ctx: commands.Context, beatmapset_id: int):
        try:
            data = await osu_client.get_beatmap(beatmapset_id)
            embed = build_beatmapset_embed(data)

            await ctx.send(embed=embed)

        except Exception:
            await ctx.send(
                "Не удалось получить сетку. "
                "Проверь ID и попробуй позже."
            )


    @bot.command(name="check")
    async def check(ctx, limit: int = 10):
        limit = max(1, min(limit, 15))

        await ctx.send(f"Проверяю карты. Лимит: {limit}")

        try:
            sent = await monitor.check_beatmapsets(limit=limit)

            await ctx.send(
                f"Проверка завершена. Отправлено сетов: {sent}"
            )

        except Exception:
            logging.exception("Ошибка ручной проверки")
            await ctx.send("При проверке произошла ошибка.")


