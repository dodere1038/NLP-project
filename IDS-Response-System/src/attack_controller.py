"""
Attack Controller - Launches attacks from UNSW-NB15 dataset on GNS3 testbed
"""

import random
import time
import paramiko
import pandas as pd
import os
from datetime import datetime

class AttackController:
    """
    Controls attack execution on GNS3 testbed based on UNSW-NB15 dataset
    """
    
    def __init__(self, kali_ip="192.168.206.10", kali_user="kali", kali_pass="kali",
                 win10_ip="192.168.177.10", win10_user="", win10_pass=""):
        """
        Initialize Attack Controller
        
        Args:
            kali_ip: Kali VM IP address
            kali_user: Kali SSH username
            kali_pass: Kali SSH password
            win10_ip: Windows 10 VM IP address (jump host)
            win10_user: Windows 10 username
            win10_pass: Windows 10 password
        """
        self.kali_ip = kali_ip
        self.kali_user = kali_user
        self.kali_pass = kali_pass
        self.win10_ip = win10_ip
        self.win10_user = win10_user
        self.win10_pass = win10_pass
        self.ssh_client = None
        self.win10_client = None
        self.attack_log = []
        self.real_attacks_launched = 0
        self.simulated_attacks = 0
        self.attack_types = {
            0: 'Normal',
            1: 'DoS',
            2: 'Backdoor',
            3: 'Exploits',
            4: 'Fuzzers',
            5: 'Generic',
            6: 'Reconnaissance',
            7: 'Shellcode',
            8: 'Worms'
        }
        self.attack_counter = {i: 0 for i in range(1, 9)}
        
    def connect_to_kali(self):
        """Establish SSH connection to Kali via Windows 10 jump host"""
        try:
            # Check if we have Windows 10 credentials
            if not self.win10_user or not self.win10_pass:
                print(f"\n[SSH] No Windows 10 credentials provided, trying direct connection...")
                return self._connect_direct()
            
            print(f"\n[SSH] Connecting to Windows 10 at {self.win10_ip}...")
            self.win10_client = paramiko.SSHClient()
            self.win10_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.win10_client.connect(
                hostname=self.win10_ip,
                username=self.win10_user,
                password=self.win10_pass,
                timeout=30
            )
            print(f"[SSH] Connected to Windows 10")
            
            print(f"[SSH] Creating tunnel to Kali at {self.kali_ip}...")
            transport = self.win10_client.get_transport()
            
            # Check if transport exists
            if transport is None:
                print(f"[SSH] Failed to get transport")
                return self._connect_direct()
                
            channel = transport.open_channel(
                "direct-tcpip",
                (self.kali_ip, 22),
                ("127.0.0.1", 0)
            )
            
            print(f"[SSH] Connecting to Kali through tunnel...")
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                "127.0.0.1",
                port=22,
                username=self.kali_user,
                password=self.kali_pass,
                sock=channel,
                timeout=30,
                banner_timeout=200
            )
            
            # Test the connection
            stdin, stdout, stderr = self.ssh_client.exec_command("whoami", timeout=10)
            result = stdout.read().decode().strip()
            if result == "kali":
                print(f"[SSH] Connected to Kali through tunnel")
                print(f"[SSH] SSH connection verified")
                return True
            else:
                print(f"[SSH] SSH test failed - got: {result}")
                return False
                
        except paramiko.AuthenticationException:
            print(f"[SSH] Authentication failed! Check Windows 10 username/password")
            return self._connect_direct()
        except paramiko.SSHException as e:
            print(f"[SSH] SSH error: {e}")
            return self._connect_direct()
        except Exception as e:
            print(f"[SSH] Failed to connect via tunnel: {e}")
            return self._connect_direct()
    
    def _connect_direct(self):
        """Fallback: Try direct connection to Kali"""
        try:
            print(f"\n[SSH] Trying direct connection to Kali at {self.kali_ip}...")
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=self.kali_ip,
                username=self.kali_user,
                password=self.kali_pass,
                timeout=30,
                banner_timeout=200,
                auth_timeout=60,
                allow_agent=False,
                look_for_keys=False
            )
            
            stdin, stdout, stderr = self.ssh_client.exec_command("whoami", timeout=10)
            result = stdout.read().decode().strip()
            if result == "kali":
                print(f"[SSH] Connected to Kali directly")
                print(f"[SSH] SSH connection verified")
                return True
            else:
                print(f"[SSH] Direct connection test failed")
                return False
                
        except Exception as e:
            print(f"[SSH] Direct connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close SSH connections"""
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        if self.win10_client:
            self.win10_client.close()
            self.win10_client = None
    
    def execute_command(self, command):
        """Execute command on Kali VM"""
        if not self.ssh_client:
            return None, "Not connected"
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=30)
            return stdout.read().decode(), stderr.read().decode()
        except Exception as e:
            return None, str(e)
    
    def _generate_simulated_attacks(self, num_samples=10):
        """Generate simulated attack samples when dataset not available"""
        print(f"[ATTACK] Generating {num_samples} simulated attack samples")
        
        attack_samples = []
        attack_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        
        for i in range(num_samples):
            attack_id = attack_ids[i % len(attack_ids)]
            attack_samples.append({
                'attack_id': attack_id,
                'attack_name': self.attack_types[attack_id],
                'proto': random.choice(['tcp', 'udp']),
                'sport': random.randint(1024, 65535),
                'dport': random.choice([80, 443, 22, 21]),
                'duration': random.uniform(0.1, 2.0)
            })
        
        random.shuffle(attack_samples)
        return attack_samples
    
    def load_dataset_attacks(self, dataset_path, num_samples=10):
        """Load attack samples from UNSW-NB15 dataset"""
        if not os.path.exists(dataset_path):
            print(f"[DATASET] File not found: {dataset_path}")
            print(f"[DATASET] Using simulated attack samples")
            return self._generate_simulated_attacks(num_samples)
        
        try:
            print(f"[DATASET] Loading from: {dataset_path}")
            df = pd.read_csv(dataset_path)
            
            attack_name_to_id = {
                'Normal': 0, 'DoS': 1, 'Backdoor': 2, 'Exploits': 3,
                'Fuzzers': 4, 'Generic': 5, 'Reconnaissance': 6,
                'Shellcode': 7, 'Worms': 8
            }
            
            if 'attack_cat' not in df.columns:
                print("[DATASET] Missing 'attack_cat' column, using simulated")
                return self._generate_simulated_attacks(num_samples)
            
            attack_samples = []
            for _, row in df.iterrows():
                attack_name = str(row['attack_cat']).strip()
                if attack_name in attack_name_to_id:
                    attack_id = attack_name_to_id[attack_name]
                    if attack_id != 0:
                        attack_samples.append({
                            'attack_id': attack_id,
                            'attack_name': attack_name,
                            'proto': str(row.get('proto', 'tcp')) if pd.notna(row.get('proto')) else 'tcp',
                            'sport': int(row.get('sport', 0)) if pd.notna(row.get('sport')) else random.randint(1024, 65535),
                            'dport': int(row.get('dsport', 0)) if pd.notna(row.get('dsport')) else random.choice([80, 443]),
                            'duration': float(row.get('dur', 1.0)) if pd.notna(row.get('dur')) else 1.0
                        })
            
            if len(attack_samples) == 0:
                return self._generate_simulated_attacks(num_samples)
            
            if len(attack_samples) > num_samples:
                attack_samples = random.sample(attack_samples, num_samples)
            
            print(f"[DATASET] Loaded {len(attack_samples)} real attack samples")
            return attack_samples
            
        except Exception as e:
            print(f"[DATASET] Error: {e}, using simulated")
            return self._generate_simulated_attacks(num_samples)
    
    def launch_attack(self, attack_id, target_ip="192.168.177.10"):
        """Launch specific attack type on Kali"""
        commands = {
            1: f"echo '[DoS]'; sudo hping3 -S --flood -p 80 {target_ip} 2>&1 & sleep 2 && killall hping3 2>/dev/null",
            2: f"echo '[Backdoor]'; nc -zv {target_ip} 21 2>&1",
            3: f"echo '[Exploit]'; nmap -sV -Pn {target_ip} | head -15",
            4: f"echo '[Fuzzer]'; wfuzz -c -z range,1-10 http://{target_ip}:80/FUZZ 2>/dev/null | head -8 & sleep 2 && killall wfuzz 2>/dev/null",
            5: f"echo '[Generic]'; nmap -sS -Pn {target_ip} | head -15",
            6: f"echo '[Recon]'; nmap -A -Pn {target_ip} | head -15",
            7: f"echo '[Shellcode]'; echo 'Shellcode simulation'",
            8: f"echo '[Worm]'; echo 'Worm simulation'"
        }
        
        if attack_id not in commands:
            print(f"Unknown attack ID: {attack_id}")
            return False
        
        self.attack_counter[attack_id] = self.attack_counter.get(attack_id, 0) + 1
        
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] LAUNCHING {self.attack_types[attack_id].upper()} ATTACK")
        print(f"{'='*60}")
        print(f"Target: {target_ip}")
        
        # Check if SSH is actually connected
        if self.ssh_client is None:
            print(f"[ERROR] SSH NOT CONNECTED to Kali!")
            print(f"[RESULT] SIMULATED attack (no real packets)")
            self.simulated_attacks += 1
            self.attack_log.append({
                'timestamp': datetime.now().isoformat(),
                'attack_id': attack_id,
                'attack_name': self.attack_types[attack_id],
                'target': target_ip,
                'simulated': True,
                'real': False,
                'error': 'SSH not connected'
            })
            return True
        
        # Test SSH connection with a quick command
        try:
            test_stdin, test_stdout, test_stderr = self.ssh_client.exec_command("echo 'test'", timeout=5)
            test_result = test_stdout.read().decode().strip()
            if test_result != "test":
                print(f"[ERROR] SSH connection is dead!")
                print(f"[RESULT] SIMULATED attack (no real packets)")
                self.simulated_attacks += 1
                self.attack_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'attack_id': attack_id,
                    'attack_name': self.attack_types[attack_id],
                    'target': target_ip,
                    'simulated': True,
                    'real': False,
                    'error': 'SSH connection dead'
                })
                return True
        except Exception as e:
            print(f"[ERROR] SSH test failed: {e}")
            print(f"[RESULT] SIMULATED attack (no real packets)")
            self.simulated_attacks += 1
            self.attack_log.append({
                'timestamp': datetime.now().isoformat(),
                'attack_id': attack_id,
                'attack_name': self.attack_types[attack_id],
                'target': target_ip,
                'simulated': True,
                'real': False,
                'error': str(e)
            })
            return True
        
        # Only now we have a REAL SSH connection
        print(f"[SSH] Sending REAL attack command")
        
        try:
            print(f"[EXEC] Running: {commands[attack_id][:80]}...")
            stdout, stderr = self.execute_command(commands[attack_id])
            
            self.real_attacks_launched += 1
            self.attack_log.append({
                'timestamp': datetime.now().isoformat(),
                'attack_id': attack_id,
                'attack_name': self.attack_types[attack_id],
                'target': target_ip,
                'simulated': False,
                'real': True,
                'output': stdout[:200] if stdout else ''
            })
            
            print(f"[RESULT] REAL attack launched!")
            if stdout:
                print(f"[OUTPUT] {stdout[:100]}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Attack failed: {e}")
            return False
    
    def get_attack_stats(self):
        """Get statistics of launched attacks"""
        stats = {
            'total': len(self.attack_log),
            'real': self.real_attacks_launched,
            'simulated': self.simulated_attacks,
            'by_type': {}
        }
        
        for log in self.attack_log:
            attack_name = log['attack_name']
            if attack_name not in stats['by_type']:
                stats['by_type'][attack_name] = {'total': 0, 'real': 0, 'simulated': 0}
            stats['by_type'][attack_name]['total'] += 1
            if log.get('real', False):
                stats['by_type'][attack_name]['real'] += 1
            else:
                stats['by_type'][attack_name]['simulated'] += 1
        
        return stats

__all__ = ['AttackController']