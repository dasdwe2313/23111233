import discord
from discord.ext import commands
from services.youtube import search_youtube
from services.spotify import get_track_name

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="play")
    async def play(self, ctx, *, query):
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

        if "open.spotify.com" in query:
            query = get_track_name(query) or query

        url = search_youtube(query)
        if not url:
            await ctx.send("❌ Música não encontrada.")
            return

        ctx.voice_client.stop()
        ydl_opts = {'format': 'bestaudio'}
        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']

        source = await discord.FFmpegOpusAudio.from_probe(audio_url)
        ctx.voice_client.play(source)
        await ctx.send(f"🎵 Tocando: {url}")

    @commands.command(name="pause")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Música pausada.")
        else:
            await ctx.send("⚠️ Nenhuma música tocando.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Música retomada.")
        else:
            await ctx.send("⚠️ Nenhuma música pausada.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Música parada e bot desconectado.")

    @commands.command(name="menu")
    async def menu(self, ctx):
        embed = discord.Embed(
            title="🎶 Menu de Comandos - Bot de Música",
            description="Bot com suporte a YouTube e Spotify",
            color=discord.Color.blue()
        )
        embed.add_field(name="📀 !play [nome ou link]", value="Toca uma música via YouTube ou Spotify", inline=False)
        embed.add_field(name="⏸️ !pause", value="Pausa a música atual", inline=False)
        embed.add_field(name="▶️ !resume", value="Continua a música pausada", inline=False)
        embed.add_field(name="🛑 !stop", value="Para tudo e sai do canal de voz", inline=False)
        embed.add_field(name="ℹ️ !menu", value="Exibe esse menu de ajuda", inline=False)
        embed.set_footer(text="🔧 Desenvolvido por Kennedy | Versão 1.0")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Music(bot))
