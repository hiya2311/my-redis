def parse_resp(data):
    """
    Converts Redis message format into a simple Python list
    Example: b"*3\r\n$3\r\nSET\r\n$4\r\nname\r\n$4\r\nHiya\r\n"
    Becomes: ["SET", "name", "Hiya"]
    """
    
    lines = data.decode().split('\r\n')
    
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('*'):
            i += 1
            continue
        
        elif line.startswith('$'):
            i += 1
            if i < len(lines) and lines[i]:
                result.append(lines[i])
            i += 1
            continue
        
        else:
            i += 1
    
    return result


# Test it
if __name__ == "__main__":
    test_data = b"*3\r\n$3\r\nSET\r\n$4\r\nname\r\n$4\r\nHiya\r\n"
    result = parse_resp(test_data)
    print(f"Parsed result: {result}")
    # Should print: ['SET', 'name', 'Hiya']