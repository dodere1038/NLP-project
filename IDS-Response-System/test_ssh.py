import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(
    hostname="192.168.206.10",
    username="kali",
    password="kali",
    timeout=30
)

stdin, stdout, stderr = ssh.exec_command("whoami")
print(stdout.read().decode())

ssh.close()
