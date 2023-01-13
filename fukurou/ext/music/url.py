# pylint: disable = C0114, W0703
import re
import yt_dlp

from fukurou.config import config
from fukurou.enums import (
    Origin,
    Playlist,
    Site
)
import fukurou.ext.music as m

REGEX_URL = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

def to_playlist(url: str):
    '''Resolve URL to playlist type.'''
    if url is None or url.isspace():
        return Site.Unknown

    if "playlist?list=" in url:
        return Playlist.YouTube_Playlist

    if "https://open.spotify.com/playlist" in url or "https://open.spotify.com/album" in url:
        return Playlist.Spotify_Playlist

    if "bandcamp.com/album/" in url:
        return Playlist.BandCamp_Playlist

    return Playlist.Unknown

def to_site(url: str):
    '''Resolve URL to site type.'''
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

def get_music(url: str):
    '''Get music data from the URL.'''
    if not is_url(url):
        return None

    # Clear subdomains
    if url.startswith('https://m.'):
        url = url.replace('https://m.', 'https://')

    if url.startswith('https://music.'):
        url = url.replace('https://music.', 'https://')

    host = to_site(url)
    playlist = to_playlist(url)

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

        music = m.Music(Origin.Default, host,
            uploader = uploader,
            title = title,
            duration = duration,
            url = url,
            webpage_url = webpage_url,
            thumbnail = thumbnail)

        return music

def is_url(content: str):
    '''Check if the string is URL.'''
    regex = re.compile(REGEX_URL)

    if re.search(regex, content):
        result = regex.search(content)
        url = result.group(0)
        return url

    return None
