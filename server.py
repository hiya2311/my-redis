import socket
import threading
from resp_parser import parse_resp
from commands import handle_command

def handle_client(client_socket, client_address):
    print(f"New client connected: {client_address}")
    
    while True:
        try:
            data = client_socket.recv(1024)
            
            if not data:
                print(f"Client disconnected: {client_address}")
                break
            
            parts = parse_resp(data)
            print(f"Command from {client_address}: {parts}")
            
            response = handle_command(parts)
            client_socket.send(response.encode())
            
        except Exception as e:
            print(f"Error with {client_address}: {e}")
            break
    
    client_socket.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('localhost', 6380))
server.listen(10)

print("My Redis server running on port 6380...")
print("Supported: PING, SET, GET, DEL, EXISTS, TTL")
print("Now handling multiple clients simultaneously!")

while True:
    client_socket, client_address = server.accept()
    
    thread = threading.Thread(
        target=handle_client,
        args=(client_socket, client_address)
    )
    thread.daemon = True
    thread.start()
    
    print(f"Active connections: {threading.active_count() - 1}")