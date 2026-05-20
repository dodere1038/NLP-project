"""
Response Selector - Maps attack IDs to response algorithms
Based on the 9 algorithms from the presentation
"""

class ResponseSelector:
    """
    Selects appropriate response algorithm based on attack type
    Implements all 9 algorithms from the presentation
    """
    
    def __init__(self):
        # Map attack IDs to response methods
        self.response_map = {
            1: self.ddos_mitigation,        # DoS/DDoS
            2: self.backdoor_eradication,    # Backdoor
            3: self.exploit_mitigation,      # Exploits
            4: self.fuzzing_protection,      # Fuzzers
            5: self.generic_response,        # Generic
            6: self.reconnaissance_counter,  # Reconnaissance
            7: self.shellcode_block,         # Shellcode
            8: self.worm_containment,        # Worms
            9: self.analysis_counter         # Analysis
        }
        
        # Priority levels from presentation
        self.priority_map = {
            1: 'CRITICAL',   # DoS/DDoS
            2: 'CRITICAL',   # Backdoor
            3: 'HIGH',       # Exploits
            4: 'MEDIUM',     # Fuzzers
            5: 'MEDIUM',     # Generic
            6: 'MEDIUM',     # Reconnaissance
            7: 'HIGH',       # Shellcode
            8: 'HIGH',       # Worms
            9: 'LOW'         # Analysis
        }
        
        self.response_log = []
    
    def select_response(self, attack_id, target_info):
        """
        Select and execute response based on attack ID
        """
        if attack_id not in self.response_map:
            print(f"Unknown attack ID: {attack_id}, using generic response")
            attack_id = 5  # Generic
        
        print(f"\n{'='*50}")
        print(f"SELECTING RESPONSE FOR ATTACK")
        print(f"Attack Type: {self._get_attack_name(attack_id)}")
        print(f"Priority: {self.priority_map.get(attack_id, 'MEDIUM')}")
        print(f"{'='*50}")
        
        # Get the response function
        response_func = self.response_map[attack_id]
        
        # Execute response
        result = response_func(target_info)
        
        # Log the response
        self.response_log.append({
            'attack_id': attack_id,
            'attack_name': self._get_attack_name(attack_id),
            'timestamp': result.get('timestamp', ''),
            'actions': result.get('actions', [])
        })
        
        return result
    
    def _get_attack_name(self, attack_id):
        """Get attack name from ID"""
        names = {
            1: 'DoS/DDoS',
            2: 'Backdoor',
            3: 'Exploits',
            4: 'Fuzzers',
            5: 'Generic',
            6: 'Reconnaissance',
            7: 'Shellcode',
            8: 'Worms',
            9: 'Analysis'
        }
        return names.get(attack_id, 'Unknown')
    
    def ddos_mitigation(self, target):
        """
        Algorithm 1: DDoS_Mitigation
        For: DoS/DDoS attacks
        Priority: CRITICAL
        Steps: Activate protection, Redirect traffic, Block source IPs, Enable rate limiting
        """
        print("\n[ALGORITHM 1] DDoS MITIGATION")
        print("-" * 40)
        
        actions = [
            "Activating DDoS protection on firewall",
            "Redirecting traffic through scrubbers",
            "Blocking attack source IPs",
            "Enabling rate limiting on all interfaces"
        ]
        
        for i, action in enumerate(actions, 1):
            print(f"  Step {i}: {action}")
        
        return {
            'algorithm': 'DDoS_Mitigation',
            'target': target.get('ip', 'unknown'),
            'actions': actions,
            'status': 'completed',
            'priority': 'CRITICAL',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def backdoor_eradication(self, target):
        """
        Algorithm 2: Backdoor_Eradication
        For: Backdoor attacks
        Priority: CRITICAL
        Steps: Disconnect system, Scan for malware, Remove files, Change credentials
        """
        print("\n[ALGORITHM 2] BACKDOOR ERADICATION")
        print("-" * 40)
        
        actions = [
            f"Disconnecting system {target.get('hostname', 'target')} from network",
            "Scanning for malware and backdoor files",
            "Removing malicious files",
            "Changing all system credentials"
        ]
        
        for i, action in enumerate(actions, 1):
            print(f"  Step {i}: {action}")
        
        return {
            'algorithm': 'Backdoor_Eradication',
            'target': target.get('ip', 'unknown'),
            'actions': actions,
            'status': 'completed',
            'priority': 'CRITICAL',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def worm_containment(self, target):
        """
        Algorithm 3: Worm_Containment
        For: Worm attacks
        Priority: HIGH
        Steps: Isolate network, Block ports, Update antivirus, Scan all systems
        """
        print("\n[ALGORITHM 3] WORM CONTAINMENT")
        print("-" * 40)
        
        actions = [
            "Isolating affected network segment",
            "Blocking common worm ports (445, 139, 135)",
            "Pushing updated antivirus signatures",
            "Scanning all connected systems"
        ]
        
        for i, action in enumerate(actions, 1):
            print(f"  Step {i}: {action}")
        
        return {
            'algorithm': 'Worm_Containment',
            'target': target.get('ip', 'unknown'),
            'actions': actions,
            'status': 'completed',
            'priority': 'HIGH',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def exploit_mitigation(self, target):
        """
        Algorithm 4: Exploit_Mitigation
        For: Exploit attacks
        Priority: HIGH
        Steps: Isolate system, Block attacker, Scan vulnerabilities, Apply patches
        """
        print("\n[ALGORITHM 4] EXPLOIT MITIGATION")
        print("-" * 40)
        
        actions = [
            f"Isolating system {target.get('ip', 'unknown')}",
            f"Blocking attacker IP {target.get('attacker_ip', 'unknown')} at firewall",
            "Scanning for vulnerabilities",
            "Applying critical security patches"
        ]
        
        for i, action in enumerate(actions, 1):
            print(f"  Step {i}: {action}")
        
        return {
            'algorithm': 'Exploit_Mitigation',
            'target': target.get('ip', 'unknown'),
            'actions': actions,
            'status': 'completed',
            'priority': 'HIGH',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def shellcode_block(self, target):
        """
        Algorithm 5: Shellcode_Block
        For: Shellcode attacks
        Priority: HIGH
        Steps: Enable DEP, Enable ASLR, Block injection, Monitor process
        """
        print("\n[ALGORITHM 5] SHELLCODE BLOCK")
        print("-" * 40)
        
        actions = [
            "Enabling Data Execution Prevention (DEP)",
            "Enabling Address Space Layout Randomization (ASLR)",
            "Blocking code injection attempts",
            "Monitoring process memory"
        ]
        
        for i, action in enumerate(actions, 1):
            print(f"  Step {i}: {action}")
        
        return {
            'algorithm': 'Shellcode_Block',
            'target': target.get('ip', 'unknown'),
            'actions': actions,
            'status': 'completed',
            'priority': 'HIGH',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def fuzzing_protection(self, target):
        """
        Algorithm 6: Fuzzing_Protection
        For: Fuzzer attacks
        Priority: MEDIUM
        Steps: Validate input, Throttle rate, Log malformed inputs
        """
        print("\n[ALGORITHM 6] FUZZING PROTECTION")
        print("-" * 40)
        
        actions = [
            "Validating all input data",
            "Throttling request rate",
            "Logging malformed inputs for analysis"
        ]
        
        for i, action in enumerate(actions, 1):
            print(f"  Step {i}: {action}")
        
        return {
            'algorithm': 'Fuzzing_Protection',
            'target': target.get('ip', 'unknown'),
            'actions': actions,
            'status': 'completed',
            'priority': 'MEDIUM',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def reconnaissance_counter(self, target):
        """
        Algorithm 7: Reconnaissance_Counter
        For: Reconnaissance attacks
        Priority: MEDIUM
        Steps: Deploy honeypot, Log scanning, Obfuscate info, Alert team
        """
        print("\n[ALGORITHM 7] RECONNAISSANCE COUNTER")
        print("-" * 40)
        
        actions = [
            "Deploying honeypot decoys",
            "Logging all scanning activity",
            "Obfuscating system information",
            "Alerting security team"
        ]
        
        for i, action in enumerate(actions, 1):
            print(f"  Step {i}: {action}")
        
        return {
            'algorithm': 'Reconnaissance_Counter',
            'target': target.get('ip', 'unknown'),
            'actions': actions,
            'status': 'completed',
            'priority': 'MEDIUM',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def analysis_counter(self, target):
        """
        Algorithm 8: Analysis_Counter
        For: Analysis attacks
        Priority: LOW
        Steps: Deploy decoy info, Monitor enumeration, Log requests, Alert on sensitive access
        """
        print("\n[ALGORITHM 8] ANALYSIS COUNTER")
        print("-" * 40)
        
        actions = [
            "Deploying decoy information",
            "Monitoring enumeration attempts",
            "Logging all requests",
            "Alerting on sensitive data access"
        ]
        
        for i, action in enumerate(actions, 1):
            print(f"  Step {i}: {action}")
        
        return {
            'algorithm': 'Analysis_Counter',
            'target': target.get('ip', 'unknown'),
            'actions': actions,
            'status': 'completed',
            'priority': 'LOW',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def generic_response(self, target):
        """
        Algorithm 9: Generic_Response
        For: Generic/Unknown attacks
        Priority: MEDIUM
        Steps: Block source IP, Log details, Alert team, Monitor for patterns
        """
        print("\n[ALGORITHM 9] GENERIC RESPONSE")
        print("-" * 40)
        
        actions = [
            f"Blocking source IP {target.get('source_ip', 'unknown')} at firewall",
            "Logging attack details to SIEM",
            "Alerting security team",
            "Monitoring for similar attack patterns"
        ]
        
        for i, action in enumerate(actions, 1):
            print(f"  Step {i}: {action}")
        
        return {
            'algorithm': 'Generic_Response',
            'target': target.get('ip', 'unknown'),
            'actions': actions,
            'status': 'completed',
            'priority': 'MEDIUM',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }

__all__ = ['ResponseSelector']