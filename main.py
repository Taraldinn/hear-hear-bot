"""
Main Bot Entry Point
Author: aldinn
Email: kferdoush617@gmail.com

Hear! Hear! Bot - A comprehensive debate bot with timing, motions, and tournament features
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from typing import Optional, Tuple
from aiohttp.web import AppRunner

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    import discord
    from config.settings import Config
    from src.bot.client import create_bot
    from web.server import WebServer
except ImportError as e:
    print(f"Critical import error: {e}")
    print(
        "Please ensure all dependencies are installed and the project structure is correct."
    )
    sys.exit(1)


class BotLogger:
    """Enhanced logging setup for production"""

    @staticmethod
    def setup_logging() -> logging.Logger:
        """Setup comprehensive logging with file rotation and proper formatting"""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # Configure logging format
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Setup root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Remove default handlers to avoid duplication
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # File handler for general logs
        file_handler = logging.FileHandler(logs_dir / "bot.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Console handler for real-time monitoring
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Error file handler for critical issues
        error_handler = logging.FileHandler(logs_dir / "errors.log", encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # Add all handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(error_handler)

        # Suppress some noisy libraries
        logging.getLogger("discord.gateway").setLevel(logging.WARNING)
        logging.getLogger("discord.client").setLevel(logging.WARNING)
        logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

        return logging.getLogger(__name__)


class GracefulShutdown:
    """Handle graceful shutdown of bot and web server"""

    def __init__(
        self,
        bot,
        web_server: Optional[WebServer] = None,
        web_runner: Optional[AppRunner] = None,
    ):
        self.bot = bot
        self.web_server = web_server
        self.web_runner = web_runner
        self.logger = logging.getLogger(__name__)
        self.shutdown_initiated = False

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""

        def signal_handler(signum, _frame):
            if self.shutdown_initiated:
                self.logger.warning("Force shutdown requested!")
                sys.exit(1)

            self.logger.info(
                "Received signal %s, initiating graceful shutdown...", signum
            )
            self.shutdown_initiated = True

            # Create shutdown task
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.shutdown())
            else:
                asyncio.run(self.shutdown())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def shutdown(self):
        """Perform graceful shutdown"""
        try:
            self.logger.info("Starting graceful shutdown...")

            # Close bot connection
            if self.bot and not self.bot.is_closed():
                await self.bot.close()
                self.logger.info("Bot connection closed")

            # Stop web server
            if self.web_server:
                await self.web_server.stop_server()
                self.logger.info("Web server stopped")

            # Stop web runner
            if self.web_runner:
                await self.web_runner.cleanup()
                self.logger.info("Web runner cleaned up")

            self.logger.info("Graceful shutdown complete")

        except (OSError, asyncio.CancelledError, discord.DiscordException) as e:
            self.logger.error("Error during shutdown: %s", e)
        finally:
            # Force exit if needed
            sys.exit(0)


async def start_web_server(
    bot, logger
) -> Tuple[Optional[WebServer], Optional[AppRunner]]:
    """Start the web server with proper error handling"""
    web_server = None
    web_runner = None

    try:
        web_server = WebServer(bot)
        port = int(os.environ.get("PORT", 8080))

        logger.info("Starting web server on port %s...", port)
        web_runner = await web_server.start_server(port)
        logger.info("✅ Web server started successfully on port %s", port)

        # Log available endpoints
        logger.info("Available endpoints:")
        logger.info("  - Health check: http://localhost:%s/", port)
        logger.info("  - Documentation: http://localhost:%s/docs", port)
        logger.info("  - Bot stats: http://localhost:%s/stats", port)

    except (OSError, ConnectionError, ImportError) as e:
        logger.error("Failed to start web server: %s", e)
        logger.info("Continuing without web server...")
        web_server = None
        web_runner = None

    return web_server, web_runner


async def main():
    """Main bot execution function with comprehensive error handling"""
    # Setup logging
    logger = BotLogger.setup_logging()

    logger.info("=" * 60)
    logger.info("🚀 Starting Hear! Hear! Bot")
    logger.info("📋 Bot Name: %s", Config.BOT_NAME)
    logger.info("📦 Version: %s", Config.BOT_VERSION)
    logger.info("👤 Author: %s", Config.BOT_AUTHOR)
    logger.info("🔗 GitHub: %s", Config.BOT_GITHUB)
    logger.info("=" * 60)

    bot = None
    web_server = None
    web_runner = None

    try:
        # Validate configuration
        Config.validate_config()
        logger.info("✅ Configuration validated")

        # Create bot instance
        logger.info("🤖 Creating bot instance...")
        bot = create_bot()
        logger.info("✅ Bot instance created")

        # Setup graceful shutdown
        shutdown_handler = GracefulShutdown(bot)
        shutdown_handler.setup_signal_handlers()
        logger.info("✅ Signal handlers configured")

        # Start web server
        web_server, web_runner = await start_web_server(bot, logger)
        shutdown_handler.web_server = web_server
        shutdown_handler.web_runner = web_runner

        # Start the bot
        logger.info("🔌 Connecting to Discord...")
        async with bot:
            await bot.start(Config.BOT_TOKEN)

    except discord.LoginFailure:
        logger.error(
            "❌ Invalid bot token! Please check your DISCORD_BOT_TOKEN environment variable."
        )
        sys.exit(1)

    except discord.HTTPException as e:
        logger.error("❌ Discord HTTP error: %s", e)
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("🛑 Bot shutdown requested by user")

    except Exception as e:
        logger.error("💥 Fatal error: %s", e, exc_info=True)
        raise

    finally:
        # Final cleanup is handled by GracefulShutdown
        logger.info("👋 Bot shutdown complete")


if __name__ == "__main__":
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required!")
            sys.exit(1)

        # Run the bot
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n🛑 Bot startup cancelled by user")

    except SystemExit:
        pass  # Expected exit

    except (RuntimeError, ImportError, OSError) as e:
        print(f"❌ Fatal startup error: {e}")
        sys.exit(1)
