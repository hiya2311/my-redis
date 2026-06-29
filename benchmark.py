import socket
import time

def send_command(sock, *args):
    """Send a command to our Redis server"""
    command = f"*{len(args)}\r\n"
    for arg in args:
        command += f"${len(str(arg))}\r\n{arg}\r\n"
    sock.send(command.encode())
    return sock.recv(1024).decode()

def run_benchmark(host, port, num_commands):
    """Run benchmark and return commands per second"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    # Warm up
    send_command(sock, "PING")
    
    # Benchmark SET
    start = time.time()
    for i in range(num_commands):
        send_command(sock, "SET", f"key{i}", f"value{i}")
    set_time = time.time() - start
    
    # Benchmark GET
    start = time.time()
    for i in range(num_commands):
        send_command(sock, "GET", f"key{i}")
    get_time = time.time() - start
    
    sock.close()
    
    set_ops = int(num_commands / set_time)
    get_ops = int(num_commands / get_time)
    
    return set_ops, get_ops

def print_bar(label, value, max_value, width=30):
    """Print a visual progress bar"""
    filled = int((value / max_value) * width)
    bar = "█" * filled + "░" * (width - filled)
    print(f"{label:12} |{bar}| {value:,} ops/sec")

def main():
    NUM_COMMANDS = 1000
    
    print("=" * 60)
    print("       MyRedis Benchmark Tool")
    print("=" * 60)
    print(f"Running {NUM_COMMANDS} commands per operation...")
    print()
    
    # Benchmark MY Redis
    print("Benchmarking YOUR Redis (port 6380)...")
    try:
        my_set, my_get = run_benchmark("localhost", 6380, NUM_COMMANDS)
        my_success = True
    except Exception as e:
        print(f"Could not connect to your Redis: {e}")
        my_success = False
    
    # Benchmark REAL Redis
    print("Benchmarking Real Redis (port 6379)...")
    try:
        real_set, real_get = run_benchmark("localhost", 6379, NUM_COMMANDS)
        real_success = True
    except Exception as e:
        print(f"Could not connect to real Redis: {e}")
        real_success = False
    
    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if my_success:
        print(f"\nYOUR Redis:")
        max_val = max(my_set, my_get)
        if real_success:
            max_val = max(my_set, my_get, real_set, real_get)
        print_bar("SET", my_set, max_val)
        print_bar("GET", my_get, max_val)
    
    if real_success:
        print(f"\nReal Redis:")
        max_val = max(my_set, my_get, real_set, real_get)
        print_bar("SET", real_set, max_val)
        print_bar("GET", real_get, max_val)
    
    if my_success and real_success:
        set_ratio = round(real_set / my_set, 1)
        get_ratio = round(real_get / my_get, 1)
        print()
        print("=" * 60)
        print("ANALYSIS")
        print("=" * 60)
        print(f"Real Redis SET is {set_ratio}x faster than yours")
        print(f"Real Redis GET is {get_ratio}x faster than yours")
        print()
        print("Why? Real Redis is written in C, yours is in Python.")
        print("Same protocol. Same logic. Different language = speed gap.")
        print()
        print(f"YOUR Redis performance: {my_set:,} SET/sec, {my_get:,} GET/sec")
        print("This is production-comparable for low-traffic use cases.")
    
    print()
    print("=" * 60)
    print("Benchmark complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()