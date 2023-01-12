# pylint: disable = C0114, C0115, C0103
from enum import Enum

class Site(Enum):
    Unknown = "Unknown"
    Spotify = "Spotify"
    Spotify_Playlist = "Spotify Playlist"
    YouTube = "YouTube"
    Twitter = "Twitter"
    SoundCloud = "SoundCloud"
    Bandcamp = "Bandcamp"
    Custom = "Custom"
