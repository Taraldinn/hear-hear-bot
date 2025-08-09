"""
Database connection and operations
Author: Tasdid Tahsin
Email: tasdidtahsin@gmail.com
"""

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
        """Establish database connection"""
        try:
            self.client = MongoClient(Config.MONGODB_CONNECTION_STRING)
            self.db = self.client[Config.DATABASE_NAME]
            self.tabby_db = self.client[Config.TABBY_DATABASE_NAME]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully!")
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            self.db = None
            self.tabby_db = None
    
    def get_collection(self, collection_name, use_tabby_db=False):
        """Get a specific collection"""
        if use_tabby_db and self.tabby_db:
            return self.tabby_db[collection_name]
        elif self.db:
            return self.db[collection_name]
        else:
            logger.error("Database not connected")
            return None
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

# Global database instance
database = Database()
