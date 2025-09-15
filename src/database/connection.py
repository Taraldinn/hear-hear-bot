import pymongo
from pymongo import MongoClient
from config.settings import Config
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection and operations manager"""

    def __init__(self):
        self.client = None
        self.db = None
        self.tabby_db = None
        self.connect()

    def connect(self):
        """Establish database connection with SSL configuration"""
        try:
            # Configure SSL options for MongoDB Atlas
            connection_string = Config.MONGODB_CONNECTION_STRING

            # If the connection string doesn't include SSL options, add them
            if connection_string and "ssl=" not in connection_string.lower():
                # Add SSL parameters for Atlas compatibility
                if "?" in connection_string:
                    connection_string += "&ssl=true&tlsInsecure=true"
                else:
                    connection_string += "?ssl=true&tlsInsecure=true"

            # Create client with additional SSL configuration
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,  # Shorter timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=10,
                retryWrites=True,
                # SSL options
                ssl=True,
                tlsInsecure=True,  # Allow insecure TLS
            )

            self.db = self.client[Config.DATABASE_NAME]
            self.tabby_db = self.client[Config.TABBY_DATABASE_NAME]

            # Test connection with shorter timeout
            self.client.admin.command("ping")
            logger.info("Connected to MongoDB successfully!")

        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            logger.info("Bot will continue without database functionality")
            self.client = None
            self.db = None
            self.tabby_db = None

    def get_collection(self, collection_name, use_tabby_db=False):
        """Get a specific collection"""
        try:
            if use_tabby_db and self.tabby_db is not None:
                return self.tabby_db[collection_name]
            elif self.db is not None:
                return self.db[collection_name]
            else:
                logger.warning("Database not connected - returning None")
                return None
        except Exception as e:
            logger.error(f"Error getting collection {collection_name}: {e}")
            return None

    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

    async def close(self):
        """Async close method for bot shutdown"""
        self.close_connection()


# Global database instance
database = Database()
