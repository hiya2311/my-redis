# MyRedis — Build Your Own Redis From Scratch

A fully functional Redis server implementation built from scratch in Python.
Implements the core Redis protocol (RESP) and supports real Redis clients.

## Features

- TCP server handling multiple concurrent clients via threading
- Full RESP protocol parser — compatible with redis-cli and any Redis client
- Commands: SET, GET, DEL, EXISTS, TTL, KEYS, PING, SAVE, INCR, DECR, INCRBY
- Key expiry with TTL support (auto-deletion after timeout)
- Data persistence — survives server restarts via JSON snapshots
- Tested against real redis-cli

## Tech Stack

- Python 3.10+
- Raw TCP sockets (no frameworks)
- Threading for concurrent connections
- JSON for persistence layer

## Getting Started

### Prerequisites
- Python 3.10+
- redis-cli (for testing)

### Run The Server

git clone https://github.com/hiya2311/my-redis
cd my-redis
python server.py

### Test With redis-cli

redis-cli -p 6380 set name Hiya
redis-cli -p 6380 get name
redis-cli -p 6380 set session abc ex 30
redis-cli -p 6380 ttl session
redis-cli -p 6380 incr counter
redis-cli -p 6380 keys *

## Architecture

Client (redis-cli)
      ↓ TCP Connection
server.py — accepts connections, spawns threads
      ↓
resp_parser.py — parses RESP protocol into Python lists
      ↓
commands.py — executes commands against in-memory dictionary
      ↓
redis_data.json — persistence layer (written on every SET/DEL)

## Commands Supported

| Command | Usage | Description |
|---------|-------|-------------|
| PING | PING | Health check |
| SET | SET key value | Store a value |
| SET EX | SET key value EX 30 | Store with expiry |
| GET | GET key | Retrieve a value |
| DEL | DEL key | Delete a key |
| EXISTS | EXISTS key | Check if key exists |
| TTL | TTL key | Check remaining expiry time |
| KEYS | KEYS * | List all keys |
| SAVE | SAVE | Manually save to disk |
| INCR | INCR key | Increment value by 1 |
| DECR | DECR key | Decrement value by 1 |
| INCRBY | INCRBY key 10 | Increment by specific amount |

## What I Learned

- TCP socket programming and network protocols
- Binary protocol parsing (RESP — Redis Serialization Protocol)
- Concurrent programming with Python threading
- In-memory data structure design
- Atomic operations implementation
- File-based persistence strategies

## Author

Hiya Khurana — BCA Student
GitHub: https://github.com/hiya2311
## Performance Analysis

Benchmarked against real Redis (1000 operations):

| Operation | My Redis | Real Redis | Gap |
|-----------|----------|-------------|-----|
| SET | 50 ops/sec | 4,012 ops/sec | 80x |
| GET | 1,144 ops/sec | 4,935 ops/sec | 4.3x |

**Key Finding:** SET is significantly slower than GET due to synchronous 
disk writes on every command (writing full JSON snapshot per SET). Real 
Redis avoids this using asynchronous persistence strategies (RDB snapshots 
and AOF logging).

**Potential Improvement:** Implement write-behind caching — batch writes 
every N seconds or N operations instead of synchronous writes per command.