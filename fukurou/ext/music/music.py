# pylint: disable = C0114, R0902, R0913, W0703
import datetime
import re
import discord
import yt_dlp

from fukurou.config import config
from fukurou.enums import (
    Origin,
    Playlist,
    Site
)
import fukurou.ext.music.url as u

class Music():
    '''
    A music object.

    Attributes:
        origin (Origin): Represent if it's from playlist or not.
        host (Site): The website where the music is.
        uploader (str): Uploader who uploaded the music.
        title (str): Title of the music.
        duration (int): Total duration of the music.
        url (str): The webpage link of the music.
        webpage_url (str):
        thumbnail (str): The url of the thumbnail.
    '''

    def __init__(self, origin: Origin, host: Site,
                 uploader: str = None,
                 title: str = None,
                 duration: int = None,
                 url: str = None,
                 webpage_url: str = None,
                 thumbnail: str = None):
        self.origin = origin
        self.host = host
        self.uploader = uploader
        self.title = title
        self.duration = duration
        self.url = url
        self.webpage_url = webpage_url
        self.thumbnail = thumbnail
        self.output = ""

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
