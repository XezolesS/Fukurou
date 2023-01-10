import discord
from discord import ApplicationContext
from config import config
from discord.ext import commands
from discord.ext.commands import has_permissions
import utils
from ext.music import AudioController
from utils import guild_to_audiocontroller, guild_to_settings

class General(commands.Cog):
    """ A collection of the commands for moving the bot around in you server.

        Attributes:
            bot: The instance of the bot that is executing the commands.
    """

    def __init__(self, bot):
        self.bot = bot

    # logic is split to uconnect() for wide usage
    @commands.slash_command(name='connect', description=config.HELP_CONNECT_SHORT)
    async def __connect(self, ctx: ApplicationContext):  # dest_channel_name: str
        audiocontroller = utils.guild_to_audiocontroller[ctx.guild]
        
        await audiocontroller.uconnect(ctx)
        await ctx.respond(f'Connected to {ctx.voice_client.channel}')

    @commands.slash_command(name='disconnect', description=config.HELP_DISCONNECT_SHORT)
    async def __disconnect(self, ctx: ApplicationContext):
        connected_channel = ctx.voice_client.channel;
        audiocontroller = utils.guild_to_audiocontroller[ctx.guild]

        await audiocontroller.udisconnect()
        await ctx.respond(f'Disconnected from {connected_channel}')

    @commands.slash_command(name='reset', description=config.HELP_DISCONNECT_SHORT)
    async def __reset(self, ctx: ApplicationContext):
        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        await utils.guild_to_audiocontroller[ctx.guild].stop_player()
        await ctx.guild.voice_client.disconnect(force=True)

        guild_to_audiocontroller[ctx.guild] = AudioController(self.bot, ctx.guild)
        await guild_to_audiocontroller[ctx.guild].register_voice_channel(ctx.author.voice.channel)

        await ctx.respond("{} Connected to {}".format(":white_check_mark:", ctx.author.voice.channel.name))

    @commands.slash_command(name='changechannel', description=config.HELP_CHANGECHANNEL_SHORT)
    async def __changechannel(self, ctx: ApplicationContext):
        vchannel = await utils.is_connected(ctx)
        if vchannel == ctx.author.voice.channel:
            await ctx.respond("{} Already connected to {}".format(":white_check_mark:", vchannel.name))
            return

        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        await utils.guild_to_audiocontroller[ctx.guild].stop_player()
        await ctx.guild.voice_client.disconnect(force=True)

        guild_to_audiocontroller[ctx.guild] = AudioController(
            self.bot, ctx.guild)
        await guild_to_audiocontroller[ctx.guild].register_voice_channel(ctx.author.voice.channel)

        await ctx.respond("{} Switched to {}".format(":white_check_mark:", ctx.author.voice.channel.name))

    @commands.slash_command(name='ping', description=config.HELP_PING_SHORT)
    async def __ping(self, ctx: ApplicationContext):
        await ctx.respond("Pong")

    @commands.slash_command(name='setting', description=config.HELP_SETTINGS_SHORT)
    @has_permissions(administrator=True)
    async def __setting(self, ctx: ApplicationContext, *args):

        sett = guild_to_settings[ctx.guild]

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
    bot.add_cog(General(bot))
