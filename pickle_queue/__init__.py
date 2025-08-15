"""A queue implementation using pickle serialization with file locking.

"""
__version__ = "1.0.0"

from .queue import EmptyQueueError, Queue

__all__ = ["Queue", "EmptyQueueError"]
