import threading
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from commands import handle_command, database, is_expired

class RedisAPIHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        pass  # Suppress default logging
    
    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        # GET /get?key=name
        if parsed.path == "/get":
            if "key" not in params:
                self.send_json(400, {"error": "key parameter required"})
                return
            key = params["key"][0]
            response = handle_command(["GET", key])
            if response == "$-1\r\n":
                self.send_json(200, {"value": None})
            else:
                value = response.split("\r\n")[1]
                self.send_json(200, {"value": value})
        
        # GET /keys  -- reads database dict directly, no RESP parsing
        elif parsed.path == "/keys":
            valid_keys = [k for k in list(database.keys()) if not is_expired(k)]
            self.send_json(200, {"keys": valid_keys})
        
        # GET /delete?key=name
        elif parsed.path == "/delete":
            if "key" not in params:
                self.send_json(400, {"error": "key parameter required"})
                return
            key = params["key"][0]
            response = handle_command(["DEL", key])
            deleted = response.strip() == ":1"
            self.send_json(200, {"deleted": deleted})
        # GET /all -- returns all keys with their values in ONE request
elif parsed.path == "/all":
    valid_keys = [k for k in list(database.keys()) if not is_expired(k)]
    result = {}
    for k in valid_keys:
        result[k] = database[k]["value"]
    self.send_json(200, {"data": result})
        # GET /stats
        elif parsed.path == "/stats":
            valid_keys = [k for k in list(database.keys()) if not is_expired(k)]
            self.send_json(200, {
                "total_keys": len(valid_keys),
                "keys": valid_keys
            })
        
        else:
            self.send_json(404, {"error": "endpoint not found"})
    
    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        
        try:
            data = json.loads(body)
        except:
            self.send_json(400, {"error": "invalid JSON"})
            return
        
        # POST /set   body: {"key": "name", "value": "Hiya"}
        if parsed.path == "/set":
            if "key" not in data or "value" not in data:
                self.send_json(400, {"error": "key and value required"})
                return
            
            parts = ["SET", data["key"], data["value"]]
            
            # Optional expiry: {"key": "x", "value": "y", "ex": 30}
            if "ex" in data:
                parts += ["EX", str(data["ex"])]
            
            handle_command(parts)
            self.send_json(200, {"ok": True})
        
        # POST /incr   body: {"key": "counter"}
        elif parsed.path == "/incr":
            if "key" not in data:
                self.send_json(400, {"error": "key required"})
                return
            response = handle_command(["INCR", data["key"]])
            value = int(response.strip().replace(":", ""))
            self.send_json(200, {"value": value})
        
        else:
            self.send_json(404, {"error": "endpoint not found"})


def start_api(port=8080):
    server = HTTPServer(("localhost", port), RedisAPIHandler)
    print(f"HTTP API running on http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    start_api()