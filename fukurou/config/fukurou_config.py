# pylint: disable = C0114, W0702
import json
from os.path import exists
import sys

CONFIG_CLIENT_ID = 'client_id'
CONFIG_PERMISSIONS = 'permissions'
CONFIG_TOKEN = 'token'
CONFIG_ENABLE_LOGGER = 'enable_logger'
DEFAULT_FORMAT = {
    CONFIG_CLIENT_ID: 'INSERT_CLIENTID_HERE',
    CONFIG_PERMISSIONS: 'INSERT_PERMISSIONS_HERE',
    CONFIG_TOKEN: 'INSERT_TOKEN_HERE',
    CONFIG_ENABLE_LOGGER: False
}

FILE_PATH = './discord_token.json'

class FukurouConfig:
    '''
    Config manager for Fukurou bot.
    '''

    def exists(self):
        '''Check if config gile exists.'''
        return exists(FILE_PATH)

    def init(self, force_init = False):
        '''Initialize config. Reset config file when "force_init = True".'''
        if not force_init and self.exists():
            return

        json_str = json.dumps(DEFAULT_FORMAT, sort_keys = True, indent = 4)

        with open(file = FILE_PATH, mode = 'w', encoding = 'utf-8') as file:
            file.write(json_str)

    def get_client_id(self):
        '''Read a Client ID from config file.'''
        deserialized = self.__read_config()

        try:
            return deserialized[CONFIG_CLIENT_ID]
        except:
            print(f'CONFIG: No attribute "{CONFIG_CLIENT_ID}" found!')
            sys.exit()

    def get_permissions(self):
        '''Read permissions from config file'''
        deserialized = self.__read_config()

        try:
            return deserialized[CONFIG_PERMISSIONS]
        except:
            print(f'CONFIG: No attribute "{CONFIG_PERMISSIONS}" found!')
            sys.exit()

    # Read a token from json file
    def get_token(self):
        '''Read a token from config file.'''
        deserialized = self.__read_config()

        try:
            return deserialized[CONFIG_TOKEN]
        except:
            print(f'CONFIG: No attribute "{CONFIG_TOKEN}" found!')
            sys.exit()

    def get_enable_logger(self):
        '''Read a enable_logger flag from config file.'''
        deserialized = self.__read_config()

        try:
            return deserialized[CONFIG_ENABLE_LOGGER]
        except:
            print(f'CONFIG: No attribute "{CONFIG_ENABLE_LOGGER}" found!')
            sys.exit()

    def get_invite_link(self):
        '''Read a config file and build invite link.'''
        if not self.exists():
            print(f'CONFIG: Cannot find {FILE_PATH}!')
            return None

        client_id = self.get_client_id()
        permissions = self.get_permissions()

        return f'https://discord.com/oauth2/authorize?client_id={client_id}&permissions={permissions}&scope=bot'

    def __read_config(self):
        if not self.exists():
            print(f'CONFIG: Cannot find {FILE_PATH}!')
            return None

        with open(file = FILE_PATH, mode = 'r', encoding = 'utf-8') as file:
            json_str = file.read()

        return json.loads(json_str)
