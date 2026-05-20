"""
Extracts UNSW-NB15 features from network traffic
"""

import pandas as pd
import numpy as np
from datetime import datetime

class FeatureExtractor:
    """
    Extracts UNSW-NB15 compatible features from network traffic
    """
    
    def __init__(self):
        self.feature_names = [
            'dur', 'proto', 'service', 'state', 'spkts', 'dpkts',
            'sbytes', 'dbytes', 'rate', 'sttl', 'dttl', 'sload',
            'dload', 'sloss', 'dloss', 'sinpkt', 'dinpkt', 'sjit',
            'djit', 'swin', 'stcpb', 'dtcpb', 'dwin', 'tcprtt',
            'synack', 'ackdat', 'smean', 'dmean', 'trans_depth',
            'response_body_len', 'ct_srv_src', 'ct_state_ttl',
            'ct_dst_ltm', 'ct_src_dport_ltm', 'ct_dst_sport_ltm',
            'ct_dst_src_ltm', 'is_ftp_login', 'ct_ftp_cmd',
            'ct_flw_http_mthd', 'ct_src_ltm', 'ct_srv_dst',
            'is_sm_ips_ports'
        ]
        
        # Protocol mapping
        self.protocol_map = {
            'tcp': 6, 'udp': 17, 'icmp': 1, 'arp': 0, 'ip': 4,
            '6': 6, '17': 17, '1': 1
        }
    
    def extract_from_packet(self, packet_data):
        """
        Extract features from a single packet
        """
        features = {}
        
        # Basic duration (would need flow tracking for accurate)
        features['dur'] = packet_data.get('duration', 0)
        
        # Protocol
        proto = packet_data.get('protocol', 'tcp').lower()
        features['proto'] = self.protocol_map.get(proto, 0)
        
        # Service (would need deep packet inspection)
        features['service'] = self._detect_service(packet_data)
        
        # State (connection state)
        features['state'] = self._get_connection_state(packet_data)
        
        # Packet counts
        features['spkts'] = packet_data.get('src_packets', 1)
        features['dpkts'] = packet_data.get('dst_packets', 1)
        
        # Bytes
        features['sbytes'] = packet_data.get('src_bytes', 64)
        features['dbytes'] = packet_data.get('dst_bytes', 64)
        
        # Rate (packets per second)
        if features['dur'] > 0:
            features['rate'] = (features['spkts'] + features['dpkts']) / features['dur']
        else:
            features['rate'] = 1000  # Default high rate for single packet
        
        # Time to live
        features['sttl'] = packet_data.get('src_ttl', 64)
        features['dttl'] = packet_data.get('dst_ttl', 64)
        
        # Load (bytes per second)
        if features['dur'] > 0:
            features['sload'] = features['sbytes'] / features['dur']
            features['dload'] = features['dbytes'] / features['dur']
        else:
            features['sload'] = features['sbytes'] * 1000
            features['dload'] = features['dbytes'] * 1000
        
        # Loss (would need retransmission tracking)
        features['sloss'] = 0
        features['dloss'] = 0
        
        # Packet inter-arrival time (simplified)
        features['sinpkt'] = packet_data.get('src_interarrival', 0.001)
        features['dinpkt'] = packet_data.get('dst_interarrival', 0.001)
        
        # Jitter (simplified)
        features['sjit'] = 0
        features['djit'] = 0
        
        # TCP window (if TCP)
        features['swin'] = packet_data.get('src_window', 65535)
        features['dwin'] = packet_data.get('dst_window', 65535)
        
        # TCP sequence numbers (simplified)
        features['stcpb'] = packet_data.get('src_seq', 0)
        features['dtcpb'] = packet_data.get('dst_seq', 0)
        
        # RTT (would need ACK tracking)
        features['tcprtt'] = packet_data.get('rtt', 0)
        features['synack'] = packet_data.get('synack_time', 0)
        features['ackdat'] = packet_data.get('ack_time', 0)
        
        # Mean packet sizes
        features['smean'] = features['sbytes'] / max(features['spkts'], 1)
        features['dmean'] = features['dbytes'] / max(features['dpkts'], 1)
        
        # Transaction depth
        features['trans_depth'] = packet_data.get('transaction_depth', 1)
        
        # Response body length
        features['response_body_len'] = packet_data.get('response_size', 0)
        
        # Connection tracking features
        features['ct_srv_src'] = 1
        features['ct_state_ttl'] = 1
        features['ct_dst_ltm'] = 1
        features['ct_src_dport_ltm'] = 1
        features['ct_dst_sport_ltm'] = 1
        features['ct_dst_src_ltm'] = 1
        features['is_ftp_login'] = 0
        features['ct_ftp_cmd'] = 0
        features['ct_flw_http_mthd'] = 0
        features['ct_src_ltm'] = 1
        features['ct_srv_dst'] = 1
        features['is_sm_ips_ports'] = 1
        
        return [features.get(f, 0) for f in self.feature_names]
    
    def _detect_service(self, packet_data):
        """
        Detect service from packet data
        """
        dport = packet_data.get('dst_port', 0)
        proto = packet_data.get('protocol', '').lower()
        
        # Common service ports
        service_map = {
            (80, 'tcp'): 'http',
            (443, 'tcp'): 'https',
            (22, 'tcp'): 'ssh',
            (21, 'tcp'): 'ftp',
            (25, 'tcp'): 'smtp',
            (53, 'udp'): 'dns',
            (53, 'tcp'): 'dns',
            (161, 'udp'): 'snmp',
            (23, 'tcp'): 'telnet',
            (3306, 'tcp'): 'mysql',
            (5432, 'tcp'): 'postgresql'
        }
        
        service = service_map.get((dport, proto), '-')
        
        # Convert to numeric (as in UNSW-NB15)
        service_codes = {
            '-': 0, 'http': 1, 'https': 2, 'ssh': 3, 'ftp': 4,
            'smtp': 5, 'dns': 6, 'snmp': 7, 'telnet': 8,
            'mysql': 9, 'postgresql': 10
        }
        
        return service_codes.get(service, 0)
    
    def _get_connection_state(self, packet_data):
        """
        Get connection state
        """
        flags = packet_data.get('flags', '').upper()
        
        state_map = {
            'FIN': 1, 'SYN': 2, 'RST': 3, 'PSH': 4, 'ACK': 5,
            'URG': 6, 'SYN_ACK': 7, 'FIN_ACK': 8
        }
        
        if 'S' in flags and 'A' in flags:
            return state_map['SYN_ACK']
        elif 'S' in flags:
            return state_map['SYN']
        elif 'F' in flags and 'A' in flags:
            return state_map['FIN_ACK']
        elif 'F' in flags:
            return state_map['FIN']
        elif 'R' in flags:
            return state_map['RST']
        else:
            return 0