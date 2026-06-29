import time
import json
import os

# Your database
database = {}

# File where we save data
SAVE_FILE = "redis_data.json"

def save_to_disk():
    """Save database to a JSON file"""
    # We can't save time.time() based expiry directly
    # So we save the data cleanly
    saveable = {}
    for key, val in database.items():
        saveable[key] = {
            "value": val["value"],
            "expires_at": val["expires_at"]
        }
    
    with open(SAVE_FILE, "w") as f:
        json.dump(saveable, f)
    
    print(f"Data saved to disk. {len(saveable)} keys saved.")

def load_from_disk():
    """Load database from JSON file on startup"""
    global database
    
    if not os.path.exists(SAVE_FILE):
        print("No saved data found. Starting fresh.")
        return
    
    with open(SAVE_FILE, "r") as f:
        loaded = json.load(f)
    
    # Only load keys that haven't expired yet
    now = time.time()
    count = 0
    for key, val in loaded.items():
        expires_at = val["expires_at"]
        if expires_at is None or expires_at > now:
            database[key] = val
            count += 1
    
    print(f"Loaded {count} keys from disk.")

def is_expired(key):
    """Check if a key has expired"""
    if key not in database:
        return True
    
    expires_at = database[key]["expires_at"]
    
    if expires_at is None:
        return False
    
    return time.time() > expires_at


def handle_command(parts):
    if not parts:
        return "-ERR empty command\r\n"
    
    command = parts[0].upper()
    
    # PING
    if command == "PING":
        return "+PONG\r\n"
    
    # SET key value
    elif command == "SET":
        if len(parts) < 3:
            return "-ERR wrong number of arguments\r\n"
        
        key = parts[1]
        value = parts[2]
        
        expires_at = None
        if len(parts) >= 5 and parts[3].upper() == "EX":
            seconds = int(parts[4])
            expires_at = time.time() + seconds
        
        database[key] = {"value": value, "expires_at": expires_at}
        
        # Save to disk every time we set a value
        save_to_disk()
        
        print(f"Stored: {key} = {value}")
        return "+OK\r\n"
    
    # GET key
    elif command == "GET":
        if len(parts) < 2:
            return "-ERR wrong number of arguments\r\n"
        
        key = parts[1]
        
        if key not in database or is_expired(key):
            if key in database:
                del database[key]
            return "$-1\r\n"
        
        value = database[key]["value"]
        return f"${len(value)}\r\n{value}\r\n"
    
    # DEL key
    elif command == "DEL":
        if len(parts) < 2:
            return "-ERR wrong number of arguments\r\n"
        
        key = parts[1]
        if key in database:
            del database[key]
            save_to_disk()
            return ":1\r\n"
        return ":0\r\n"
    
    # EXISTS key
    elif command == "EXISTS":
        if len(parts) < 2:
            return "-ERR wrong number of arguments\r\n"
        
        key = parts[1]
        if key in database and not is_expired(key):
            return ":1\r\n"
        return ":0\r\n"
    
    # TTL key
    elif command == "TTL":
        if len(parts) < 2:
            return "-ERR wrong number of arguments\r\n"
        
        key = parts[1]
        
        if key not in database:
            return ":-2\r\n"
        
        if is_expired(key):
            del database[key]
            return ":-2\r\n"
        
        expires_at = database[key]["expires_at"]
        
        if expires_at is None:
            return ":-1\r\n"
        
        remaining = int(expires_at - time.time())
        return f":{remaining}\r\n"
    
    # SAVE command - manually save to disk
    elif command == "SAVE":
        save_to_disk()
        return "+OK\r\n"
    
    # KEYS command - show all keys
    elif command == "KEYS":
        valid_keys = [k for k in database.keys() if not is_expired(k)]
        if not valid_keys:
            return "*0\r\n"
        
        response = f"*{len(valid_keys)}\r\n"
        for k in valid_keys:
            response += f"${len(k)}\r\n{k}\r\n"
        return response
    
    else:
        return f"-ERR unknown command '{command}'\r\n"


# Load saved data when this file is imported
load_from_disk()