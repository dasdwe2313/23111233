import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Carrega variáveis do .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configura intents
intents = discord.Intents.default()
intents.message_content = True  # ESSENCIAL para ler comandos de texto

# Cria o bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Lista de cogs a serem carregados
initial_extensions = ["cogs.music"]

# Evento on_ready
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# Função principal para carregar cogs e iniciar bot
async def main():
    for ext in initial_extensions:
        await bot.load_extension(ext)  # Aqui é onde o cog é carregado
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
