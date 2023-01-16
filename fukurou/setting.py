# pylint: disable = C0114, W0702
import os
import json

import discord
from discord import (
    Guild
)
from fukurou.config import config
from fukurou.ext import music

SETTINGS_FOLDER_NAME = 'settings'
SETTINGS_PATH = os.path.join(os.path.realpath(os.path.curdir), SETTINGS_FOLDER_NAME)

class Settings():
    '''
    Base settings class for extensions.

    Attributes:
        name (str): Name of the extension.
    '''

    def __init__(self, guild: Guild, name: str = None) -> None:
        self.guild = guild
        self.name = type(self).__name__.lower().replace('settings', '') if name is None else name
        self.settings = {}

    def set(self, key: str, value: object) -> None:
        '''Set guild settings.'''
        if self.guild is None:
            print('SETTINGS: No guild found.')
            return

        try:
            self.settings[key] = value
            self.reload()
        except:
            print('SETTINGS: No key exists.')

    def get(self, key: str) -> None | object:
        '''Get guild settings.'''
        if self.guild is None:
            print('SETTINGS: No guild found.')
            return None

        try:
            return self.settings[key]
        except:
            print('SETTINGS: No key exists.')

    def write(self) -> None:
        '''Write currently stored settings to the file.'''
        data = {}
        # Open json file and read it if it exists.
        if self.exists() is True:
            with open(file = self.__get_path(), mode = 'r', encoding = 'utf-8') as file:
                content = file.read()
                if len(content) != 0:
                    data = json.loads(content)

        # Overwrite settings that has specific key.
        data[self.name] = self.settings
        with open(file = self.__get_path(), mode = 'w', encoding = 'utf-8') as file:
            file.write(json.dumps(data, indent = 4))

    def read(self) -> int:
        '''
        Read guild settings from the file.

        Returns:
            (int) Settings count.
        '''
        if self.exists() is False:
            print('SETTINGS: No guild settings file found.')
            return

        # Open json file and read it.
        with open(file = self.__get_path(), mode = 'r', encoding = 'utf-8') as file:
            data = json.loads(file.read())

        settings = data[self.name]      # Settings read

        # Override to current settings.
        for setting in self.settings:
            if setting in settings:
                self.settings[setting] = settings[setting]

        return len(settings)

    def reload(self) -> None:
        '''
        Reload guild settings.\n
        Write current settings to the file and load it to the memory.
        '''
        self.write()
        self.read()

    def exists(self) -> bool:
        '''Check if settings file is exist.'''
        return os.path.exists(self.__get_path())

    def __get_path(self) -> None | str:
        if self.guild is None:
            print('SETTINGS: No guild found.')
            return None

        if os.path.exists(SETTINGS_PATH) is False:
            print('SETTINGS: No settings directory found.')
            return None

        return os.path.join(SETTINGS_PATH, f'{self.guild.id}.setting')

class GuildSettings():
    '''
    Settings for each registered guild.
    '''

    def __init__(self) -> None:
        # Check if directory exists
        if not os.path.exists(SETTINGS_PATH):
            os.makedirs(SETTINGS_PATH)

        self.json_data = None
        self.config = None
        self.settings = []

    def init_settings(self, guild: Guild, force_init: bool = False) -> None:
        '''
        Register settings for the guild.
        If the guild has no settings file, then create new one with the default settings.
        Otherwise, read it from exist settings file.
        '''
        if guild is None:
            return

        # Search all classes that inherit Settings class and load it.
        for child in Settings.__subclasses__():
            sett_toload = child(guild = guild)

            if sett_toload not in self.settings:
                # Write a guild file if it's not exist or force_init is enabled.
                if not sett_toload.exists() or force_init is True:
                    sett_toload.reload()
                else:
                    sett_total = len(sett_toload.settings)
                    sett_count = sett_toload.read()

                    # If the number of settings in the guild file
                    # is not equals to the number of base settings,
                    # write it over new settings.
                    if sett_count != sett_total:
                        sett_toload.reload()

                self.settings.append(sett_toload)

                print(f'Settings "{type(sett_toload).__name__}" loaded as "{sett_toload.name}" for guild {guild.name}')

    def add_settings(self, guild: Guild) -> None:
        '''Add settings for the guild.'''
        self.init_settings(guild)

    def get_settings(self, guild: Guild) -> None | Settings:
        for setting in self.settings:
            if setting.guild == guild:
                return setting

        return None
