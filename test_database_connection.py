#!/usr/bin/env python3
"""
Database Connection Test Script
Author: aldinn

Quick test script to debug MongoDB Atlas SSL connection issues.
Run this to test database connectivity outside of the main bot.
"""

import os
import sys
import ssl
import logging
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    OperationFailure,
    ConfigurationError,
    NetworkTimeout,
    AutoReconnect
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_env_file():
    """Load environment variables from .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("✅ Loaded environment variables from .env file")
    except ImportError:
        logger.warning("⚠️  python-dotenv not installed, reading env vars directly")
    except Exception as e:
        logger.error(f"❌ Error loading .env file: {e}")

def test_basic_connection(connection_string: str) -> bool:
    """Test basic MongoDB connection"""
    logger.info("🔌 Testing basic MongoDB connection...")
    
    try:
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
        )
        
        # Test connection
        client.admin.command("ping")
        logger.info("✅ Basic connection successful!")
        
        # Get server info
        server_info = client.server_info()
        logger.info(f"📊 MongoDB version: {server_info.get('version', 'unknown')}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic connection failed: {e}")
        return False

def test_ssl_connection(connection_string: str) -> bool:
    """Test MongoDB connection with SSL settings"""
    logger.info("🔒 Testing SSL MongoDB connection...")
    
    try:
        client = MongoClient(
            connection_string,
            # Timeouts
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            
            # SSL settings (fixed - removed conflicting options)
            tls=True,
            tlsAllowInvalidCertificates=False,
            tlsAllowInvalidHostnames=False,
            
            # Connection pooling
            maxPoolSize=5,
            minPoolSize=1,
            
            # Reliability
            retryWrites=True,
            w="majority",
        )
        
        # Test connection
        client.admin.command("ping")
        logger.info("✅ SSL connection successful!")
        
        client.close()
        return True
        
    except ssl.SSLError as e:
        logger.error(f"🔒 SSL Error: {e}")
        return False
    except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout, AutoReconnect) as e:
        logger.error(f"❌ SSL connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"💥 Unexpected SSL error: {e}")
        return False

def test_fallback_ssl_connection(connection_string: str) -> bool:
    """Test MongoDB connection with minimal SSL settings"""
    logger.info("🔄 Testing minimal SSL connection...")
    
    try:
        client = MongoClient(
            connection_string,
            # Timeouts
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            
            # Minimal SSL settings
            tls=True,
            
            # Basic settings
            maxPoolSize=3,
            minPoolSize=1,
            retryWrites=True,
        )
        
        # Test connection
        client.admin.command("ping")
        logger.info("✅ Minimal SSL connection successful!")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Minimal SSL connection failed: {e}")
        return False

def test_legacy_ssl_connection(connection_string: str) -> bool:
    """Test MongoDB connection with legacy SSL parameters"""
    logger.info("🔄 Testing legacy SSL connection...")
    
    try:
        client = MongoClient(
            connection_string,
            # Timeouts
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            
            # Legacy SSL settings
            ssl=True,
            ssl_cert_reqs='CERT_NONE',
            
            # Basic settings
            maxPoolSize=3,
        )
        
        # Test connection
        client.admin.command("ping")
        logger.warning("⚠️  Legacy SSL connection successful (not recommended for production)")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Legacy SSL connection failed: {e}")
        return False

def test_driver_default_connection(connection_string: str) -> bool:
    """Test MongoDB connection with driver defaults"""
    logger.info("🔄 Testing driver default connection...")
    
    try:
        client = MongoClient(
            connection_string,
            # Only basic timeouts, let driver handle SSL
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            maxPoolSize=3,
        )
        
        # Test connection
        client.admin.command("ping")
        logger.info("✅ Driver default connection successful!")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Driver default connection failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting MongoDB Atlas connection tests...")
    
    # Load environment variables
    load_env_file()
    
    # Get connection string
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    
    if not connection_string:
        logger.error("❌ MONGODB_CONNECTION_STRING environment variable not found!")
        logger.info("💡 Make sure to set your MongoDB Atlas connection string in .env file")
        sys.exit(1)
    
    # Mask sensitive parts for logging
    masked_connection = connection_string[:30] + "***" + connection_string[-10:]
    logger.info(f"🔗 Using connection string: {masked_connection}")
    
    # Test different connection methods
    tests = [
        ("Basic Connection", test_basic_connection),
        ("SSL Connection", test_ssl_connection),
        ("Minimal SSL Connection", test_fallback_ssl_connection),
        ("Legacy SSL Connection", test_legacy_ssl_connection),
        ("Driver Default Connection", test_driver_default_connection),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            results[test_name] = test_func(connection_string)
        except Exception as e:
            logger.error(f"💥 Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("📋 TEST RESULTS SUMMARY")
    logger.info(f"{'='*50}")
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    if any(results.values()):
        logger.info("\n🎉 At least one connection method works!")
        logger.info("💡 Check the logs above to see which method succeeded")
    else:
        logger.error("\n💥 All connection methods failed!")
        logger.info("💡 Troubleshooting tips:")
        logger.info("   1. Check your MongoDB Atlas network access list")
        logger.info("   2. Verify your connection string is correct")
        logger.info("   3. Ensure your IP address is whitelisted")
        logger.info("   4. Check if your MongoDB Atlas cluster is running")
        logger.info("   5. Verify your database user credentials")

if __name__ == "__main__":
    main()