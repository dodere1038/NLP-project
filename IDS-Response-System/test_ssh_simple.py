import paramiko
import time

print("Testing SSH connection...")
print("IP: 192.168.206.10")
print("User: kali")
print("Pass: kali")
print("-" * 40)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("Connecting...")
    ssh.connect(
        hostname="192.168.206.10",
        username="kali",
        password="kali",
        timeout=10,
        allow_agent=False,
        look_for_keys=False
    )
    
    print("✓ Connected!")
    
    stdin, stdout, stderr = ssh.exec_command("echo 'SSH WORKS!'")
    result = stdout.read().decode()
    print(f"Command result: {result}")
    
    ssh.close()
    print("✓ Test passed!")
    
except Exception as e:
    print(f"✗ Failed: {e}")
