from flask import Flask, jsonify 
from flask_cors import CORS
import socket

app = Flask(__name__)
CORS(app)

def send_to_redis(*args):
    """
    Connects to our Redis server, sends a command in RESP format,
    and returns the raw response
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 6380))
    
    # Build the RESP command
    command = f"*{len(args)}\r\n"
    for arg in args:
        command += f"${len(str(arg))}\r\n{arg}\r\n"
    
    sock.send(command.encode())
    response = sock.recv(1024).decode()
    sock.close()
    
    return response


@app.route('/ping', methods=['GET'])
def ping():
    """Test endpoint - checks if our Redis server is alive"""
    try:
        response = send_to_redis("PING")
        return jsonify({"status": "success", "redis_response": response.strip()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/set', methods=['POST'])
def set_key():
    """
    Stores a key-value pair
    Usage: POST http://localhost:5000/set
    Body (JSON): {"key": "name", "value": "Hiya"}
    """
    from flask import request
    
    data = request.get_json()
    
    if not data or 'key' not in data or 'value' not in data:
        return jsonify({"status": "error", "message": "key and value are required"}), 400
    
    key = data['key']
    value = data['value']
    
    response = send_to_redis("SET", key, value)
    
    return jsonify({"status": "success", "message": f"Stored {key} = {value}"})


@app.route('/get/<key>', methods=['GET'])
def get_key(key):
    """
    Retrieves a value by key
    Usage: GET http://localhost:5000/get/name
    """
    response = send_to_redis("GET", key)
    
    # Check if key was not found
    if response.startswith("$-1"):
        return jsonify({"status": "error", "message": "key not found"}), 404
    
    # Parse the RESP response to extract just the value
    # Format is: $<length>\r\n<value>\r\n
    lines = response.split('\r\n')
    value = lines[1] if len(lines) > 1 else None
    
    return jsonify({"status": "success", "key": key, "value": value})


@app.route('/del/<key>', methods=['DELETE'])
def delete_key(key):
    """
    Deletes a key
    Usage: DELETE http://localhost:5000/del/name
    """
    response = send_to_redis("DEL", key)
    deleted = response.strip() == ":1"
    
    return jsonify({"status": "success", "deleted": deleted})


@app.route('/keys', methods=['GET'])
def list_keys():
    """
    Lists all keys currently stored
    Usage: GET http://localhost:5000/keys
    """
    response = send_to_redis("KEYS", "*")
    
    # Parse RESP array format to extract key names
    lines = response.split('\r\n')
    keys = []
    
    for line in lines:
        # Skip lines starting with * or $ (these are RESP markers)
        if not line.startswith('*') and not line.startswith('$') and line:
            keys.append(line)
    
    return jsonify({"status": "success", "keys": keys, "count": len(keys)})


@app.route('/incr/<key>', methods=['POST'])
def increment_key(key):
    """
    Increments a value by 1
    Usage: POST http://localhost:5000/incr/counter
    """
    response = send_to_redis("INCR", key)
    
    # Extract the number from response like ":5"
    value = response.strip().replace(":", "")
    
    return jsonify({"status": "success", "key": key, "new_value": int(value)})
@app.route('/flush', methods=['POST'])
def flush_all():
    """
    Deletes ALL keys - useful for demo/testing cleanup
    Usage: POST http://localhost:5000/flush
    """
    keys_response = send_to_redis("KEYS", "*")
    lines = keys_response.split('\r\n')
    keys = [line for line in lines if not line.startswith('*') and not line.startswith('$') and line]
    
    for key in keys:
        send_to_redis("DEL", key)
    
    return jsonify({"status": "success", "message": f"Deleted {len(keys)} keys"})
if __name__ == '__main__':
    print("Starting HTTP API on http://localhost:5000")
    app.run(debug=True, port=5000)