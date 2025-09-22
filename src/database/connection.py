"""
Enhanced Database Connection Manager - Production Ready
Author: aldinn
Email: kferdoush617@gmail.com

Robust database connection management with enhanced error handling,
connection pooling, and production optimizations.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database as MongoDatabase
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    OperationFailure,
    ConfigurationError
)

from config.settings import Config

logger = logging.getLogger(__name__)


class DatabaseHealthChecker:
    """Monitor database connection health"""
    
    def __init__(self, client: Optional[MongoClient]):
        self.client = client
        self.last_health_check = None
        self.health_check_interval = 300  # 5 minutes
    
    async def check_health(self) -> bool:
        """Check if database connection is healthy"""
        if not self.client:
            return False
            
        try:
            # Simple ping command to test connectivity
            result = self.client.admin.command("ping")
            self.last_health_check = asyncio.get_event_loop().time()
            return result.get("ok", 0) == 1
        except Exception as e:
            logger.warning("Database health check failed: %s", str(e))
            return False


class Database:
    """
    Enhanced database connection and operations manager
    
    Features:
    - Automatic connection retry with exponential backoff
    - Connection health monitoring
    - Comprehensive error handling
    - Connection pooling optimization
    - Graceful degradation when database is unavailable
    """

    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[MongoDatabase] = None
        self.tabby_db: Optional[MongoDatabase] = None
        self.health_checker: Optional[DatabaseHealthChecker] = None
        self.connection_attempts = 0
        self.max_connection_attempts = 3
        self.is_connected = False
        
        # Initialize connection
        self.connect()

    def connect(self) -> bool:
        """
        Establish database connection with comprehensive error handling
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        connection_string = Config.MONGODB_CONNECTION_STRING

        if not connection_string:
            logger.warning("⚠️  MONGODB_CONNECTION_STRING not provided - database features disabled")
            self._set_disconnected_state()
            return False

        for attempt in range(1, self.max_connection_attempts + 1):
            try:
                logger.info("🔌 Attempting database connection (attempt %d/%d)...", 
                          attempt, self.max_connection_attempts)
                
                # Create client with production-optimized settings
                self.client = MongoClient(
                    connection_string,
                    # Connection timeouts
                    serverSelectionTimeoutMS=Config.DATABASE_TIMEOUT * 1000,
                    connectTimeoutMS=Config.DATABASE_TIMEOUT * 1000,
                    socketTimeoutMS=Config.DATABASE_TIMEOUT * 1000,
                    
                    # Connection pooling
                    maxPoolSize=Config.DATABASE_MAX_POOL_SIZE,
                    minPoolSize=5,
                    maxIdleTimeMS=30000,
                    
                    # Reliability settings
                    retryWrites=True,
                    retryReads=True,
                    w="majority",
                    
                    # Application name for monitoring
                    appName=f"{Config.BOT_NAME}-v{Config.BOT_VERSION}",
                )

                # Get database instances
                self.db = self.client[Config.DATABASE_NAME]
                self.tabby_db = self.client[Config.TABBY_DATABASE_NAME]

                # Test connection with ping
                self.client.admin.command("ping")
                
                # Initialize health checker
                self.health_checker = DatabaseHealthChecker(self.client)
                
                self.is_connected = True
                self.connection_attempts = attempt
                
                logger.info("✅ Successfully connected to MongoDB!")
                logger.info("📊 Database: %s, Tabby Database: %s", 
                          Config.DATABASE_NAME, Config.TABBY_DATABASE_NAME)
                
                return True

            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning("❌ Database connection failed (attempt %d): %s", attempt, str(e))
                
            except ConfigurationError as e:
                logger.error("⚙️  Database configuration error: %s", str(e))
                break  # Don't retry configuration errors
                
            except OperationFailure as e:
                logger.error("🔐 Database authentication failed: %s", str(e))
                break  # Don't retry auth failures
                
            except Exception as e:
                logger.error("💥 Unexpected database error (attempt %d): %s", attempt, str(e))
                
            # Wait before retrying (exponential backoff)
            if attempt < self.max_connection_attempts:
                wait_time = 2 ** attempt
                logger.info("⏰ Retrying in %d seconds...", wait_time)
                import time
                time.sleep(wait_time)

        # All connection attempts failed
        logger.error("❌ Failed to establish database connection after %d attempts", 
                    self.max_connection_attempts)
        logger.info("🔄 Bot will continue without database functionality")
        
        self._set_disconnected_state()
        return False

    def _set_disconnected_state(self):
        """Set the database to disconnected state"""
        self.client = None
        self.db = None
        self.tabby_db = None
        self.health_checker = None
        self.is_connected = False

    def get_collection(self, collection_name: str, use_tabby_db: bool = False) -> Optional[Collection]:
        """
        Get a specific collection with error handling
        
        Args:
            collection_name: Name of the collection
            use_tabby_db: Whether to use the Tabby database instead of main
            
        Returns:
            Collection instance or None if unavailable
        """
        try:
            if not self.is_connected:
                logger.debug("Database not connected - collection '%s' unavailable", collection_name)
                return None

            if use_tabby_db and self.tabby_db is not None:
                return self.tabby_db[collection_name]
            elif self.db is not None:
                return self.db[collection_name]
            else:
                logger.warning("Database instance not available for collection '%s'", collection_name)
                return None
                
        except Exception as e:
            logger.error("Error accessing collection '%s': %s", collection_name, str(e))
            return None

    def get_database(self, use_tabby_db: bool = False) -> Optional[MongoDatabase]:
        """
        Get the database instance
        
        Args:
            use_tabby_db: Whether to return the Tabby database
            
        Returns:
            Database instance or None if unavailable
        """
        if not self.is_connected:
            return None
            
        return self.tabby_db if use_tabby_db else self.db

    async def health_check(self) -> bool:
        """
        Perform a health check on the database connection
        
        Returns:
            bool: True if database is healthy, False otherwise
        """
        if not self.health_checker:
            return False
            
        return await self.health_checker.check_health()

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics and health information"""
        stats = {
            "is_connected": self.is_connected,
            "connection_attempts": self.connection_attempts,
            "databases": {
                "main": Config.DATABASE_NAME if self.db is not None else None,
                "tabby": Config.TABBY_DATABASE_NAME if self.tabby_db is not None else None,
            }
        }
        
        if self.client and self.is_connected:
            try:
                # Get server info
                server_info = self.client.server_info()
                stats.update({
                    "server_version": server_info.get("version", "unknown"),
                    "max_pool_size": Config.DATABASE_MAX_POOL_SIZE,
                    "timeout_ms": Config.DATABASE_TIMEOUT * 1000,
                })
            except Exception as e:
                logger.warning("Could not retrieve server stats: %s", str(e))
                
        return stats

    def reconnect(self) -> bool:
        """
        Attempt to reconnect to the database
        
        Returns:
            bool: True if reconnection successful
        """
        logger.info("🔄 Attempting database reconnection...")
        
        # Close existing connection
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logger.warning("Error closing old connection: %s", str(e))
        
        # Reset state and reconnect
        self._set_disconnected_state()
        return self.connect()

    def close_connection(self):
        """Close database connection gracefully"""
        if self.client:
            try:
                self.client.close()
                logger.info("🔌 Database connection closed")
            except Exception as e:
                logger.warning("Error closing database connection: %s", str(e))
        
        self._set_disconnected_state()

    async def close(self):
        """Async close method for bot shutdown"""
        logger.info("🛑 Shutting down database connection...")
        self.close_connection()


# Global database instance
database = Database()


# Export commonly used functions for backward compatibility
def get_collection(collection_name: str, use_tabby_db: bool = False) -> Optional[Collection]:
    """Get a collection from the global database instance"""
    return database.get_collection(collection_name, use_tabby_db)


def get_database(use_tabby_db: bool = False) -> Optional[MongoDatabase]:
    """Get a database from the global database instance"""
    return database.get_database(use_tabby_db)


def is_database_available() -> bool:
    """Check if database is available"""
    return database.is_connected