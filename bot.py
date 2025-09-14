import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp as ytdl
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import imageio_ffmpeg as ffmpeg  # Para FFmpeg sem sudo

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Créditos
BOT_VERSION = "1.1"
BOT_AUTHOR = "Kennedy"

# Spotify client
sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-read-playback-state,user-modify-playback-state"
))

# YTDL options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extract_flat': 'in_playlist',
    'default_search': 'ytsearch',
}
ytdl_instance = ytdl.YoutubeDL(ytdl_format_options)

# Fila de música
music_queue = {}
is_playing = {}

async def play_next(ctx):
    guild_id = ctx.guild.id
    if music_queue.get(guild_id):
        source = music_queue[guild_id].pop(0)
        voice_client = ctx.voice_client
        if not voice_client:
            voice_channel = ctx.author.voice.channel
            voice_client = await voice_channel.connect()
        voice_client.play(discord.FFmpegPCMAudio(source, executable=ffmpeg.get_ffmpeg_exe()), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
    else:
        is_playing[guild_id] = False

@bot.event
async def on_ready():
    print(f"{bot.user} conectado! Versão {BOT_VERSION} de {BOT_AUTHOR}")
    await bot.change_presence(activity=discord.Game(name="🎵 Tocando músicas"))

# Comando de play
@bot.command(name="play", help="Toca música do YouTube pelo nome")
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        await ctx.send("Você precisa estar em um canal de voz! ❌")
        return
    guild_id = ctx.guild.id
    if guild_id not in music_queue:
        music_queue[guild_id] = []
    if guild_id not in is_playing:
        is_playing[guild_id] = False
    try:
        info = ytdl_instance.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = info['url']
    except Exception:
        await ctx.send("❌ Não foi possível encontrar a música.")
        return

    music_queue[guild_id].append(url)
    await ctx.send(f"✅ Adicionado à fila: **{info['title']}** 🎶")

    if not is_playing[guild_id]:
        is_playing[guild_id] = True
        await play_next(ctx)

# Comando stop
@bot.command(name="stop", help="Para a música e limpa a fila")
async def stop(ctx):
    voice_client = ctx.voice_client
    guild_id = ctx.guild.id
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        music_queue[guild_id] = []
        is_playing[guild_id] = False
        await ctx.send("⏹ Música parada e fila limpa.")

# Comando pause
@bot.command(name="pause", help="Pausa a música atual")
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("⏸ Música pausada.")

# Comando resume
@bot.command(name="resume", help="Resume a música pausada")
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("▶ Música retomada.")

# Comando fila
@bot.command(name="queue", help="Mostra as próximas músicas na fila")
async def queue(ctx):
    guild_id = ctx.guild.id
    queue_list = music_queue.get(guild_id, [])
    if queue_list:
        msg = "\n".join([f"{i+1}. {song}" for i, song in enumerate(queue_list)])
        await ctx.send(f"🎶 Fila atual:\n{msg}")
    else:
        await ctx.send("📭 A fila está vazia.")

bot.run(TOKEN)
