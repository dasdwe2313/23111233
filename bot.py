import os
import discord
from discord.ext import commands
from dotenv import load_dotenv  # opcional, útil para testes locais

load_dotenv()  # carrega variáveis de .env se estiver rodando localmente

TOKEN = os.getenv("DISCORD_TOKEN")  # <- aqui está o nome correto da variável!

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
