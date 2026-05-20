"""
Attack Response Algorithms - Implementation of 9 response types
"""

import time
import json
import os
from datetime import datetime

class AttackAlgorithms:
    """
    Implementation of the 9 response algorithms from the presentation
    """
    
    def __init__(self):
        self.response_log = []
        self.log_file = 'response_log.json'
        self._load_log()
    
    def _load_log(self):
        """Load existing response log"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.response_log = json.load(f)
            except:
                self.response_log = []
    
    def ddos_mitigation(self, target):
        """
        Algorithm 1: DDoS_Mitigation
        For DoS/DDoS attacks
        Priority: CRITICAL
        """
        print("\n[ALGORITHM 1] DDoS MITIGATION")
        print("-" * 40)
        print("Steps:")
        print("1. Activate DDoS protection")
        print("2. Redirect traffic through scrubbers")
        print("3. Block source IPs")
        print("4. Enable rate limiting")
        
        target_ip = target.get('ip', 'unknown')
        
        # Simulated actions
        actions = [
            f"Activating DDoS protection on router",
            f"Redirecting traffic from {target_ip} to scrubbers",
            f"Blocking attack source IPs",
            f"Enabling rate limiting on interface"
        ]
        
        for action in actions:
            print(f"  → {action}")
            time.sleep(0.5)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': 'DDoS_Mitigation',
            'target': target_ip,
            'actions': actions,
            'status': 'completed',
            'priority': 'CRITICAL'
        }
        
        self._log_response(result)
        return result
    
    def backdoor_eradication(self, target):
        """
        Algorithm 2: Backdoor_Eradication
        For Backdoor attacks
        Priority: CRITICAL
        """
        print("\n[ALGORITHM 2] BACKDOOR ERADICATION")
        print("-" * 40)
        print("Steps:")
        print("1. Disconnect compromised system")
        print("2. Scan for malware")
        print("3. Remove backdoor files")
        print("4. Change all credentials")
        
        target_ip = target.get('ip', 'unknown')
        hostname = target.get('hostname', 'unknown')
        
        actions = [
            f"Disconnecting {hostname} from network",
            f"Running malware scan on {hostname}",
            f"Removing backdoor files",
            f"Changing all system credentials"
        ]
        
        for action in actions:
            print(f"  → {action}")
            time.sleep(0.5)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': 'Backdoor_Eradication',
            'target': target_ip,
            'hostname': hostname,
            'actions': actions,
            'status': 'completed',
            'priority': 'CRITICAL'
        }
        
        self._log_response(result)
        return result
    
    def worm_containment(self, target):
        """
        Algorithm 3: Worm_Containment
        For Worm attacks
        Priority: HIGH
        """
        print("\n[ALGORITHM 3] WORM CONTAINMENT")
        print("-" * 40)
        print("Steps:")
        print("1. Isolate affected network segment")
        print("2. Block worm propagation ports")
        print("3. Update antivirus signatures")
        print("4. Scan all connected systems")
        
        target_ip = target.get('ip', 'unknown')
        
        actions = [
            f"Isolating network segment containing {target_ip}",
            f"Blocking common worm ports (445, 139, 135)",
            f"Pushing updated antivirus signatures",
            f"Scanning all systems on network"
        ]
        
        for action in actions:
            print(f"  → {action}")
            time.sleep(0.5)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': 'Worm_Containment',
            'target': target_ip,
            'actions': actions,
            'status': 'completed',
            'priority': 'HIGH'
        }
        
        self._log_response(result)
        return result
    
    def exploit_mitigation(self, target):
        """
        Algorithm 4: Exploit_Mitigation
        For Exploit attacks
        Priority: HIGH
        """
        print("\n[ALGORITHM 4] EXPLOIT MITIGATION")
        print("-" * 40)
        print("Steps:")
        print("1. Isolate compromised system")
        print("2. Block attacker IP")
        print("3. Scan for vulnerabilities")
        print("4. Apply necessary patches")
        
        target_ip = target.get('ip', 'unknown')
        attacker_ip = target.get('attacker_ip', 'unknown')
        
        actions = [
            f"Isolating system {target_ip}",
            f"Blocking attacker IP {attacker_ip} at firewall",
            f"Scanning for vulnerabilities on {target_ip}",
            f"Applying critical security patches"
        ]
        
        for action in actions:
            print(f"  → {action}")
            time.sleep(0.5)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': 'Exploit_Mitigation',
            'target': target_ip,
            'attacker': attacker_ip,
            'actions': actions,
            'status': 'completed',
            'priority': 'HIGH'
        }
        
        self._log_response(result)
        return result
    
    def shellcode_block(self, target):
        """
        Algorithm 5: Shellcode_Block
        For Shellcode attacks
        Priority: HIGH
        """
        print("\n[ALGORITHM 5] SHELLCODE BLOCK")
        print("-" * 40)
        print("Steps:")
        print("1. Enable DEP (Data Execution Prevention)")
        print("2. Enable ASLR (Address Space Layout Randomization)")
        print("3. Block code injection attempts")
        print("4. Monitor process memory")
        
        target_ip = target.get('ip', 'unknown')
        
        actions = [
            f"Enabling DEP on {target_ip}",
            f"Enforcing ASLR on all processes",
            f"Blocking code injection attempts at kernel level",
            f"Starting process memory monitoring"
        ]
        
        for action in actions:
            print(f"  → {action}")
            time.sleep(0.5)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': 'Shellcode_Block',
            'target': target_ip,
            'actions': actions,
            'status': 'completed',
            'priority': 'HIGH'
        }
        
        self._log_response(result)
        return result
    
    def fuzzing_protection(self, target):
        """
        Algorithm 6: Fuzzing_Protection
        For Fuzzer attacks
        Priority: MEDIUM
        """
        print("\n[ALGORITHM 6] FUZZING PROTECTION")
        print("-" * 40)
        print("Steps:")
        print("1. Validate all input")
        print("2. Throttle request rate")
        print("3. Log malformed inputs")
        
        target_ip = target.get('ip', 'unknown')
        
        actions = [
            f"Enabling input validation on all services",
            f"Rate limiting connections to {target_ip}",
            f"Logging all malformed requests for analysis"
        ]
        
        for action in actions:
            print(f"  → {action}")
            time.sleep(0.5)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': 'Fuzzing_Protection',
            'target': target_ip,
            'actions': actions,
            'status': 'completed',
            'priority': 'MEDIUM'
        }
        
        self._log_response(result)
        return result
    
    def reconnaissance_counter(self, target):
        """
        Algorithm 7: Reconnaissance_Counter
        For Reconnaissance attacks
        Priority: MEDIUM
        """
        print("\n[ALGORITHM 7] RECONNAISSANCE COUNTER")
        print("-" * 40)
        print("Steps:")
        print("1. Deploy honeypot decoys")
        print("2. Log all scanning activity")
        print("3. Obfuscate system information")
        print("4. Alert security team")
        
        target_ip = target.get('ip', 'unknown')
        
        actions = [
            f"Deploying honeypot decoys on network",
            f"Logging all port scans from {target_ip}",
            f"Obfuscating banner information",
            f"Sending alert to security team"
        ]
        
        for action in actions:
            print(f"  → {action}")
            time.sleep(0.5)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': 'Reconnaissance_Counter',
            'target': target_ip,
            'actions': actions,
            'status': 'completed',
            'priority': 'MEDIUM'
        }
        
        self._log_response(result)
        return result
    
    def analysis_counter(self, target):
        """
        Algorithm 8: Analysis_Counter
        For Analysis attacks
        Priority: LOW
        """
        print("\n[ALGORITHM 8] ANALYSIS COUNTER")
        print("-" * 40)
        print("Steps:")
        print("1. Deploy decoy information")
        print("2. Monitor enumeration attempts")
        print("3. Log all requests")
        print("4. Alert on sensitive access")
        
        target_ip = target.get('ip', 'unknown')
        
        actions = [
            f"Deploying decoy files with fake credentials",
            f"Monitoring system enumeration attempts",
            f"Logging all access requests",
            f"Setting alerts for sensitive data access"
        ]
        
        for action in actions:
            print(f"  → {action}")
            time.sleep(0.5)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': 'Analysis_Counter',
            'target': target_ip,
            'actions': actions,
            'status': 'completed',
            'priority': 'LOW'
        }
        
        self._log_response(result)
        return result
    
    def generic_response(self, target):
        """
        Algorithm 9: Generic_Response
        For Generic/Unknown attacks
        Priority: MEDIUM
        """
        print("\n[ALGORITHM 9] GENERIC RESPONSE")
        print("-" * 40)
        print("Steps:")
        print("1. Block source IP")
        print("2. Log attack details")
        print("3. Alert security team")
        print("4. Monitor for patterns")
        
        target_ip = target.get('ip', 'unknown')
        src_ip = target.get('source_ip', 'unknown')
        
        actions = [
            f"Blocking source IP {src_ip} at firewall",
            f"Logging all attack details to SIEM",
            f"Alerting security operations team",
            f"Starting pattern monitoring for similar attacks"
        ]
        
        for action in actions:
            print(f"  → {action}")
            time.sleep(0.5)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': 'Generic_Response',
            'target': target_ip,
            'source': src_ip,
            'actions': actions,
            'status': 'completed',
            'priority': 'MEDIUM'
        }
        
        self._log_response(result)
        return result
    
    def normal_traffic(self, target):
        """
        For Normal traffic (no attack)
        """
        print("\n[NORMAL TRAFFIC] No response needed")
        print("-" * 40)
        print("Monitoring only")
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': 'Normal_Monitoring',
            'target': target.get('ip', 'unknown'),
            'actions': ['Continue monitoring'],
            'status': 'monitoring',
            'priority': 'LOW'
        }
        
        return result
    
    def _log_response(self, response):
        """
        Log response to file
        """
        self.response_log.append(response)
        
        # Save to file
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.response_log, f, indent=2)
        except:
            pass
    
    def get_recent_responses(self, count=5):
        """
        Get most recent responses
        """
        return self.response_log[-count:] if self.response_log else []