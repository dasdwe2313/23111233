import discord
from discord.ext import commands
import yt_dlp
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

# Configura Spotify
sp_client_id = os.getenv("SPOTIPY_CLIENT_ID")
sp_client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
spotify = Spotify(auth_manager=SpotifyClientCredentials(client_id=sp_client_id,
                                                        client_secret=sp_client_secret))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="play")
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            return await ctx.send("❌ Você precisa estar em um canal de voz.")

        channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await channel.connect()
        vc = ctx.voice_client

        # Detecta Spotify link
        if "open.spotify.com/track/" in query:
            track_id = query.split("/")[-1].split("?")[0]
            track_info = spotify.track(track_id)
            search_query = f"{track_info['name']} {track_info['artists'][0]['name']}"
        else:
            search_query = query

        # yt-dlp procura no YouTube
        ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if "youtube.com" in search_query or "youtu.be" in search_query:
                info = ydl.extract_info(search_query, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{search_query}", download=False)["entries"][0]

            audio_url = info["formats"][0]["url"]
            title = info["title"]

        # Toca o áudio
        ffmpeg_opts = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                       "options": "-vn"}
        vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts))
        await ctx.send(f"🎶 Tocando: {title}")

async def setup(bot):
    await bot.add_cog(Music(bot))
