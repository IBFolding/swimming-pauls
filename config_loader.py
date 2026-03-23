#!/usr/bin/env python3
"""
Swimming Pauls - Config Loader
Loads configuration from config.yaml
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    'defaults': {'pauls': 50, 'rounds': 20, 'timeout_seconds': 120},
    'server': {'websocket_port': 8765, 'ui_port': 3005, 'host': 'localhost'},
    'auto_resolver': {'enabled': True, 'interval_minutes': 60},
    'price_tracker': {'enabled': True, 'interval_minutes': 30},
    'notifications': {'enabled': False},
    'learning': {'track_accuracy': True, 'min_predictions_for_leaderboard': 1},
    'paper_trading': {'enabled': True, 'update_interval_seconds': 30}
}

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml or return defaults."""
    config_path = Path(__file__).parent / 'config.yaml'
    
    if not config_path.exists():
        # Try example config
        example_path = Path(__file__).parent / 'config.example.yaml'
        if example_path.exists():
            print("ℹ️  Using config.example.yaml (copy to config.yaml to customize)")
            config_path = example_path
        else:
            return DEFAULT_CONFIG
    
    try:
        with open(config_path) as f:
            user_config = yaml.safe_load(f)
        
        # Merge with defaults
        config = DEFAULT_CONFIG.copy()
        config.update(user_config)
        return config
        
    except Exception as e:
        print(f"⚠️  Error loading config: {e}")
        return DEFAULT_CONFIG

# Global config instance
CONFIG = load_config()
