"""
Production Configuration Settings
Author: aldinn
Email: kferdoush617@gmail.com

Comprehensive configuration management with validation,
environment variable loading, and production optimizations.
"""

import os
import sys
import importlib
import importlib.util
from typing import List, Optional, Dict, Any
from pathlib import Path


def _load_environment_variables():
    """
    Load environment variables from .env file if available.
    Uses python-dotenv if installed, gracefully degrades if not.
    Loads in priority order: .env.local > .env
    """
    try:
        spec = importlib.util.find_spec("dotenv")
        if spec is not None:
            dotenv = importlib.import_module("dotenv")
            if hasattr(dotenv, "load_dotenv"):
                project_root = Path(__file__).parent.parent

                # Priority order: .env.local (local config) > .env (template/defaults)
                env_files = [
                    project_root / ".env.local",  # Local overrides (not committed)
                    project_root / ".env",  # Default template
                ]

                loaded = False
                for env_file in env_files:
                    if env_file.exists():
                        dotenv.load_dotenv(env_file, override=True)
                        print(f"✅ Loaded environment variables from {env_file.name}")
                        loaded = True

                if not loaded:
                    # Fallback to current directory
                    dotenv.load_dotenv()
                    print("✅ Loaded environment variables from current directory")
    except (ImportError, AttributeError, OSError) as e:
        print(f"⚠️  Could not load .env file: {e}")


# Load environment variables on module import
_load_environment_variables()


class ConfigValidator:
    """Validate configuration settings and environment"""

    @staticmethod
    def validate_python_version():
        """Ensure minimum Python version requirement"""
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8 or higher is required!")

    @staticmethod
    def validate_required_vars(
        required_vars: List[str], config_dict: Dict[str, Any]
    ) -> List[str]:
        """Check for missing required environment variables"""
        missing_vars = []
        for var in required_vars:
            if not config_dict.get(var):
                missing_vars.append(var)
        return missing_vars

    @staticmethod
    def validate_optional_vars(
        optional_vars: Dict[str, str], config_dict: Dict[str, Any]
    ) -> List[str]:
        """Check for missing optional variables and their impact"""
        missing_optional = []
        for var, impact in optional_vars.items():
            if not config_dict.get(var):
                missing_optional.append(f"{var} ({impact})")
        return missing_optional


