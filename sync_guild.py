#!/usr/bin/env python3
"""
Quick Guild Sync - Sync commands to a specific server for immediate testing
Replace YOUR_GUILD_ID with your server's ID
"""

import asyncio
import sys
from pathlib import Path
import discord

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config.settings import Config
from src.bot.client import create_bot

# Replace this with your server ID for instant testing
YOUR_GUILD_ID = 123456789012345678  # Replace with your actual server ID


async def main():
    print("🔄 Starting guild-specific command sync...")

    if YOUR_GUILD_ID == 123456789012345678:
        print(
            "❌ Please edit this script and replace YOUR_GUILD_ID with your actual server ID"
        )
        print("   To get your server ID:")
        print(
            "   1. Enable Developer Mode in Discord (Settings > Advanced > Developer Mode)"
        )
        print("   2. Right-click your server name and select 'Copy Server ID'")
        return False

    try:
        bot = create_bot()

        @bot.event
        async def on_ready():
            print(f"✅ Bot connected as {bot.user}")

            # Sync to specific guild (instant)
            guild = discord.Object(id=YOUR_GUILD_ID)
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ Synced {len(synced)} commands to guild {YOUR_GUILD_ID}")
            print("🎉 Commands should be available immediately!")

            await bot.close()

        await bot.start(Config.BOT_TOKEN)

    except Exception as e:
        print(f"❌ Error during guild sync: {e}")
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("✅ Guild sync completed successfully")
    else:
        print("❌ Guild sync failed")
        sys.exit(1)
