# pylint: disable = C0114, E1101, W0221, W0702, W0703
import sys
import discord
from discord import (
    Intents,
    Guild
)
from discord.ext.commands import Bot

from fukurou.ext import music
from .config import config
from .config.fukurou_config import (
    DEFAULT_FORMAT,
    CONFIG_TOKEN,
    FukurouConfig
)
from .setting import GuildSettings
from .logging import GuildLoggers

class Fukurou(Bot):
    '''
    The client of Fukurou bot.

    Attribute:
        intents (Intents): Discord intents.
    '''
    def __init__(self, intents: Intents = discord.Intents.default()):
        super().__init__(intents = intents)

        # Initialize bot config
        fukurou_config = FukurouConfig()
        fukurou_config.init()

        self.loggers = GuildLoggers()
        self.settings = GuildSettings()
        self.players = {}
        self.token = fukurou_config.get_token()
        if self.token in ('', DEFAULT_FORMAT[CONFIG_TOKEN]):
            sys.exit()

    async def on_ready(self):
        '''A handler to be called when Fukurou bot is ready.'''
        await self.change_presence(
            status = discord.Status.online,
            activity = discord.Game(name = ':D')
        )

        for guild in self.guilds:
            await self.__register(guild)

    async def on_guild_join(self, guild: Guild):
        '''A handler to be called when Fukurou bot joined the guild.'''
        await self.__register(guild)

    async def __register(self, guild: Guild):
        self.loggers.add_logger(guild)
        self.settings.add_settings(guild)
        self.players[guild.id] = music.Player(self, guild)

        self.loggers.get_logger(guild).info(f'Registered to guild {guild.name}')

        # setting = self.settings
        # try:
        #    await guild.me.edit(nick = setting.get('default_nickname'))
        # except:
        #    pass

        # await self.__autojoin_voicechannel(guild = guild)

    async def __autojoin_voicechannel(self, guild: Guild):
        if config.GLOBAL_DISABLE_AUTOJOIN_VC is True:
            return

        setting = self.settings[guild.id]
        if setting.get('vc_timeout') is True:
            return

        vc_channels = guild.voice_channels
        setting = self.settings[guild.id]

        if setting.get('start_voice_channel') is None:
            try:
                await self.players[guild.id].register_voice_channel(guild.voice_channels[0])
            except Exception as exception:
                print(exception)

        else:
            for vc in vc_channels:
                if vc.id == setting.get('start_voice_channel'):
                    try:
                        await self.players[guild.id].register_voice_channel(vc_channels[vc_channels.index(vc)])
                    except Exception as exception:
                        print(exception)

    def run(self):
        super().run(self.token)
