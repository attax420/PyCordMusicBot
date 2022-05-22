import asyncio
import discord
import youtube_dl
from discord.ext import commands

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",}
ffmpeg_options = {"options": "-vn"}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
token = 'INSERT YOUR BOT TOKEN HERE!!!'

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]
        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, *, url):
        channel = discord.VoiceChannel = ctx.message.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()    
        voice_client = discord.utils.get(bot.voice_clients) 
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            voice_client.play(player, after=lambda _: asyncio.run_coroutine_threadsafe(
                            coro=voice_client.disconnect(),
                            loop=voice_client.loop
                            ).result())
        await ctx.send(f"Now playing: {player.title}")
       
    @commands.command()
    async def volume(self, ctx, volume: int):
        voice_client = discord.utils.get(bot.voice_clients) 
        if voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        voice_client = discord.utils.get(bot.voice_clients) 
        await voice_client.disconnect()


if __name__ == '__main__':
    bot = commands.Bot(command_prefix="!", description="extremely simple music bot")
    bot.add_cog(Music(bot))
    bot.run(token)
