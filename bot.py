import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("OTA0MDY2MTc2MDk3ODQ5NDM0.GnBXYm.UesJD5wHakobg8d3howHMuO09lOOaT9F-4JfkQ")
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

initial_extensions = ['cogs.music']
for ext in initial_extensions:
    bot.load_extension(ext)

bot.run(TOKEN)
