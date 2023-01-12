# pylint: disable = C0114
import os
import sys
import datetime
import logging
from discord import Guild

from .config.fukurou_config import FukurouConfig

LOGGER_FOLDER_NAME = 'logs'
LOGGER_PATH = os.path.join(os.path.realpath(os.path.curdir), LOGGER_FOLDER_NAME)
LOGGER_FORMAT_CONSOLE = '%(asctime)s  [%(name)s] [%(levelname)s] %(message)s'
LOGGER_FORMAT_FILE = '%(asctime)s  [%(levelname)s]\t%(message)s'
LOGGER_NAME = 'Fukurou'

class GuildLoggers():
    '''
    Loggers for each registered guild.

    Attributes:
        name (str): A logger name.
        level (int, _Level): A logger level.
    '''

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
        self.is_enabled = fukurou_config.get_enable_logger()
        self.loggers = {}

    def add_logger(self, guild: Guild) -> None:
        '''Add a logger for the guild.'''
        if guild is None:
            return

        # Check if directory exists
        log_dir = self.__get_dir(guild)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = logging.getLogger(f'{self.name}, {guild.name}')
        formatter = logging.Formatter(LOGGER_FORMAT_FILE)
        file_handler = logging.FileHandler(
            filename = self.__get_path(guild),
            mode = 'a',
            encoding = 'utf-8'
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.disabled = not self.is_enabled

        self.loggers[guild.id] = logger

    def get_logger(self, guild: Guild) -> logging.Logger:
        '''Get a logger object which is assigned for given guild.'''
        if guild is None:
            return None

        return self.loggers[guild.id]

    def __get_dir(self, guild: Guild):
        '''
        Get logger directory.\n
        format: {LOGGER_PATH}/{guild.id}
        '''
        if guild is None:
            return None

        return os.path.join(LOGGER_PATH, f'{guild.id}')

    def __get_path(self, guild: Guild) -> str:
        '''
        Get logger path.\n
        format: {LOGGER_PATH}/{guild.id}/{today}.log
        '''
        if guild is None:
            return None

        return os.path.join(self.__get_dir(guild), f'{datetime.date.today()}.log')
