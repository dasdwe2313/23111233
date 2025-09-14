# bot.py
import discord
from discord.ext import commands
import asyncio
import yt_dlp as ytdlp

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Fila de músicas por guilda
queues = {}

# Configuração do YTDLP
YTDLP_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch1",  # Busca pelo nome
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

# ------------------ FUNÇÕES ------------------

async def play_next(ctx):
    queue = queues.get(ctx.guild.id)
    if queue and len(queue) > 0:
        # Pega a próxima música
        url = queue.pop(0)
        ctx.voice_client.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
    else:
        await ctx.voice_client.disconnect()


async def search_youtube(query):
    with ytdlp.YoutubeDL(YTDLP_OPTIONS) as ydl:
        info = ydl.extract_info(query, download=False)
        return info["entries"][0]["url"] if "entries" in info else info["url"]

# ------------------ COMANDOS ------------------

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Conectado ao canal {channel}")
    else:
        await ctx.send("Você precisa estar em um canal de voz!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Desconectado do canal de voz.")
    else:
        await ctx.send("Não estou em nenhum canal!")

@bot.command()
async def play(ctx, *, query):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Você precisa estar em um canal de voz!")
            return

    # Adiciona música à fila
    url = await search_youtube(query)
    queue = queues.setdefault(ctx.guild.id, [])
    queue.append(url)

    if not ctx.voice_client.is_playing():
        await ctx.send(f"Tocando: {query}")
        await play_next(ctx)
    else:
        await ctx.send(f"Adicionado à fila: {query}")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Música pulada!")
    else:
        await ctx.send("Nenhuma música tocando agora.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        queues[ctx.guild.id] = []
        await ctx.send("Música parada e fila limpa!")
    else:
        await ctx.send("Não estou tocando nada.")

# ------------------ TESTE ------------------

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# ------------------ RODA BOT ------------------

TOKEN = "SEU_TOKEN_AQUI"
bot.run(TOKEN)
