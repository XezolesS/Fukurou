# pylint: disable = C0114
from discord import Guild

from fukurou.setting import Settings

ST_VOLUME = 'voice_volume'
ST_VOLUME_VAL = 100
ST_COMMAND_CHANNEL = 'command_channel'
ST_COMMAND_CHANNEL_VAL = 'any'

class MusicSettings(Settings):
    '''Music Settings'''

    def __init__(self, guild: Guild, name: str = None):
        super().__init__(guild = guild, name = name)
        self.settings = {
            ST_VOLUME: ST_VOLUME_VAL,
            ST_COMMAND_CHANNEL: ST_COMMAND_CHANNEL_VAL
        }

    def set_volume(self, volume: int) -> None:
        self.set(key = ST_VOLUME, value = volume)

    def get_volume(self) -> int:
        return self.get(key = ST_VOLUME)

    def set_command_channel(self, channel_id: (None | int) = ST_COMMAND_CHANNEL_VAL) -> None:
        '''
        Set the only channel in where the commands are allowed to be called.\n
        If it's none(any, not int), commands can be executed in anywhere.
        '''
        self.set(key = ST_COMMAND_CHANNEL, value = channel_id)

    def get_command_channel(self) -> (None | int):
        '''
        Get the only channel in where the commands are allowed to be called.\n
        If it's none(any, not int), commands can be executed in anywhere.
        '''
        return self.get(key = ST_COMMAND_CHANNEL)
