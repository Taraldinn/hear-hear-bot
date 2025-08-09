"""
Configuration Settings
Author: aldinn
Email: kferdoush617@gmail.com
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration settings"""
    
    # Bot settings
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    BOT_PREFIX = ['.', '?']  # Keep for legacy support
    SHARD_COUNT = 2
    USE_SLASH_COMMANDS = True
    
    # Database settings
    MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
    DATABASE_NAME = 'hearhear-bot'
    TABBY_DATABASE_NAME = 'tabbybot'
    
    # External APIs
    TOPGG_TOKEN = os.getenv('TOPGG_TOKEN')
    
    # Bot metadata
    BOT_NAME = "Hear! Hear!"
    BOT_AUTHOR = "aldinn"
    BOT_EMAIL = "kferdoush617@gmail.com"
    BOT_GITHUB = "https://github.com/Taraldinn"
    BOT_VERSION = "2.0.0"
    
    # Server settings
    KEEP_ALIVE_PORT = int(os.getenv('PORT', 8080))
    
    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are set"""
        # Only BOT_TOKEN is strictly required
        required_vars = ['BOT_TOKEN']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Warn about optional but recommended variables
        if not cls.MONGODB_CONNECTION_STRING:
            print("⚠️  Warning: MONGODB_CONNECTION_STRING not set - database features will be disabled")
        
        return True

# Validate configuration on import
Config.validate_config()
