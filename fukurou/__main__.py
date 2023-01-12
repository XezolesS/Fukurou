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

    # Instantiate bot
    bot = Fukurou(intents = intents)

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)
            
    bot.run()