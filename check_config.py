#!/usr/bin/env python3
"""
Environment Configuration Check Script
Verifies all environment variables are properly configured
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import os

# Load environment variables manually
env_local = project_root / ".env.local"
env_file = project_root / ".env"

print("=" * 80)
print("🔍 HEAR! HEAR! BOT - ENVIRONMENT CONFIGURATION CHECK")
print("=" * 80)

# Check which files exist
print("\n📁 ENVIRONMENT FILES:")
files_status = []
if env_local.exists():
    print(f"  ✅ .env.local - EXISTS ({env_local.stat().st_size} bytes)")
    files_status.append((".env.local", env_local))
else:
    print(f"  ❌ .env.local - NOT FOUND")

if env_file.exists():
    print(f"  ✅ .env - EXISTS ({env_file.stat().st_size} bytes)")
    files_status.append((".env", env_file))
else:
    print(f"  ❌ .env - NOT FOUND")

# Load environment variables in priority order
print("\n🔄 LOADING ENVIRONMENT VARIABLES...")
loaded_from = None
for name, path in files_status:
    if load_dotenv(path, override=True):
        print(f"  ✅ Loaded from {name}")
        loaded_from = name
        break

if not loaded_from:
    print("  ⚠️  No environment files loaded, using system environment")

# Now import and check Config
from config.settings import Config

print("\n" + "=" * 80)
print("📊 CONFIGURATION STATUS")
print("=" * 80)

# Critical settings
print("\n✅ REQUIRED (Bot cannot start without these):")
critical = [
    ("DISCORD_BOT_TOKEN", Config.BOT_TOKEN, "Discord bot authentication"),
    ("DATABASE_URL", Config.DATABASE_URL, "PostgreSQL database connection"),
]

all_critical_ok = True
for name, value, description in critical:
    if value:
        # Mask the value for security
        if len(value) > 8:
            masked = f"{value[:4]}...{value[-4:]}"
        else:
            masked = "***"
        print(f"  ✅ {name}")
        print(f"     Value: {masked} ({len(value)} chars)")
        print(f"     Purpose: {description}")
    else:
        print(f"  ❌ {name} - NOT SET")
        print(f"     Purpose: {description}")
        all_critical_ok = False

# Top.gg integration (optional but recommended)
print("\n🎯 TOP.GG INTEGRATION:")
topgg_settings = [
    ("BOT_ID", Config.BOT_ID, "Discord application ID"),
    ("TOPGG_TOKEN", Config.TOPGG_TOKEN, "Top.gg API token"),
]

topgg_ok = True
for name, value, description in topgg_settings:
    if value:
        if len(value) > 8:
            masked = f"{value[:4]}...{value[-4:]}"
        else:
            masked = value
        print(f"  ✅ {name}")
        print(f"     Value: {masked} ({len(value)} chars)")
        print(f"     Purpose: {description}")
    else:
        print(f"  ⚠️  {name} - NOT SET")
        print(f"     Purpose: {description}")
        topgg_ok = False

# Optional settings
print("\n📦 OPTIONAL FEATURES:")
optional = [
    ("MOTIONS_CSV_URL_ENGLISH", Config.MOTIONS_CSV_URL_ENGLISH, "Motion database"),
    ("TABBYCAT_API_KEY", Config.TABBYCAT_API_KEY, "Tournament integration"),
]

for name, value, description in optional:
    if value:
        print(f"  ✅ {name} - Configured")
        print(f"     Purpose: {description}")
    else:
        print(f"  ⚠️  {name} - Not configured")
        print(f"     Purpose: {description} (will be disabled)")

# Bot configuration
print("\n🤖 BOT CONFIGURATION:")
print(f"  Name: {Config.BOT_NAME}")
print(f"  Version: {Config.BOT_VERSION}")
print(f"  Shard Count: {Config.SHARD_COUNT}")
print(f"  Log Level: {Config.LOG_LEVEL}")
print(f"  Development Mode: {Config.IS_DEVELOPMENT}")

# Database configuration
print("\n🗄️  DATABASE CONFIGURATION:")
print(f"  Database: {Config.POSTGRES_DB}")
print(f"  Timeout: {Config.DATABASE_TIMEOUT}s")
print(
    f"  Connection Pool: {Config.DATABASE_MIN_POOL_SIZE}-{Config.DATABASE_MAX_POOL_SIZE}"
)

# Web server
print("\n🌍 WEB SERVER:")
print(f"  Host: {Config.WEB_SERVER_HOST}")
print(f"  Port: {Config.WEB_SERVER_PORT}")
print(f"  Debug: {Config.WEB_SERVER_DEBUG}")

# Final summary
print("\n" + "=" * 80)
print("📋 SUMMARY")
print("=" * 80)

if all_critical_ok:
    print("\n✅ ALL CRITICAL SETTINGS ARE CONFIGURED")
    print("   Your bot is ready to start!")

    if topgg_ok:
        print("\n✅ TOP.GG INTEGRATION IS FULLY CONFIGURED")
        print("   Server count will be posted automatically every 30 minutes")
    else:
        print("\n⚠️  TOP.GG INTEGRATION IS INCOMPLETE")
        print("   Bot will start but won't post to top.gg")
        print("   To enable: Set BOT_ID and TOPGG_TOKEN in .env.local")

    print("\n🚀 READY TO START:")
    print("   Run: python main.py")
    print("   Or: python start.py")

else:
    print("\n❌ MISSING CRITICAL CONFIGURATION")
    print("   Bot cannot start without:")
    for name, value, description in critical:
        if not value:
            print(f"   - {name} ({description})")
    print("\n🔧 TO FIX:")
    print("   1. Copy .env.example to .env.local")
    print("   2. Edit .env.local and add your credentials")
    print("   3. Run this script again to verify")
    sys.exit(1)

print("=" * 80)
