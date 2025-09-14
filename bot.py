import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# ======= Configurações =======
VERSION = "1.1"
AUTHOR = "Kennedy"

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

queues = {}

# ======= Função tocar música =======
async def play_music(ctx, search):
    guild_id = ctx.guild.id
    if guild_id not in queues:
        queues[guild_id] = []

    try:
        results = sp.search(q=search, type="track", limit=1)
        track = results['tracks']['items'][0]
        url = track['external_urls']['spotify']
        title = f"{track['name']} - {track['artists'][0]['name']}"
    except:
        ydl_opts = {'format': 'bestaudio', 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            url = info['webpage_url']
            title = info['title']

    queues[guild_id].append({'title': title, 'url': url})

    if not ctx.voice_client or not ctx.voice_client.is_playing():
        if not ctx.author.voice:
            await ctx.send("❌ Você precisa estar em um canal de voz!")
            return
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        await start_queue(ctx)
    else:
        await ctx.send(f"➕ **Adicionado à fila:** {title}")

# ======= Função fila =======
async def start_queue(ctx):
    guild_id = ctx.guild.id
    vc = ctx.voice_client

    while queues[guild_id]:
        track = queues[guild_id].pop(0)
        ydl_opts = {'format': 'bestaudio'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(track['url'], download=False)
            url2 = info['url']

        vc.play(discord.FFmpegPCMAudio(url2, executable="ffmpeg"), after=lambda e: print(f'Erro: {e}') if e else None)

        embed = discord.Embed(
            title=f"🎶 Tocando agora: {track['title']}",
            description=f"💡 **Bot versão:** {VERSION}\n👤 **Criador:** {AUTHOR}",
            color=discord.Color.green()
        )
        embed.set_footer(text="🎧 Bot Music by Kennedy")
        await ctx.send(embed=embed)

        while vc.is_playing():
            await asyncio.sleep(1)

    await vc.disconnect()

# ======= Comandos =======
@bot.command()
async def play(ctx, *, search: str):
    await play_music(ctx, search)

@bot.command()
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Música pausada!")
    else:
        await ctx.send("❌ Nenhuma música tocando!")

@bot.command()
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Música retomada!")
    else:
        await ctx.send("❌ Nenhuma música pausada!")

@bot.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Música pulada!")
    else:
        await ctx.send("❌ Nenhuma música tocando!")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        queues[ctx.guild.id] = []
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Música parada e fila limpa!")

@bot.command()
async def queue(ctx):
    guild_id = ctx.guild.id
    if guild_id in queues and queues[guild_id]:
        desc = "\n".join([f"{i+1}. {t['title']}" for i, t in enumerate(queues[guild_id])])
        embed = discord.Embed(
            title="🎵 Fila de músicas",
            description=desc,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Fila vazia!")

# ======= Evento pronto =======
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user} | Versão {VERSION} | Criador: {AUTHOR}")
    activity = discord.Game(name=f"🎧 Tocando música | Versão {VERSION}")
    await bot.change_presence(status=discord.Status.online, activity=activity)

# ======= Run bot =======
bot.run(TOKEN)
