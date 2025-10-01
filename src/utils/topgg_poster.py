"""
Top.gg Server Count Poster
Author: aldinn
Email: kferdoush617@gmail.com

Automatically posts Discord bot server count to top.gg
at regular intervals for bot list statistics.
"""

import asyncio
import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


class TopGGPoster:
    """
    Handles automatic posting of bot server count to top.gg.

    This class manages a background task that periodically updates
    the bot's server count on top.gg using their API.
    """

    def __init__(self, bot):
        """
        Initialize the TopGG poster.

        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.bot_id: Optional[str] = None
        self.api_token: Optional[str] = None
        self.post_interval: int = 1800  # 30 minutes (top.gg recommended)
        self.task: Optional[asyncio.Task] = None
        self._running: bool = False

    def setup(self, bot_id: str, api_token: str, interval: int = 1800) -> bool:
        """
        Configure the top.gg poster with credentials.

        Args:
            bot_id: Your Discord bot's ID
            api_token: Your top.gg API token
            interval: Posting interval in seconds (default: 1800 = 30 minutes)

        Returns:
            bool: True if setup successful, False otherwise
        """
        if not bot_id or not api_token:
            logger.warning("⚠️  Top.gg credentials not provided, poster disabled")
            return False

        self.bot_id = bot_id
        self.api_token = api_token
        self.post_interval = interval

        logger.info(
            "✅ Top.gg poster configured (bot_id: %s, interval: %ds)", bot_id, interval
        )
        return True

    def start(self) -> bool:
        """
        Start the background task for posting server counts.

        Returns:
            bool: True if task started successfully, False otherwise
        """
        if not self.bot_id or not self.api_token:
            logger.warning("⚠️  Top.gg not configured, cannot start poster")
            return False

        if self._running:
            logger.warning("⚠️  Top.gg poster already running")
            return False

        self._running = True
        self.task = self.bot.loop.create_task(self._posting_loop())
        logger.info("🚀 Top.gg poster task started")
        return True

    def stop(self):
        """Stop the background posting task."""
        if self.task and not self.task.done():
            self.task.cancel()
            self._running = False
            logger.info("🛑 Top.gg poster task stopped")

    def is_running(self) -> bool:
        """
        Check if the poster is currently running.

        Returns:
            bool: True if running, False otherwise
        """
        return self._running

    async def post_stats(self) -> bool:
        """
        Post current server count to top.gg.

        Returns:
            bool: True if post successful, False otherwise
        """
        if not self.bot_id or not self.api_token:
            logger.error("❌ Top.gg credentials not configured")
            return False

        server_count = len(self.bot.guilds)
        url = f"https://top.gg/api/bots/{self.bot_id}/stats"

        headers = {"Authorization": self.api_token, "Content-Type": "application/json"}

        payload = {"server_count": server_count}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        logger.info(
                            "✅ Posted to top.gg: %d servers (status: %d)",
                            server_count,
                            response.status,
                        )
                        return True

                    error_text = await response.text()
                    logger.error(
                        "❌ Top.gg API error (status %d): %s",
                        response.status,
                        error_text,
                    )
                    return False

        except aiohttp.ClientError as e:
            logger.error("❌ Network error posting to top.gg: %s", e)
            return False
        except asyncio.TimeoutError:
            logger.error("❌ Timeout posting to top.gg")
            return False
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("❌ Unexpected error posting to top.gg: %s", e, exc_info=True)
            return False

    async def _posting_loop(self):
        """Background task that posts server count at regular intervals."""
        await self.bot.wait_until_ready()

        logger.info(
            "📊 Top.gg posting loop started (interval: %d seconds)", self.post_interval
        )

        while self._running:
            try:
                # Post stats
                success = await self.post_stats()

                if success:
                    logger.debug(
                        "✅ Top.gg stats posted successfully, next post in %d seconds",
                        self.post_interval,
                    )
                else:
                    logger.warning(
                        "⚠️  Failed to post to top.gg, will retry in %d seconds",
                        self.post_interval,
                    )

                # Wait for next interval
                await asyncio.sleep(self.post_interval)

            except asyncio.CancelledError:
                logger.info("🛑 Top.gg posting loop cancelled")
                break
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(
                    "❌ Error in top.gg posting loop: %s (retrying in %d seconds)",
                    e,
                    self.post_interval,
                    exc_info=True,
                )
                await asyncio.sleep(self.post_interval)

    def get_status(self) -> dict:
        """
        Get the current status of the top.gg poster.

        Returns:
            dict: Status information including configuration and running state
        """
        return {
            "configured": bool(self.bot_id and self.api_token),
            "running": self._running,
            "bot_id": self.bot_id if self.bot_id else "Not configured",
            "interval": self.post_interval,
            "server_count": len(self.bot.guilds) if self.bot else 0,
        }
