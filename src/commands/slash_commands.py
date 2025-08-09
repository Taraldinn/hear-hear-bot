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
    
    # Timer Commands Group
    timer_group = app_commands.Group(name="timer", description="Timer commands for debates")
    
    @timer_group.command(name="start", description="Start a new debate timer")
    async def timer_start(self, interaction: discord.Interaction):
        """Start a debate timer"""
        user_id = interaction.user.id
        channel_id = interaction.channel.id
        timer_manager = self.bot.timer_manager
        
        if timer_manager.is_timer_active(user_id, channel_id):
            elapsed = timer_manager.get_elapsed_time(user_id, channel_id)
            time_str = timer_manager.get_time_string(elapsed)
            await interaction.response.send_message(f"⏱️ You already have an active timer: {time_str}", ephemeral=True)
            return
        
        timer_manager.start_timer(user_id, channel_id)
        
        embed = discord.Embed(
            title="⏱️ Timer Started",
            description=f"Timer started for {interaction.user.mention}",
            color=discord.Color.green(),
            timestamp=interaction.created_at
        )
        
        embed.add_field(name="Commands", value="Use `/timer stop` to stop\nUse `/timer check` to check time", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @timer_group.command(name="stop", description="Stop your active timer")
    async def timer_stop(self, interaction: discord.Interaction):
        """Stop your timer"""
        user_id = interaction.user.id
        channel_id = interaction.channel.id
        timer_manager = self.bot.timer_manager
        
        elapsed = timer_manager.stop_timer(user_id, channel_id)
        
        if elapsed is None:
            await interaction.response.send_message("❌ You don't have an active timer in this channel.", ephemeral=True)
            return
        
        time_str = timer_manager.format_time(elapsed)
        
        embed = discord.Embed(
            title="⏹️ Timer Stopped",
            description=f"Timer stopped for {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=interaction.created_at
        )
        
        embed.add_field(name="Total Time", value=time_str, inline=True)
        
        # Add performance feedback
        if elapsed >= 420:  # 7 minutes
            embed.add_field(name="Performance", value="⚠️ Over time limit", inline=True)
        elif elapsed >= 360:  # 6 minutes
            embed.add_field(name="Performance", value="⏰ Close to time limit", inline=True)
        else:
            embed.add_field(name="Performance", value="✅ Within time limit", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @timer_group.command(name="check", description="Check your current timer status")
    async def timer_check(self, interaction: discord.Interaction):
        """Check timer status"""
        user_id = interaction.user.id
        channel_id = interaction.channel.id
        timer_manager = self.bot.timer_manager
        
        if not timer_manager.is_timer_active(user_id, channel_id):
            await interaction.response.send_message("❌ You don't have an active timer in this channel.", ephemeral=True)
            return
        
        elapsed = timer_manager.get_elapsed_time(user_id, channel_id)
        time_str = timer_manager.get_time_string(elapsed)
        
        embed = discord.Embed(
            title="⏱️ Timer Status",
            description=f"Current timer for {interaction.user.mention}",
            color=discord.Color.blue(),
            timestamp=interaction.created_at
        )
        
        embed.add_field(name="Elapsed Time", value=time_str, inline=True)
        
        # Add progress indicator
        if elapsed < 300:  # Under 5 minutes
            progress = "🟢 Good pace"
        elif elapsed < 360:  # Under 6 minutes
            progress = "🟡 Approaching limit"
        elif elapsed < 420:  # Under 7 minutes
            progress = "🟠 Near time limit"
        else:
            progress = "🔴 Over time!"
        
        embed.add_field(name="Status", value=progress, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    # Debate Commands
    @app_commands.command(name="randommotion", description="Get a random debate motion")
    @app_commands.describe(language="Language for the motion")
    @app_commands.choices(language=[
        app_commands.Choice(name="English", value="english"),
        app_commands.Choice(name="Bangla", value="bangla")
    ])
    async def randommotion(self, interaction: discord.Interaction, language: str = "english"):
        """Get a random debate motion"""
        # Validate language
        if language not in language_manager.get_available_languages():
            available = ", ".join(language_manager.get_available_languages())
            await interaction.response.send_message(f"❌ Language not supported. Available: {available}", ephemeral=True)
            return
        
        # Get random motion
        motion = language_manager.get_random_motion(language)
        
        # Create embed
        embed = discord.Embed(
            title="🎯 Random Debate Motion",
            description=motion,
            color=discord.Color.gold(),
            timestamp=interaction.created_at
        )
        
        embed.add_field(name="Language", value=language.title(), inline=True)
        embed.add_field(
            name="Total Motions", 
            value=language_manager.get_motion_count(language), 
            inline=True
        )
        
        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}", 
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)
    
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
    
    # Admin Commands
    @app_commands.command(name="unmute", description="Unmute a member in voice chat")
    @app_commands.describe(member="The member to unmute")
    @app_commands.default_permissions(manage_roles=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        """Unmute a member"""
        try:
            await member.edit(mute=False)
            await interaction.response.send_message(f"> {member.mention} was unmuted successfully")
            logger.info(f"Unmuted {member} in {interaction.guild}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to unmute members.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error unmuting member: {str(e)}", ephemeral=True)
            logger.error(f"Error unmuting {member}: {e}")
    
    @app_commands.command(name="undeafen", description="Undeafen a member in voice chat")
    @app_commands.describe(member="The member to undeafen")
    @app_commands.default_permissions(manage_roles=True)
    async def undeafen(self, interaction: discord.Interaction, member: discord.Member):
        """Undeafen a member"""
        try:
            await member.edit(deafen=False)
            await interaction.response.send_message(f"> {member.mention} was undeafened successfully")
            logger.info(f"Undeafened {member} in {interaction.guild}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to undeafen members.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error undeafening member: {str(e)}", ephemeral=True)
            logger.error(f"Error undeafening {member}: {e}")
    
    # Utility Commands
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
            "`/timer start/stop/check` - Manage debate timer",
            "`/randommotion [lang]` - Get random motion",
            "`/coinflip` - Flip a coin",
            "`/diceroll [sides]` - Roll a dice",
            "`/unmute <member>` - Unmute member (Admin)",
            "`/undeafen <member>` - Undeafen member (Admin)",
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
