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
token = 'INSERT DISCORD BOT TOKEN HERE!!!!'

class YTDLSource(discord.PCMVolumeTransformer):
    '''youtube downloader class'''                         
    def __init__(self, source, *, data, volume=0.5):        
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        '''method for downloading or streaming music from youtube (List detection is BUGGY)'''           
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]
        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


global queue
queue = []
global ind
ind = 0 

class Music(commands.Cog):                                              #music bot class
    def __init__(self, bot):
        self.bot = bot          
   
   
    async def start_playing(self):
        '''audioplayer function that is called from commands and the "after=" attribute of voice_client.play()'''
        global queue
        global ind 
        global q1
        ind = ind+1       
        
        voice_client = discord.utils.get(self.bot.voice_clients)            
        if len(queue) > 0:
            print('DEBUG!!!! len queue > 0')               
            if not voice_client.is_playing():            
                print('\n\n\nDEBUG COUNTER: '+str(ind)+'\n\n\n')
                print('DEBUG start_playing queue:   '+str(queue)) 
                try:
                    global q1
                    q1 = queue[0]            
                    queue.pop(0)
                    voice_client = discord.utils.get(self.bot.voice_clients)            
                    voice_client.play(q1, after=lambda _: asyncio.run_coroutine_threadsafe(
                                    coro=self.start_playing(),
                                    loop=voice_client.loop
                                    ).result()) 
                except IndexError:
                    print('\n\n\nDEBUG!!! queue empty!!!!\n\n\n')
                    await voice_client.disconnect()                    
                                                
                print('DEBUG q1:   '+str(q1))
            
            else:
                pass
        else: 
            print('DEBUG!!!! len queue < 1')
            await voice_client.disconnect()
     
     
    @commands.command()
    async def join(self, ctx):
        '''joins your voice channel'''
        channel = discord.VoiceChannel = ctx.message.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect() 
        
                
    @commands.command()
    async def play(self, ctx, *, url): 
        '''joins your channel and plays song'''    
        channel = discord.VoiceChannel = ctx.message.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()                      
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)              
        queue.append(player)            
        print('DEBUG self.queue:   '+str(queue))
        await ctx.send(f':mag_right: **Searching for** ``' + url + '``\n**Now Playing:** ``{}'.format(player.title) + "``")
        await self.start_playing()
            
                
    @commands.command()
    async def q(self,ctx,* , url):
        '''add song to queue'''
        global queue
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)               
        print('DEBUG!!!!! q')
        queue.append(player)
        print('DEBUG global queue:   '+str(queue)) 
        await ctx.send(f':mag_right: **Searching for** ``' + url + '``\n**Added to queue:** ``{}'.format(player.title) + "``")
        print('DEBUG:   '+str(len(queue)))
        
    
    @commands.command()
    async def skip(self,ctx):
        '''skips to next song in queue'''
        global queue
        voice_client = discord.utils.get(self.bot.voice_clients)
        print('DEBUG skip queue before append:   '+str(queue))
        
        if len(queue) > 0:
            queue.append(queue[0])
            print('DEBUG skip queue after append:   '+str(queue))            
            voice_client.stop()
            await self.start_playing()               
        else:
            await voice_client.disconnect()
              
        print('DEBUG skip queue end:   '+str(queue))
        
        
    @commands.command()
    async def pause(self, ctx):
        '''pauses playback'''       
        voice_client = discord.utils.get(self.bot.voice_clients) 
        voice_client.pause()
        

    @commands.command()
    async def resume(self,ctx):
        '''resumes playback''' 
        voice_client = discord.utils.get(self.bot.voice_clients)
        voice_client.resume()

           
    @commands.command()
    async def volume(self, ctx, volume: int):
        '''sets volume for everyone (0-100)'''
        voice_client = discord.utils.get(self.bot.voice_clients)
        voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")


    @commands.command()
    async def kick(self, ctx):
        '''disconnects bot from voice channel'''         
        voice_client = discord.utils.get(self.bot.voice_clients)
        await voice_client.disconnect()


if __name__ == '__main__':
    bot = commands.Bot(command_prefix="!", description="A simple musicbot written in python")
    bot.add_cog(Music(bot))
    bot.run(token)
