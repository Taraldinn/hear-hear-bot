"""
Main Bot Client
Author: Tasdid Tahsin
Email: tasdidtahsin@        # Load command modules
        extensions = [
            'src.commands.admin',
            'src.commands.debate',
            'src.commands.timer',
            'src.commands.tabby',
            'src.commands.utility',
            'src.commands.slash_commands',  # Modern slash commands
            'src.events.member',
            'src.events.error'
        ]"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
from config.settings import Config
from src.database.connection import database
from src.utils.timer import timer_manager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HearHearBot(commands.AutoShardedBot):
    """Main bot class extending AutoShardedBot"""
    
    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=Config.BOT_PREFIX,
            shard_count=Config.SHARD_COUNT,
            intents=intents,
            help_command=None  # We'll create a custom help command
        )
        
        self.database = database
        self.timer_manager = timer_manager
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Setting up bot...")
        
        # Load all extensions
        await self.load_extensions()
        
        # Sync slash commands
        try:
            if Config.USE_SLASH_COMMANDS:
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")
        
        # Start background tasks
        self.loop.create_task(self.update_presence())
        self.loop.create_task(self.keep_alive_ping())
        
    async def load_extensions(self):
        """Load all command extensions"""
        extensions = [
            'src.commands.admin',
            'src.commands.debate',
            'src.commands.timer',
            'src.commands.tabby',
            'src.commands.utility',
            'src.events.member',
            'src.events.error'
        ]
        
        for extension in extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Bot logged in as {self.user}")
        logger.info(f"Bot ID: {self.user.id}")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info(f"Serving {sum(guild.member_count for guild in self.guilds)} users")
        logger.info("=" * 50)
    
    async def update_presence(self):
        """Update bot presence periodically"""
        await self.wait_until_ready()
        
        activities = [
            discord.Activity(type=discord.ActivityType.watching, name=f"debates in {len(self.guilds)} servers"),
            discord.Activity(type=discord.ActivityType.listening, name="debate arguments"),
            discord.Activity(type=discord.ActivityType.playing, name="with timer functions"),
            discord.Activity(type=discord.ActivityType.watching, name="for .help command")
        ]
        
        current_activity = 0
        
        while not self.is_closed():
            try:
                activity = activities[current_activity]
                await self.change_presence(activity=activity)
                current_activity = (current_activity + 1) % len(activities)
                await asyncio.sleep(180)  # Change every 3 minutes
            except Exception as e:
                logger.error(f"Error updating presence: {e}")
                await asyncio.sleep(60)
    
    async def keep_alive_ping(self):
        """Keep the bot alive with periodic pings"""
        await self.wait_until_ready()
        
        while not self.is_closed():
            try:
                # This can be used for health checks or keeping services alive
                logger.debug("Keep alive ping")
                await asyncio.sleep(300)  # Ping every 5 minutes
            except Exception as e:
                logger.error(f"Error in keep alive ping: {e}")
                await asyncio.sleep(60)
    
    async def get_language(self, guild_id):
        """Get language setting for a guild"""
        if not self.database.db:
            return 'english'
        
        try:
            collection = self.database.get_collection('guilds')
            guild_data = collection.find_one({'_id': guild_id})
            
            if guild_data and 'language' in guild_data:
                return guild_data['language']
            else:
                return 'english'  # Default language
        except Exception as e:
            logger.error(f"Error getting language for guild {guild_id}: {e}")
            return 'english'
    
    async def set_language(self, guild_id, language):
        """Set language for a guild"""
        if not self.database.db:
            return False
        
        try:
            collection = self.database.get_collection('guilds')
            collection.update_one(
                {'_id': guild_id},
                {'$set': {'language': language}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting language for guild {guild_id}: {e}")
            return False
    
    async def close(self):
        """Clean shutdown"""
        logger.info("Shutting down bot...")
        
        # Clean up timers
        self.timer_manager.cleanup_timers()
        
        # Close database connection
        self.database.close_connection()
        
        await super().close()

def create_bot():
    """Factory function to create bot instance"""
    return HearHearBot()
