"""
Enhanced Bot Client - Production Ready
Author: aldinn
Email: kferdoush617@gmail.com

Modern, scalable Discord bot client with comprehensive error handling,
logging, and production optimizations.
"""

import asyncio
import logging
import os
import time
from typing import Optional, List, Dict, Any, Union

import discord
from discord.ext import commands
from discord import app_commands

from config.settings import Config
from src.database.connection import database
from src.utils.topgg_poster import TopGGPoster

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
        self.topgg_poster = TopGGPoster(self)
        self._bot_ready: bool = False
        self._shutdown_requested: bool = False

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

            # Setup and start top.gg poster if configured
            bot_id = str(self.user.id) if self.user else os.getenv("BOT_ID", "")
            if self.topgg_poster.setup(bot_id, Config.TOPGG_TOKEN):
                self.topgg_poster.start()
            else:
                logger.info("ℹ️  Top.gg integration not configured, skipping")

            logger.info("✅ Bot setup completed successfully")

        except Exception as e:
            logger.error("❌ Critical error in setup_hook: %s", e, exc_info=True)
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

        logger.info("📦 Loading %d extensions...", len(extensions))

        for extension in extensions:
            try:
                await self.load_extension(extension)
                self.loaded_extensions.append(extension)
                logger.info("✅ Loaded: %s", extension)

            except commands.ExtensionNotFound:
                logger.warning("⚠️  Extension not found: %s", extension)
                self.failed_extensions.append(extension)

            except commands.ExtensionFailed as e:
                logger.error("❌ Failed to load %s: %s", extension, e)
                self.failed_extensions.append(extension)

            except (commands.ExtensionError, ImportError, AttributeError) as e:
                logger.error(
                    "💥 Unexpected error loading %s: %s", extension, e, exc_info=True
                )
                self.failed_extensions.append(extension)

        logger.info(
            "📊 Extension Summary: %d loaded, %d failed",
            len(self.loaded_extensions),
            len(self.failed_extensions),
        )

        if self.failed_extensions:
            logger.warning(
                "⚠️  Failed extensions: %s", ", ".join(self.failed_extensions)
            )

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
                    "🔄 Syncing commands to guild %s for instant testing...", guild_id
                )

                # Clear and copy global commands to guild
                self.tree.clear_commands(guild=guild)
                self.tree.copy_global_to(guild=guild)

                # Sync to guild
                synced = await self.tree.sync(guild=guild)
                logger.info(
                    "⚡ Successfully synced %d commands to guild %s",
                    len(synced),
                    guild_id,
                )

                # Log command names for debugging
                logger.info(
                    "📝 Guild commands: %s", ", ".join(cmd.name for cmd in synced)
                )
                return

            # Global sync logic
            logger.info("🌍 Syncing global commands...")

            try:
                existing_commands = await self.tree.fetch_commands()
                logger.info(
                    "📋 Found %d existing global commands", len(existing_commands)
                )

                # Sync global commands
                synced = await self.tree.sync()
                logger.info("✅ Successfully synced %d global commands", len(synced))

                # Log synced commands
                logger.info(
                    "📝 Global commands: %s", ", ".join(cmd.name for cmd in synced)
                )

                if len(synced) != len(existing_commands):
                    logger.info(
                        "📊 Command count changed: %d → %d",
                        len(existing_commands),
                        len(synced),
                    )

            except discord.HTTPException as e:
                logger.error("❌ HTTP error during command sync: %s", e)
                if e.status == 429:  # Rate limited
                    logger.warning("⏰ Rate limited, will retry later")

            except discord.ConnectionClosed as e:
                logger.error(
                    "💥 Connection error during command sync: %s", e, exc_info=True
                )

        except (
            discord.HTTPException,
            discord.ConnectionClosed,
            discord.LoginFailure,
        ) as e:
            logger.error("💥 Critical error in sync_commands: %s", e, exc_info=True)

    async def heartbeat_task(self):
        """Background task to monitor bot health"""
        await self.wait_until_ready()

        while not self.is_closed() and not self._shutdown_requested:
            try:
                self.metrics.update_heartbeat()

                # Log periodic health check
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    logger.info(
                        "💓 Heartbeat - Guilds: %d, Users: %d, Latency: %dms, Uptime: %s",
                        len(self.guilds),
                        len(self.users),
                        self.get_latency_ms(),
                        self.metrics.get_uptime(),
                    )

                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                logger.info("💓 Heartbeat task cancelled")
                break
            except discord.ConnectionClosed as e:
                logger.error("❌ Error in heartbeat task: %s", e)
                await asyncio.sleep(60)

    async def on_ready(self):
        """Called when the bot is ready and connected"""
        if self._bot_ready:
            logger.info("🔄 Bot reconnected")
            return

        self._bot_ready = True
        logger.info("=" * 60)
        logger.info("🤖 %s is now online!", self.user)
        logger.info("👥 Connected to %d guilds", len(self.guilds))
        logger.info("👤 Serving %d users", len(self.users))
        logger.info("🏓 Latency: %dms", self.get_latency_ms())
        logger.info("📊 Extensions loaded: %d", len(self.loaded_extensions))

        if Config.TEST_GUILD_ID:
            logger.info("🧪 Test guild configured: %s", Config.TEST_GUILD_ID)

        # Start top.gg poster if not already started
        if not self.topgg_poster.is_running() and self.user:
            bot_id = str(self.user.id)
            if self.topgg_poster.setup(bot_id, Config.TOPGG_TOKEN):
                self.topgg_poster.start()

        logger.info("=" * 60)

        # Set bot status
        try:
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=f"debates in {len(self.guilds)} servers | /help",
            )
            await self.change_presence(activity=activity)
            logger.info("✅ Bot status updated")

        except (discord.HTTPException, discord.LoginFailure) as e:
            logger.error("❌ Failed to set bot status: %s", e)

    async def on_command(self, ctx):  # pylint: disable=unused-argument
        """Called when a command is invoked"""
        self.metrics.increment_command()
        logger.debug(
            "Command used: %s by %s in %s", ctx.command.name, ctx.author, ctx.guild
        )

    async def on_command_error(self, ctx, error):  # pylint: disable=arguments-differ
        """Global command error handler"""
        self.metrics.increment_error()

        # Log the error
        logger.error("Command error in %s: %s", ctx.command, error, exc_info=error)

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

        logger.error("Slash command error: %s", error, exc_info=error)

        # Respond to the interaction if not already responded
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while processing your command. Please try again later.",
                    ephemeral=True,
                )
        except (discord.HTTPException, discord.NotFound) as e:
            logger.error("Failed to send error response: %s", e)

    def get_latency_ms(self) -> int:
        """Get bot latency in milliseconds"""
        return round(self.latency * 1000)

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics"""
        stats = {
            "uptime": self.metrics.get_uptime(),
            "latency_ms": self.get_latency_ms(),
            "guilds": len(self.guilds),
            "users": len(self.users),
            "commands_used": self.metrics.command_count,
            "errors": self.metrics.error_count,
            "extensions_loaded": len(self.loaded_extensions),
            "extensions_failed": len(self.failed_extensions),
            "memory_usage": self._get_memory_usage(),
            "is_ready": self._bot_ready,
        }

        # Add top.gg status if available
        if self.topgg_poster:
            stats["topgg"] = self.topgg_poster.get_status()

        return stats

    def _get_memory_usage(self) -> Dict[str, Union[int, float, str]]:
        """Get memory usage statistics"""
        try:
            import psutil  # pylint: disable=import-outside-toplevel # type: ignore

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
            # Stop top.gg poster
            if self.topgg_poster:
                self.topgg_poster.stop()
                logger.info("📊 Top.gg poster stopped")

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

        except (OSError, discord.ConnectionClosed, asyncio.CancelledError) as e:
            logger.error("❌ Error during shutdown: %s", e)
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
