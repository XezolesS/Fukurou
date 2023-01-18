# pylint: disable = C0114, W0703
import re
import yt_dlp

import fukurou.ext.music as m

REGEX_URL = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

class UrlConverter:
    def __init__(self):
        pass

async def to_musiclist(url: str):
    '''Get music data from the URL.'''
    if not is_url(url):
        return None

    options = {
        'format': 'bestaudio/best',
        'extract_flat': True
    }

    with yt_dlp.YoutubeDL(options) as ytdlp:
        info = ytdlp.extract_info(url, download = False)

    music_list = []

    # When the link is a playlist.
    if info.get('playlist_count'):
        entries = info.get('entries')
        for entry in entries:
            music_list.append(m.Music(entry.get('url'), title = entry.get('title')))
    else:
        music_list.append(m.Music(info.get('webpage_url'), title = info.get('title')))

    return music_list

def is_url(content: str):
    '''Check if the string is URL.'''
    regex = re.compile(REGEX_URL)

    if re.search(regex, content):
        result = regex.search(content)
        url = result.group(0)
        return url

    return None
