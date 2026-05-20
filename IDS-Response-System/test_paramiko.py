import paramiko

print("Testing SSH with paramiko...")
print("-" * 40)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(
        "192.168.206.10",
        username="kali",
        password="kali",
        timeout=10,
        allow_agent=False,
        look_for_keys=False
    )
    print("✓ SSH CONNECTION SUCCESSFUL!")
    
    stdin, stdout, stderr = ssh.exec_command("echo 'Hello from Kali!'")
    print("Command output:", stdout.read().decode())
    
    ssh.close()
    
except Exception as e:
    print(f"✗ Failed: {e}")
