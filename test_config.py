#!/usr/bin/env python3
"""
Test script to verify bot configuration and imports
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from config.settings import Config
        print("✅ Config loaded successfully")
        
        from src.utils.language import language_manager
        print("✅ Language manager loaded")
        
        from src.utils.timer import TimerManager
        print("✅ Timer manager loaded")
        
        from src.database.connection import Database
        print("✅ Database manager loaded")
        
        # Test bot creation
        from src.bot.client import create_bot
        print("✅ Bot client can be created")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration validation"""
    print("\nTesting configuration...")
    
    try:
        from config.settings import Config
        
        print(f"Bot Name: {Config.BOT_NAME}")
        print(f"Version: {Config.BOT_VERSION}")
        print(f"Author: {Config.BOT_AUTHOR}")
        print(f"Slash Commands: {Config.USE_SLASH_COMMANDS}")
        print(f"Prefix: {Config.BOT_PREFIX}")
        
        # Check if required env vars are noted
        if not Config.BOT_TOKEN:
            print("⚠️  BOT_TOKEN not set (expected for testing)")
        if not Config.MONGODB_CONNECTION_STRING:
            print("⚠️  MONGODB_CONNECTION_STRING not set (expected for testing)")
        
        print("✅ Configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_language_data():
    """Test language data loading"""
    print("\nTesting language data...")
    
    try:
        from src.utils.language import language_manager
        
        languages = language_manager.get_available_languages()
        print(f"Available languages: {languages}")
        
        for lang in languages:
            count = language_manager.get_motion_count(lang)
            print(f"  {lang}: {count} motions")
            
            # Test getting a random motion
            motion = language_manager.get_random_motion(lang)
            print(f"  Sample motion: {motion[:50]}...")
        
        print("✅ Language data test passed")
        return True
        
    except Exception as e:
        print(f"❌ Language data error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Hear! Hear! Bot - Configuration Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_language_data
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Bot is ready to run.")
        print("\nTo start the bot:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your Discord bot token and MongoDB connection")
        print("3. Run: python main.py")
    else:
        print("❌ Some tests failed. Please check the configuration.")
        sys.exit(1)
