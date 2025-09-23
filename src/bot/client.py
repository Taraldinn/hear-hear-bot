"""
Enhanced Bot Client - Production Ready
Author: aldinn
Email: kferdoush617@gmail.com

Modern, scalable Discord bot client with comprehensive error handling,
logging, and production optimizations.
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
import time
from typing import Optional, List, Dict, Any
from pathlib import Path

from config.settings import Config
from src.database.connection import database

# Configure module logger
logger = logging.getLogger(__name__)


class BotMetrics:
    """Track bot performance metrics"""

    def __init__(self):
        self.command_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self.last_heartbeat = time.time()

    def increment_command(self):
        """Increment command usage counter"""
        self.command_count += 1

    def increment_error(self):
        """Increment error counter"""
        self.error_count += 1

    def update_heartbeat(self):
        """Update last heartbeat timestamp"""
        self.last_heartbeat = time.time()

    def get_uptime(self) -> str:
        """Get formatted uptime string"""
        uptime_seconds = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds or not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)


class HearHearBot(commands.AutoShardedBot):
    """
    Enhanced Discord bot with production-ready features:
    - Auto-sharding for scalability
    - Comprehensive error handling
    - Performance monitoring
    - Graceful shutdown handling
    - Database integration
    """

    def __init__(self):
        # Configure intents for optimal performance
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True

        super().__init__(
            command_prefix=Config.BOT_PREFIX,
            shard_count=Config.SHARD_COUNT,
            intents=intents,
            help_command=None,  # Custom help command
            # Performance optimizations
            chunk_guilds_at_startup=False,
            member_cache_flags=discord.MemberCacheFlags.from_intents(intents),
            max_messages=1000,  # Limit message cache for memory efficiency
        )

        # Initialize components
        self.database = database
        self.metrics = BotMetrics()
        self.web_server = None
        self._ready = False
        self._shutdown_requested = False

        # Extension tracking
        self.loaded_extensions: List[str] = []
        self.failed_extensions: List[str] = []

    async def setup_hook(self):
        """
        Called when the bot is starting up.
        Loads extensions and syncs commands.
        """
        logger.info("🔧 Bot setup hook initiated")

        try:
            # Load all extensions
            await self.load_extensions()

            # Sync slash commands
            await self.sync_commands()

            # Start background tasks
            self.loop.create_task(self.heartbeat_task())

            logger.info("✅ Bot setup completed successfully")

        except Exception as e:
            logger.error(f"❌ Critical error in setup_hook: {e}", exc_info=True)
            raise

    async def load_extensions(self):
        """Load all bot extensions with comprehensive error handling"""
        extensions = [
            "src.commands.slash_commands",
            "src.commands.timer",
            "src.commands.debate",
            "src.commands.utility",
            "src.commands.admin",
            "src.commands.tabby",
            "src.commands.tournament",
            "src.commands.reaction_roles",
            "src.commands.configuration",
            "src.commands.moderation",
            "src.commands.logging",
            "src.commands.help",
            "src.events.error",
            "src.events.member",
        ]

        logger.info(f"📦 Loading {len(extensions)} extensions...")

        for extension in extensions:
            try:
                await self.load_extension(extension)
                self.loaded_extensions.append(extension)
                logger.info(f"✅ Loaded: {extension}")

            except commands.ExtensionNotFound:
                logger.warning(f"⚠️  Extension not found: {extension}")
                self.failed_extensions.append(extension)

            except commands.ExtensionFailed as e:
                logger.error(f"❌ Failed to load {extension}: {e}")
                self.failed_extensions.append(extension)

            except Exception as e:
                logger.error(
                    f"💥 Unexpected error loading {extension}: {e}", exc_info=True
                )
                self.failed_extensions.append(extension)

        logger.info(
            f"📊 Extension Summary: {len(self.loaded_extensions)} loaded, {len(self.failed_extensions)} failed"
        )

        if self.failed_extensions:
            logger.warning(f"⚠️  Failed extensions: {', '.join(self.failed_extensions)}")

    async def sync_commands(self, guild_id: Optional[int] = None):
        """
        Sync slash commands with enhanced error handling and logging

        Args:
            guild_id: If provided, sync to specific guild for instant testing
        """
        try:
            # Brief delay to ensure Discord API readiness
            await asyncio.sleep(2)

            if guild_id:
                # Guild-specific sync for testing
                guild = discord.Object(id=guild_id)
                logger.info(
                    f"🔄 Syncing commands to guild {guild_id} for instant testing..."
                )

                # Clear and copy global commands to guild
                self.tree.clear_commands(guild=guild)
                self.tree.copy_global_to(guild=guild)

                # Sync to guild
                synced = await self.tree.sync(guild=guild)
                logger.info(
                    f"⚡ Successfully synced {len(synced)} commands to guild {guild_id}"
                )

                # Log command names for debugging
                command_names = [cmd.name for cmd in synced]
                logger.info(f"📝 Guild commands: {', '.join(command_names)}")
                return

            # Global sync logic
            logger.info("🌍 Syncing global commands...")

            try:
                existing_commands = await self.tree.fetch_commands()
                logger.info(
                    f"📋 Found {len(existing_commands)} existing global commands"
                )

                # Sync global commands
                synced = await self.tree.sync()
                logger.info(f"✅ Successfully synced {len(synced)} global commands")

                # Log synced commands
                command_names = [cmd.name for cmd in synced]
                logger.info(f"📝 Global commands: {', '.join(command_names)}")

                if len(synced) != len(existing_commands):
                    logger.info(
                        f"📊 Command count changed: {len(existing_commands)} → {len(synced)}"
                    )

            except discord.HTTPException as e:
                logger.error(f"❌ HTTP error during command sync: {e}")
                if e.status == 429:  # Rate limited
                    logger.warning("⏰ Rate limited, will retry later")

            except Exception as e:
                logger.error(
                    f"💥 Unexpected error during command sync: {e}", exc_info=True
                )

        except Exception as e:
            logger.error(f"💥 Critical error in sync_commands: {e}", exc_info=True)

    async def heartbeat_task(self):
        """Background task to monitor bot health"""
        await self.wait_until_ready()

        while not self.is_closed() and not self._shutdown_requested:
            try:
                self.metrics.update_heartbeat()

                # Log periodic health check
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    logger.info(
                        f"💓 Heartbeat - Guilds: {len(self.guilds)}, "
                        f"Users: {len(self.users)}, Latency: {self.get_latency_ms()}ms, "
                        f"Uptime: {self.metrics.get_uptime()}"
                    )

                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                logger.info("💓 Heartbeat task cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in heartbeat task: {e}")
                await asyncio.sleep(60)

    async def on_ready(self):
        """Called when the bot is ready and connected"""
        if self._ready:
            logger.info("🔄 Bot reconnected")
            return

        self._ready = True
        logger.info("=" * 60)
        logger.info(f"🤖 {self.user} is now online!")
        logger.info(f"👥 Connected to {len(self.guilds)} guilds")
        logger.info(f"👤 Serving {len(self.users)} users")
        logger.info(f"🏓 Latency: {self.get_latency_ms()}ms")
        logger.info(f"📊 Extensions loaded: {len(self.loaded_extensions)}")

        if Config.TEST_GUILD_ID:
            logger.info(f"🧪 Test guild configured: {Config.TEST_GUILD_ID}")

        logger.info("=" * 60)

        # Set bot status
        try:
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=f"debates in {len(self.guilds)} servers | /help",
            )
            await self.change_presence(activity=activity)
            logger.info("✅ Bot status updated")

        except Exception as e:
            logger.error(f"❌ Failed to set bot status: {e}")

    async def on_command(self, ctx):
        """Called when a command is invoked"""
        self.metrics.increment_command()
        logger.debug(f"Command used: {ctx.command.name} by {ctx.author} in {ctx.guild}")

    async def on_command_error(self, ctx, error):
        """Global command error handler"""
        self.metrics.increment_error()

        # Log the error
        logger.error(f"Command error in {ctx.command}: {error}", exc_info=error)

        # Handle specific error types
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                "❌ I don't have the required permissions to execute this command."
            )

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏰ Command is on cooldown. Try again in {error.retry_after:.2f} seconds."
            )

        else:
            await ctx.send("❌ An unexpected error occurred. Please try again later.")

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        """Global slash command error handler"""
        self.metrics.increment_error()

        logger.error(f"Slash command error: {error}", exc_info=error)

        # Respond to the interaction if not already responded
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while processing your command. Please try again later.",
                    ephemeral=True,
                )
        except Exception as e:
            logger.error(f"Failed to send error response: {e}")

    def get_latency_ms(self) -> int:
        """Get bot latency in milliseconds"""
        return round(self.latency * 1000)

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics"""
        return {
            "uptime": self.metrics.get_uptime(),
            "latency_ms": self.get_latency_ms(),
            "guilds": len(self.guilds),
            "users": len(self.users),
            "commands_used": self.metrics.command_count,
            "errors": self.metrics.error_count,
            "extensions_loaded": len(self.loaded_extensions),
            "extensions_failed": len(self.failed_extensions),
            "memory_usage": self._get_memory_usage(),
            "is_ready": self._ready,
        }

    def _get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage statistics"""
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss": memory_info.rss,
                "vms": memory_info.vms,
                "percent": process.memory_percent(),
            }
        except ImportError:
            return {"error": "psutil not available"}

    async def close(self):
        """Enhanced shutdown with proper cleanup"""
        if self._shutdown_requested:
            return

        self._shutdown_requested = True
        logger.info("🛑 Bot shutdown initiated")

        try:
            # Stop background tasks
            for task in asyncio.all_tasks():
                if task != asyncio.current_task() and not task.done():
                    task.cancel()

            # Close database connection
            if self.database:
                await self.database.close()
                logger.info("🗄️  Database connection closed")

            # Close bot connection
            if not self.is_closed():
                await super().close()
                logger.info("🔌 Bot connection closed")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
        finally:
            logger.info("✅ Bot shutdown complete")

    async def force_sync_commands(self, guild_id: Optional[int] = None):
        """Force sync commands - useful for manual sync operations"""
        logger.info("🔄 Force syncing commands...")
        await self.sync_commands(guild_id)


def create_bot() -> HearHearBot:
    """
    Create and return a configured bot instance

    Returns:
        HearHearBot: Configured bot instance ready for use
    """
    logger.info("🏗️  Creating bot instance...")
    bot = HearHearBot()
    logger.info("✅ Bot instance created successfully")
    return bot
