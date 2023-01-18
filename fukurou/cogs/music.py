# pylint: disable = C0114, W0238, W0702
import discord
from discord import (
    ApplicationContext,
    ApplicationCommandError,
    Guild
)
from discord.ext import (
    commands,
    pages
)

from fukurou.config import config
from fukurou.ext.music import (
    MusicSettings,
    Music,
    to_musiclist
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

    music_commands = discord.SlashCommandGroup(
        name = 'music',
        description = 'Commands about playing music!',
        guild_only = True
    )

    # configs = music.create_subgroup(
    #    name = 'config',
    #    description = 'Configs about music.'
    # )

    def cog_check(self, ctx: ApplicationContext) -> None:
        # Check command channel
        def predicate_command_channel(ctx: ApplicationContext) -> bool:
            self.__register_guild_command_channel(ctx.guild)

            # Allow all channel
            if self.channel_id[ctx.guild.id] == -1:
                return True

            # Check if it's music channel
            if self.channel_id[ctx.guild.id] != ctx.channel.id:
                raise commands.CheckFailure('You cannot use music commands in this channel!\n' +
                                           f'Try it on <#{self.channel_id[ctx.guild.id]}>')

            return True

        return (
            super().cog_check(ctx) and
            predicate_command_channel(ctx)
        )

    async def cog_command_error(self, ctx: ApplicationContext, error: ApplicationCommandError) -> None:
        await ctx.respond(error, ephemeral = True)

    @commands.slash_command(
        name = 'connect',
        description = config.HELP_CONNECT_SHORT,
        guild_only = True
    )
    async def __connect(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        # Client connected check
        if ctx.author.voice is None:
            raise commands.CheckFailure("You're not in the voice channel!")

        await player.connect(ctx)
        await ctx.respond(f'Connected to {ctx.voice_client.channel}')

    @commands.slash_command(
        name = 'disconnect',
        description = config.HELP_DISCONNECT_SHORT,
        guild_only = True
    )
    async def __disconnect(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        # Not connected check
        if not player.is_connected():
            raise commands.CheckFailure("I'm not in the voice channel now!")

        connected_channel = ctx.voice_client.channel

        await player.disconnect()
        await ctx.respond(f'Disconnected from {connected_channel}')

    @commands.slash_command(
        name = 'switch',
        description = config.HELP_CHANGECHANNEL_SHORT,
        guild_only = True
    )
    async def __switch(self, ctx: ApplicationContext):
        player = self.bot.players[ctx.guild.id]

        # Client connected check
        if ctx.author.voice is None:
            raise commands.CheckFailure("You're not in the voice channel!")

        # Not connected check
        # If not connected, connect to the channel.
        if not player.is_connected():
            if await player.connect(ctx) is False:
                raise commands.CheckFailure('Cannot connected to voice channel.')

        # Channel not changed check
        if player.guild.voice_client.channel == ctx.author.voice.channel:
            raise commands.CheckFailure(f'Already connected to {player.guild.voice_client.channel}')

        await player.reconnect(ctx)
        await ctx.respond(f':white_check_mark: Switched to {ctx.voice_client.channel}')

    @music_commands.command(
        name = 'play',
        description = config.HELP_YT_SHORT,
        options = [
            discord.Option(
                str,
                name = 'track',
                description = 'Search keyword or URL of the song to play',
                required = True
            )
        ]
    )
    async def __play(self, ctx: ApplicationContext, *, track: str) -> None:
        player = self.bot.players[ctx.guild.id]

        # Client connected check
        if ctx.author.voice is None:
            raise commands.CheckFailure("You're not in the voice channel!")

        # Not connected check
        # If not connected, connect to the channel.
        if not player.is_connected(ctx.author.voice.channel):
            if await player.connect(ctx) is False:
                raise commands.CheckFailure('Cannot connected to voice channel.')

        # Response setup
        await ctx.response.defer()
        message = await ctx.followup.send('Loading...')

        # Resolve links to list of musics.
        musics = await to_musiclist(track)

        # Unknown music check
        if musics is None or len(musics) == 0:
            raise commands.CheckFailure(config.SONGINFO_ERROR)

        for music in musics:
            player.add_track(music)

        if not player.is_playing():
            await player.play()

        await ctx.followup.edit_message(
            message_id = message.id,
            content = '',
            embed = player.current_track.to_embed(f'{len(musics)} Music(s) are added to the queue!')
        )

    @music_commands.command(
        name = 'stop',
        description = config.HELP_STOP_SHORT
    )
    async def __stop(self, ctx: ApplicationContext) -> None:
        player = self.bot.players[ctx.guild.id]

        if not player.is_playing():
            return

        player.stop()
        await ctx.respond('Stopped all sessions :octagonal_sign:')

    @music_commands.command(
        name = 'pause',
        description = config.HELP_PAUSE_SHORT
    )
    async def __pause(self, ctx: ApplicationContext) -> None:
        player = self.bot.players[ctx.guild.id]

        if not player.is_playing():
            await ctx.respond('The player is not playing.')
            return

        player.pause()
        await ctx.respond('Playback Paused :pause_button:')

    @music_commands.command(
        name = 'resume',
        description = config.HELP_RESUME_SHORT
    )
    async def __resume(self, ctx: ApplicationContext) -> None:
        player = self.bot.players[ctx.guild.id]

        if not player.is_paused():
            await ctx.respond('The player is not paused.')
            return

        player.resume()
        await ctx.respond('Resumed playback :arrow_forward:')

    @music_commands.command(
        name = 'skip',
        description = config.HELP_SKIP_SHORT
    )
    async def __skip(self, ctx: ApplicationContext) -> None:
        player = self.bot.players[ctx.guild.id]

        if not player.is_playing():
            await ctx.respond('The player is not playing.')
            return

        player.skip()
        await ctx.respond('Skipped current song :fast_forward:')

    @music_commands.command(
        name = 'previous',
        description = config.HELP_PREV_SHORT
    )
    async def __previous(self, ctx: ApplicationContext) -> None:
        player = self.bot.players[ctx.guild.id]

        if not player.is_playing():
            await ctx.respond('The player is not playing.')
            return

        player.previous()
        await ctx.respond('Playing previous song :track_previous:')

    @music_commands.command(
        name = 'nowplaying',
        description = config.HELP_SONGINFO_SHORT
    )
    async def __nowplaying(self, ctx: ApplicationContext) -> None:
        player = self.bot.players[ctx.guild.id]

        if not player.is_playing():
            await ctx.respond('The player is not playing.')
            return

        playing = player.current_track

        await ctx.respond(embed = playing.to_embed(config.SONGINFO_SONGINFO))

    @music_commands.command(
        name = 'queue',
        description = config.HELP_QUEUE_SHORT
    )
    async def __queue(self, ctx: ApplicationContext) -> None:
        player = self.bot.players[ctx.guild.id]

        if player.playlist.is_empty():
            await ctx.respond('Queue is empty :x:')
            return

        playlist_page = PlaylistPage(playlist = player.playlist.queue, title = 'Queue')
        await playlist_page.respond(ctx.interaction, ephemeral = True)

    @music_commands.command(
        name = 'history',
        description = config.HELP_HISTORY_SHORT
    )
    async def __history(self, ctx: ApplicationContext) -> None:
        player = self.bot.players[ctx.guild.id]

        if player.playlist.is_history_empty():
            await ctx.respond('History is empty :x:')
            return

        playlist_page = PlaylistPage(playlist = player.playlist.history, title = 'History')
        await playlist_page.respond(ctx.interaction, ephemeral = True)

    @music_commands.command(
        name = 'loop',
        description = config.HELP_LOOP_SHORT
    )
    async def __loop(self, ctx: ApplicationContext) -> None:
        player = self.bot.players[ctx.guild.id]

        toggled = player.toggle_loop()
        if toggled:
            await ctx.respond('Loop enabled :arrows_counterclockwise:')
        else:
            await ctx.respond('Loop disabled :x:')

    @music_commands.command(
        name = 'shuffle',
        description = config.HELP_SHUFFLE_SHORT
    )
    async def __shuffle(self, ctx: ApplicationContext) -> None:
        player = self.bot.players[ctx.guild.id]

        if player.playlist.is_empty():
            await ctx.respond('Queue is empty :x:')
            return

        player.playlist.shuffle()
        await ctx.respond('Shuffled queue :twisted_rightwards_arrows:')

    @music_commands.command(
        name = 'volume',
        description = config.HELP_VOL_SHORT,
        options = [
            discord.Option(
                int,
                name = 'amount',
                description = 'Set the volume in % (100 to 0)',
                min_value = 0,
                max_value = 100,
                required = False
            )
        ]
    )
    async def __volume(self, ctx: ApplicationContext, amount: int) -> None:
        player = self.bot.players[ctx.guild.id]

        if amount is None:
            await ctx.respond(f'Current volume: {player.volume}% :speaker:')
            return

        if player.set_volume(amount):
            await ctx.respond(f'Volume set to {amount}% :loud_sound:')
        else:
            await ctx.respond('Failed to change volume.')

    @music_commands.command(
        name = 'command_channel',
        description = 'Set the only channel in where the commands are allowed to be called.',
        options = [
            discord.Option(
                discord.TextChannel,
                name = 'channel',
                description = 'Text channel to call music commands on. Empty to set anywhere.',
                required = False
            )
        ],
        default_member_permissions = discord.Permissions(manage_channels = True)
    )
    # @commands.has_permissions(manage_channels = True)
    async def __command_channel(self, ctx: ApplicationContext, channel: discord.TextChannel) -> None:
        settings = self.__get_guild_settings(ctx.guild)

        if channel is None:
            settings.set_command_channel()
            self.__register_guild_command_channel(ctx.guild, reload = True)

            await ctx.respond('Music commands are now can be used in anywhere.')
            return

        settings.set_command_channel(channel.id)
        self.__register_guild_command_channel(ctx.guild, reload = True)

        await ctx.respond(f'Now you can use music command only in #{channel.name}')

    @music_commands.command(
        name = 'player',
        description = 'Opens music player.',
    )
    async def __player(self, ctx: ApplicationContext):
        await ctx.respond(view = PlayerView(ctx = ctx))

    def __get_guild_settings(self, guild: Guild) -> MusicSettings:
        return self.bot.settings.get_settings(guild)

    def __register_guild_command_channel(self, guild: Guild, reload: bool = False) -> None:
        settings = self.__get_guild_settings(guild)

        if reload is True or guild.id not in self.channel_id:
            self.channel_id[guild.id] = settings.get_command_channel()

class PlayerView(discord.ui.View):
    def __init__(self, *items: discord.ui.Item, ctx: ApplicationContext, timeout: float | None = 180, disable_on_timeout: bool = False):
        super().__init__(*items, timeout = timeout, disable_on_timeout = disable_on_timeout)

        self.context = ctx

        # Command initialization
        self.commands = {}

        for cmd in self.context.bot.get_cog('MusicCog').walk_commands():
            if 'music ' not in cmd.qualified_name:
                continue

            self.commands[cmd.name] = cmd

    @discord.ui.button(
        style = discord.ButtonStyle.gray,
        label = 'Prev',
        emoji = '\N{Black Left-Pointing Double Triangle with Vertical Bar}'
    )
    async def __button_previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.context.invoke(self.commands['previous'])

    @discord.ui.button(
        style = discord.ButtonStyle.red,
        label = 'Stop',
        emoji = '\N{Black Square for Stop}'
    )
    async def __button_stop(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.context.invoke(self.commands['stop'])

    @discord.ui.button(
        style = discord.ButtonStyle.gray,
        label = 'Pause',
        emoji = '\N{Double Vertical Bar}'
    )
    async def __button_pause(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.context.invoke(self.commands['pause'])

    @discord.ui.button(
        style = discord.ButtonStyle.gray,
        label = 'Next',
        emoji = '\N{Black Right-Pointing Double Triangle with Vertical Bar}'
    )
    async def __button_next(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.context.invoke(self.commands['skip'])

class PlaylistPage(pages.Paginator):
    def __init__(self, playlist: list[Music], title: str, **kwargs) -> None:
        super().__init__(pages = self.__build_pages(playlist = playlist), **kwargs)

        self.title = title
        self.custom_buttons = [
            pages.PaginatorButton(
                "first",
                label = "<<-", 
                style = discord.ButtonStyle.green
            ),
            pages.PaginatorButton(
                "prev",
                label = "<-",
                style = discord.ButtonStyle.green
            ),
            pages.PaginatorButton(
                "page_indicator",
                style = discord.ButtonStyle.gray,
                disabled = True
            ),
            pages.PaginatorButton(
                "next",
                label = "->",
                style = discord.ButtonStyle.green
            ),
            pages.PaginatorButton(
                "last",
                label="->>",
                style=discord.ButtonStyle.green
            ),
        ]

    def __build_pages(self, playlist):
        playlist_pages = []

        for count, music in enumerate(playlist, start = 1):
            if count % 10 == 1:
                current_embed = discord.Embed(title = f':scroll:  {self.title} (Page {int(count / 10 + 1)})')
                playlist_pages.append(current_embed)

            current_embed.add_field(
                name = '',
                value = f'**{count:02d}.** [__{music.title}__]({music.webpage_url})',
                inline = False
            )

        return playlist_pages

def setup(bot):
    bot.add_cog(MusicCog(bot))
