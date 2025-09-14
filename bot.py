import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import yt_dlp
import ffmpeg
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Carrega variáveis do .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

# Configura intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Configura Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

# Fila de músicas por guilda
music_queues = {}

# Função para tocar música
async def play_music(ctx, url):
    guild_id = ctx.guild.id
    if guild_id not in music_queues or not music_queues[guild_id]:
        await ctx.send("Fila de reprodução vazia!")
        return

    # Pega o próximo item da fila
    current_url = music_queues[guild_id].pop(0)

    # Baixa áudio com yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'outtmpl': 'song.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(current_url, download=True)
        filename = ydl.prepare_filename(info)

    # Toca música no canal de voz
    voice_client = ctx.voice_client
    if not voice_client:
        await ctx.send("Bot não está conectado a um canal de voz!")
        return

    audio_source = discord.FFmpegPCMAudio(source=filename)
    voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(next_song(ctx), bot.loop))

async def next_song(ctx):
    guild_id = ctx.guild.id
    if guild_id in music_queues and music_queues[guild_id]:
        await play_music(ctx, music_queues[guild_id][0])
    else:
        await ctx.voice_client.disconnect()

# Comando de entrar no canal
@bot.command(name="join")
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Conectado ao canal {channel.name}!")
    else:
        await ctx.send("Você não está conectado a nenhum canal de voz!")

# Comando de sair do canal
@bot.command(name="leave")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Desconectado do canal de voz.")
    else:
        await ctx.send("O bot não está conectado a nenhum canal de voz.")

# Comando para adicionar música
@bot.command(name="play")
async def play(ctx, *, url):
    guild_id = ctx.guild.id
    if guild_id not in music_queues:
        music_queues[guild_id] = []

    music_queues[guild_id].append(url)
    await ctx.send(f"Adicionado à fila: {url}")

    # Se o bot não estiver tocando nada, toca a música
    if not ctx.voice_client.is_playing():
        await play_music(ctx, url)

# Evento ready
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}!")

# Start do bot
async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
