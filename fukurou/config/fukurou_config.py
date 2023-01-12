import json
import logging
from os.path import exists
import sys

CONFIG_CLIENT_ID = 'client_id'
CONFIG_PERMISSIONS = 'permissions'
CONFIG_TOKEN = 'token'
CONFIG_ENABLE_LOGGER = 'enable_logger'

class FukurouConfig:
    FILE_PATH = './discord_token.json'
    DEFAULT_FORMAT = {
        CONFIG_CLIENT_ID: 'INSERT_CLIENTID_HERE',
        CONFIG_PERMISSIONS: 'INSERT_PERMISSIONS_HERE',
        CONFIG_TOKEN: 'INSERT_TOKEN_HERE',
        CONFIG_ENABLE_LOGGER: False
    }

    # Check if json file exists
    def exists(self): 
        return exists(self.FILE_PATH)
    
    # Initialize json for token
    def init(self, force_init = False):
        if not force_init and self.exists():
            return

        json_str = json.dumps(self.DEFAULT_FORMAT, sort_keys = True, indent = 4)

        file = open(self.FILE_PATH, "w")
        file.write(json_str)
        file.close()

    # Read a Client ID from json file
    def getClientId(self):
        deserialized = self.__readConfig()
        # self.logger.debug(f"Read client_id from {self.FILE_PATH}: " + deserialized[CONFIG_CLIENT_ID])

        try:
            return deserialized[CONFIG_CLIENT_ID]
        except:
            print(f'CONFIG: No attribute "{CONFIG_CLIENT_ID}" found!')
            sys.exit()

    # Read permissions from json file
    def getPermissions(self):
        deserialized = self.__readConfig()
        # self.logger.debug(f"Read permissions from {self.FILE_PATH}: " + deserialized[CONFIG_PERMISSIONS])

        try:
            return deserialized[CONFIG_PERMISSIONS]
        except:
            print(f'CONFIG: No attribute "{CONFIG_PERMISSIONS}" found!')
            sys.exit()

    # Read a token from json file
    def getToken(self):
        deserialized = self.__readConfig()
        # self.logger.debug(f"Read token from {self.FILE_PATH}: " + deserialized["token"])

        try:
            return deserialized[CONFIG_TOKEN]
        except:
            print(f'CONFIG: No attribute "{CONFIG_TOKEN}" found!')
            sys.exit()

    def getEnableLogger(self):
        deserialized = self.__readConfig()

        try:
            return deserialized[CONFIG_ENABLE_LOGGER]
        except:
            print(f'CONFIG: No attribute "{CONFIG_ENABLE_LOGGER}" found!')
            sys.exit()

    def getInviteLink(self):
        if not self.exists():
            self.logger.error(f"Cannot find {self.FILE_PATH}!")
            return None

        client_id = self.getClientId()
        permissions = self.getPermissions()

        return f"https://discord.com/oauth2/authorize?client_id={client_id}&permissions={permissions}&scope=bot"

    def __readConfig(self):
        if not self.exists():
            self.logger.error(f"Cannot find {self.FILE_PATH}!")
            return None

        file = open(self.FILE_PATH, "r")
        json_str = file.read()
        
        return json.loads(json_str)