class Config:
    """
    Production-ready configuration class with comprehensive validation
    and environment variable management.
    """

    # ==================== BOT CORE SETTINGS ====================
    BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
    BOT_ID: str = os.getenv("BOT_ID", "")  # Discord bot ID for top.gg
    BOT_PREFIX: List[str] = [".", "?"]  # Legacy prefix support
    SHARD_COUNT: int = int(os.getenv("SHARD_COUNT", "2"))
    USE_SLASH_COMMANDS: bool = True
    GLOBAL_COMMANDS: bool = True
    TEST_GUILD_ID: Optional[int] = None

    # Bot invite URL (auto-generated if not set)
    BOT_INVITE_URL: str = os.getenv("BOT_INVITE_URL", "")
    if not BOT_INVITE_URL and BOT_ID:
        # Generate default invite URL with recommended permissions
        BOT_INVITE_URL = (
            f"https://discord.com/api/oauth2/authorize?"
            f"client_id={BOT_ID}"
            f"&permissions=8"
            f"&scope=bot%20applications.commands"
        )
    # Initialize TEST_GUILD_ID safely
    _test_guild_env = os.getenv("TEST_GUILD_ID")
    if _test_guild_env and _test_guild_env.isdigit():
        TEST_GUILD_ID = int(_test_guild_env)

    # ==================== DATABASE SETTINGS ====================
    # PostgreSQL Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "hearhear_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "hearhear_bot")
    POSTGRES_SSL_MODE: str = os.getenv("POSTGRES_SSL_MODE", "prefer")

    # Connection pool settings
    DATABASE_TIMEOUT: int = int(os.getenv("DATABASE_TIMEOUT", "30"))  # seconds
    DATABASE_MAX_POOL_SIZE: int = int(os.getenv("DATABASE_MAX_POOL_SIZE", "20"))
    DATABASE_MIN_POOL_SIZE: int = int(os.getenv("DATABASE_MIN_POOL_SIZE", "5"))

    # Legacy MongoDB settings (for backward compatibility during migration)
    MONGODB_CONNECTION_STRING: str = os.getenv("MONGODB_CONNECTION_STRING", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "hearhear-bot")
    TABBY_DATABASE_NAME: str = os.getenv("TABBY_DATABASE_NAME", "tabbybot")

    # ==================== EXTERNAL SERVICES ====================
    TOPGG_TOKEN: str = os.getenv("TOPGG_TOKEN", "")
    TABBYCAT_API_KEY: str = os.getenv("TABBYCAT_API_KEY", "")

    # ==================== BOT METADATA ====================
    BOT_NAME: str = "AldinnBot"
    BOT_AUTHOR: str = "aldinn"
    BOT_EMAIL: str = "kferdoush617@gmail.com"
    BOT_GITHUB: str = "https://github.com/Taraldinn/hear-hear-bot"
    BOT_VERSION: str = "2.1.0"
    BOT_DESCRIPTION: str = (
        "A comprehensive debate bot with timing, motions, and tournament features"
    )
    BOT_TAGLINE: str = "The Ultimate Discord Bot for Debate Tournaments"
    BOT_KEYWORDS: List[str] = [
        "discord bot",
        "debate bot",
        "tournament bot",
        "timer bot",
        "motion database",
        "tabbycat integration",
        "debate tournaments",
        "parliamentary debate",
        "debate timer",
        "debate management",
    ]

    # ==================== SERVER SETTINGS ====================
    WEB_SERVER_PORT: int = int(os.getenv("PORT", "8080"))
    WEB_SERVER_HOST: str = os.getenv("HOST", "0.0.0.0")
    WEB_SERVER_DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # ==================== MOTIONS CONFIGURATION ====================
    # Google Sheets CSV URLs for motions
    MOTIONS_CSV_URL_COMBINED: str = os.getenv("MOTIONS_CSV_URL_COMBINED", "")
    MOTIONS_CSV_URL_ENGLISH: str = os.getenv("MOTIONS_CSV_URL_ENGLISH", "")
    MOTIONS_CSV_URL_BANGLA: str = os.getenv("MOTIONS_CSV_URL_BANGLA", "")

    # ==================== PERFORMANCE SETTINGS ====================
    MAX_MESSAGE_CACHE: int = int(os.getenv("MAX_MESSAGE_CACHE", "1000"))
    COMMAND_TIMEOUT: int = int(os.getenv("COMMAND_TIMEOUT", "30"))  # seconds
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "100"))  # requests per minute

    # ==================== LOGGING CONFIGURATION ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "True").lower() == "true"
    LOG_ROTATION: bool = os.getenv("LOG_ROTATION", "True").lower() == "true"
    LOG_MAX_SIZE: str = os.getenv("LOG_MAX_SIZE", "10MB")
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    # ==================== SECURITY SETTINGS ====================
    ADMIN_ONLY_COMMANDS: List[str] = [
        "sync",
        "reload",
        "shutdown",
        "eval",
        "exec",
        "sql",
    ]
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    MAX_COMMANDS_PER_USER: int = int(
        os.getenv("MAX_COMMANDS_PER_USER", "10")
    )  # per minute

    # ==================== FEATURE FLAGS ====================
    ENABLE_WEB_SERVER: bool = os.getenv("ENABLE_WEB_SERVER", "True").lower() == "true"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    ENABLE_TABBYCAT: bool = os.getenv("ENABLE_TABBYCAT", "True").lower() == "true"
    ENABLE_TOURNAMENT_FEATURES: bool = (
        os.getenv("ENABLE_TOURNAMENT_FEATURES", "True").lower() == "true"
    )

    # ==================== ENVIRONMENT DETECTION ====================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production").lower()
    IS_DEVELOPMENT: bool = ENVIRONMENT == "development"
    IS_PRODUCTION: bool = ENVIRONMENT == "production"
    IS_TESTING: bool = ENVIRONMENT == "testing"

    @classmethod
    def get_postgres_url(cls) -> str:
        """
        Build PostgreSQL connection URL from individual components or use DATABASE_URL

        Returns:
            str: PostgreSQL connection URL
        """
        if cls.DATABASE_URL:
            return cls.DATABASE_URL

        # Build URL from components
        if not cls.POSTGRES_PASSWORD:
            return ""

        url = (
            f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        )

        # Add SSL mode if specified
        if cls.POSTGRES_SSL_MODE and cls.POSTGRES_SSL_MODE != "disable":
            url += f"?sslmode={cls.POSTGRES_SSL_MODE}"

        return url

    @classmethod
    def get_async_postgres_url(cls) -> str:
        """
        Get async PostgreSQL URL for asyncpg

        Returns:
            str: Async PostgreSQL connection URL
        """
        url = cls.get_postgres_url()
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @classmethod
    def validate_config(cls) -> bool:
        """
        Comprehensive configuration validation with detailed error reporting

        Returns:
            bool: True if configuration is valid

        Raises:
            RuntimeError: If critical configuration issues are found
        """
        print("🔍 Validating configuration...")

        # Validate Python version
        ConfigValidator.validate_python_version()

        # Build configuration dictionary for validation
        config_dict = {
            "BOT_TOKEN": cls.BOT_TOKEN,
            "MONGODB_CONNECTION_STRING": cls.MONGODB_CONNECTION_STRING,
            "TOPGG_TOKEN": cls.TOPGG_TOKEN,
            "TABBYCAT_API_KEY": cls.TABBYCAT_API_KEY,
        }

        # Required variables
        required_vars = ["BOT_TOKEN"]
        missing_required = ConfigValidator.validate_required_vars(
            required_vars, config_dict
        )

        if missing_required:
            raise RuntimeError(
                f"❌ Missing required environment variables: {', '.join(missing_required)}\n"
                f"Please set these variables in your environment or .env file."
            )

        # Optional but recommended variables
        optional_vars = {
            "MONGODB_CONNECTION_STRING": "database features disabled",
            "TOPGG_TOKEN": "Top.gg integration disabled",
            "TABBYCAT_API_KEY": "Tabbycat integration limited",
        }
        missing_optional = ConfigValidator.validate_optional_vars(
            optional_vars, config_dict
        )

        if missing_optional:
            print("⚠️  Missing optional environment variables:")
            for var in missing_optional:
                print(f"   - {var}")

        # Validate specific settings
        cls._validate_specific_settings()

        # Environment-specific validation
        cls._validate_environment_settings()

        print("✅ Configuration validation complete!")
        return True

    @classmethod
    def _validate_specific_settings(cls):
        """Validate specific configuration values"""
        # Validate shard count
        if cls.SHARD_COUNT < 1:
            raise ValueError("SHARD_COUNT must be at least 1")

        # Validate timeouts
        if cls.DATABASE_TIMEOUT < 1:
            raise ValueError("DATABASE_TIMEOUT must be at least 1 second")

        if cls.COMMAND_TIMEOUT < 1:
            raise ValueError("COMMAND_TIMEOUT must be at least 1 second")

        # Validate port
        if not 1024 <= cls.WEB_SERVER_PORT <= 65535:
            raise ValueError("WEB_SERVER_PORT must be between 1024 and 65535")

    @classmethod
    def _validate_environment_settings(cls):
        """Validate environment-specific settings"""
        if cls.IS_DEVELOPMENT:
            print("🛠️  Development mode enabled")
            if not cls.TEST_GUILD_ID:
                print("⚠️  Consider setting TEST_GUILD_ID for faster command testing")

        elif cls.IS_PRODUCTION:
            print("🚀 Production mode enabled")
            if cls.WEB_SERVER_DEBUG:
                print("⚠️  DEBUG mode should be disabled in production")

        elif cls.IS_TESTING:
            print("🧪 Testing mode enabled")

    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """Get a summary of current configuration (excluding sensitive data)"""
        return {
            "bot_name": cls.BOT_NAME,
            "bot_version": cls.BOT_VERSION,
            "environment": cls.ENVIRONMENT,
            "shard_count": cls.SHARD_COUNT,
            "web_server_port": cls.WEB_SERVER_PORT,
            "database_configured": bool(cls.MONGODB_CONNECTION_STRING),
            "topgg_configured": bool(cls.TOPGG_TOKEN),
            "tabbycat_configured": bool(cls.TABBYCAT_API_KEY),
            "test_guild_configured": bool(cls.TEST_GUILD_ID),
            "features": {
                "web_server": cls.ENABLE_WEB_SERVER,
                "metrics": cls.ENABLE_METRICS,
                "tabbycat": cls.ENABLE_TABBYCAT,
                "tournaments": cls.ENABLE_TOURNAMENT_FEATURES,
            },
        }

    @classmethod
    def print_config_summary(cls):
        """Print a formatted configuration summary"""
        summary = cls.get_config_summary()

        print("=" * 60)
        print("📊 CONFIGURATION SUMMARY")
        print("=" * 60)
        print(f"🤖 Bot: {summary['bot_name']} v{summary['bot_version']}")
        print(f"🌍 Environment: {summary['environment']}")
        print(f"🔀 Shards: {summary['shard_count']}")
        print(f"🌐 Web Server: Port {summary['web_server_port']}")
        print()
        print("🔌 INTEGRATIONS:")
        print(f"   Database: {'✅' if summary['database_configured'] else '❌'}")
        print(f"   Top.gg: {'✅' if summary['topgg_configured'] else '❌'}")
        print(f"   Tabbycat: {'✅' if summary['tabbycat_configured'] else '❌'}")
        print(f"   Test Guild: {'✅' if summary['test_guild_configured'] else '❌'}")
        print()
        print("🚀 FEATURES:")
        for feature, enabled in summary["features"].items():
            print(f"   {feature.title()}: {'✅' if enabled else '❌'}")
        print("=" * 60)


# Validate configuration immediately when module is imported
# This ensures early detection of configuration issues
if __name__ != "__main__":
    try:
        Config.validate_config()
    except (RuntimeError, ValueError, OSError) as e:
        print(f"❌ Configuration validation failed: {e}")
        # Don't exit here - let the main application handle the error
