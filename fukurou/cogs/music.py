import asyncio
import discord
from discord import ApplicationContext
from config import config
from discord.ext import commands
import linkutils
import utils

class Music(commands.Cog):
    """ A collection of the commands related to music playback.

        Attributes:
            bot: The instance of the bot that is executing the commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='play', description=config.HELP_YT_SHORT)
    async def __play(self, ctx: ApplicationContext, *, track: str):
        audiocontroller = utils.guild_to_audiocontroller[ctx.guild]

        if (await utils.is_connected(ctx) == None):
            if await audiocontroller.uconnect(ctx) == False:
                return

        if track.isspace() or not track:
            return

        if await utils.play_check(ctx) == False:
            return

        # reset timer
        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)

        if audiocontroller.playlist.loop == True:
            await ctx.respond("Loop is enabled! Use {}loop to disable".format(config.BOT_PREFIX))
            return

        song = await audiocontroller.process_song(track)

        if song is None:
            await ctx.respond(config.SONGINFO_ERROR)
            return

        if song.origin == linkutils.Origin.Default:

            if audiocontroller.current_song != None and len(audiocontroller.playlist.playque) == 0:
                await ctx.respond(embed=song.format_output(config.SONGINFO_NOW_PLAYING))
            else:
                await ctx.respond(embed=song.format_output(config.SONGINFO_QUEUE_ADDED))

        elif song.origin == linkutils.Origin.Playlist:
            await ctx.respond(config.SONGINFO_PLAYLIST_QUEUED)

    @commands.slash_command(name='loop', description=config.HELP_LOOP_SHORT)
    async def __loop(self, ctx: ApplicationContext):
        audiocontroller = utils.guild_to_audiocontroller[ctx.guild]

        if await utils.play_check(ctx) == False:
            return

        if len(audiocontroller.playlist.playque) < 1 and ctx.guild.voice_client.is_playing() == False:
            await ctx.respond("No songs in queue!")
            return

        if audiocontroller.playlist.loop == False:
            audiocontroller.playlist.loop = True
            await ctx.respond("Loop enabled :arrows_counterclockwise:")
        else:
            audiocontroller.playlist.loop = False
            await ctx.respond("Loop disabled :x:")

    @commands.slash_command(name='shuffle', description=config.HELP_SHUFFLE_SHORT)
    async def __shuffle(self, ctx: ApplicationContext):
        audiocontroller = utils.guild_to_audiocontroller[ctx.guild]

        if await utils.play_check(ctx) == False:
            return

        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        if ctx.guild.voice_client is None or not ctx.guild.voice_client.is_playing():
            await ctx.respond("Queue is empty :x:")
            return

        audiocontroller.playlist.shuffle()
        await ctx.respond("Shuffled queue :twisted_rightwards_arrows:")

        for song in list(audiocontroller.playlist.playque)[:config.MAX_SONG_PRELOAD]:
            asyncio.ensure_future(audiocontroller.preload(song))

    @commands.slash_command(name='pause', description=config.HELP_PAUSE_SHORT)
    async def __pause(self, ctx: ApplicationContext):
        if await utils.play_check(ctx) == False:
            return

        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        if ctx.guild.voice_client is None or not ctx.guild.voice_client.is_playing():
            return
        ctx.guild.voice_client.pause()
        await ctx.respond("Playback Paused :pause_button:")

    @commands.slash_command(name='queue', description=config.HELP_QUEUE_SHORT)
    async def __queue(self, ctx: ApplicationContext):
        if await utils.play_check(ctx) == False:
            return

        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return

        if ctx.guild.voice_client is None or not ctx.guild.voice_client.is_playing():
            await ctx.respond("Queue is empty :x:")
            return

        playlist = utils.guild_to_audiocontroller[ctx.guild].playlist

        # Embeds are limited to 25 fields
        if config.MAX_SONG_PRELOAD > 25:
            config.MAX_SONG_PRELOAD = 25

        embed = discord.Embed(title=":scroll: Queue [{}]".format(
            len(playlist.playque)), color=config.EMBED_COLOR, inline=False)

        for counter, song in enumerate(list(playlist.playque)[:config.MAX_SONG_PRELOAD], start=1):
            if song.info.title is None:
                embed.add_field(name="{}.".format(str(counter)), value="[{}]({})".format(
                    song.info.webpage_url, song.info.webpage_url), inline=False)
            else:
                embed.add_field(name="{}.".format(str(counter)), value="[{}]({})".format(
                    song.info.title, song.info.webpage_url), inline=False)

        await ctx.respond(embed=embed)

    @commands.slash_command(name='stop', description=config.HELP_STOP_SHORT)
    async def __stop(self, ctx: ApplicationContext):
        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[ctx.guild]
        audiocontroller.playlist.loop = False
        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        await utils.guild_to_audiocontroller[ctx.guild].stop_player()
        await ctx.respond("Stopped all sessions :octagonal_sign:")

    @commands.slash_command(name='move', description=config.HELP_MOVE_SHORT)
    async def __move(self, ctx: ApplicationContext, *args):
        if len(args) != 2:
            ctx.respond("Wrong number of arguments")
            return

        try:
            oldindex, newindex = map(int, args)
        except ValueError:
            ctx.respond("Wrong argument")
            return

        audiocontroller = utils.guild_to_audiocontroller[ctx.guild]
        if ctx.guild.voice_client is None or (
                not ctx.guild.voice_client.is_paused() and not ctx.guild.voice_client.is_playing()):
            await ctx.respond("Queue is empty :x:")
            return
        try:
            audiocontroller.playlist.move(oldindex - 1, newindex - 1)
        except IndexError:
            await ctx.respond("Wrong position")
            return
        await ctx.respond("Moved")

    @commands.slash_command(name='skip', description=config.HELP_SKIP_SHORT)
    async def __skip(self, ctx: ApplicationContext):
        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[ctx.guild]
        audiocontroller.playlist.loop = False

        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)

        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        if ctx.guild.voice_client is None or (
                not ctx.guild.voice_client.is_paused() and not ctx.guild.voice_client.is_playing()):
            await ctx.respond("Queue is empty :x:")
            return
        ctx.guild.voice_client.stop()
        await ctx.respond("Skipped current song :fast_forward:")

    @commands.slash_command(name='clear', description=config.HELP_CLEAR_SHORT)
    async def __clear(self, ctx: ApplicationContext):
        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[ctx.guild]
        audiocontroller.clear_queue()
        ctx.guild.voice_client.stop()
        audiocontroller.playlist.loop = False
        await ctx.respond("Cleared queue :no_entry_sign:")

    @commands.slash_command(name='previous', description=config.HELP_PREV_SHORT)
    async def __previous(self, ctx: ApplicationContext):
        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[ctx.guild]
        audiocontroller.playlist.loop = False

        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)

        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        await utils.guild_to_audiocontroller[ctx.guild].prev_song()
        await ctx.respond("Playing previous song :track_previous:")

    @commands.slash_command(name='resume', description=config.HELP_RESUME_SHORT)
    async def __resume(self, ctx: ApplicationContext):
        if await utils.play_check(ctx) == False:
            return

        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        ctx.guild.voice_client.resume()
        await ctx.respond("Resumed playback :arrow_forward:")

    @commands.slash_command(name='songinfo', description=config.HELP_SONGINFO_SHORT)
    async def _songinfo(self, ctx: ApplicationContext):
        if await utils.play_check(ctx) == False:
            return

        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        song = utils.guild_to_audiocontroller[ctx.guild].current_song
        if song is None:
            return
        await ctx.respond(embed=song.format_output(config.SONGINFO_SONGINFO))

    @commands.slash_command(name='history', description=config.HELP_HISTORY_SHORT)
    async def __history(self, ctx: ApplicationContext):
        if await utils.play_check(ctx) == False:
            return

        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        await ctx.respond(utils.guild_to_audiocontroller[ctx.guild].track_history())

    @commands.slash_command(name='volume', description=config.HELP_VOL_SHORT)
    async def __volume(self, ctx: ApplicationContext, *args):
        if ctx.guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return

        if await utils.play_check(ctx) == False:
            return

        if len(args) == 0:
            await ctx.respond("Current volume: {}% :speaker:".format(utils.guild_to_audiocontroller[ctx.guild]._volume))
            return

        try:
            volume = args[0]
            volume = int(volume)
            if volume > 100 or volume < 0:
                raise Exception('')
            current_guild = utils.get_guild(self.bot, ctx.message)

            if utils.guild_to_audiocontroller[current_guild]._volume >= volume:
                await ctx.respond('Volume set to {}% :sound:'.format(str(volume)))
            else:
                await ctx.respond('Volume set to {}% :loud_sound:'.format(str(volume)))
            utils.guild_to_audiocontroller[current_guild].volume = volume
        except:
            await ctx.respond("Error: Volume must be a number 1-100")

def setup(bot):
    bot.add_cog(Music(bot))
