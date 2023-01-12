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

    @staticmethod
    def from_url(url: str):
        if not Music.is_url(url):
            return None

        # Clear subdomains
        if url.startswith('https://m.'):
            url = url.replace('https://m.', 'https://')

        if url.startswith('https://music.'):
            url = url.replace('https://music.', 'https://')

        host = Music.url2site(url)
        playlist = Music.url2playlist(url)

        # Site not supported
        if host == Site.Unknown:
            return None

        # Not playlist (Single music)
        if playlist == Playlist.Unknown:
            downloader = yt_dlp.YoutubeDL(
                {
                    'format': 'bestaudio',
                    'title': True
                }
            )

            try:
                meta = downloader.extract_info(url, download = False)
            except Exception as exception:
                print(exception)
                return None

            uploader = meta.get('uploader')
            title = meta.get('title')
            duration = meta.get('duration')
            url = meta.get('url')
            webpage_url = meta.get('webpage_url')
            thumbnail = (None if meta.get('thumbnails') is None
                else meta.get('thumbnails')[-1]['url'])

            music = Music(Origin.Default, host,
                uploader = uploader,
                title = title,
                duration = duration,
                url = url,
                webpage_url = webpage_url,
                thumbnail = thumbnail)

            return music

    @staticmethod
    def is_url(content: str):
        regex = re.compile(
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

        if re.search(regex, content):
            result = regex.search(content)
            url = result.group(0)
            return url

        return None

    @staticmethod
    def url2site(url: str):
        if url is None or url.isspace():
            return Site.Unknown

        if any(youtube_links in url for youtube_links in [
                'https://www.youtube.com',
                'https://youtube.com',
                'https://youtu.be']):
            return Site.YouTube

        if "https://open.spotify.com/track" in url:
            return Site.Spotify

        if "https://open.spotify.com/playlist" in url or "https://open.spotify.com/album" in url:
            return Site.Spotify_Playlist

        if "bandcamp.com/track/" in url:
            return Site.Bandcamp

        if "https://twitter.com/" in url:
            return Site.Twitter

        if url.lower().endswith(config.SUPPORTED_EXTENSIONS):
            return Site.Custom

        if "soundcloud.com/" in url:
            return Site.SoundCloud
        
        return Site.Unknown

    @staticmethod
    def url2playlist(url: str):
        if url is None or url.isspace():
            return Site.Unknown

        if "playlist?list=" in url:
            return Playlist.YouTube_Playlist

        if "https://open.spotify.com/playlist" in url or "https://open.spotify.com/album" in url:
            return Playlist.Spotify_Playlist

        if "bandcamp.com/album/" in url:
            return Playlist.BandCamp_Playlist

        return Playlist.Unknown

    def format_output(self, playtype):
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
