"""
Slash Commands - Discord Application Commands
Author: aldinn
Email: kferdoush617@gmail.com
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from src.utils.language import language_manager

logger = logging.getLogger(__name__)

class SlashCommands(commands.Cog):
    """Modern slash commands for the bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # Utility Commands - Non-duplicate slash commands
    @app_commands.command(name="coinflip", description="Flip a coin for random decisions")
    async def coinflip(self, interaction: discord.Interaction):
        """Flip a coin"""
        import random
        result = random.choice(['Heads', 'Tails'])
        
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"**{result}**",
            color=discord.Color.orange(),
            timestamp=interaction.created_at
        )
        
        embed.set_footer(
            text=f"Flipped by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="diceroll", description="Roll a dice")
    @app_commands.describe(sides="Number of sides on the dice (default: 6)")
    async def diceroll(self, interaction: discord.Interaction, sides: int = 6):
        """Roll a dice"""
        import random
        
        if sides < 2 or sides > 100:
            await interaction.response.send_message("❌ Dice must have between 2 and 100 sides.", ephemeral=True)
            return
        
        result = random.randint(1, sides)
        
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"**{result}** (out of {sides})",
            color=discord.Color.purple(),
            timestamp=interaction.created_at
        )
        
        embed.set_footer(
            text=f"Rolled by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)
    
    # Additional Utility Commands  
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency"""
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green(),
            timestamp=interaction.created_at
        )
        
        # Bot latency
        latency = round(self.bot.latency * 1000)
        embed.add_field(name="Bot Latency", value=f"{latency}ms", inline=True)
        
        # Status indicator
        if latency < 100:
            status = "🟢 Excellent"
        elif latency < 200:
            status = "🟡 Good"
        else:
            status = "🔴 Poor"
        
        embed.add_field(name="Status", value=status, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="help", description="Show bot help and commands")
    async def help(self, interaction: discord.Interaction):
        """Show help information"""
        embed = discord.Embed(
            title="🤖 Hear! Hear! Bot - Help",
            description="A comprehensive debate bot with timing, motions, and tournament features",
            color=discord.Color.blue()
        )
        
        # Slash commands
        slash_cmds = [
            "`/timer` - Interactive debate timer with buttons",
            "`/randommotion [lang]` - Get random motion (in debate commands)",
            "`/coinflip` - Flip a coin",
            "`/diceroll [sides]` - Roll a dice", 
            "`/unmute <member>` - Unmute member (in admin commands)",
            "`/undeafen <member>` - Undeafen member (in admin commands)",
            "`/ping` - Check bot latency"
        ]
        
        # Legacy prefix commands
        prefix_cmds = [
            "`.sync <url> <token>` - Sync with Tabbycat (Admin)",
            "`.register <key>` - Register for tournament",
            "`.checkin/.checkout` - Tournament attendance",
            "`.motion <round>` - Get round motion",
            "`.setlanguage <lang>` - Set server language (Admin)"
        ]
        
        embed.add_field(name="🆕 Slash Commands", value="\n".join(slash_cmds), inline=False)
        embed.add_field(name="📝 Prefix Commands", value="\n".join(prefix_cmds), inline=False)
        
        embed.add_field(
            name="💡 Note",
            value="Slash commands (/) are the modern way to interact with bots!\nPrefix commands (.) are still supported for advanced features.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
