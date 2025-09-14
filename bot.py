import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="!", intents=commands.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

initial_extensions = ['cogs.music']
for ext in initial_extensions:
    bot.load_extension(ext)

bot.run(TOKEN)
