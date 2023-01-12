import datetime
import discord
from discord import Guild
import logging
import os
import sys

from .config.fukurou_config import FukurouConfig

LOGGER_FOLDER_NAME = 'logs'
LOGGER_PATH = os.path.join(os.path.realpath(os.path.curdir), LOGGER_FOLDER_NAME)
LOGGER_FORMAT_CONSOLE = "%(asctime)s  [%(name)s] [%(levelname)s] %(message)s"
LOGGER_FORMAT_FILE = "%(asctime)s  [%(levelname)s]\t%(message)s"
LOGGER_NAME = 'Fukurou'

class GuildLoggers():
    def __init__(self, name: str = LOGGER_NAME, level: int = logging.INFO) -> None:
        # Setup global logger configuration
        logging.basicConfig(
            level = level,
            format = LOGGER_FORMAT_CONSOLE,
            handlers = [logging.StreamHandler(sys.stdout)]
        )

        fukurou_config = FukurouConfig()
        fukurou_config.init()

        self.name = name
        self.is_enabled = fukurou_config.getEnableLogger()
        self.Loggers = {}

    def addLogger(self, guild: Guild) -> None:
        if guild is None:
            return

        # Check if directory exists
        dir = self.__getLoggerDirectory(guild)
        if not os.path.exists(dir):
            os.makedirs(dir)

        logger = logging.getLogger(f'{self.name}, {guild.name}')
        formatter = logging.Formatter(LOGGER_FORMAT_FILE)
        file_handler = logging.FileHandler(
            filename = self.__getLoggerPath(guild),
            mode = 'a',
            encoding = 'utf-8'
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.disabled = not self.is_enabled

        self.Loggers[guild.id] = logger

    def getLogger(self, guild: Guild) -> logging.Logger:
        if guild is None:
            return

        return self.Loggers[guild.id]

    def __getLoggerDirectory(self, guild: Guild):
        """
            Get logger directory\n
            format: {LOGGER_PATH}/{guild.id}
        """
        if guild is None:
            return

        return os.path.join(LOGGER_PATH, f'{guild.id}')

    def __getLoggerPath(self, guild: Guild) -> str:
        """
            Get logger path\n
            format: {LOGGER_PATH}/{guild.id}/{today}.log
        """
        if guild is None:
            return

        return os.path.join(self.__getLoggerDirectory(guild), f'{datetime.date.today()}.log')