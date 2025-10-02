"""
MongoDB Database Connection Manager
Author: aldinn
Email: kferdoush617@gmail.com

Asynchronous MongoDB connection management built on top of Motor with
robust error handling, pooling, and health checks.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional, Dict, Any

from motor.motor_asyncio import (  # type: ignore[import]
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from pymongo.errors import ConfigurationError, ConnectionFailure, PyMongoError

from config.settings import Config

logger = logging.getLogger(__name__)


class MongoDatabase:
    """Asynchronous MongoDB connection manager."""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.tabby_db: Optional[AsyncIOMotorDatabase] = None
        self.is_connected: bool = False
        self.connection_attempts: int = 0
        self.max_connection_attempts: int = 3
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        """Establish a connection to MongoDB if needed."""
        async with self._lock:
            if self.is_connected and self.client:
                return True

            connection_string = Config.get_mongo_connection_string()
            if not connection_string:
                logger.error(
                    "❌ MongoDB connection string missing. "
                    "Set MONGODB_CONNECTION_STRING in the environment."
                )
                await self.close()
                return False

            for attempt in range(1, self.max_connection_attempts + 1):
                try:
                    logger.info(
                        "🔌 Connecting to MongoDB (attempt %d/%d)...",
                        attempt,
                        self.max_connection_attempts,
                    )

                    client = AsyncIOMotorClient(
                        connection_string,
                        maxPoolSize=Config.MONGODB_MAX_POOL_SIZE,
                        minPoolSize=Config.MONGODB_MIN_POOL_SIZE,
                        serverSelectionTimeoutMS=Config.MONGODB_CONNECT_TIMEOUT_MS,
                        socketTimeoutMS=Config.MONGODB_SOCKET_TIMEOUT_MS,
                        uuidRepresentation="standard",
                    )

                    await client.admin.command("ping")

                    primary_db_name = Config.DATABASE_NAME or "hearhear-bot"
                    tabby_db_name = Config.TABBY_DATABASE_NAME or "tabbybot"

                    self.client = client
                    self.db = client[primary_db_name]
                    self.tabby_db = client[tabby_db_name]

                    self.is_connected = True
                    self.connection_attempts = attempt

                    logger.info("✅ Connected to MongoDB database: %s", primary_db_name)
                    return True

                except (ConfigurationError, ConnectionFailure, PyMongoError) as exc:
                    logger.error(
                        "❌ MongoDB connection failed on attempt %d: %s", attempt, exc
                    )
                    await asyncio.sleep(min(2**attempt, 10))
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    logger.error(
                        "💥 Unexpected error while connecting to MongoDB: %s", exc
                    )
                    await asyncio.sleep(min(2**attempt, 10))

            logger.error(
                "❌ Failed to connect to MongoDB after %d attempts",
                self.max_connection_attempts,
            )
            await self.close()
            return False

    async def ensure_connected(self) -> bool:
        """Ensure the MongoDB connection is active."""
        if self.is_connected and self.client:
            return True
        return await self.connect()

    async def ping(self) -> bool:
        """Ping the MongoDB server to verify connectivity."""
        if not await self.ensure_connected() or not self.client:
            return False

        try:
            client = self.client
            if client is None:
                return False

            await client.admin.command("ping")
            return True
        except PyMongoError as exc:
            logger.error("MongoDB ping failed: %s", exc)
            await self.close()
            return False

    async def get_collection(
        self, name: str, *, use_tabby_db: bool = False
    ) -> Optional[AsyncIOMotorCollection]:
        """Return a MongoDB collection, ensuring the connection first."""
        if not await self.ensure_connected():
            return None

        target_db = self.tabby_db if use_tabby_db else self.db
        if target_db is None:
            logger.error(
                "MongoDB database reference missing (use_tabby_db=%s)", use_tabby_db
            )
            return None

        collection: AsyncIOMotorCollection = target_db[name]
        return collection

    def __getitem__(self, name: str) -> AsyncIOMotorCollection:
        """Allow dict-style access to collections for compatibility."""
        if self.db is None:
            raise KeyError("MongoDB is not connected")
        return self.db[name]

    def get_connection_stats(self) -> Dict[str, Any]:
        """Return diagnostic information about the current connection."""
        stats: Dict[str, Any] = {
            "is_connected": self.is_connected,
            "connection_attempts": self.connection_attempts,
            "database_type": "MongoDB",
            "database": {
                "primary": Config.DATABASE_NAME,
                "tabby": Config.TABBY_DATABASE_NAME,
                "max_pool_size": Config.MONGODB_MAX_POOL_SIZE,
                "min_pool_size": Config.MONGODB_MIN_POOL_SIZE,
            },
        }

        client = self.client
        if client is not None:
            address = getattr(client, "address", None)
            if callable(address):
                address = address()
            if isinstance(address, tuple) and len(address) == 2:
                host, port = address
                stats["address"] = f"{host}:{port}"

        return stats

    async def close(self):
        """Close the MongoDB client and reset state."""
        if self.client:
            self.client.close()
        self.client = None
        self.db = None
        self.tabby_db = None
        self.is_connected = False
        self.connection_attempts = 0
        logger.info("🔌 MongoDB connection closed")


# Global database instance for the bot
_database_instance = MongoDatabase()


def get_database() -> MongoDatabase:
    """Internal helper to return the shared database instance."""
    return _database_instance


# Backwards compatibility alias used across the codebase
Database = MongoDatabase

database: MongoDatabase = _database_instance
