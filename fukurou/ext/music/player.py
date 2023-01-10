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
    def __init__(self, bot: Fukurou, guild: Guild):
        self.bot = bot
        self.guild = guild

        self.playlist = Playlist()
        self.current_track = None
        self.loop = False
        self.volume = 100

        self.timer = Timer(self.handler_timeout)

    async def connect(self, ctx: ApplicationContext):
        """Connect to voice channel that the client is joining."""
        if ctx.author.voice is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return False

        if self.is_connected():
            await ctx.respond(config.ALREADY_CONNECTED_MESSAGE)
            return False

        await ctx.author.voice.channel.connect(reconnect=True, timeout=None)

    async def disconnect(self):
        """Disconnect from assigned voice channel."""
        self.stop()
        await self.guild.voice_client.disconnect(force=True)
    
    async def play(self):
        """Plays the first track of the playlist if one available."""
        if len(self.playlist) == 0:
            return None

        self.current_track = self.playlist.next()

        # Play the track
        source = discord.FFmpegPCMAudio(
            self.current_track.url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
        self.guild.voice_client.play(source, after=lambda error: self.on_track_finished(error))
        self.guild.voice_client.source = discord.PCMVolumeTransformer(
            self.guild.voice_client.source
        )
        self.set_volume(self.volume)

        # Reset the timer
        self.timer.reset()
        
    def stop(self):
        """Stops the player and clears queue."""
        if self.guild.voice_client is None:
            return

        self.loop = False
        self.playlist.clear()
        self.guild.voice_client.stop()

    def pause(self):
        """Pause the player."""
        if self.guild.voice_client is None:
            return

        if not self.is_playing():
            return
        
        self.guild.voice_client.pause()

    def resume(self):
        """Resume the player."""
        if self.guild.voice_client is None:
            return

        if not self.is_paused():
            return

        self.guild.voice_client.resume()

    def skip(self):
        self.guild.voice_client.stop()

    def previous(self):
        self.guild.voice_client.stop()
        self.playlist.insert(0, self.playlist.previous())

    def add_track(self, track: Music):
        self.playlist.add(track=track)

    def toggle_loop(self):
        """Toggle loop"""
        self.loop = not self.loop
        return self.loop

    def set_volume(self, volume: int):
        """Set a volume to a value of 1-100"""
        if volume not in range(0, 100 + 1):
            return False

        self.volume = volume
        self.guild.voice_client.source.volume = float(self.volume) / 100.0

        return True

    def is_connected(self, channel: VoiceChannel = None):
        """Check if the bot is connected to voice channel."""
        if self.guild.voice_client is None:
            return False

        if channel is None:
            return True
        else:
            return self.guild.voice_client.channel == channel

    def is_playing(self):
        return (self.is_connected() and
            self.current_track is not None and 
            self.guild.voice_client.is_playing())
    
    def is_paused(self):
        return (self.is_connected() and 
            self.current_track is not None and 
            self.guild.voice_client.is_paused())

    def on_track_finished(self, error):
        """
            A callback after play() has finished.\n
            Automatically plays next song if one available.
        """
        self.playlist.add_history(self.current_track)
        self.current_track = None

        if self.playlist.is_empty():
            return

        if self.loop == True:
            played = self.playlist.previous()
            self.playlist.add(played)

        self.bot.loop.create_task(self.play())

    async def handler_timeout(self):
        if self.guild.voice_client.channel is not None:
            pass

class Timer:
    def __init__(self, callback):
        self._callback = callback
        self._task = asyncio.create_task(self._job())

    async def _job(self):
        await asyncio.sleep(config.VC_TIMEOUT)
        await self._callback()

    def reset(self):
        self.cancel()
        self._task = asyncio.create_task(self._job())

    def cancel(self):
        self._task.cancel()