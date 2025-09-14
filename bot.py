import discord
from discord.ext import commands
import asyncio
import yt_dlp
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Spotify
spotify = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Fila de música
music_queue = {}

# YTDL Options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

# Função de tocar música
async def play_next(ctx):
    if not music_queue[ctx.guild.id]:
        await ctx.send("Fila de música vazia 🎵")
        return
    url = music_queue[ctx.guild.id].pop(0)
    voice_channel = ctx.author.voice.channel
    if ctx.guild.voice_client is None:
        await voice_channel.connect()
    ctx.guild.voice_client.stop()
    info = ytdl.extract_info(url, download=False)
    source = discord.FFmpegPCMAudio(info['url'], **ffmpeg_options)
    ctx.guild.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
    embed = discord.Embed(
        title="🎶 Tocando agora!",
        description=f"[{info['title']}]({info['webpage_url']})",
        color=discord.Color.purple()
    )
    embed.set_footer(text="Bot Kennedy v1.1")
    await ctx.send(embed=embed)

# Comandos
@bot.command()
async def play(ctx, *, query):
    """Toca uma música do YouTube ou Spotify pelo nome."""
    if ctx.author.voice is None:
        await ctx.send("Você precisa estar em um canal de voz 🎧")
        return

    # Busca no Spotify
    if "open.spotify.com" in query:
        try:
            track_id = query.split("/")[-1].split("?")[0]
            track = spotify.track(track_id)
            query = f"{track['name']} {track['artists'][0]['name']}"
        except:
            await ctx.send("Erro ao buscar música no Spotify ❌")
            return

    info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
    url = info['webpage_url']

    if ctx.guild.id not in music_queue:
        music_queue[ctx.guild.id] = []
    music_queue[ctx.guild.id].append(url)

    await ctx.send(f"✅ Adicionado à fila: **{info['title']}**")

    if not ctx.guild.voice_client or not ctx.guild.voice_client.is_playing():
        await play_next(ctx)

@bot.command()
async def skip(ctx):
    """Pula a música atual"""
    if ctx.guild.voice_client and ctx.guild.voice_client.is_playing():
        ctx.guild.voice_client.stop()
        await ctx.send("⏭ Música pulada!")
    else:
        await ctx.send("Não há música tocando 🎶")

@bot.command()
async def stop(ctx):
    """Para a música e limpa a fila"""
    if ctx.guild.voice_client:
        ctx.guild.voice_client.stop()
        music_queue[ctx.guild.id] = []
        await ctx.guild.voice_client.disconnect()
        await ctx.send("⏹ Música parada e fila limpa!")
    else:
        await ctx.send("Não há música tocando 🎶")

@bot.command()
async def queue(ctx):
    """Mostra a fila de músicas"""
    if ctx.guild.id not in music_queue or not music_queue[ctx.guild.id]:
        await ctx.send("Fila vazia 🎵")
        return
    desc = "\n".join([f"{i+1}. {ytdl.extract_info(url, download=False)['title']}" for i, url in enumerate(music_queue[ctx.guild.id])])
    embed = discord.Embed(title="🎶 Fila de músicas", description=desc, color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"{bot.user} está online!")

bot.run(TOKEN)
