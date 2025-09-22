"""
Enhanced Database Connection Manager - Production Ready
Author: aldinn
Email: kferdoush617@gmail.com

Robust database connection management with enhanced error handling,
connection pooling, and production optimizations.
"""

import asyncio
import logging
import ssl
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database as MongoDatabase
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    OperationFailure,
    ConfigurationError,
    NetworkTimeout,
    AutoReconnect
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
                
                # Create client with enhanced SSL/TLS configuration for MongoDB Atlas
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
                    
                    # Enhanced SSL/TLS Configuration for MongoDB Atlas
                    tls=True,
                    tlsAllowInvalidCertificates=False,
                    tlsAllowInvalidHostnames=False,
                    
                    # Additional connection stability settings
                    heartbeatFrequencyMS=10000,
                    waitQueueTimeoutMS=10000,
                    
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
                
                logger.info("✅ Successfully connected to MongoDB Atlas!")
                logger.info("📊 Database: %s, Tabby Database: %s", 
                          Config.DATABASE_NAME, Config.TABBY_DATABASE_NAME)
                
                return True

            except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout, AutoReconnect) as e:
                error_msg = str(e).lower()
                if "ssl" in error_msg or "tls" in error_msg:
                    logger.warning("❌ SSL/TLS connection failed (attempt %d): %s", attempt, str(e))
                    logger.info("💡 Tip: Verify MongoDB Atlas network access list and SSL settings")
                    
                    # Try fallback connection on last attempt
                    if attempt == self.max_connection_attempts:
                        logger.info("🔄 Attempting alternative SSL configuration...")
                        if self._try_alternative_ssl_connection(connection_string):
                            return True
                else:
                    logger.warning("❌ Database connection failed (attempt %d): %s", attempt, str(e))
                
            except ConfigurationError as e:
                logger.error("⚙️  Database configuration error: %s", str(e))
                break  # Don't retry configuration errors
                
            except OperationFailure as e:
                logger.error("🔐 Database authentication failed: %s", str(e))
                break  # Don't retry auth failures
                
            except ssl.SSLError as e:
                logger.error("🔒 SSL Certificate error (attempt %d): %s", attempt, str(e))
                logger.info("💡 This might be due to network restrictions or outdated certificates")
                
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
        logger.warning("🔄 This is likely due to Python 3.13+ and OpenSSL 3.0+ compatibility issues with MongoDB Atlas")
        logger.info("� The bot will continue in database-free mode with reduced functionality:")
        logger.info("   ✅ Discord commands will work normally")
        logger.info("   ✅ Timer functionality will work")
        logger.info("   ❌ User preferences won't be saved")
        logger.info("   ❌ Persistent data features disabled")
        logger.info("   ❌ Analytics and logging reduced")
        
        logger.info("🔧 To fix this issue:")
        logger.info("   1. Use Python 3.11 or 3.12 instead of 3.13+")
        logger.info("   2. Update to a newer pymongo version when available")
        logger.info("   3. Check MongoDB Atlas network access whitelist")
        logger.info("   4. Verify your connection string is correct")
        
        self._set_disconnected_state()
        return False

    def _try_alternative_ssl_connection(self, connection_string: str) -> bool:
        """
        Try connection with alternative SSL configuration for OpenSSL compatibility
        Uses different approaches to handle Python 3.13+ and OpenSSL 3.0+ compatibility issues
        """
        
        # Strategy 1: Force older TLS version by modifying connection string
        try:
            logger.info("🔄 Trying connection with TLS 1.2 enforcement...")
            
            # Add TLS version parameter to connection string if not present
            if "tlsVersion=" not in connection_string:
                separator = "&" if "?" in connection_string else "?"
                modified_connection = f"{connection_string}{separator}tlsVersion=1.2"
            else:
                modified_connection = connection_string
            
            self.client = MongoClient(
                modified_connection,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                maxPoolSize=5,
                retryWrites=True,
            )
            
            # Test connection
            self.db = self.client[Config.DATABASE_NAME]
            self.tabby_db = self.client[Config.TABBY_DATABASE_NAME]
            self.client.admin.command("ping")
            
            # Initialize health checker
            self.health_checker = DatabaseHealthChecker(self.client)
            self.is_connected = True
            
            logger.info("✅ Connected using TLS 1.2 enforcement!")
            logger.info("📊 Database: %s, Tabby Database: %s", 
                      Config.DATABASE_NAME, Config.TABBY_DATABASE_NAME)
            
            return True
            
        except Exception as e:
            logger.warning(f"❌ TLS 1.2 enforcement failed: {str(e)[:100]}...")
        
        # Strategy 2: Use legacy ssl parameter instead of tls
        try:
            logger.info("🔄 Trying legacy SSL parameter...")
            
            self.client = MongoClient(
                connection_string,
                ssl=True,  # Use old ssl parameter
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                maxPoolSize=3,
                retryWrites=True,
            )
            
            # Test connection
            self.db = self.client[Config.DATABASE_NAME]
            self.tabby_db = self.client[Config.TABBY_DATABASE_NAME]
            self.client.admin.command("ping")
            
            # Initialize health checker
            self.health_checker = DatabaseHealthChecker(self.client)
            self.is_connected = True
            
            logger.warning("⚠️  Connected using legacy SSL parameter")
            logger.info("📊 Database: %s, Tabby Database: %s", 
                      Config.DATABASE_NAME, Config.TABBY_DATABASE_NAME)
            
            return True
            
        except Exception as e:
            logger.warning(f"❌ Legacy SSL parameter failed: {str(e)[:100]}...")
        
        # Strategy 3: Connection string only (let MongoDB handle SSL automatically)
        try:
            logger.info("🔄 Trying connection string defaults...")
            
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=45000,  # Longer timeout
                connectTimeoutMS=45000,
                maxPoolSize=3,
            )
            
            # Test connection
            self.db = self.client[Config.DATABASE_NAME]
            self.tabby_db = self.client[Config.TABBY_DATABASE_NAME]
            self.client.admin.command("ping")
            
            # Initialize health checker
            self.health_checker = DatabaseHealthChecker(self.client)
            self.is_connected = True
            
            logger.info("✅ Connected using connection string defaults!")
            logger.info("📊 Database: %s, Tabby Database: %s", 
                      Config.DATABASE_NAME, Config.TABBY_DATABASE_NAME)
            
            return True
            
        except Exception as e:
            logger.warning(f"❌ Connection string defaults failed: {str(e)[:100]}...")
        
        # Strategy 4: Modified connection string for compatibility
        try:
            logger.info("🔄 Trying compatibility connection string modifications...")
            
            # Remove potential problematic parameters and add compatibility ones
            base_connection = connection_string.split('?')[0]
            compat_params = "?retryWrites=true&w=majority&tlsVersion=1.2&ssl=true"
            
            compat_connection = f"{base_connection}{compat_params}"
            
            self.client = MongoClient(
                compat_connection,
                serverSelectionTimeoutMS=60000,  # Very long timeout
                connectTimeoutMS=60000,
                maxPoolSize=2,  # Minimal pool
            )
            
            # Test connection
            self.db = self.client[Config.DATABASE_NAME]
            self.tabby_db = self.client[Config.TABBY_DATABASE_NAME]
            self.client.admin.command("ping")
            
            # Initialize health checker
            self.health_checker = DatabaseHealthChecker(self.client)
            self.is_connected = True
            
            logger.warning("⚠️  Connected using compatibility modifications")
            logger.info("📊 Database: %s, Tabby Database: %s", 
                      Config.DATABASE_NAME, Config.TABBY_DATABASE_NAME)
            
            return True
            
        except Exception as e:
            logger.warning(f"❌ Compatibility modifications failed: {str(e)[:100]}...")
        
        logger.error("❌ All alternative SSL strategies failed")
        logger.info("💡 This might be due to:")
        logger.info("   - Python 3.13+ and OpenSSL 3.0+ compatibility issues with MongoDB Atlas")
        logger.info("   - Network firewall blocking MongoDB Atlas connections")
        logger.info("   - IP address not whitelisted in MongoDB Atlas")
        logger.info("   - MongoDB Atlas cluster is paused or unavailable")
        
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