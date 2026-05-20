import paramiko
import socket

print("Testing minimal SSH connection...")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)

try:
    sock.connect(("192.168.206.10", 22))
    print("TCP connection successful")
    
    # Read banner manually
    banner = sock.recv(1024)
    print(f"Banner received: {banner}")
    
    sock.close()
    
except Exception as e:
    print(f"Failed: {e}")