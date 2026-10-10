import discord
from discord.ext import commands
import logging


def create_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
    )


    @bot.event
    async def on_command_error(
        ctx: commands.Context,
        error: commands.CommandError,
    ):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Command Error",
                description=(
                    f"{ctx.author.mention}, попробуй ещё раз "
                    f"через **{error.retry_after:.1f} сек.**"
                ),
                color=discord.Colour.from_rgb(255, 102, 171),
            )

            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url,)

            await ctx.reply(embed=embed, mention_author=False, delete_after=10)

        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Command Error",
                description=(
                    f"{ctx.author.mention}, у тебя недостаточно "
                    "прав для этой команды."
                ),
                color=discord.Colour.from_rgb(255, 102, 171),
            )

            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=embed, mention_author=False, delete_after=10)

        elif isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(
                title="Command Error",
                description="Эту команду можно использовать только на сервере.",
                color=discord.Colour.from_rgb(255, 102, 171),
            )

            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url,)
            await ctx.reply(embed=embed, mention_author=False, delete_after=10)

        elif isinstance(error, commands.CommandNotFound):
            return

        else:
            logging.error(
                "Ошибка команды %s: %r",
                ctx.command,
                error,
                exc_info=(type(error), error, error.__traceback__),
            )

    return bot