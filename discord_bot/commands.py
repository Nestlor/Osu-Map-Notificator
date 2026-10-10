import discord
from discord import app_commands
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

    @bot.tree.command(
        name="beatmap",
        description="Получить информацию о beatmapset osu!",
    )
    @app_commands.describe(beatmapset_id="ID набора карт")
    async def beatmap_slash(
        interaction: discord.Interaction,
        beatmapset_id: int,
    ):
        await interaction.response.defer()

        try:
            data = await osu_client.get_beatmap(beatmapset_id)
            embed = build_beatmapset_embed(data)

            await interaction.followup.send(embed=embed)

        except Exception:
            logging.exception("Ошибка Slash-команды beatmap")
            await interaction.followup.send(
                "Не удалось получить сет. Проверь ID и попробуй позже."
            )

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @bot.command(name="check")
    async def check(ctx, limit: int = 10):
        limit = max(1, min(limit, 15))

        await ctx.send(f"Проверяю карты. Лимит: {limit}")

        try:
            sent = await monitor.check_beatmapsets(
                guild_id=ctx.guild.id,
                limit=limit,
            )

            await ctx.send(
                f"Проверка завершена. Отправлено сетов: {sent}"
            )

        except Exception:
            logging.exception("Ошибка ручной проверки")
            await ctx.send("При проверке произошла ошибка.")


    @bot.command(name="setchannel")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def set_channel(ctx, channel: discord.TextChannel):
        try:
            await monitor.repository.set_channel(ctx.guild.id, channel.id)

            await ctx.reply(
                f"Канал уведомлений установлен: {channel.mention}"
            )
        except Exception:
            logging.exception("Ошибка при указании канала")
            await ctx.send("Не правильно указан канал")


    @bot.tree.command(
        name="setchannel",
        description="Установить канал уведомлений osu!",
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def set_channel_slash(
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ):
        await monitor.repository.set_channel(
            interaction.guild_id,
            channel.id,
        )

        await interaction.response.send_message(
            f"Канал уведомлений установлен: {channel.mention}",
            ephemeral=True,
        )