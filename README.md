# Pickle Queue

A python queue implementation using pickle serialization with file locking for persistence across processes.

## Features

- Thread-safe operations using file locking
- Persistent storage using pickle serialization
- Simple API
- Cross-process compatibility

## Installation

```bash
git clone https://github.com/seaspaceman/pickle-queue.git
cd pickle-queue
pip install -e .
```

## Quick Start

```python
from pickle_queue import Queue, EmptyQueueError

# Load queue, will create queue.pkl if it doesn't exist
queue = Queue("queue.pkl")

# Add items to the queue
queue.put("Item 1")
queue.put("Item 2")
queue.put("Item 3")
queue.put("Item 4")

# Get size of the queue
size = queue.size() # Returns 4
print(f"Queue size: {size}")

# Get items from the queue, default behavior is FIFO
item = queue.get()  # Returns "Item 1"
print(f"Got: {item}")

# Get from specific position, 0 = first, -1 = last
last_item = queue.get(position=-1)  # Returns "Item 4"
print(f"Got last item: {last_item}")

# Get all remaining items
all_items = queue.get_all()  # Returns ["Item 2", "Item 3"]
print(f"All items: {all_items}")

# Clear the queue
queue.clear()

# Add multiple items with put_batch
batch_items = ["Item A", "Item B", "Item C"]
queue.put_batch(batch_items)
print(f"Added {len(batch_items)} items in one operation")

# Get a batch of items
batch = queue.get_batch(batch_size=3)  # Returns ["Item A", "Item B", "Item C"]
print(f"Got batch: {batch}") 

# Handle empty queue
try:
    item = queue.get()
except EmptyQueueError:
    print("Queue is empty!")

# Delete the queue from disk
queue.delete()
```

## Timeout Behavior

All queue methods have a `timeout` parameter for controlling the behavior of the queue when it is locked by another process:

- **`timeout=-1`** (default): Wait indefinitely for the file lock
- **`timeout=0`**: Return immediately if the lock cannot be acquired
- **`timeout=N`** (positive number): Wait up to N seconds for the lock

### Timeout Examples

```python
from pickle_queue import Queue

queue = Queue("shared_queue.pkl")

# Non-blocking operations, fails immediately if blocked
try:
    queue.put("urgent_data", timeout=0)
    queue.put_batch(["batch1", "batch2"], timeout=0)
    item = queue.get(timeout=0)
except TimeoutError:
    print("Queue is currently locked by another process")

# Time-limited operations
try:
    # Add a batch of items, waiting up to 15 seconds for queue to be unlocked before timing out
    large_batch = [f"item_{i}" for i in range(100)]
    queue.put_batch(large_batch, timeout=15)
    print(f"Added {len(large_batch)} items within 15 seconds")
    
    # Get a batch of items, waiting up to 30 seconds for queue to be unlocked before timing out
    batch = queue.get_batch(batch_size=5, timeout=30)
    print(f"Got {len(batch)} items within 30 seconds")
except TimeoutError:
    print("Operation timed out")

# Infinite wait, default behavior
item = queue.get()  # Will wait indefinitely for queue to be unlocked
```

## API Reference

### Queue(queue_file="queue.pkl")

Create a new pickle queue instance.

**Parameters:**
- `queue_file` (str): Path to the queue file for persistence. Defaults to "queue.pkl".

### EmptyQueueError

A custom exception raised when attempting to get an item from an empty queue.

### Methods

#### put(item, timeout=-1)
Add an item to the queue.

**Parameters:**
- `item` (Any): The item to add to the queue. Can be any pickle-serializable object.
- `timeout` (int, optional): Timeout in seconds. If -1 (default), wait indefinitely. If 0, return immediately. If positive, wait up to that many seconds.

**Raises:**
- `TimeoutError`: If the operation times out.


#### put_batch(items, timeout=-1)
Add multiple items to the queue in a single operation.

**Parameters:**
- `items` (list[Any]): A list of items to add to the queue. Each item can be any pickle-serializable object.
- `timeout` (int, optional): Timeout in seconds. If -1 (default), wait indefinitely. If 0, return immediately. If positive, wait up to that many seconds.

**Raises:**
- `TimeoutError`: If the operation times out.

#### get(position=0, timeout=-1)
Remove and return an item from the queue.

**Parameters:**
- `position` (int, optional): The position to pop from. Defaults to 0 for FIFO behavior.
- `timeout` (int, optional): Timeout in seconds. If -1 (default), wait indefinitely. If 0, return immediately. If positive, wait up to that many seconds.

**Returns:**
- The item at the specified position in the queue.

**Raises:**
- `EmptyQueueError`: If the queue is empty.
- `IndexError`: If the position is out of range.
- `TimeoutError`: If the operation times out.

#### get_batch(batch_size, timeout=-1)
Remove and return multiple items from the queue.

**Parameters:**
- `batch_size` (int): The maximum number of items to return.
- `timeout` (int, optional): Timeout in seconds. If -1 (default), wait indefinitely. If 0, return immediately. If positive, wait up to that many seconds.

**Returns:**
- `list[Any]`: A list of items from the queue. May contain fewer items than requested if the queue doesn't have enough items.

**Raises:**
- `EmptyQueueError`: If the queue is empty.
- `TimeoutError`: If the operation times out.


#### get_all(timeout=-1)
Return all items from the queue without removing them.

**Parameters:**
- `timeout` (int, optional): Timeout in seconds. If -1 (default), wait indefinitely. If 0, return immediately. If positive, wait up to that many seconds.

**Returns:**
- `list[Any]`: A list of all items currently in the queue.

**Raises:**
- `TimeoutError`: If the operation times out.

#### size(timeout=-1)
Return the number of items in the queue.

**Parameters:**
- `timeout` (int, optional): Timeout in seconds. If -1 (default), wait indefinitely. If 0, return immediately. If positive, wait up to that many seconds.

**Returns:**
- `int`: The number of items in the queue.

**Raises:**
- `TimeoutError`: If the operation times out.

#### clear(timeout=-1)
Remove all items from the queue.

**Parameters:**
- `timeout` (int, optional): Timeout in seconds. If -1 (default), wait indefinitely. If 0, return immediately. If positive, wait up to that many seconds.

**Raises:**
- `TimeoutError`: If the operation times out.

#### delete(timeout=-1)
Deletes the queue from disk.

**Parameters:**
- `timeout` (int, optional): Timeout in seconds. If -1 (default), wait indefinitely. If 0, return immediately. If positive, wait up to that many seconds.

**Raises:**
- `TimeoutError`: If the operation times out.

## Requirements

- Python 3.8+
- filelock (https://github.com/tox-dev/py-filelock)

## License

GPL-3.0
