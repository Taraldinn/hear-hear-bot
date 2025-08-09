"""
Main Bot Entry Point
Author: Tasdid Tahsin
Email: tasdidtahsin@gmail.com

Hear! Hear! Bot - A comprehensive debate bot with timing, motions, and tournament features
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config.settings import Config
from src.bot.client import create_bot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_signal_handlers(bot):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(bot.close())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main bot execution function"""
    logger.info("Starting Hear! Hear! Bot...")
    logger.info(f"Bot Name: {Config.BOT_NAME}")
    logger.info(f"Version: {Config.BOT_VERSION}")
    logger.info(f"Author: {Config.BOT_AUTHOR}")
    logger.info("=" * 50)
    
    # Create bot instance
    bot = create_bot()
    
    # Setup signal handlers
    setup_signal_handlers(bot)
    
    try:
        # Start the bot
        async with bot:
            await bot.start(Config.BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    try:
        # Validate configuration before starting
        Config.validate_config()
        
        # Run the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot startup cancelled by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)
