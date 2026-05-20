"""
GNS3 Network Monitor - Captures and processes network traffic
"""

import sys
import os
import time
import threading
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import gns3fy
except ImportError:
    print("gns3fy not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gns3fy"])
    import gns3fy

class GNS3Monitor:
    """
    Monitors network traffic from GNS3 nodes and extracts features
    """
    
    def __init__(self, server_url="http://localhost:3080", project_name="IRS_RL_Testbed"):
        self.server_url = server_url
        self.project_name = project_name
        self.connector = None
        self.project = None
        self.nodes = {}
        self.captures = {}
        self.running = False
        self.monitor_thread = None
        
        self.connect_to_project()
    
    def connect_to_project(self):
        """
        Connect to GNS3 project
        """
        try:
            self.connector = gns3fy.Gns3Connector(self.server_url)
            
            version = self.connector.get_version()
            print(f"Connected to GNS3 server v{version.get('version', 'unknown')}")
            
            projects = self.connector.get_projects()
            
            for p in projects:
                if p['name'] == self.project_name:
                    self.project = gns3fy.Project(
                        project_id=p['project_id'],
                        connector=self.connector,
                        name=self.project_name
                    )
                    self.project.get()
                    
                    if self.project.status == 'closed':
                        print(f"Project '{self.project_name}' is closed. Opening it...")
                        self.project.open()
                        time.sleep(3)
                        self.project.get()
                        print(f"Project '{self.project_name}' opened successfully")
                    else:
                        print(f"Project '{self.project_name}' is already open")
                    
                    self._update_nodes()
                    return True
            
            print(f"Project '{self.project_name}' not found")
            print("Available projects:")
            for p in projects:
                status = " (opened)" if p['status'] == 'opened' else " (closed)"
                print(f"  - {p['name']}{status}")
            return False
            
        except Exception as e:
            print(f"Error connecting to GNS3: {e}")
            return False
    
    def _update_nodes(self):
        """Update node information"""
        if self.project is not None:
            try:
                self.project.get()
                self.nodes = {}
                for node in self.project.nodes:
                    self.nodes[node.name] = {
                        'node_id': node.node_id,
                        'status': node.status,
                        'node_type': node.node_type,
                        'console': node.console,
                        'name': node.name
                    }
                print(f"Updated {len(self.nodes)} nodes")
            except Exception as e:
                print(f"Error updating nodes: {e}")
    
    def start_capture(self, node_name, interface='eth0'):
        """Start packet capture on a node"""
        if self.connector is None or self.project is None:
            print("Not connected to GNS3")
            return False
            
        if node_name not in self.nodes:
            print(f"Node '{node_name}' not found")
            return False
        
        node_id = self.nodes[node_name]['node_id']
        
        try:
            url = f"{self.connector.endpoint}/projects/{self.project.project_id}/nodes/{node_id}/interfaces/{interface}/capture/start"
            response = self.connector.session.post(url)
            
            if response.status_code == 201:
                print(f"Started capture on {node_name}:{interface}")
                self.captures[f"{node_name}_{interface}"] = {
                    'node': node_name,
                    'interface': interface,
                    'start_time': datetime.now()
                }
                return True
            else:
                print(f"Failed to start capture: {response.text}")
                return False
        except Exception as e:
            print(f"Error starting capture: {e}")
            return False
    
    def stop_capture(self, node_name, interface='eth0'):
        """Stop packet capture"""
        if self.connector is None or self.project is None:
            print("Not connected to GNS3")
            return False
            
        capture_key = f"{node_name}_{interface}"
        if capture_key not in self.captures:
            print(f"No active capture for {node_name}:{interface}")
            return False
        
        node_id = self.nodes[node_name]['node_id']
        
        try:
            url = f"{self.connector.endpoint}/projects/{self.project.project_id}/nodes/{node_id}/interfaces/{interface}/capture/stop"
            response = self.connector.session.post(url)
            
            if response.status_code == 204:
                print(f"Stopped capture on {node_name}:{interface}")
                del self.captures[capture_key]
                return True
            else:
                print(f"Failed to stop capture: {response.text}")
                return False
        except Exception as e:
            print(f"Error stopping capture: {e}")
            return False
    
    def get_node_status(self, node_name):
        """Get current status of a node"""
        self._update_nodes()
        if node_name in self.nodes:
            return self.nodes[node_name]['status']
        return 'unknown'
    
    def start_node(self, node_name):
        """Start a node"""
        if self.project is None:
            print("Not connected to GNS3")
            return False
            
        if node_name not in self.nodes:
            print(f"Node '{node_name}' not found")
            return False
        
        try:
            node = None
            for n in self.project.nodes:
                if n.name == node_name:
                    node = n
                    break
            
            if node is None:
                print(f"Node '{node_name}' not found in project")
                return False
                
            node.start()
            time.sleep(2)
            self._update_nodes()
            return True
        except Exception as e:
            print(f"Error starting node: {e}")
            return False
    
    def stop_node(self, node_name):
        """Stop a node"""
        if self.project is None:
            print("Not connected to GNS3")
            return False
            
        if node_name not in self.nodes:
            print(f"Node '{node_name}' not found")
            return False
        
        try:
            node = None
            for n in self.project.nodes:
                if n.name == node_name:
                    node = n
                    break
            
            if node is None:
                print(f"Node '{node_name}' not found in project")
                return False
                
            node.stop()
            time.sleep(2)
            self._update_nodes()
            return True
        except Exception as e:
            print(f"Error stopping node: {e}")
            return False
    
    def monitor_traffic_loop(self, interval=5):
        """Continuously monitor traffic"""
        self.running = True
        while self.running:
            try:
                self._update_nodes()
            except Exception as e:
                print(f"Error in monitor loop: {e}")
            time.sleep(interval)
    
    def start_monitoring(self):
        """Start monitoring thread"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self.monitor_traffic_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            print("Traffic monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
            print("Traffic monitoring stopped")
    
    def get_network_state(self):
        """Get current network state for RL agent"""
        self._update_nodes()
        
        nodes_up = 0
        nodes_down = 0
        
        for node_name, info in self.nodes.items():
            if info['status'] == 'started':
                nodes_up += 1
            else:
                nodes_down += 1
        
        return {
            'nodes_up': nodes_up,
            'nodes_down': nodes_down,
            'alerts': self._check_alerts(),
            'packet_errors': self._get_packet_errors(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _check_alerts(self):
        """Check for IDS alerts (placeholder)"""
        return 0
    
    def _get_packet_errors(self):
        """Get packet errors (placeholder)"""
        return 0
    
    def list_nodes(self):
        """List all nodes in the project"""
        if not self.nodes:
            print("No nodes found")
            return []
        
        print(f"\nNodes in project '{self.project_name}':")
        for name, info in self.nodes.items():
            status_symbol = "🟢" if info['status'] == 'started' else "🔴"
            print(f"  {status_symbol} {name} - {info['status']} ({info['node_type']})")
        
        return self.nodes
    
    def get_project_info(self):
        """Get project information"""
        if self.project:
            return {
                'name': self.project.name,
                'status': self.project.status,
                'nodes_count': len(self.nodes),
                'project_id': self.project.project_id
            }
        return None