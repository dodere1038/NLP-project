import paramiko
import socket
import time

class KaliTunnel:
    def __init__(self, windows10_ip, windows10_user, windows10_pass):
        self.windows10_ip = windows10_ip
        self.windows10_user = windows10_user
        self.windows10_pass = windows10_pass
        self.windows10_client = None
        self.kali_client = None
        
    def connect(self):
        print(f"Connecting to Windows10 ({self.windows10_ip})...")
        self.windows10_client = paramiko.SSHClient()
        self.windows10_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        self.windows10_client.connect(
            hostname=self.windows10_ip,
            username=self.windows10_user,
            password=self.windows10_pass,
            timeout=30
        )
        print("Connected to Windows10")
        
        print("Creating tunnel to Kali...")
        transport = self.windows10_client.get_transport()
        dest_addr = ("192.168.206.10", 22)
        local_addr = ("127.0.0.1", 0)
        
        channel = transport.open_channel("direct-tcpip", dest_addr, local_addr)
        print("Tunnel created")
        
        print("Connecting to Kali...")
        self.kali_client = paramiko.SSHClient()
        self.kali_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        self.kali_client.connect(
            hostname="127.0.0.1",
            port=22,
            username="kali",
            password="kali",
            sock=channel,
            timeout=30,
            banner_timeout=200
        )
        print("Connected to Kali")
        
        return self.kali_client
    
    def exec_command(self, command):
        if not self.kali_client:
            self.connect()
        
        stdin, stdout, stderr = self.kali_client.exec_command(command)
        return stdout.read().decode()
    
    def close(self):
        if self.kali_client:
            self.kali_client.close()
        if self.windows10_client:
            self.windows10_client.close()


WINDOWS10_IP = "192.168.177.10"
WINDOWS10_USER = "rashan"
WINDOWS10_PASS = "win@123s"


print("="*40)
print("Kali SSH Tunnel via Windows10 Testbed")
print("="*40)

tunnel = KaliTunnel(WINDOWS10_IP, WINDOWS10_USER, WINDOWS10_PASS)

try:
    ssh = tunnel.connect()
    
    print("\nExecuting Commands")
    print("-"*40)
    
    result = tunnel.exec_command("whoami")
    print(f"User: {result.strip()}")
    
    result = tunnel.exec_command("hostname")
    print(f"Hostname: {result.strip()}")
    
    result = tunnel.exec_command("ip a | grep eth0")
    print(f"Kali IP:\n{result}")
    
    print("\nSSH tunnel working successfully")
    
except Exception as e:
    print(f"\nError: {e}")
    print("\nTroubleshooting:")
    print("1. Check Windows10 IP is correct")
    print("2. Verify Windows10 username and password")
    print("3. Make sure Windows10 is running")
    print("4. Check Kali is running and IP is 192.168.206.10")
    
finally:
    tunnel.close()
    print("\nConnections closed")