import discord
from discord import ApplicationContext
from discord.ext import commands
from discord.ext.commands import has_permissions

from fukurou.config import config
from fukurou.ext.music import Player
from fukurou.fukurou import Fukurou

class GeneralCog(commands.Cog):
    """ A collection of the commands for moving the bot around in you server.

        Attributes:
            bot: The instance of the bot that is executing the commands.
    """
    def __init__(self, bot: Fukurou):
        self.bot = bot

    @commands.slash_command(name='connect', description=config.HELP_CONNECT_SHORT)
    async def __connect(self, ctx: ApplicationContext):  # dest_channel_name: str
        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return

        player = self.bot.players[ctx.guild.id]
        
        await player.connect(ctx)
        await ctx.respond(f'Connected to {ctx.voice_client.channel}')

    @commands.slash_command(name='disconnect', description=config.HELP_DISCONNECT_SHORT)
    async def __disconnect(self, ctx: ApplicationContext):
        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return

        connected_channel = ctx.voice_client.channel
        player = self.bot.players[ctx.guild.id]

        await player.disconnect()
        await ctx.respond(f'Disconnected from {connected_channel}')

    @commands.slash_command(name='reset', description=config.HELP_DISCONNECT_SHORT)
    async def __reset(self, ctx: ApplicationContext):
        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        
        player = self.bot.players[ctx.guild.id]
        await player.stop()

        player = Player(self.bot, ctx.guild)
        await player.connect(ctx)

        await ctx.respond("{} Connected to {}".format(":white_check_mark:", ctx.voice_client.channel))

    @commands.slash_command(name='switch', description=config.HELP_CHANGECHANNEL_SHORT)
    async def __switch(self, ctx: ApplicationContext):
        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return

        player = self.bot.players[ctx.guild.id]
        if not player.is_connected():
            await player.connect(ctx)
            await ctx.respond(f'Connected to {ctx.voice_client.channel}')
            return

        previous_channel = player.guild.voice_client.channel
        if previous_channel == ctx.author.voice.channel:
            await ctx.respond("{} Already connected to {}".format(":white_check_mark:", previous_channel))
            return

        await player.stop()
        await player.disconnect()

        player = Player(self.bot, ctx.guild)
        await player.connect(ctx)

        await ctx.respond("{} Switched to {}".format(":white_check_mark:", ctx.voice_client.channel))

    @commands.slash_command(name='ping', description=config.HELP_PING_SHORT)
    async def __ping(self, ctx: ApplicationContext):
        await ctx.respond("Pong")

    @commands.slash_command(name='setting', description=config.HELP_SETTINGS_SHORT)
    @has_permissions(administrator=True)
    async def __setting(self, ctx: ApplicationContext, *args):
        sett = self.bot.settings[ctx.guild]

        if len(args) == 0:
            await ctx.respond(embed=await sett.format())
            return

        args_list = list(args)
        args_list.remove(args[0])

        response = await sett.write(args[0], " ".join(args_list), ctx)

        if response is None:
            await ctx.respond("`Error: Setting not found`")
        elif response is True:
            await ctx.respond("Setting updated!")

    @commands.slash_command(name='addbot', description=config.HELP_ADDBOT_SHORT)
    async def __addbot(self, ctx: ApplicationContext):
        embed = discord.Embed(title="Invite", description=config.ADD_MESSAGE +
                              "(https://discordapp.com/oauth2/authorize?client_id={}&scope=bot>)".format(self.bot.user.id))

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(GeneralCog(bot))
