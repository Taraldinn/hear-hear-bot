"""
Main Bot Client
Author: aldinn
Email: kferdoush617@gmail.com
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
import time
from config.settings import Config
from src.database.connection import database

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
        self.start_time = time.time()  # Track bot start time
        self.web_server = None  # Will be set up later
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Bot is starting up...")
        
        # Load all extensions
        await self.load_extensions()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")
    
    async def load_extensions(self):
        """Load all command extensions"""
        extensions = [
            'src.commands.admin',
            'src.commands.debate',
            'src.commands.timer',
            'src.commands.tabby',
            'src.commands.utility',
            # 'src.commands.slash_commands',  # Disabled to avoid duplicate command registration
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
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot ID: {self.user.id}')
        logger.info(f'Guilds: {len(self.guilds)}')
        logger.info(f'Users: {len(self.users)}')
        
        # Set bot status
        activity = discord.Game(name=f"{Config.BOT_PREFIX}help | Debate Timer")
        await self.change_presence(status=discord.Status.online, activity=activity)
        
        logger.info("Bot is ready!")
    
    async def on_guild_join(self, guild):
        """Called when bot joins a guild"""
        logger.info(f"Joined guild: {guild.name} ({guild.id})")
        
        # Try to send a welcome message to the first available text channel
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="🎯 Hear! Hear! Bot",
                    description=f"Thanks for adding me to {guild.name}!",
                    color=0x3B82F6
                )
                embed.add_field(
                    name="Get Started",
                    value=f"Use `{Config.BOT_PREFIX}help` to see all commands or try `/timer start` for slash commands!",
                    inline=False
                )
                embed.add_field(
                    name="Timer Commands",
                    value="Perfect for timing debate speeches and managing tournaments",
                    inline=False
                )
                embed.set_footer(text="Made for the debate community ❤️")
                
                try:
                    await channel.send(embed=embed)
                    break
                except discord.Forbidden:
                    continue
    
    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild"""
        logger.info(f"Left guild: {guild.name} ({guild.id})")
    
    async def on_command_error(self, ctx, error):
        """Global error handler for prefix commands"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to execute this command.")
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param}`")
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided.")
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"❌ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
            return
        
        # Log unexpected errors
        logger.error(f"Unexpected error in command {ctx.command}: {error}", exc_info=True)
        
        embed = discord.Embed(
            title="❌ An Error Occurred",
            description="An unexpected error occurred while processing your command.",
            color=0xFF0000
        )
        embed.add_field(
            name="Error Details",
            value=f"```{str(error)[:1000]}```",
            inline=False
        )
        embed.set_footer(text="This error has been logged for investigation.")
        
        try:
            await ctx.send(embed=embed)
        except:
            pass
    
    def get_uptime(self):
        """Get bot uptime as a formatted string"""
        uptime_seconds = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    def get_latency_ms(self):
        """Get bot latency in milliseconds"""
        return round(self.latency * 1000)
    
    async def close(self):
        """Clean shutdown"""
        logger.info("Bot is shutting down...")
        
        # Close web server if running
        if self.web_server:
            await self.web_server.close()
        
        # Close database connection
        if self.database:
            await self.database.close()
        
        await super().close()
        logger.info("Bot shutdown complete")

# Function to create and configure the bot
def create_bot():
    """Create and return a configured bot instance"""
    return HearHearBot()
