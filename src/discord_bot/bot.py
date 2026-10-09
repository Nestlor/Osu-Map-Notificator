import discord
from discord.ext import commands


def create_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
    )

    return bot