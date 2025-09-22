#!/usr/bin/env python3
"""
Command Sync Utility
Use this to sync slash commands with Discord when you get "Unknown Integration" errors
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config.settings import Config
from src.bot.client import create_bot


async def sync_commands():
    """Sync slash commands with Discord"""
    bot = create_bot()

    async with bot:
        await bot.start(Config.BOT_TOKEN, reconnect=False)


async def main():
    print("🔄 Starting command sync...")

    try:
        bot = create_bot()

        @bot.event
        async def on_ready():
            print(f"✅ Bot connected as {bot.user}")
            print(f"📊 Connected to {len(bot.guilds)} guilds")

            # Sync commands globally
            print("🌍 Syncing commands globally...")
            synced = await bot.tree.sync()
            print(f"✅ Synced {len(synced)} global commands")

            # Optionally sync to specific guild for testing (faster)
            # Replace GUILD_ID with your test server ID
            # guild = discord.Object(id=YOUR_GUILD_ID)
            # synced = await bot.tree.sync(guild=guild)
            # print(f"✅ Synced {len(synced)} commands to test guild")

            print("🎉 Command sync completed!")
            print("📝 Commands should be available in Discord within a few minutes.")
            print("🔄 If you still see 'Unknown Integration', try:")
            print("   • Restart Discord client")
            print("   • Wait up to 1 hour for global commands to propagate")
            print("   • Check bot permissions in your server")

            await bot.close()

        await bot.start(Config.BOT_TOKEN)

    except Exception as e:
        print(f"❌ Error during command sync: {e}")
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("✅ Sync completed successfully")
    else:
        print("❌ Sync failed")
        sys.exit(1)
