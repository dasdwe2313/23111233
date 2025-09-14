import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import yt_dlp
import asyncio
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # necessário para tocar música

bot = commands.Bot(command_prefix="!", intents=intents)

# Spotify
spotify = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Fila de reprodução
queues = {}

ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'extract_flat': 'in_playlist'
}

# --------------------------
# Eventos
# --------------------------
@bot.event
async def on_ready():
    print(f"Bot logado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)  # IMPORTANTE para comandos funcionarem

# --------------------------
# Comandos de música
# --------------------------
async def play_audio(ctx, url):
    guild_id = ctx.guild.id
    if guild_id not in queues or len(queues[guild_id]) == 0:
        await ctx.send("Fila vazia!")
        return

    voice_client = ctx.guild.voice_client
    if not voice_client or not voice_client.is_connected():
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
        else:
            await ctx.send("Você precisa estar em um canal de voz para tocar música!")
            return

    current = queues[guild_id][0]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(current, download=False)
        url2 = info['url']

    voice_client.play(discord.FFmpegPCMAudio(url2, executable="ffmpeg"), after=lambda e: asyncio.run_coroutine_threadsafe(next_song(ctx), bot.loop))

async def next_song(ctx):
    guild_id = ctx.guild.id
    queues[guild_id].pop(0)
    if len(queues[guild_id]) > 0:
        await play_audio(ctx, queues[guild_id][0])
    else:
        await ctx.send("Fila finalizada!")

@bot.command()
async def play(ctx, *, url):
    guild_id = ctx.guild.id
    if guild_id not in queues:
        queues[guild_id] = []

    queues[guild_id].append(url)
    await ctx.send(f"Adicionado à fila: {url}")

    voice_client = ctx.guild.voice_client
    if not voice_client or not voice_client.is_playing():
        await play_audio(ctx, url)

@bot.command()
async def skip(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Música pulada!")
    else:
        await ctx.send("Nenhuma música tocando!")

@bot.command()
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client:
        queues[ctx.guild.id] = []
        await voice_client.disconnect()
        await ctx.send("Música parada e fila limpa!")
    else:
        await ctx.send("Nenhuma música tocando!")

@bot.command()
async def queue(ctx):
    guild_id = ctx.guild.id
    if guild_id not in queues or len(queues[guild_id]) == 0:
        await ctx.send("Fila vazia!")
    else:
        msg = "\n".join([f"{i+1}. {song}" for i, song in enumerate(queues[guild_id])])
        await ctx.send(f"Fila atual:\n{msg}")

# --------------------------
# Comando simples de teste
# --------------------------
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(TOKEN)
