# pylint: disable = C0114, R0902, R0913, W0703
import datetime
import discord
import yt_dlp

from fukurou.config import config
import fukurou.ext.music.url as u

class Music():
    '''
    A music object.

    Attributes:
        webpage_url (str): The webpage link of the music.

    Optional Attributes:
        title (str): Title of the music.
        uploader (str): Uploader who uploaded the music.
        duration (int): Total duration of the music.
        url (str): The content link of the music.
        thumbnail (str): The url of the thumbnail.
    '''

    def __init__(self, webpage_url: str, **kwargs):
        self.webpage_url = webpage_url

        if kwargs is not None:
            self.title = kwargs.get('title')
            self.uploader = kwargs.get('uploader')
            self.duration = kwargs.get('duration')
            self.url = kwargs.get('url')
            self.thumbnail = kwargs.get('thumbnail')

    async def load(self):
        options = {
            'format': 'bestaudio/best',
            'extract_flat': True
        }

        with yt_dlp.YoutubeDL(options) as ytdlp:
            info = ytdlp.extract_info(self.webpage_url, download = False)

        self.title = info.get('title')
        self.uploader = info.get('uploader')
        self.duration = info.get('duration')
        self.url = info.get('url')
        self.thumbnail = info.get('thumbnails')[-1]['url']

    def to_embed(self, playtype):
        '''Convert music info to discord embed to display.'''
        embed = discord.Embed(
            title = playtype,
            description = f"[{self.title}]({self.webpage_url})",
            color = config.EMBED_COLOR
        )

        if self.thumbnail is not None:
            embed.set_thumbnail(url = self.thumbnail)

        embed.add_field(
            name = config.SONGINFO_UPLOADER,
            value = self.uploader, inline = False
        )

        if self.duration is not None:
            embed.add_field(
                name = config.SONGINFO_DURATION,
                value = f"{datetime.timedelta(seconds = self.duration)}",
                inline = False
            )
        else:
            embed.add_field(
                name = config.SONGINFO_DURATION,
                value = config.SONGINFO_UNKNOWN_DURATION,
                inline = False
            )

        return embed
