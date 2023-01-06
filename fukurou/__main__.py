import discord
from discord.ext import commands
import logging
import sys
import os


from config import config
from config.bot_config import FukurouConfig
from audiocontroller import AudioController
from settings import Settings
from utils import guild_to_audiocontroller, guild_to_settings

initial_extensions = ['commands.music',
                      'commands.general', 'plugins.button']
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=config.BOT_PREFIX,
                   intents = intents,
                   pm_help=True, case_insensitive=True)


@bot.event
async def on_ready():
    print(config.STARTUP_MESSAGE)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Music, type {}help".format(config.BOT_PREFIX)))

    for guild in bot.guilds:
        await register(guild)
        print("Joined {}".format(guild.name))

    print(config.STARTUP_COMPLETE_MESSAGE)


@bot.event
async def on_guild_join(guild):
    print(guild.name)
    await register(guild)


async def register(guild):

    guild_to_settings[guild] = Settings(guild)
    guild_to_audiocontroller[guild] = AudioController(bot, guild)

    sett = guild_to_settings[guild]

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
                await guild_to_audiocontroller[guild].register_voice_channel(guild.voice_channels[0])
            except Exception as e:
                print(e)

        else:
            for vc in vc_channels:
                if vc.id == sett.get('start_voice_channel'):
                    try:
                        await guild_to_audiocontroller[guild].register_voice_channel(vc_channels[vc_channels.index(vc)])
                    except Exception as e:
                        print(e)


if __name__ == '__main__':

    config.ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    config.COOKIE_PATH = config.ABSOLUTE_PATH + config.COOKIE_PATH

    # Setting up a logger
    logger = logging.getLogger("Fukurou")
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(filename = "fukurou.log", encoding = "utf-8", mode = "w")
    handler.setFormatter(logging.Formatter("[%(asctime)s | %(levelname)s] %(name)s\t%(message)s"))

    logger.addHandler(handler)

    # Initialize bot config
    fukurou_config = FukurouConfig(logger = logger)
    fukurou_config.init()

    bot_token = fukurou_config.getToken()
    
    if bot_token == "" or bot_token == fukurou_config.DEFAULT_FORMAT["token"]:
        print("Error: No bot token!")
        sys.exit()

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)

    bot.run(bot_token)