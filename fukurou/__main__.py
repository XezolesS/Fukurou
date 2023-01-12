# pylint: disable = C0114, E0237, W0703
import os
import discord

from .fukurou import Fukurou
from .config import config

initial_extensions = [
    'fukurou.cogs.general',
    'fukurou.cogs.music'
]

if __name__ == '__main__':
    config.ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    config.COOKIE_PATH = config.ABSOLUTE_PATH + config.COOKIE_PATH

    intents = discord.Intents.default()
    intents.message_content = True

    # Instantiate bot
    bot = Fukurou(intents = intents)

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)

    bot.run()
