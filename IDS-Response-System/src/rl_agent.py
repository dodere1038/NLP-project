"""
DQN Agent for Reinforcement Learning-based Intrusion Response
Simplified version - No TensorFlow dependency
"""

import numpy as np
import random
from collections import deque
import os

class DQNAgent:
    """
    Simplified RL Agent for selecting optimal response actions
    Uses rule-based approach instead of neural networks
    """
    
    def __init__(self, state_size, action_size, learning_rate=0.001, gamma=0.95,
                 epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995,
                 memory_size=10000, batch_size=64):
        """
        Initialize RL Agent
        """
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=memory_size)
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.q_table = {}  # Simple Q-table instead of neural network
        print("RL Agent initialized (simplified mode)")

    def _get_state_key(self, state):
        """Convert state array to a hashable key"""
        return tuple(np.round(state, 2))

    def update_target_model(self):
        """Placeholder for compatibility"""
        pass

    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """
        Choose action using epsilon-greedy policy
        Based on attack type (state[2] is attack_id)
        """
        # If exploring, choose random action
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        
        # Get attack type from state
        attack_id = int(state[2]) if len(state) > 2 else 0
        
        # Rule-based action selection based on attack type
        if attack_id == 1:  # DoS
            return 1
        elif attack_id == 2:  # Backdoor
            return 2
        elif attack_id == 3:  # Exploits
            return 3
        elif attack_id == 4:  # Fuzzers
            return 4
        elif attack_id == 5:  # Generic
            return 5
        elif attack_id == 6:  # Reconnaissance
            return 6
        elif attack_id == 7:  # Shellcode
            return 7
        elif attack_id == 8:  # Worms
            return 8
        else:
            return 0  # Normal traffic

    def replay(self):
        """
        Simple Q-learning update (simplified)
        """
        if len(self.memory) < self.batch_size:
            return
        
        # Sample random batch
        minibatch = random.sample(self.memory, self.batch_size)
        
        for state, action, reward, next_state, done in minibatch:
            state_key = self._get_state_key(state)
            next_state_key = self._get_state_key(next_state)
            
            # Initialize Q-values if not exist
            if state_key not in self.q_table:
                self.q_table[state_key] = np.zeros(self.action_size)
            if next_state_key not in self.q_table:
                self.q_table[next_state_key] = np.zeros(self.action_size)
            
            # Q-learning update
            if done:
                self.q_table[state_key][action] = reward
            else:
                self.q_table[state_key][action] = reward + self.gamma * np.max(self.q_table[next_state_key])
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, filepath):
        """Load Q-table from file"""
        if os.path.exists(filepath):
            try:
                import json
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to tuples
                    self.q_table = {eval(k): np.array(v) for k, v in data.items()}
                print(f"Model loaded from {filepath}")
            except Exception as e:
                print(f"Error loading model: {e}")
        else:
            print(f"No model found at {filepath}")

    def save(self, filepath):
        """Save Q-table to file"""
        try:
            import json
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            # Convert tuple keys to strings for JSON
            data = {str(k): v.tolist() for k, v in self.q_table.items()}
            with open(filepath, 'w') as f:
                json.dump(data, f)
            print(f"Model saved to {filepath}")
        except Exception as e:
            print(f"Error saving model: {e}")

__all__ = ['DQNAgent']