import pickle
from pathlib import Path
from typing import Any

from filelock import FileLock, Timeout


class EmptyQueueError(Exception):
    """Exception raised when attempting to get from an empty queue."""
    pass


class Queue:
    """A thread-safe queue implementation using pickle serialization and file locking."""

    def __init__(self, queue_file: str = "queue.pkl") -> None:
        """Initialize the pickle queue.
        
        Args:
            queue_file: Path to the queue file for persistence
        """
        self.queue_file = Path(queue_file)
        self.lock_file = Path(f"{queue_file}.lock")
        self._create_queue()

    def _create_queue(self) -> None:
        """Create an empty queue file if it doesn't exist."""
        if not self.queue_file.exists():
            with FileLock(self.lock_file):
                if not self.queue_file.exists():
                    with open(self.queue_file, 'wb') as file:
                        pickle.dump([], file)

    def put(self, item: Any, timeout: int = -1) -> None:
        """Add an item to the queue.
        
        Args:
            item: The item to add to the queue
            timeout: The timeout in seconds to wait for the item to be added. If -1, wait indefinitely. If 0, return immediately.
        """
        try:
            with FileLock(self.lock_file, timeout=timeout):
                queue_data = self._load_queue()
                queue_data.append(item)
                self._save_queue(queue_data=queue_data)
        except Timeout:
            raise TimeoutError("Timed out waiting for item to be added")

    def put_batch(self, items: list[Any], timeout: int = -1) -> None:
        """Add a batch of items to the queue.
        
        Args:
            items: The list of items to add to the queue
            timeout: The timeout in seconds to wait for the items to be added. If -1, wait indefinitely. If 0, return immediately.
        """
        try:
            with FileLock(self.lock_file, timeout=timeout):
                queue_data = self._load_queue()
                queue_data.extend(items)
                self._save_queue(queue_data=queue_data)
        except Timeout:
            raise TimeoutError("Timed out waiting for items to be added")

    def get(self, position: int = 0, timeout: int = -1) -> Any:
        """Remove and return an item from the queue.
        
        Args:
            position: The position to pop from (default is 0 for FIFO behavior)
            timeout: The timeout in seconds to wait for the item to be available. If -1, wait indefinitely. If 0, return immediately.

        Returns:
            The item at the specified position in the queue
            
        Raises:
            EmptyQueueError: If the queue is empty
            IndexError: If the position is out of range
        """
        try:
            with FileLock(self.lock_file, timeout=timeout):
                queue_data = self._load_queue()
                if not queue_data:
                    raise EmptyQueueError("Cannot get item from empty queue")
                try:
                    item = queue_data.pop(position)
                    self._save_queue(queue_data=queue_data)
                    return item
                except IndexError:
                    raise IndexError(f"Position {position} is out of range for queue of size {len(queue_data)}")
        except Timeout:
            raise TimeoutError("Timed out waiting for item to be available")

    def get_batch(self, batch_size: int, timeout: int = -1) -> list[Any]:
        """Return a batch of items from the queue.
        
        Args:
            batch_size: The number of items to return
            timeout: The timeout in seconds to wait for the items to be available. If -1, wait indefinitely. If 0, return immediately.
        """
        try:
            with FileLock(self.lock_file, timeout=timeout):
                queue_data = self._load_queue()
                if not queue_data:
                    raise EmptyQueueError("Cannot get batch from empty queue")
                items = []
                for _ in range(batch_size):
                    if queue_data:
                        items.append(queue_data.pop(0))
                    else:
                        break
                self._save_queue(queue_data=queue_data)
                return items
        except Timeout:
            raise TimeoutError("Timed out waiting for items to be available")

    def get_all(self, timeout: int = -1) -> list[Any]:
        """Return all items from the queue.
        
        Args:
            timeout: The timeout in seconds to wait for the items to be available. If -1, wait indefinitely. If 0, return immediately.

        Returns:
            A list of all items in the queue
        """
        try:
            with FileLock(self.lock_file, timeout=timeout):
                items = self._load_queue()
                self._save_queue(queue_data=[])
                return items
        except Timeout:
            raise TimeoutError("Timed out waiting for items to be available")

    def clear(self, timeout: int = -1) -> None:
        """Remove all items from the queue.
        
        Args:
            timeout: The timeout in seconds to wait for the items to be available. If -1, wait indefinitely. If 0, return immediately.
        """
        try:
            with FileLock(self.lock_file, timeout=timeout):
                self._save_queue(queue_data=[])
        except Timeout:
            raise TimeoutError("Timed out waiting for items to be available")

    def size(self, timeout: int = -1) -> int:
        """Return the number of items in the queue.
        
        Args:
            timeout: The timeout in seconds to wait for the items to be available. If -1, wait indefinitely. If 0, return immediately.
        """
        try:
            with FileLock(self.lock_file, timeout=timeout):
                return len(self._load_queue())
        except Timeout:
            raise TimeoutError("Timed out waiting for items to be available")

    def delete(self, timeout: int = -1) -> None:
        """Delete the queue. Deletes the queue file and lock file.
        
        Args:
            timeout: The timeout in seconds to wait for the items to be available. If -1, wait indefinitely. If 0, return immediately.
        """
        try:
            with FileLock(self.lock_file, timeout=timeout):
                self.queue_file.unlink()
                self.lock_file.unlink()
        except Timeout:
            raise TimeoutError("Timed out waiting for items to be available")

    def _load_queue(self) -> list[Any]:
        """Load queue data from the pickle file.
        
        Returns:
            The queue data as a list
        """
        try:
            with open(self.queue_file, 'rb') as file:
                return pickle.load(file)
        except (FileNotFoundError, EOFError):
            return []

    def _save_queue(self, queue_data: list[Any]) -> None:
        """Save queue data to the pickle file.
        
        Args:
            queue_data: The queue data to save
        """
        with open(self.queue_file, 'wb') as file:
            pickle.dump(queue_data, file)
