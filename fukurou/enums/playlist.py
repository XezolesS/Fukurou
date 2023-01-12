# pylint: disable = C0114, C0115, C0103
from enum import Enum

class Playlist(Enum):
    Unknown = "Unknown"
    Spotify_Playlist = "Spotify Playlist"
    YouTube_Playlist = "YouTube Playlist"
    BandCamp_Playlist = "BandCamp Playlist"
