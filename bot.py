# bot.py
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import yt_dlp as youtube_dl
import asyncio
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# ===== CONFIGURAÇÕES =====
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# ===== SPOTIFY =====
sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-read-playback-state,user-modify-playback-state"
))

# ===== BOT =====
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ===== YTDLP CONFIG =====
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extract_flat': 'in_playlist',
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -loglevel info'
}

# ===== FILA DE MÚSICAS =====
queues = {}

# ===== FUNÇÕES =====
async def play_next(ctx):
    if queues.get(ctx.guild.id):
        next_url = queues[ctx.guild.id].pop(0)
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        try:
            source = FFmpegPCMAudio(
                next_url,
                executable="/usr/bin/ffmpeg",  # ajuste se FFmpeg estiver em outro path
                **ffmpeg_options
            )
            voice.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        except Exception as e:
            await ctx.send(f"❌ Erro ao tocar música: {e}")
    else:
        await ctx.send("🎵 **Fila finalizada!**")

# ===== COMANDOS =====
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("✅ Conectado ao canal de voz!")
    else:
        await ctx.send("❌ Você precisa estar em um canal de voz.")

@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice:
        await voice.disconnect()
        await ctx.send("👋 Desconectado do canal de voz.")
    else:
        await ctx.send("❌ Não estou em um canal de voz.")

@bot.command()
async def play(ctx, *, query=None):
    if query is None:
        await ctx.send("❌ Você precisa informar uma música ou link.")
        return

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice:
        if ctx.author.voice:
            voice = await ctx.author.voice.channel.connect()
        else:
            await ctx.send("❌ Você precisa estar em um canal de voz.")
            return

    # Buscar no YouTube
    try:
        info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = info['url']
        title = info.get('title', 'Música desconhecida')
    except Exception as e:
        await ctx.send(f"❌ Não consegui encontrar a música. Erro: {e}")
        return

    # Inicializa fila se necessário
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    queues[ctx.guild.id].append(url)
    await ctx.send(f"🎶 **Adicionado à fila:** {title}")

    # Tocar se nada estiver tocando
    if not voice.is_playing():
        await play_next(ctx)

@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.pause()
        await ctx.send("⏸ Música pausada!")
    else:
        await ctx.send("❌ Nenhuma música tocando.")

@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        voice.resume()
        await ctx.send("▶ Música retomada!")
    else:
        await ctx.send("❌ Nenhuma música pausada.")

@bot.command()
async def skip(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("⏭ Música pulada!")
    else:
        await ctx.send("❌ Nenhuma música tocando.")

@bot.command()
async def spotify(ctx, *, query=None):
    if query is None:
        await ctx.send("❌ Informe o nome da música no Spotify.")
        return
    results = sp.search(q=query, type="track", limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        await ctx.send(f"🎧 **Spotify track:** {track['name']} - {track['artists'][0]['name']}\n{track['external_urls']['spotify']}")
    else:
        await ctx.send("❌ Música não encontrada no Spotify.")

# ===== EVENTOS =====
@bot.event
async def on_ready():
    print(f"✅ Logado como {bot.user}")
    for guild in bot.guilds:
        if guild.id not in queues:
            queues[guild.id] = []
    print("🎵 Bot pronto! Kennedy Bot v2.0")

# ===== RODAR BOT =====
bot.run(TOKEN)
