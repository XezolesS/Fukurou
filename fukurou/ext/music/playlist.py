import random
from collections import deque

from fukurou.config import config
from .music import Music

class Playlist:
    """Stores the youtube links of songs to be played and already played and offers basic operation on the queues"""
    def __init__(self):
        # Stores the links os the songs in queue and the ones already played
        self.queue = deque()
        self.history = deque()

    def __len__(self):
        return len(self.queue)

    def add(self, track: Music):
        """Add a track to the queue."""
        self.queue.append(track)
    
    def add_history(self, track: Music):
        """Add a track to the history."""
        self.history.append(track)

        # Pop-left if history max length exceeded.
        if len(self.history) > config.MAX_HISTORY_LENGTH:
            self.history.popleft()

    def insert(self, index: int, track: Music):
        """Insert a track into the selected position."""
        self.queue.insert(index, track)

    def next(self):
        """ 
            Get next track.\n
            The track will be removed from the queue.
        """
        if len(self.queue) == 0:
            return None

        track = self.queue.popleft()

        return track

    def previous(self):
        """
            Get previous track.\n
            Previous track is the last track of the history.
        """
        track = self.history[-1]

        return track

    def move(self, old_index: int, new_index: int):
        temp = self.queue[old_index]
        del self.queue[old_index]
        self.queue.insert(new_index, temp)

    def shuffle(self):
        random.shuffle(self.queue)

    def clear(self):
        self.queue.clear()
        self.history.clear()

    def is_empty(self):
        """
            Check if the playlist queue is empty.\n
            Same as is_queue_empty()
        """
        return self.is_queue_empty()

    def is_queue_empty(self):
        """
            Check if the playlist queue is empty.\n
            Same as is_empty()
        """
        return len(self) == 0

    def is_history_empty(self):
        """Check if the playlist history is empty."""
        return len(self.history) == 0
