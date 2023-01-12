import discord
from discord import (
    Intents, 
    Guild
)
from discord.ext.commands import Bot
import sys

from .config import config
from .config.fukurou_config import FukurouConfig
from .settings import Settings
from .logging import GuildLoggers

class Fukurou(Bot):
    def __init__(self, intents: Intents = discord.Intents.default()):
        super().__init__(intents = intents)

        # Initialize bot config
        fukurou_config = FukurouConfig()
        fukurou_config.init()

        self.settings = {}
        self.players = {}
        self.loggers = GuildLoggers()
        self.token = fukurou_config.getToken()
        if self.token == "" or self.token == fukurou_config.DEFAULT_FORMAT["token"]:
            sys.exit()

    async def on_ready(self):
        await self.change_presence(
            status=discord.Status.online, 
            activity=discord.Game(name=':D')
        )

        for guild in self.guilds:
            await self.__register(guild)

    async def on_guild_join(self, guild: Guild):
        await self.__register(guild)

    async def __register(self, guild: Guild):   
        from .ext.music import Player

        self.settings[guild.id] = Settings(guild)
        self.players[guild.id] = Player(self, guild)
        self.loggers.addLogger(guild)

        self.loggers.getLogger(guild).info(f'Registered to guild {guild.name}')

        setting = self.settings[guild.id]
        try:
            await guild.me.edit(nick=setting.get('default_nickname'))
        except:
            pass

        await self.__autojoin_voicechannel(guild = guild)

    async def __autojoin_voicechannel(self, guild: Guild):
        if config.GLOBAL_DISABLE_AUTOJOIN_VC == True:
            return

        setting = self.settings[guild.id]
        if setting.get('vc_timeout') == True:
            return

        vc_channels = guild.voice_channels
        setting = self.settings[guild.id]

        if setting.get('start_voice_channel') == None:
            try:
                await self.players[guild.id].register_voice_channel(guild.voice_channels[0])
            except Exception as e:
                print(e)

        else:
            for vc in vc_channels:
                if vc.id == setting.get('start_voice_channel'):
                    try:
                        await self.players[guild.id].register_voice_channel(vc_channels[vc_channels.index(vc)])
                    except Exception as e:
                        print(e)

    def run(self):
        super().run(self.token)