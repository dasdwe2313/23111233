import os
import discord
from discord.ext import commands

TOKEN = os.getenv("3Ch_x_kjwhG5Z4CpRAck2UDNXHvpBbi1")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

initial_extensions = ['cogs.music']

import asyncio

async def main():
    for ext in initial_extensions:
        await bot.load_extension(ext)
    await bot.start(TOKEN)

asyncio.run(main())
