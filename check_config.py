#!/usr/bin/env python3
"""Environment Configuration Check Script.

Verifies all environment variables are properly configured.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent

try:
    from config.settings import Config
except ModuleNotFoundError:  # pragma: no cover - fallback for direct execution
    sys.path.insert(0, str(PROJECT_ROOT))
    from config.settings import Config

ENV_LOCAL = PROJECT_ROOT / ".env.local"
ENV_FILE = PROJECT_ROOT / ".env"


def mask_secret(value: str, *, allow_plain_short: bool = False) -> str:
    """Return a masked representation of a secret for safe logging."""

    if not value:
        return "***"

    if allow_plain_short and len(value) <= 8:
        return value

    if len(value) > 8:
        return f"{value[:4]}...{value[-4:]}"

    return "***"


def load_environment_files() -> Optional[str]:
    """Attempt to load environment variables from known files."""

    print("\n📁 ENVIRONMENT FILES:")
    files_status: list[tuple[str, Path]] = []

    if ENV_LOCAL.exists():
        print(f"  ✅ .env.local - EXISTS ({ENV_LOCAL.stat().st_size} bytes)")
        files_status.append((".env.local", ENV_LOCAL))
    else:
        print("  ❌ .env.local - NOT FOUND")

    if ENV_FILE.exists():
        print(f"  ✅ .env - EXISTS ({ENV_FILE.stat().st_size} bytes)")
        files_status.append((".env", ENV_FILE))
    else:
        print("  ❌ .env - NOT FOUND")

    print("\n🔄 LOADING ENVIRONMENT VARIABLES...")
    for name, path in files_status:
        if load_dotenv(path, override=True):
            print(f"  ✅ Loaded from {name}")
            return name

    print("  ⚠️  No environment files loaded, using system environment")
    return None


def report_critical_settings() -> bool:
    """Report critical configuration and return whether all are present."""

    print("\n✅ REQUIRED (Bot cannot start without these):")
    settings = [
        ("DISCORD_BOT_TOKEN", Config.BOT_TOKEN, "Discord bot authentication"),
        (
            "MONGODB_CONNECTION_STRING",
            Config.MONGODB_CONNECTION_STRING,
            "MongoDB database connection",
        ),
    ]

    all_present = True
    for name, value, description in settings:
        if value:
            masked = mask_secret(value)
            print(f"  ✅ {name}")
            print(f"     Value: {masked} ({len(value)} chars)")
            print(f"     Purpose: {description}")
        else:
            print(f"  ❌ {name} - NOT SET")
            print(f"     Purpose: {description}")
            all_present = False

    return all_present


def report_topgg_settings() -> bool:
    """Report Top.gg configuration and return whether all are present."""

    print("\n🎯 TOP.GG INTEGRATION:")
    settings = [
        ("BOT_ID", Config.BOT_ID, "Discord application ID"),
        ("TOPGG_TOKEN", Config.TOPGG_TOKEN, "Top.gg API token"),
    ]

    all_present = True
    for name, value, description in settings:
        if value:
            masked = mask_secret(value, allow_plain_short=True)
            print(f"  ✅ {name}")
            print(f"     Value: {masked} ({len(value)} chars)")
            print(f"     Purpose: {description}")
        else:
            print(f"  ⚠️  {name} - NOT SET")
            print(f"     Purpose: {description}")
            all_present = False

    return all_present


def report_optional_settings() -> None:
    """Report optional configuration values."""

    print("\n📦 OPTIONAL FEATURES:")
    settings = [
        (
            "MOTIONS_CSV_URL_ENGLISH",
            Config.MOTIONS_CSV_URL_ENGLISH,
            "Motion database",
        ),
        ("TABBYCAT_API_KEY", Config.TABBYCAT_API_KEY, "Tournament integration"),
    ]

    for name, value, description in settings:
        if value:
            print(f"  ✅ {name} - Configured")
            print(f"     Purpose: {description}")
        else:
            print(f"  ⚠️  {name} - Not configured")
            print(f"     Purpose: {description} (will be disabled)")


def print_bot_configuration() -> None:
    """Print the bot metadata section."""

    print("\n🤖 BOT CONFIGURATION:")
    print(f"  Name: {Config.BOT_NAME}")
    print(f"  Version: {Config.BOT_VERSION}")
    print(f"  Shard Count: {Config.SHARD_COUNT}")
    print(f"  Log Level: {Config.LOG_LEVEL}")
    print(f"  Development Mode: {Config.IS_DEVELOPMENT}")


def print_database_configuration() -> None:
    """Print the database configuration section."""

    print("\n🗄️  DATABASE CONFIGURATION:")
    provided = "✅" if Config.MONGODB_CONNECTION_STRING else "❌"
    print(f"  Connection string provided: {provided}")
    print(f"  Primary Database: {Config.DATABASE_NAME}")
    print(f"  Tabby Database: {Config.TABBY_DATABASE_NAME}")
    print(
        "  Pool Size: " f"{Config.MONGODB_MIN_POOL_SIZE}-{Config.MONGODB_MAX_POOL_SIZE}"
    )
    print(f"  Connect Timeout: {Config.MONGODB_CONNECT_TIMEOUT_MS} ms")
    print(f"  Socket Timeout: {Config.MONGODB_SOCKET_TIMEOUT_MS} ms")


def print_web_configuration() -> None:
    """Print the web server configuration section."""

    print("\n🌍 WEB SERVER:")
    print(f"  Host: {Config.WEB_SERVER_HOST}")
    print(f"  Port: {Config.WEB_SERVER_PORT}")
    print(f"  Debug: {Config.WEB_SERVER_DEBUG}")


def report_settings_status() -> tuple[bool, bool]:
    """Print the configuration report and return status flags."""

    print("\n" + "=" * 80)
    print("📊 CONFIGURATION STATUS")
    print("=" * 80)

    critical_ok = report_critical_settings()
    topgg_ok = report_topgg_settings()
    report_optional_settings()
    print_bot_configuration()
    print_database_configuration()
    print_web_configuration()

    return critical_ok, topgg_ok


def summarize(critical_ok: bool, topgg_ok: bool) -> int:
    """Print the summary section and return the exit code."""

    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)

    if critical_ok:
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
        return 0

    print("\n❌ MISSING CRITICAL CONFIGURATION")
    print("   Bot cannot start without:")
    print("   - DISCORD_BOT_TOKEN (Discord bot authentication)")
    print("   - MONGODB_CONNECTION_STRING (MongoDB database connection)")
    print("\n🔧 TO FIX:")
    print("   1. Copy .env.example to .env.local")
    print("   2. Edit .env.local and add your credentials")
    print("   3. Run this script again to verify")
    return 1


def main() -> int:
    """Entry point for the configuration check script."""

    print("=" * 80)
    print("🔍 HEAR! HEAR! BOT - ENVIRONMENT CONFIGURATION CHECK")
    print("=" * 80)

    load_environment_files()
    critical_ok, topgg_ok = report_settings_status()
    exit_code = summarize(critical_ok, topgg_ok)

    print("=" * 80)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
