# bot.py
import discord
from discord.ext import commands
import asyncio
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

# ================================
# Configurações iniciais
# ================================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Créditos
BOT_AUTHOR = "Kennedy"
BOT_VERSION = "1.1"

# ================================
# Spotify API
# ================================
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# ================================
# YTDL / FFmpeg Config
# ================================
ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'ignoreerrors': True,
    'default_search': 'auto',
}
ffmpeg_opts = {
    'options': '-vn'
}
ytdl = yt_dlp.YoutubeDL(ytdl_opts)

# ================================
# Fila de músicas
# ================================
music_queues = {}

# ================================
# Função de reprodução
# ================================
async def play_next(ctx):
    guild_id = ctx.guild.id
    if guild_id not in music_queues or len(music_queues[guild_id]) == 0:
        await ctx.send("🎵 A fila terminou!")
        return

    # Pega a próxima música
    song = music_queues[guild_id].pop(0)

    # Conecta no canal de voz se não estiver conectado
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Você precisa estar em um canal de voz para reproduzir músicas!")
            return

    # Toca a música
    ctx.voice_client.stop()
    ctx.voice_client.play(
        discord.FFmpegPCMAudio(song['url'], **ffmpeg_opts),
        after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
    )
    await ctx.send(f"▶️ Tocando agora: **{song['title']}**")

# ================================
# Comando play
# ================================
@bot.command()
async def play(ctx, *, query: str):
    guild_id = ctx.guild.id
    if guild_id not in music_queues:
        music_queues[guild_id] = []

    # Busca música
    try:
        if query.startswith("spotify:track:") or "open.spotify.com/track" in query:
            # Spotify
            results = sp.track(query)
            search_query = f"{results['name']} {results['artists'][0]['name']}"
        else:
            # YouTube
            search_query = query

        info = ytdl.extract_info(f"ytsearch:{search_query}", download=False)['entries'][0]
        music_queues[guild_id].append({
            'title': info['title'],
            'url': info['url']
        })

        await ctx.send(f"✅ Música adicionada à fila: **{info['title']}**")

        # Se não estiver tocando, inicia
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await play_next(ctx)
    except Exception as e:
        await ctx.send(f"❌ Erro ao buscar música: {e}")

# ================================
# Comando skip
# ================================
@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭ Música pulada!")
    else:
        await ctx.send("❌ Nenhuma música está tocando.")

# ================================
# Comando stop
# ================================
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹ Parando todas as músicas e saindo do canal!")
        music_queues[ctx.guild.id] = []
    else:
        await ctx.send("❌ Não estou conectado em nenhum canal de voz.")

# ================================
# Comando queue
# ================================
@bot.command()
async def queue(ctx):
    guild_id = ctx.guild.id
    if guild_id not in music_queues or len(music_queues[guild_id]) == 0:
        await ctx.send("🎵 A fila está vazia!")
    else:
        queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(music_queues[guild_id])])
        await ctx.send(f"🎶 Fila de músicas:\n{queue_list}")

# ================================
# Comando créditos
# ================================
@bot.command()
async def credits(ctx):
    await ctx.send(f"🤖 Bot versão {BOT_VERSION} desenvolvido por {BOT_AUTHOR}")

# ================================
# Evento ready
# ================================
@bot.event
async def on_ready():
    print(f"{bot.user} conectado!")
    print(f"Versão {BOT_VERSION} | Autor: {BOT_AUTHOR}")

# ================================
# Run bot
# ================================
bot.run(TOKEN)
