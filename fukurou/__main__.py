import discord
from discord.ext import commands
import logging
import sys
import os

import fukurou.cogs
from .config import config
from fukurou.fukurou import Fukurou

initial_extensions = [
    'fukurou.cogs.general',
    'fukurou.cogs.music'
]
                      
intents = discord.Intents.default()
intents.message_content = True

if __name__ == '__main__':
    config.ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    config.COOKIE_PATH = config.ABSOLUTE_PATH + config.COOKIE_PATH

    # Setting up a logger
    logger = logging.getLogger("Fukurou")
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(filename = "fukurou.log", encoding = "utf-8", mode = "w")
    handler.setFormatter(logging.Formatter("[%(asctime)s | %(levelname)s] %(name)s\t%(message)s"))

    logger.addHandler(handler)

    # Instantiate bot
    bot = Fukurou(logger = logger, intents = intents)

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)
            
    bot.run()