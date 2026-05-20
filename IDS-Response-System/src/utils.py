# src/utils.py
def create_config():
    """Create configuration"""
    config = {
        'data': {
            'test_size': 0.3,
            'random_state': 42,
            'n_samples': 10000
        },
        'model': {
            'n_estimators': 200,
            'max_depth': 20
        },
        'dqn': {
            'state_size': 20,
            'action_size': 15,
            'learning_rate': 0.001,
            'gamma': 0.99,
            'epsilon_start': 1.0,
            'epsilon_decay': 0.995,
            'epsilon_min': 0.01,
            'batch_size': 64,
            'memory_size': 10000
        },
        'attack_types': {
            'mapping': {
                0: 'Normal',
                1: 'Analysis',
                2: 'Backdoor',
                3: 'DoS',
                4: 'Exploits',
                5: 'Fuzzers',
                6: 'Generic',
                7: 'Reconnaissance',
                8: 'Shellcode',
                9: 'Worms'
            }
        }
    }
    return config