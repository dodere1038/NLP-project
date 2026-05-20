"""
Random Forest-based attack detector trained on UNSW-NB15 dataset
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import os

class AttackDetector:
    """
    Detects network attacks using Random Forest trained on UNSW-NB15
    """
    
    def __init__(self, model_path=None):
        self.model = None
        self.feature_names = None
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
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def train(self, csv_path, save_path='models/random_forest_model.pkl'):
        """
        Train Random Forest on UNSW-NB15 dataset
        """
        print("Loading UNSW-NB15 dataset...")
        df = pd.read_csv(csv_path)
        
        # Select features
        feature_columns = [
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
        
        # Convert categorical to numerical
        df['proto'] = pd.Categorical(df['proto']).codes
        df['service'] = pd.Categorical(df['service']).codes
        df['state'] = pd.Categorical(df['state']).codes
        
        X = df[feature_columns].fillna(0)
        y = df['attack_cat'].fillna(0)
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print("Training Random Forest classifier...")
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        self.feature_names = feature_columns
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Save model
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'feature_names': feature_columns,
            'attack_types': self.attack_types
        }, save_path)
        print(f"Model saved to {save_path}")
        
        return accuracy
    
    def load_model(self, model_path):
        """Load trained model"""
        if not os.path.exists(model_path):
            print(f"Model file not found: {model_path}")
            return False
            
        data = joblib.load(model_path)
        self.model = data.get('model')
        self.feature_names = data.get('feature_names')
        self.attack_types = data.get('attack_types', self.attack_types)
        print(f"Model loaded from {model_path}")
        return True
    
    def predict(self, features):
        """Predict attack type from features"""
        if self.model is None:
            # Return default prediction if model not loaded
            return {
                'attack_id': 0,
                'attack_name': 'Normal',
                'confidence': 0.5
            }
        
        # Ensure features are in correct format
        if isinstance(features, dict):
            if self.feature_names:
                features = [features.get(f, 0) for f in self.feature_names]
            else:
                features = list(features.values())
        
        features = np.array(features).reshape(1, -1)
        
        if hasattr(self.model, 'predict_proba'):
            prediction = self.model.predict(features)[0]
            confidence = np.max(self.model.predict_proba(features)[0])
        else:
            prediction = self.model.predict(features)[0]
            confidence = 0.5
        
        attack_name = self.attack_types.get(int(prediction), 'Unknown')
        
        return {
            'attack_id': int(prediction),
            'attack_name': attack_name,
            'confidence': float(confidence)
        }
    
    def get_feature_importance(self):
        """Get feature importance scores"""
        if self.model is None or self.feature_names is None:
            return []
        
        importance = self.model.feature_importances_
        features = sorted(zip(self.feature_names, importance), 
                         key=lambda x: x[1], reverse=True)
        return features