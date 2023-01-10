import discord
from discord import Intents
from discord import Guild
from discord.ext.commands import Bot
from logging import Logger
import sys

from .config import config
from .config.fukurou_config import FukurouConfig
from .settings import Settings

class Fukurou(Bot):
    def __init__(self, logger: Logger, intents: Intents = discord.Intents.default()):
        # Initialize bot config
        fukurou_config = FukurouConfig(logger = logger)
        fukurou_config.init()

        self.token = fukurou_config.getToken()
        
        if self.token == "" or self.token == fukurou_config.DEFAULT_FORMAT["token"]:
            print("Error: No bot token!")
            sys.exit()

        intents = intents

        super().__init__(intents = intents)

        self.settings = {}
        self.players = {}

    async def on_ready(self):
        print(config.STARTUP_MESSAGE)
        await self.change_presence(status=discord.Status.online, activity=discord.Game(name="Music, type {}help".format(config.BOT_PREFIX)))

        for guild in self.guilds:
            await self.register(guild)
            print("Joined {}".format(guild.name))

        print(config.STARTUP_COMPLETE_MESSAGE)

    async def on_guild_join(self, guild: Guild):
        print(guild.name)
        await self.register(guild)

    async def register(self, guild: Guild):   
        from .ext.music import Player

        self.settings[guild.id] = Settings(guild)
        self.players[guild.id] = Player(self, guild)

        print(f'add players to guild {guild.id}')

        sett = self.settings[guild.id]

        try:
            await guild.me.edit(nick=sett.get('default_nickname'))
        except:
            pass

        if config.GLOBAL_DISABLE_AUTOJOIN_VC == True:
            return

        vc_channels = guild.voice_channels

        if sett.get('vc_timeout') == False:
            if sett.get('start_voice_channel') == None:
                try:
                    await self.players[guild.id].register_voice_channel(guild.voice_channels[0])
                except Exception as e:
                    print(e)

            else:
                for vc in vc_channels:
                    if vc.id == sett.get('start_voice_channel'):
                        try:
                            await self.players[guild.id].register_voice_channel(vc_channels[vc_channels.index(vc)])
                        except Exception as e:
                            print(e)

    def run(self):
        super().run(self.token)