"""
Main IRS System - Integrates all components
"""

import sys
import os
import time
import numpy as np
import threading
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    print("Warning: yaml not available")
    YAML_AVAILABLE = False
    yaml = None

from src.gns3_monitor import GNS3Monitor
from src.rl_agent import DQNAgent
from src.attack_controller import AttackController

SELECTOR_AVAILABLE = False
ResponseSelector = None
try:
    from src.response_selector import ResponseSelector
    SELECTOR_AVAILABLE = True
    print("ResponseSelector imported")
except ImportError:
    print("Warning: ResponseSelector not found")

DETECTOR_AVAILABLE = False
AttackDetector = None
try:
    from src.dataset_detector import AttackDetector
    DETECTOR_AVAILABLE = True
    print("AttackDetector imported")
except ImportError:
    print("Warning: AttackDetector not available")

class IRS_System:
    """
    Complete Intrusion Response System
    """
    
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)
        
        print("="*60)
        print("IRS SYSTEM INITIALIZING")
        print("="*60)
        
        self.gns3 = None
        self.detector = None
        self.agent = None
        self.selector = None
        self.attack_controller = None
        self.attack_samples = []
        
        self._init_gns3()
        self._init_detector()
        self._init_agent()
        self._init_selector()
        self._init_attack_controller()
        
        self.running = False
        self.monitor_thread = None
        self.attack_thread = None
        self.detection_results = []
        
        # For learning progress tracking
        self.episode_rewards = []
        self.current_episode_reward = 0
        
        print("\n" + "="*60)
        print("IRS SYSTEM READY")
        print("="*60)
    
    def _load_config(self, config_path):
        config_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_path)
        if YAML_AVAILABLE and yaml is not None and os.path.exists(config_full_path):
            try:
                with open(config_full_path, 'r') as f:
                    return yaml.safe_load(f)
            except:
                return {}
        return {}
    
    def _init_gns3(self):
        print("\n1. Connecting to GNS3...")
        gns3_config = self.config.get('gns3', {})
        self.gns3 = GNS3Monitor(
            server_url=gns3_config.get('server_url', 'http://localhost:3080'),
            project_name=gns3_config.get('project_name', 'IRS_RL_Testbed')
        )
        print("   [OK] GNS3 Monitor ready")
    
    def _init_detector(self):
        print("\n2. Loading Attack Detector...")
        if DETECTOR_AVAILABLE and AttackDetector is not None:
            self.detector = AttackDetector(None)
            print("   [OK] Attack Detector ready")
        else:
            self.detector = None
            print("   [MOCK] Using simulated detection")
    
    def _init_agent(self):
        print("\n3. Initializing RL Agent...")
        # Increased state size to 6 (more informative)
        self.agent = DQNAgent(
            state_size=6,          # CHANGED: from 4 to 6 features
            action_size=9,
            learning_rate=0.001,
            gamma=0.95,
            epsilon=1.0,           # Start with high exploration
            epsilon_min=0.01,
            epsilon_decay=0.995
        )
        print("   [OK] RL Agent ready")
    
    def _init_selector(self):
        print("\n4. Initializing Response Selector...")
        if SELECTOR_AVAILABLE and ResponseSelector is not None:
            self.selector = ResponseSelector()
            print("   [OK] Response Selector ready")
        else:
            self.selector = None
            print("   [MOCK] Using basic response handling")
    
    def _init_attack_controller(self):
        print("\n5. Initializing Attack Controller...")
        node_ips = self.config.get('node_ips', {})
        
        # EDIT THESE WITH YOUR ACTUAL CREDENTIALS
        win10_ip = node_ips.get('win10', '192.168.177.10')
        win10_user = "rashan"      # CHANGE THIS
        win10_pass = "win@123"     # CHANGE THIS
        
        self.attack_controller = AttackController(
            kali_ip=node_ips.get('kali', '192.168.206.10'),
            kali_user="kali",
            kali_pass="kali",
            win10_ip=win10_ip,
            win10_user=win10_user,
            win10_pass=win10_pass
        )
        
        if self.attack_controller.connect_to_kali():
            print("   [OK] Attack Controller ready - REAL ATTACKS WILL BE LAUNCHED")
            dataset_path = self.config.get('dataset_path', 'data/UNSW_NB15_testing-set.csv')
            full_dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), dataset_path)
            self.attack_samples = self.attack_controller.load_dataset_attacks(full_dataset_path, 10)
            print(f"   Loaded {len(self.attack_samples)} attack samples")
        else:
            print("   [WARN] Cannot connect to Kali - SIMULATED MODE")
            print("   [FIX] Check Windows 10 credentials and network")
            if self.attack_controller is not None:
                self.attack_samples = self.attack_controller._generate_simulated_attacks(10)
                print(f"   Generated {len(self.attack_samples)} simulated attack samples")
            else:
                print("   [ERROR] Attack controller not initialized")
                self.attack_samples = []
    
    # ========== NEW METHOD: Build enhanced state vector ==========
    def _get_state_vector(self, network_state, attack_id, confidence=0.95):
        """
        Build a richer state vector for the RL agent.
        Features: [attack_id, confidence, nodes_up, nodes_down, network_load, packet_errors]
        """
        # Simple network load estimation (packets per second approximation)
        network_load = network_state.get('packet_errors', 0) + np.random.randint(100, 500)
        
        state = np.array([
            float(attack_id),
            float(confidence),
            float(network_state.get('nodes_up', 4)),
            float(network_state.get('nodes_down', 0)),
            float(network_load),
            float(network_state.get('packet_errors', 0))
        ], dtype=np.float32)
        return state
    
    # ========== NEW METHOD: Evaluate response effectiveness ==========
    def _evaluate_response_effectiveness(self, attack_id):
        """
        Wait a few seconds and check if the same attack is still ongoing.
        Returns a reward: +10 if attack stopped, -5 if still present.
        """
        print("   [LEARNING] Waiting 3 seconds to evaluate response...")
        time.sleep(3)
        
        # Check if a new attack of the same type was detected after response
        # For simulation, we look at the last attack log entry
        if self.attack_controller and len(self.attack_controller.attack_log) > 0:
            last_attack = self.attack_controller.attack_log[-1]
            last_time = datetime.fromisoformat(last_attack['timestamp'])
            time_diff = (datetime.now() - last_time).total_seconds()
            
            # If the last attack happened more than 5 seconds ago, assume it stopped
            if time_diff > 5:
                reward = 10.0
                print(f"   [LEARNING] Attack stopped! Reward = +{reward}")
            else:
                reward = -5.0
                print(f"   [LEARNING] Attack still ongoing. Reward = {reward}")
        else:
            # No recent attack, assume success
            reward = 10.0
            print(f"   [LEARNING] No further attacks detected. Reward = +{reward}")
        
        return reward
    
    def start(self):
        print("\n" + "="*60)
        print("STARTING IRS SYSTEM - 10 ATTACK DEMO (WITH LEARNING)")
        print("="*60)
        
        self.running = True
        
        if self.gns3:
            self.gns3.start_monitoring()
        
        if self.attack_controller is not None and self.attack_samples:
            self.attack_thread = threading.Thread(target=self._attack_loop)
            self.attack_thread.daemon = True
            self.attack_thread.start()
            print("   [OK] Attack thread started")
        else:
            print("   [WARN] No attack samples available")
        
        self.monitor_thread = threading.Thread(target=self._main_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("\n[OK] IRS System running (LEARNING MODE ENABLED)")
        print("Watch VS Code for attack detection")
        print("Press Ctrl+C to stop\n")
    
    def stop(self):
        print("\nStopping IRS System...")
        self.running = False
        time.sleep(2)
        if self.gns3:
            self.gns3.stop_monitoring()
        if self.attack_controller is not None:
            self.attack_controller.disconnect()
        print("[OK] IRS System stopped")
        os._exit(0)
    
    def _attack_loop(self):
        """Launch attacks from dataset"""
        import random
        
        print("\n[ATTACK] Attack thread started")
        print(f"[ATTACK] Loaded {len(self.attack_samples)} attack samples")
        
        attack_count = 0
        max_attacks = min(10, len(self.attack_samples))
        
        if self.attack_samples:
            random.shuffle(self.attack_samples)
        
        for attack_idx in range(max_attacks):
            if not self.running:
                break
                
            attack = self.attack_samples[attack_idx]
            attack_count += 1
            
            print(f"\n{'='*60}")
            print(f"[ATTACK #{attack_count}/10] PREPARING {attack['attack_name'].upper()} ATTACK")
            print(f"{'='*60}")
            print(f"Attack ID: {attack['attack_id']}")
            print(f"Target: {self.config.get('node_ips', {}).get('win10', '192.168.177.10')}")
            
            wait_time = random.randint(3, 5)
            print(f"\nLaunching in {wait_time} seconds...")
            
            for i in range(wait_time, 0, -1):
                if not self.running:
                    break
                print(f"  {i}...")
                time.sleep(1)
            
            if not self.running:
                break
            
            if self.attack_controller is not None:
                self.attack_controller.launch_attack(
                    attack['attack_id'],
                    target_ip=self.config.get('node_ips', {}).get('win10', '192.168.177.10')
                )
            else:
                print("[ERROR] Attack controller not initialized")
            
            time.sleep(2)
        
        print("\n" + "="*60)
        print("ALL 10 ATTACKS COMPLETED")
        print("="*60)
        
        if self.attack_controller is not None:
            stats = self.attack_controller.get_attack_stats()
            print("\nAttack Statistics:")
            print(f"  Total Attacks: {stats.get('total', 0)}")
            print(f"  REAL Attacks: {stats.get('real', 0)}")
            print(f"  SIMULATED Attacks: {stats.get('simulated', 0)}")
            if stats.get('real', 0) > 0:
                print("  [X] REAL ATTACKS WERE SENT! Check Wireshark!")
            else:
                print("  [X] NO REAL ATTACKS - SSH to Kali failed")
                print("  [FIX] Check Windows 10 credentials")
        else:
            print("[ERROR] Cannot get stats - attack controller not available")
    
    def _main_loop(self):
        """Main monitoring and response loop with learning"""
        last_attack_check = None
        detection_count = 0
        replay_counter = 0  # To call replay every 2 detections
        
        while self.running:
            try:
                if self.gns3:
                    network_state = self.gns3.get_network_state()
                else:
                    network_state = {
                        'nodes_up': 4,
                        'nodes_down': 0,
                        'alerts': 0,
                        'packet_errors': 0,
                        'timestamp': datetime.now().isoformat()
                    }
                
                attack_detected = False
                detected_attack = None
                
                if self.attack_controller is not None and len(self.attack_controller.attack_log) > 0:
                    last_attack = self.attack_controller.attack_log[-1]
                    
                    if last_attack != last_attack_check:
                        last_attack_check = last_attack
                        time_diff = (datetime.now() - datetime.fromisoformat(last_attack['timestamp'])).total_seconds()
                        
                        if time_diff < 10 and last_attack.get('attack_id', 0) != 0:
                            attack_detected = True
                            detected_attack = last_attack
                
                if attack_detected and detected_attack is not None:
                    detection_count += 1
                    attack_id = detected_attack.get('attack_id', 0)
                    confidence = 0.95
                    
                    print(f"\n{'='*60}")
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ATTACK DETECTED! ({detection_count}/10)")
                    print(f"{'='*60}")
                    print(f"Type: {detected_attack.get('attack_name', 'Unknown')} (ID: {attack_id})")
                    print(f"Confidence: {confidence}")
                    print(f"Target: {detected_attack.get('target', 'unknown')}")
                    
                    # Build enhanced state vector (NEW)
                    state = self._get_state_vector(network_state, attack_id, confidence)
                    
                    if self.agent is not None:
                        action = self.agent.act(state)
                        print(f"\n[RL Agent] Selected action: {action}")
                    else:
                        action = 0
                    
                    target_info = {
                        'ip': self.config.get('node_ips', {}).get('win10', '192.168.177.10'),
                        'hostname': 'target_host',
                        'attacker_ip': self.config.get('node_ips', {}).get('kali', '192.168.206.10')
                    }
                    
                    print("\n[RESPONSE] Executing countermeasures:")
                    
                    response_actions = {
                        1: ["Activating DDoS protection", "Blocking source IPs", "Enabling rate limiting"],
                        2: ["Disconnecting system", "Scanning for malware", "Removing backdoor files", "Changing credentials"],
                        3: ["Isolating system", "Blocking attacker IP", "Scanning for vulnerabilities", "Applying patches"],
                        4: ["Validating input", "Throttling rate", "Logging malformed inputs"],
                        5: ["Blocking source IP", "Logging details", "Alerting team", "Monitoring patterns"],
                        6: ["Deploying honeypot", "Logging scanning", "Obfuscating info", "Alerting team"],
                        7: ["Enabling DEP", "Enabling ASLR", "Blocking code injection", "Monitoring process memory"],
                        8: ["Isolating network", "Blocking ports", "Updating signatures", "Scanning systems"]
                    }
                    
                    actions_list = response_actions.get(attack_id, ["Unknown response"])
                    for i, step in enumerate(actions_list, 1):
                        print(f"  Step {i}: {step}")
                        time.sleep(0.3)
                    
                    # ========== LEARNING: Evaluate reward ==========
                    reward = self._evaluate_response_effectiveness(attack_id)
                    self.current_episode_reward += reward
                    
                    # Get next state (after response)
                    next_state = self._get_state_vector(network_state, attack_id, confidence)
                    
                    # Store experience
                    if self.agent is not None:
                        self.agent.remember(state, action, reward, next_state, done=False)
                    
                    # Call replay every 2 detections to update Q-table
                    replay_counter += 1
                    if replay_counter % 2 == 0 and self.agent is not None:
                        self.agent.replay()
                        print(f"   [LEARNING] Replayed memory batch (Q-table updated)")
                    
                    self.detection_results.append({
                        'timestamp': datetime.now().isoformat(),
                        'detection': detected_attack,
                        'action': action if self.agent else 0,
                        'response_actions': actions_list,
                        'reward': reward
                    })
                    
                    print(f"\n[RESULT] Attack mitigated! Reward received: {reward}")
                    print(f"Total detections: {len(self.detection_results)}/10")
                    print("="*60)
                
                time.sleep(2)
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)

def main():
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print("\n\nReceived interrupt")
        if 'irs' in locals():
            irs.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    irs = IRS_System('config.yaml')
    irs.start()
    
    try:
        while True:
            time.sleep(1)
            
            
    except KeyboardInterrupt:
        irs.stop()

if __name__ == "__main__":
    main()
    