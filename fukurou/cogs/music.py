# pylint: disable = C0114, W0238, W0702
import discord
from discord import (
    ApplicationContext,
    ApplicationCommandError,
    Guild
)
from discord.commands import SlashCommandGroup
from discord.ext import commands

from fukurou.config import config
from fukurou.enums import (
    Origin
)
from fukurou.ext.music import (
    MusicSettings,
    get_music
)

class MusicCog(commands.Cog):
    '''
    A collection of the commands related to music playback.

    Attributes:
        bot: The instance of the bot that is executing the music.
    '''
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = {}

    music = SlashCommandGroup(
        name = 'music',
        description = 'Commands about playing music!'
    )

    # configs = music.create_subgroup(
    #    name = 'config',
    #    description = 'Configs about music.'
    # )

    def cog_check(self, ctx: ApplicationContext):
        # Check command channel
        self.__register_guild_command_channel(ctx.guild)

        if self.channel_id[ctx.guild.id] == -1:
            return True

        return self.channel_id[ctx.guild.id] == ctx.channel.id

    async def cog_command_error(self, ctx: ApplicationContext, error: ApplicationCommandError):
        if self.channel_id[ctx.guild.id] != ctx.channel.id:
            await ctx.respond('You cannot use music commands in this channel!\n' +
                              f'Try it on <#{self.channel_id[ctx.guild.id]}>', ephemeral = True)
            return

        await ctx.respond(error, ephemeral = True)

    @music.command(
        name = 'play',
        description = config.HELP_YT_SHORT
    )
    async def __play(self, ctx: ApplicationContext, *, track: str):
        player = self.bot.players[ctx.guild.id]

        # Check if the author is currently in the channel.
        if ctx.author.voice is None:
            await ctx.message('You are not in the voice channel!')
            return

        # Check if the bot is not connected to author's channel.
        # If it's not, try to join to the channel.
        if not player.is_connected(ctx.author.voice.channel):
            if await player.connect(ctx) is False:
                return

        if track.isspace() or not track:
            return

        music = get_music(track)

        if music is None:
            await ctx.respond(config.SONGINFO_ERROR)
            return

        if music.origin == Origin.Default:
            player.add_track(music)

            if not player.is_playing():
                await player.play()
                await ctx.respond(embed = music.to_embed(config.SONGINFO_NOW_PLAYING))
            else:
                await ctx.respond(embed = music.to_embed(config.SONGINFO_QUEUE_ADDED))
        elif music.origin == Origin.Playlist:
            await ctx.respond(config.SONGINFO_PLAYLIST_QUEUED)

    @music.command(
        name = 'stop',
        description = config.HELP_STOP_SHORT
    )
    async def __stop(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        if not player.is_playing():
            return

        player.stop()
        await ctx.respond('Stopped all sessions :octagonal_sign:')

    @music.command(
        name = 'pause',
        description = config.HELP_PAUSE_SHORT
    )
    async def __pause(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        if not player.is_playing():
            await ctx.respond('The player is not playing.')
            return

        player.pause()
        await ctx.respond('Playback Paused :pause_button:')

    @music.command(
        name = 'resume',
        description = config.HELP_RESUME_SHORT
    )
    async def __resume(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        if not player.is_paused():
            await ctx.respond('The player is not paused.')
            return

        player.resume()
        await ctx.respond('Resumed playback :arrow_forward:')

    @music.command(
        name = 'skip',
        description = config.HELP_SKIP_SHORT
    )
    async def __skip(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        if not player.is_playing():
            await ctx.respond('The player is not playing.')
            return

        player.skip()
        await ctx.respond('Skipped current song :fast_forward:')

    @music.command(
        name = 'previous',
        description = config.HELP_PREV_SHORT
    )
    async def __previous(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        if not player.is_playing():
            await ctx.respond('The player is not playing.')
            return

        player.previous()
        await ctx.respond('Playing previous song :track_previous:')

    @music.command(
        name = 'nowplaying',
        description = config.HELP_SONGINFO_SHORT
    )
    async def _nowplaying(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        if not player.is_playing():
            await ctx.respond('The player is not playing.')
            return

        playing = player.current_track

        await ctx.respond(embed = playing.format_output(config.SONGINFO_SONGINFO))

    @music.command(
        name = 'queue',
        description = config.HELP_QUEUE_SHORT
    )
    async def __queue(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        if player.playlist.is_empty():
            await ctx.respond('Queue is empty :x:')
            return

        # Embeds are limited to 25 fields
        config.MAX_SONG_PRELOAD = min(config.MAX_SONG_PRELOAD, 25)

        embed = discord.Embed(
            title = f':scroll: Queue [{player.playlist.queue}]',
            color = config.EMBED_COLOR
        )

        playlist_list = list(player.playlist.queue)[:config.MAX_SONG_PRELOAD]
        for counter, music in enumerate(playlist_list, start = 1):
            if music.title is None:
                embed.add_field(
                    name = f'{counter}.',
                    value = f'[{music.webpage_url}]({music.webpage_url})',
                    inline = False
                )
            else:
                embed.add_field(
                    name = f'{counter}.',
                    value = f'[{music.title}]({music.webpage_url})',
                    inline = False
                )

        await ctx.respond(embed = embed)

    @music.command(
        name = 'history',
        description = config.HELP_HISTORY_SHORT
    )
    async def __history(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        if player.playlist.is_history_empty():
            await ctx.respond('History is empty :x:')
            return

        # Embeds are limited to 25 fields
        config.MAX_HISTORY_LENGTH = min(config.MAX_HISTORY_LENGTH, 25)

        embed = discord.Embed(
            title = f':scroll: History [{player.playlist.history}]',
            color=config.EMBED_COLOR
        )

        history_list = list(player.playlist.history)[:config.MAX_HISTORY_LENGTH]
        for counter, music in enumerate(history_list, start = 1):
            if music.title is None:
                embed.add_field(
                    name = f'{counter}.',
                    value = f'[{music.webpage_url}]({music.webpage_url})',
                    inline = False
                )
            else:
                embed.add_field(
                    name = f'{counter}.',
                    value = '[{music.title}]({music.webpage_url})',
                    inline = False
                )

        await ctx.respond(embed = embed)

    @music.command(
        name = 'loop',
        description = config.HELP_LOOP_SHORT
    )
    async def __loop(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        toggled = player.toggle_loop()
        if toggled:
            await ctx.respond('Loop enabled :arrows_counterclockwise:')
        else:
            await ctx.respond('Loop disabled :x:')

    @music.command(
        name = 'shuffle',
        description = config.HELP_SHUFFLE_SHORT
    )
    async def __shuffle(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        if player.playlist.is_empty():
            await ctx.respond('Queue is empty :x:')
            return

        player.playlist.shuffle()
        await ctx.respond('Shuffled queue :twisted_rightwards_arrows:')

    @music.command(
        name = 'volume',
        description = config.HELP_VOL_SHORT
    )
    @discord.commands.option(
        name = 'amount',
        description = 'Set the volume in % (100 to 0)',
        input_type = int,
        min_value = 0,
        max_value = 100,
        required = False
    )
    async def __volume(self, ctx: ApplicationContext, amount: int):
        player = self.bot.players[ctx.guild.id]

        if amount is None:
            await ctx.respond(f'Current volume: {player.volume}% :speaker:')
            return

        if player.set_volume(amount):
            await ctx.respond(f'Volume set to {amount}% :loud_sound:')
        else:
            await ctx.respond('Failed to change volume.')

    @music.command(
        name = 'command_channel',
        description = 'Set the only channel in where the commands are allowed to be called.'
    )
    @discord.commands.option(
        name = 'channel',
        description = 'Text channel to call music commands on. Empty to set anywhere.',
        input_type = discord.TextChannel,
        required = False
    )
    async def __command_channel(self, ctx: ApplicationContext, channel: discord.TextChannel):
        settings = self.__get_guild_settings(ctx.guild)

        if channel is None:
            settings.set_command_channel()
            self.__register_guild_command_channel(ctx.guild, reload = True)

            await ctx.respond('Music commands are now can be used in anywhere.')
            return

        settings.set_command_channel(channel.id)
        self.__register_guild_command_channel(ctx.guild, reload = True)

        await ctx.respond(f'Now you can use music command only in #{channel.name}')

    def __get_guild_settings(self, guild: Guild) -> MusicSettings:
        return self.bot.settings.get_settings(guild)

    def __register_guild_command_channel(self, guild: Guild, reload: bool = False) -> None:
        settings = self.__get_guild_settings(guild)

        if reload is True or guild.id not in self.channel_id:
            self.channel_id[guild.id] = settings.get_command_channel()

def setup(bot):
    bot.add_cog(MusicCog(bot))
