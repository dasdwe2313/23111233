import discord
from discord.ext import commands
import yt_dlp
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Spotify setup
sp = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}  # guild_id: list of (title, url)

    async def play_next(self, ctx, guild_id):
        if not self.queue[guild_id]:
            await ctx.voice_client.disconnect()
            return
        title, url = self.queue[guild_id].pop(0)
        ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info["formats"][0]["url"]

        ffmpeg_opts = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                       "options": "-vn"}
        ctx.voice_client.play(
            discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts),
            after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx, guild_id), self.bot.loop)
        )
        await ctx.send(f"🎶 Tocando: {title}")

    @commands.command(name="play")
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            return await ctx.send("❌ Você precisa estar em um canal de voz.")

        channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await channel.connect()
        guild_id = ctx.guild.id
        if guild_id not in self.queue:
            self.queue[guild_id] = []

        # Detecta Spotify link
        if "open.spotify.com/track/" in query:
            track_id = query.split("/")[-1].split("?")[0]
            track_info = sp.track(track_id)
            search_query = f"{track_info['name']} {track_info['artists'][0]['name']}"
        else:
            search_query = query

        # Pesquisa no YouTube
        ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if "youtube.com" in search_query or "youtu.be" in search_query:
                info = ydl.extract_info(search_query, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{search_query}", download=False)["entries"][0]

        title = info["title"]
        url = info["webpage_url"]

        self.queue[guild_id].append((title, url))
        await ctx.send(f"✅ Música adicionada à fila: {title}")

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx, guild_id)

    @commands.command(name="skip")
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭ Música pulada!")

    @commands.command(name="stop")
    async def stop(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send("⏹ Música parada e saí do canal.")
            self.queue[ctx.guild.id] = []

    @commands.command(name="pause")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸ Música pausada.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶ Música retomada.")

async def setup(bot):
    await bot.add_cog(Music(bot))
