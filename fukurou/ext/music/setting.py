# pylint: disable = C0114
from discord import Guild

from fukurou.setting import Settings

SETTINGS_MUSIC_VOLUME = 'voice_volume'
SETTINGS_MUSIC_VOLUME_VALUE = 100

class MusicSettings(Settings):
    '''Music Settings'''

    def __init__(self, guild: Guild, name: str):
        super().__init__(guild = guild, name = name)
        self.settings = {
            SETTINGS_MUSIC_VOLUME: SETTINGS_MUSIC_VOLUME_VALUE
        }

    def set_volume(self, volume: int) -> None:
        self.set(key = SETTINGS_MUSIC_VOLUME, value = volume)

    def get_volume(self) -> int:
        return self.get(key = SETTINGS_MUSIC_VOLUME)
