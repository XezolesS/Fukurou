# pylint: disable = C0114, W0108, W0613
import asyncio
import discord
from discord import (
    ApplicationContext,
    VoiceChannel,
    Guild
)

from fukurou.fukurou import Fukurou
from fukurou.config import config
from .music import Music
from .playlist import Playlist

class Player():
    '''
    Audio player that is assigned to the guild.

    Attributes:
        bot (Fukurou): A bot object.
        guild (Guild): A guild to be assigned.
    '''

    def __init__(self, bot: Fukurou, guild: Guild):
        self.bot = bot
        self.guild = guild

        self.timer = Timer(self.handler_timeout)
        self.logger = self.bot.loggers.get_logger(guild)
        self.settings = bot.settings.get_settings(guild)

        self.playlist = Playlist()
        self.current_track = None
        self.loop = False
        self.volume = int(self.settings.get_volume())

    async def connect(self, ctx: ApplicationContext):
        '''Connect to voice channel that the client is joining.'''
        if ctx.author.voice is None:
            self.logger.error('Failed to join voice channel: Command author not joined.\n')
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return False

        if self.is_connected():
            self.logger.error('Failed to join voice channel: Already connected.\n')
            await ctx.respond(config.ALREADY_CONNECTED_MESSAGE)
            return False

        self.logger.info(f'Joined to voice channel {ctx.author.voice.channel.name}')
        await ctx.author.voice.channel.connect(reconnect = True, timeout = None)

    async def disconnect(self):
        '''Disconnect from assigned voice channel.'''
        if self.guild.voice_client is None:
            return

        self.stop()

        self.logger.info(f'Disconnected from voice channel {self.guild.voice_client.channel}')
        await self.guild.voice_client.disconnect(force = True)

    async def reconnect(self, ctx: ApplicationContext):
        '''Reconnect to the voice channel.'''
        await self.disconnect()
        await self.connect(ctx)

    async def play(self):
        '''Plays the first track of the playlist if one available.'''
        if len(self.playlist) == 0:
            self.logger.info('All track have been played.')
            return

        # Get the next track
        self.current_track = self.playlist.next()

        # Track null check
        if self.current_track is None:
            return

        # Download the track
        await self.current_track.load()
        source = discord.FFmpegPCMAudio(
            self.current_track.url,
            before_options = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
        self.guild.voice_client.play(source, after = lambda error: self.on_track_finished(error))
        self.guild.voice_client.source = discord.PCMVolumeTransformer(
            self.guild.voice_client.source
        )
        self.guild.voice_client.source.volume = float(self.volume) / 100.0

        self.logger.info(f'Playing track {self.current_track.title}...')

        # Reset the timer
        self.timer.reset()

    def stop(self):
        '''Stops the player and clears queue.'''
        if self.guild.voice_client is None:
            self.logger.warning('Tried to stop player while is not connected to voice channel.\n')
            return

        self.loop = False
        self.playlist.clear()
        self.guild.voice_client.stop()

        self.logger.info('Player has been stopped.')

    def pause(self):
        '''Pause the player.'''
        if self.guild.voice_client is None:
            self.logger.warning('Tried to pause player while is not connected to voice channel.\n')
            return

        if not self.is_playing():
            self.logger.warning('Tried to pause player while is not playing.\n')
            return

        self.guild.voice_client.pause()

    def resume(self):
        '''Resume the player.'''
        if self.guild.voice_client is None:
            self.logger.warning('Tried to resume player while is not connected to voice channel.\n')
            return

        if not self.is_paused():
            self.logger.warning('Tried to resume player while is not paused.\n')
            return

        self.guild.voice_client.resume()

    def skip(self):
        '''Skip to next track.'''
        self.logger.info('Skipping to the next track...')
        self.guild.voice_client.stop()

    def previous(self):
        '''Skip to previous track.'''
        self.logger.info('Skipping to the previous track...')
        self.guild.voice_client.stop()
        self.playlist.insert(0, self.playlist.previous())

    def add_track(self, track: Music):
        '''Add a track to the queue.'''
        self.playlist.add(track = track)

        self.logger.info(f'The track {track.title} has been added to the queue.')

    def toggle_loop(self):
        '''Toggle loop.'''
        self.loop = not self.loop
        self.logger.info('Loop ' + 'enabled' if self.loop is True else 'disabled' + '.')

        return self.loop

    def set_volume(self, volume: int):
        '''Set a volume to a value of 1-100.'''
        if self.volume == volume:
            return False

        if volume not in range(0, 100 + 1):
            self.logger.debug('Volume is not in range of 0 to 100.')
            return False

        self.volume = volume
        if self.guild.voice_client is not None:
            self.guild.voice_client.source.volume = float(volume) / 100.0

        self.settings.set_volume(volume)

        self.logger.info(f'Player volume has been set to {volume}')

        return True

    def is_connected(self, channel: VoiceChannel = None):
        '''Check if the bot is connected to voice channel.'''
        if self.guild.voice_client is None:
            return False

        # When the bot is connected to any channel
        # and the channel is specified as none, return True.
        if channel is None:
            return True

        return self.guild.voice_client.channel == channel

    def is_playing(self):
        '''Check if the player is currently playing musics.'''
        return (self.is_connected() and
            self.current_track is not None and 
            self.guild.voice_client.is_playing())

    def is_paused(self):
        '''Check if the player is paused.'''
        return (self.is_connected() and 
            self.current_track is not None and 
            self.guild.voice_client.is_paused())

    def on_track_finished(self, error):
        '''
        A callback after play() has finished.\n
        Automatically plays next song if one available.
        '''
        self.playlist.add_history(self.current_track)
        self.current_track = None

        if self.playlist.is_empty():
            return

        if self.loop is True:
            played = self.playlist.previous()
            self.playlist.add(played)

        self.bot.loop.create_task(self.play())

    async def handler_timeout(self):
        '''A handler for timeout.'''
        if self.guild.voice_client.channel is not None:
            pass

class Timer:
    '''Timer to handle timeout from the voice channels.'''

    def __init__(self, callback):
        self._callback = callback
        self._task = asyncio.create_task(self._job())

    async def _job(self):
        await asyncio.sleep(config.VC_TIMEOUT)
        await self._callback()

    def reset(self):
        '''Reset timer.'''
        self.cancel()
        self._task = asyncio.create_task(self._job())

    def cancel(self):
        '''Cancel timer.'''
        self._task.cancel()
