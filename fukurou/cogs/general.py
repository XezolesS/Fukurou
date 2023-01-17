# pylint: disable = C0114, W0238, E1101
import discord
from discord import ApplicationContext
from discord.ext import commands

from fukurou.config import config
from fukurou.config.fukurou_config import FukurouConfig

class GeneralCog(commands.Cog):
    '''
    A collection of the commands for moving the bot around in you server.

    Attributes:
        bot: The instance of the bot that is executing the commands.
    '''
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name = 'ping', description = config.HELP_PING_SHORT)
    async def __ping(self, ctx: ApplicationContext):
        await ctx.respond('Pong')

    @commands.slash_command(name = 'addbot', description = config.HELP_ADDBOT_SHORT)
    async def __addbot(self, ctx: ApplicationContext):
        conf = FukurouConfig()

        embed = discord.Embed(
            title = 'Invite',
            description = f'{config.ADD_MESSAGE} {conf.get_invite_link()}'
        )

        await ctx.respond(embed = embed)

def setup(bot):
    bot.add_cog(GeneralCog(bot))
