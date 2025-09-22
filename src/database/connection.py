"""
Enhanced PostgreSQL Database Connection Manager - Production Ready
Author: aldinn
Email: kferdoush617@gmail.com

Robust PostgreSQL database connection management with enhanced error handling,
connection pooling, and production optimizations using asyncpg and SQLAlchemy.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List

try:
    import asyncpg

    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

try:
    from sqlalchemy.ext.asyncio import (
        create_async_engine,
        AsyncSession,
        async_sessionmaker,
    )
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import text
    from sqlalchemy.exc import (
        OperationalError,
        DatabaseError,
        TimeoutError as SQLTimeoutError,
        DisconnectionError,
    )

    SQLALCHEMY_AVAILABLE = True
    # SQLAlchemy Base for ORM models
    Base = declarative_base()
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Base = None

from config.settings import Config

logger = logging.getLogger(__name__)


class DatabaseHealthChecker:
    """Monitor PostgreSQL database connection health"""

    def __init__(self, pool):
        self.pool = pool
        self.last_health_check = None
        self.health_check_interval = 300  # 5 minutes

    async def check_health(self) -> bool:
        """Check if database connection is healthy"""
        if not self.pool or not ASYNCPG_AVAILABLE:
            return False

        try:
            async with self.pool.acquire() as connection:
                await connection.execute("SELECT 1")
                self.last_health_check = asyncio.get_event_loop().time()
                return True
        except Exception as e:
            logger.warning("Database health check failed: %s", str(e))
            return False


class Database:
    """
    Enhanced PostgreSQL database connection and operations manager

    Features:
    - Automatic connection retry with exponential backoff
    - Connection health monitoring
    - Comprehensive error handling
    - Connection pooling optimization
    - Graceful degradation when database is unavailable
    - Support for both asyncpg (raw SQL) and SQLAlchemy (ORM)
    """

    def __init__(self):
        self.pool = None
        self.engine = None
        self.session_factory = None
        self.health_checker = None
        self.connection_attempts = 0
        self.max_connection_attempts = 3
        self.is_connected = False

        # Check for required dependencies
        if not ASYNCPG_AVAILABLE:
            logger.warning("asyncpg not available - PostgreSQL features disabled")
            logger.info("Install with: pip install asyncpg")
            return

        if not SQLALCHEMY_AVAILABLE:
            logger.warning("SQLAlchemy not available - ORM features disabled")
            logger.info("Install with: pip install sqlalchemy[asyncio]")

        # Initialize connection
        asyncio.create_task(self.connect())

    async def connect(self) -> bool:
        """
        Establish PostgreSQL database connection with comprehensive error handling

        Returns:
            bool: True if connection successful, False otherwise
        """
        if not ASYNCPG_AVAILABLE:
            logger.warning("⚠️  asyncpg not available - database features disabled")
            self._set_disconnected_state()
            return False

        postgres_url = Config.get_postgres_url()

        if not postgres_url:
            logger.warning(
                "⚠️  PostgreSQL connection URL not provided - database features disabled"
            )
            logger.info(
                "💡 Set DATABASE_URL or individual POSTGRES_* environment variables"
            )
            self._set_disconnected_state()
            return False

        for attempt in range(1, self.max_connection_attempts + 1):
            try:
                logger.info(
                    "🔌 Attempting PostgreSQL connection (attempt %d/%d)...",
                    attempt,
                    self.max_connection_attempts,
                )

                # Create asyncpg connection pool
                self.pool = await asyncpg.create_pool(
                    postgres_url,
                    min_size=Config.DATABASE_MIN_POOL_SIZE,
                    max_size=Config.DATABASE_MAX_POOL_SIZE,
                    command_timeout=Config.DATABASE_TIMEOUT,
                    server_settings={
                        "application_name": f"{Config.BOT_NAME}-v{Config.BOT_VERSION}",
                        "jit": "off",  # Disable JIT for better compatibility
                    },
                )

                # Create SQLAlchemy async engine if available
                if SQLALCHEMY_AVAILABLE:
                    self.engine = create_async_engine(
                        Config.get_async_postgres_url(),
                        pool_size=Config.DATABASE_MAX_POOL_SIZE,
                        max_overflow=10,
                        pool_timeout=Config.DATABASE_TIMEOUT,
                        pool_recycle=3600,  # Recycle connections every hour
                        echo=Config.IS_DEVELOPMENT,  # Log SQL in development
                    )

                    # Create session factory
                    self.session_factory = async_sessionmaker(
                        self.engine, class_=AsyncSession, expire_on_commit=False
                    )

                # Test connection with both asyncpg and SQLAlchemy
                async with self.pool.acquire() as connection:
                    await connection.execute("SELECT 1")

                if SQLALCHEMY_AVAILABLE and self.engine:
                    async with self.engine.begin() as conn:
                        await conn.execute(text("SELECT 1"))

                # Initialize health checker
                self.health_checker = DatabaseHealthChecker(self.pool)

                self.is_connected = True
                self.connection_attempts = attempt

                logger.info("✅ Successfully connected to PostgreSQL!")
                logger.info(
                    "📊 Database: %s, Host: %s:%s",
                    Config.POSTGRES_DB,
                    Config.POSTGRES_HOST,
                    Config.POSTGRES_PORT,
                )

                return True

            except (OSError, ConnectionError) as e:
                logger.warning(
                    "❌ Database connection failed (attempt %d): %s", attempt, str(e)
                )

            except Exception as e:
                # Handle specific asyncpg errors if available
                error_type = type(e).__name__
                if "InvalidAuthorizationSpecification" in error_type:
                    logger.error("🔐 Database authentication failed: %s", str(e))
                    break  # Don't retry auth failures
                elif "InvalidCatalogName" in error_type:
                    logger.error("📂 Database does not exist: %s", str(e))
                    logger.info(
                        "💡 Please create the database first: CREATE DATABASE %s;",
                        Config.POSTGRES_DB,
                    )
                    break  # Don't retry if database doesn't exist
                else:
                    logger.error(
                        "💥 Unexpected database error (attempt %d): %s", attempt, str(e)
                    )

            # Wait before retrying (exponential backoff)
            if attempt < self.max_connection_attempts:
                wait_time = 2**attempt
                logger.info("⏰ Retrying in %d seconds...", wait_time)
                await asyncio.sleep(wait_time)

        # All connection attempts failed
        logger.error(
            "❌ Failed to establish database connection after %d attempts",
            self.max_connection_attempts,
        )
        logger.info(
            "🔄 Bot will continue in database-free mode with reduced functionality:"
        )
        logger.info("   ✅ Discord commands will work normally")
        logger.info("   ✅ Timer functionality will work")
        logger.info("   ❌ User preferences won't be saved")
        logger.info("   ❌ Persistent data features disabled")
        logger.info("   ❌ Analytics and logging reduced")

        logger.info("🔧 To fix this issue:")
        logger.info(
            "   1. Install required packages: pip install asyncpg sqlalchemy[asyncio]"
        )
        logger.info("   2. Verify PostgreSQL server is running")
        logger.info("   3. Check DATABASE_URL or POSTGRES_* environment variables")
        logger.info("   4. Ensure database and user exist")
        logger.info("   5. Verify network connectivity to database server")

        self._set_disconnected_state()
        return False

    def _set_disconnected_state(self):
        """Set the database to disconnected state"""
        self.pool = None
        self.engine = None
        self.session_factory = None
        self.health_checker = None
        self.is_connected = False

    async def get_connection(self):
        """
        Get a raw asyncpg connection for direct SQL operations

        Returns:
            asyncpg.Connection or None if unavailable
        """
        if not self.is_connected or not self.pool:
            logger.debug("Database not connected - connection unavailable")
            return None

        try:
            return await self.pool.acquire()
        except Exception as e:
            logger.error("Error acquiring database connection: %s", str(e))
            return None

    async def get_session(self):
        """
        Get a SQLAlchemy async session for ORM operations

        Returns:
            AsyncSession or None if unavailable
        """
        if not self.is_connected or not self.session_factory:
            logger.debug("Database not connected - session unavailable")
            return None

        try:
            return self.session_factory()
        except Exception as e:
            logger.error("Error creating database session: %s", str(e))
            return None

    async def execute_query(self, query: str, *args):
        """
        Execute a raw SQL query and return results

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            Query results or None if failed
        """
        if not self.is_connected:
            return None

        try:
            async with self.pool.acquire() as connection:
                return await connection.fetch(query, *args)
        except Exception as e:
            logger.error("Error executing query: %s", str(e))
            return None

    async def execute_command(self, command: str, *args) -> bool:
        """
        Execute a SQL command (INSERT, UPDATE, DELETE)

        Args:
            command: SQL command string
            *args: Command parameters

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            async with self.pool.acquire() as connection:
                await connection.execute(command, *args)
                return True
        except Exception as e:
            logger.error("Error executing command: %s", str(e))
            return False

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
            "database_type": "PostgreSQL",
            "asyncpg_available": ASYNCPG_AVAILABLE,
            "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
            "database": {
                "host": Config.POSTGRES_HOST,
                "port": Config.POSTGRES_PORT,
                "database": Config.POSTGRES_DB,
                "user": Config.POSTGRES_USER,
            },
        }

        if self.pool and self.is_connected and ASYNCPG_AVAILABLE:
            try:
                stats.update(
                    {
                        "pool_size": self.pool.get_size(),
                        "pool_min_size": Config.DATABASE_MIN_POOL_SIZE,
                        "pool_max_size": Config.DATABASE_MAX_POOL_SIZE,
                        "timeout_seconds": Config.DATABASE_TIMEOUT,
                    }
                )
            except Exception as e:
                logger.warning("Could not retrieve pool stats: %s", str(e))

        return stats

    async def close(self):
        """Close all database connections gracefully"""
        if self.pool:
            await self.pool.close()
        if self.engine:
            await self.engine.dispose()
        self._set_disconnected_state()
        logger.info("🔌 Database connections closed")


# Global database instance
database = Database()


# Backward compatibility functions
async def get_connection():
    """Get a raw connection from the global database instance"""
    return await database.get_connection()


async def get_session():
    """Get a session from the global database instance"""
    return await database.get_session()


def is_database_available() -> bool:
    """Check if database is available"""
    return database.is_connected
