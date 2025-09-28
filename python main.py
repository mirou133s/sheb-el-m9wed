
from __future__ import annotations

import re
import asyncio
import requests
import discord
from discord.ext import commands
import asyncio
import webserver
import os
DISCORD_TOKEN = os.environ['discordkey']


from discord import Embed, Intents, Activity, Status, Color, ActivityType
from discord import FFmpegOpusAudio, Message, utils
from discord.ext import commands
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
from discord import VoiceClient, Member, VoiceState
from typing import TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    from discord.ext.commands import Bot

from os import getenv

EMBED_COLOR = 0x000000

bot = commands.Bot(
    command_prefix='.',
    intents=discord.Intents.all(),
    activity=Activity(type=ActivityType.playing, name="EA SPORTS FC 26"),
    status=Status.idle,
    help_command=None
)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'socket_timeout': 10,
    'extract_flat': True

}

def is_youtube_link(message_content):
    patterns = [
        r'https?://(?:www\.)?youtu\.be/([^/?]+)',
        r'https?://(?:www\.)?youtube\.com/watch\?v=([^&]+)'
    ]
    return any(re.match(pattern, message_content) for pattern in patterns)

def is_link_valid(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_duration(time):
    if time is None:
        return "LIVE STREAM :purple_circle:"
    hours = time // 3600
    minutes = (time % 3600) // 3600
    seconds = time % 3600
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"



async def check_play_status(self, ctx):
    await asyncio.sleep(5)
    if not ctx.voice_client.is_playing() and self.current_track:
        await self.play_command(ctx, query=self.current_track.get('url'))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client: Optional[VoiceClient] = None
        self.is_loop = False
        self.should_skip = False
        self.current_track: dict = {}

    def get_audio_info(self, url: str, ctx: commands.Context) -> Optional[dict]:
        try:
            with YoutubeDL(ytdl_format_options) as ytdl:
                info = ytdl.extract_info(url, download=False)
                if 'entries' in info:  # في حالة وجود playlist
                    info = info['entries'][0]
                
                return {
                    'user': ctx.author,
                    'title': info.get('title', 'غير معروف'),
                    'url': info['url'],
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail')
                }
        except Exception as e:
            print(f"Error getting audio info: {e}")
            return None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Connected as {self.bot.user.name}")

    async def ensure_voice(self, ctx):
        if not ctx.author.voice:
            await ctx.send("ادخل للروم ولا نجي ندخلهولك")
            return False
        
        if not ctx.voice_client:
            self.voice_client = await ctx.author.voice.channel.connect()
        elif ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.voice_client.move_to(ctx.author.voice.channel)
        
        return True

    @commands.command(name='play', aliases=['p', 'ش'])
    async def play_command(self, ctx: commands.Context, *, query: Optional[str]):
        if not query:
            await ctx.send("اكتب الغنية يا شباب يا لبنين")
            return
            
        if not await self.ensure_voice(ctx):
            return

        async with ctx.typing():
            # البحث عن الأغنية
            if not is_youtube_link(query):
                try:
                    search = VideosSearch(query, limit=1)
                    result = search.result()['result']
                    if not result:
                        await ctx.send("مكاش الغنية تزيد تعيني نعيييك فواحد لبلاصة")
                        return
                    url = result[0]['link']
                except Exception as e:
                    await ctx.send(f"اكتب مليح يا لهايشة {e}")
                    return
            else:
                if not is_link_valid(query):
                    await ctx.send("ميمشيش يالبنين سقسي شيكورك mirou1s#4594")
                    return
                url = query

            # الحصول على معلومات الأغنية
            track_info = self.get_audio_info(url, ctx)
            if not track_info or not track_info.get('url'):
                await ctx.send("مركز استخبارات زكمها ملقاتش انفو على الغنية")
                return

            self.current_track = track_info

            # تشغيل الأغنية
            try:
                source = FFmpegOpusAudio(track_info['url'])
                ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.on_track_end(ctx), self.bot.loop))
                
                # إرسال رسالة التشغيل
                embed = Embed(
                    title="راح تبدا الغنية اغلقها و لا نغلقهالك",
                    description=f"[{track_info['title']}]({url})",
                    color=EMBED_COLOR
                )
                embed.add_field(name="وقت تمنييك", value=get_duration(track_info['duration']))
                embed.set_thumbnail(url=track_info['thumbnail'])
                embed.set_footer(text=f"لعطاي لحب يسمع {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(f" كاين عفسا جيب الوسمو و لا سقسي شيكور  {e}")

    async def on_track_end(self, ctx):
        if self.is_loop and not self.should_skip:
            await self.play_command(ctx, query=self.current_track.get('url', ''))
        else:
            self.current_track = {}
            self.should_skip = False

    @commands.command(name='skip', aliases=['s'])
    async def skip_command(self, ctx: commands.Context):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("مكاش وش نسكيبي تزيد تعييني نعييك ")
            return
            
        self.should_skip = True
        self.is_loop = False
        ctx.voice_client.stop()
        await ctx.send("لمرة لخرى نسكيبي مارانيش خدام عليك")

    @commands.command(name='stop', aliases=['leave', 'disconnect'])
    async def stop_command(self, ctx: commands.Context):
        if not ctx.voice_client:
            await ctx.send("يا لحمار مارانيش نغني")
            return
            
        await ctx.voice_client.disconnect()
        self.current_track = {}
        self.is_loop = False
        self.should_skip = False
        await ctx.send("اتهلا في ترمتك")

    @commands.command(name='repeat', aliases=['loop', 'r'])
    async def repeat_command(self, ctx: commands.Context):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("لمعاودة فطعام يا طري")
            return
            
        self.is_loop = not self.is_loop
        status = "rigel" if self.is_loop else " قود درك نديرهولك "
        await ctx.send(f"{status} عاودتها في خاطر الشيكور  ")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if member.id == self.bot.user.id:
            if after.channel is None:
                self.voice_client = None
                self.current_track = {}
                self.is_loop = False
                self.should_skip = False

async def setup(bot):
    await bot.add_cog(Music(bot))
    
bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
