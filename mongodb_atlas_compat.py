"""
MongoDB Atlas SSL/TLS Compatibility Fix
Author: aldinn

This module provides comprehensive MongoDB connection handling for environments
with SSL/TLS compatibility issues, particularly Python 3.13+ with OpenSSL 3.0+.
"""

import os
import ssl
import logging
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    OperationFailure,
    ConfigurationError,
    NetworkTimeout,
    AutoReconnect
)

logger = logging.getLogger(__name__)


class MongoDBAtlasConnector:
    """
    Specialized connector for MongoDB Atlas with SSL/TLS compatibility fixes
    """
    
    def __init__(self, connection_string: str, timeout_ms: int = 30000):
        self.connection_string = connection_string
        self.timeout_ms = timeout_ms
        self.client: Optional[MongoClient] = None
    
    def connect(self) -> Optional[MongoClient]:
        """
        Attempt connection using multiple strategies for maximum compatibility
        """
        strategies = [
            self._strategy_disable_ssl_verification,
            self._strategy_legacy_ssl,
            self._strategy_minimal_tls,
            self._strategy_connection_string_only,
        ]
        
        for i, strategy in enumerate(strategies, 1):
            logger.info(f"🔄 Attempting connection strategy {i}/{len(strategies)}: {strategy.__name__}")
            
            try:
                client = strategy()
                if client and self._test_connection(client):
                    logger.info(f"✅ Successfully connected using {strategy.__name__}")
                    self.client = client
                    return client
                    
            except Exception as e:
                logger.warning(f"❌ Strategy {strategy.__name__} failed: {str(e)[:100]}...")
                continue
        
        logger.error("❌ All connection strategies failed")
        return None
    
    def _test_connection(self, client: MongoClient) -> bool:
        """Test if the connection actually works"""
        try:
            client.admin.command("ping", serverSelectionTimeoutMS=5000)
            return True
        except Exception:
            return False
    
    def _strategy_disable_ssl_verification(self) -> Optional[MongoClient]:
        """Strategy 1: Disable SSL verification (development/testing only)"""
        import ssl
        
        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Force TLS 1.2 to avoid newer TLS issues
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2
        
        return MongoClient(
            self.connection_string,
            ssl_context=ssl_context,
            serverSelectionTimeoutMS=self.timeout_ms,
            connectTimeoutMS=self.timeout_ms,
            socketTimeoutMS=self.timeout_ms,
            maxPoolSize=5,
        )
    
    def _strategy_legacy_ssl(self) -> Optional[MongoClient]:
        """Strategy 2: Use legacy SSL parameters"""
        return MongoClient(
            self.connection_string,
            ssl=True,
            serverSelectionTimeoutMS=self.timeout_ms,
            connectTimeoutMS=self.timeout_ms,
            maxPoolSize=3,
        )
    
    def _strategy_minimal_tls(self) -> Optional[MongoClient]:
        """Strategy 3: Minimal TLS configuration"""
        return MongoClient(
            self.connection_string,
            tls=True,
            serverSelectionTimeoutMS=self.timeout_ms,
            connectTimeoutMS=self.timeout_ms,
            maxPoolSize=3,
        )
    
    def _strategy_connection_string_only(self) -> Optional[MongoClient]:
        """Strategy 4: Let the connection string handle everything"""
        return MongoClient(
            self.connection_string,
            serverSelectionTimeoutMS=self.timeout_ms,
            connectTimeoutMS=self.timeout_ms,
            maxPoolSize=3,
        )


def create_atlas_connection(connection_string: str, timeout_ms: int = 30000) -> Optional[MongoClient]:
    """
    Create a MongoDB Atlas connection with comprehensive SSL/TLS compatibility handling
    
    Args:
        connection_string: MongoDB Atlas connection string
        timeout_ms: Connection timeout in milliseconds
        
    Returns:
        MongoClient instance or None if connection fails
    """
    if not connection_string:
        logger.error("❌ No connection string provided")
        return None
    
    connector = MongoDBAtlasConnector(connection_string, timeout_ms)
    return connector.connect()


# Test function for standalone testing
def test_atlas_connection():
    """Test the Atlas connection with the current environment"""
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    
    if not connection_string:
        print("❌ MONGODB_CONNECTION_STRING environment variable not found")
        return False
    
    print("🚀 Testing MongoDB Atlas connection with compatibility fixes...")
    
    client = create_atlas_connection(connection_string)
    
    if client:
        try:
            # Test database operations
            db = client["test_db"]
            collection = db["test_collection"]
            
            # Simple write/read test
            test_doc = {"test": "connection", "timestamp": "2025-09-23"}
            collection.insert_one(test_doc)
            
            found_doc = collection.find_one({"test": "connection"})
            if found_doc:
                print("✅ Database read/write test successful!")
                collection.delete_one({"test": "connection"})  # Cleanup
            
            client.close()
            return True
            
        except Exception as e:
            print(f"❌ Database operation test failed: {e}")
            client.close()
            return False
    else:
        print("❌ Could not establish connection to MongoDB Atlas")
        return False


if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    test_atlas_connection()