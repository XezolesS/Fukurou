# pylint: disable = C0114
__all__ = [
    'music',
    'player',
    'playlist',
    'url'
]

import fukurou.ext.music.music
import fukurou.ext.music.player
import fukurou.ext.music.playlist
import fukurou.ext.music.url

from .music import Music
from .player import Player
from .playlist import Playlist
from .url import (
    to_playlist,
    to_site,
    get_music,
    is_url
)
