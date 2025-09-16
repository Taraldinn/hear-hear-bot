"""
Configuration Settings
Author: aldinn
Email: kferdoush617@gmail.com
"""

import os
import importlib
import importlib.util


# Load environment variables from a .env file if python-dotenv is installed
def _maybe_load_dotenv():
    spec = importlib.util.find_spec("dotenv")
    if spec is not None:
        dotenv = importlib.import_module("dotenv")
        if hasattr(dotenv, "load_dotenv"):
            dotenv.load_dotenv()


_maybe_load_dotenv()


class Config:
    """Bot configuration settings"""

    # Bot settings
    BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    BOT_PREFIX = [".", "?"]  # Keep for legacy support
    SHARD_COUNT = 2  # Auto-sharding for multiple servers
    USE_SLASH_COMMANDS = True
    GLOBAL_COMMANDS = True  # Enable global slash commands

    # Database settings
    MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
    DATABASE_NAME = "hearhear-bot"
    TABBY_DATABASE_NAME = "tabbybot"

    # External APIs
    TOPGG_TOKEN = os.getenv("TOPGG_TOKEN")

    # Bot metadata
    BOT_NAME = "Hear! Hear!"
    BOT_AUTHOR = "aldinn"
    BOT_EMAIL = "kferdoush617@gmail.com"
    BOT_GITHUB = "https://github.com/Taraldinn"
    BOT_VERSION = "2.0.0"

    # Server settings
    KEEP_ALIVE_PORT = int(os.getenv("PORT", "8080"))

    # Motions source (optional Google Sheets CSV URLs)
    # Option 1: Single combined CSV with a 'language' column (values like 'english', 'bangla') and a 'motion' column
    MOTIONS_CSV_URL_COMBINED = os.getenv("MOTIONS_CSV_URL_COMBINED")
    # Option 2: Separate CSV per language (first column should contain the motion text)
    MOTIONS_CSV_URL_ENGLISH = os.getenv("MOTIONS_CSV_URL_ENGLISH")
    MOTIONS_CSV_URL_BANGLA = os.getenv("MOTIONS_CSV_URL_BANGLA")

    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are set"""
        # Only BOT_TOKEN is strictly required
        required_vars = ["BOT_TOKEN"]
        missing_vars = []

        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        # Warn about optional but recommended variables
        if not cls.MONGODB_CONNECTION_STRING:
            print(
                "⚠️  Warning: MONGODB_CONNECTION_STRING not set - database features will be disabled"
            )

        return True


# Validate configuration on import
Config.validate_config()
