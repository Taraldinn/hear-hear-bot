"""
Timer Commands
Author: Tasdid Tahsin
Email: tasdidtahsin@gmail.com
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import time
import logging

logger = logging.getLogger(__name__)

class TimerCommands(commands.Cog):
    """Timer-related commands for debate timing"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # Slash command group for timer
    timer_group = app_commands.Group(name="timer", description="Timer commands for debates")
    
    @timer_group.command(name="start", description="Start a new debate timer")
    async def slash_timer_start(self, interaction: discord.Interaction):
        """Slash command to start a timer"""
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
    async def slash_timer_stop(self, interaction: discord.Interaction):
        """Slash command to stop a timer"""
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
    async def slash_timer_check(self, interaction: discord.Interaction):
        """Slash command to check timer status"""
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
    
    @commands.command(aliases=['time'])
    async def currenttime(self, ctx):
        """Get current time"""
        current_time = time.strftime("%H:%M:%S", time.localtime())
        current_date = time.strftime("%Y-%m-%d", time.localtime())
        
        embed = discord.Embed(
            title="🕐 Current Time",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        
        embed.add_field(name="Time", value=current_time, inline=True)
        embed.add_field(name="Date", value=current_date, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['timekeep', 't', 'chrono'])
    async def timer(self, ctx, action=None):
        """Start, stop, or check debate timer
        
        Usage: 
        .timer start - Start a new timer
        .timer stop - Stop your active timer
        .timer check - Check your current timer
        .timer - Check your current timer (default)
        """
        user_id = ctx.author.id
        channel_id = ctx.channel.id
        timer_manager = self.bot.timer_manager
        
        if action is None or action.lower() == 'check':
            # Check current timer
            if not timer_manager.is_timer_active(user_id, channel_id):
                await ctx.send("⏰ You don't have an active timer.")
                return
            
            elapsed = timer_manager.get_elapsed_time(user_id, channel_id)
            time_str = timer_manager.get_time_string(elapsed)
            
            embed = discord.Embed(
                title="⏱️ Active Timer",
                description=f"**{time_str}**",
                color=discord.Color.green(),
                timestamp=ctx.message.created_at
            )
            
            embed.set_footer(
                text=f"Timer for {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )
            
            await ctx.send(embed=embed)
        
        elif action.lower() == 'start':
            # Start new timer
            if timer_manager.is_timer_active(user_id, channel_id):
                await ctx.send("⏰ You already have an active timer. Use `.timer stop` first.")
                return
            
            timer_manager.start_timer(user_id, channel_id)
            
            embed = discord.Embed(
                title="▶️ Timer Started",
                description="Your debate timer has been started!",
                color=discord.Color.green(),
                timestamp=ctx.message.created_at
            )
            
            embed.set_footer(
                text=f"Timer started by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )
            
            await ctx.send(embed=embed)
        
        elif action.lower() == 'stop':
            # Stop timer
            elapsed = timer_manager.stop_timer(user_id, channel_id)
            
            if elapsed is None:
                await ctx.send("⏰ You don't have an active timer.")
                return
            
            time_str = timer_manager.format_time(elapsed)
            
            embed = discord.Embed(
                title="⏹️ Timer Stopped",
                description=f"**Final Time: {time_str}**",
                color=discord.Color.red(),
                timestamp=ctx.message.created_at
            )
            
            # Add time evaluation
            if elapsed >= 420:  # 7 minutes
                embed.add_field(name="Status", value="⚠️ Over time!", inline=False)
            elif elapsed >= 360:  # 6 minutes
                embed.add_field(name="Status", value="⏰ Close to time limit", inline=False)
            else:
                embed.add_field(name="Status", value="✅ Within time", inline=False)
            
            embed.set_footer(
                text=f"Timer stopped by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )
            
            await ctx.send(embed=embed)
        
        else:
            await ctx.send("❌ Invalid action. Use: `start`, `stop`, or `check`")
    
    @commands.command(aliases=['countdown'])
    async def autotimer(self, ctx, minutes: int = 7):
        """Start an automatic timer that stops after specified minutes
        
        Usage: .autotimer [minutes] (default: 7)
        """
        if minutes < 1 or minutes > 60:
            await ctx.send("❌ Timer must be between 1 and 60 minutes.")
            return
        
        user_id = ctx.author.id
        channel_id = ctx.channel.id
        timer_manager = self.bot.timer_manager
        
        if timer_manager.is_timer_active(user_id, channel_id):
            await ctx.send("⏰ You already have an active timer. Use `.timer stop` first.")
            return
        
        duration = minutes * 60  # Convert to seconds
        timer_manager.start_auto_timer(user_id, channel_id, duration)
        
        embed = discord.Embed(
            title="⏰ Auto-Timer Started",
            description=f"Timer will automatically stop after **{minutes} minute(s)**",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        
        embed.add_field(name="Duration", value=f"{minutes} minutes", inline=True)
        embed.add_field(name="Auto-stop", value="✅ Enabled", inline=True)
        
        embed.set_footer(
            text=f"Auto-timer started by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.send(embed=embed)
        
        # Send notification when timer finishes
        await asyncio.sleep(duration)
        
        # Check if timer is still active (not manually stopped)
        if timer_manager.is_timer_active(user_id, channel_id):
            timer_manager.stop_timer(user_id, channel_id)
            
            final_embed = discord.Embed(
                title="⏰ Time's Up!",
                description=f"**{minutes}-minute timer completed**",
                color=discord.Color.red(),
                timestamp=ctx.message.created_at
            )
            
            final_embed.set_footer(
                text=f"Timer for {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )
            
            await ctx.send(f"{ctx.author.mention}", embed=final_embed)
    
    @commands.command()
    async def activetimers(self, ctx):
        """Show number of active timers in the server"""
        count = self.bot.timer_manager.get_active_timers_count()
        
        embed = discord.Embed(
            title="📊 Active Timers",
            description=f"**{count}** active timer(s) across all servers",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        
        if count > 0:
            embed.add_field(
                name="💡 Tip",
                value="Use `.timer check` to see your active timer",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def timehelp(self, ctx):
        """Show timer command help"""
        embed = discord.Embed(
            title="⏱️ Timer Commands Help",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        
        commands_help = [
            "`.timer start` - Start a new timer",
            "`.timer stop` - Stop your active timer", 
            "`.timer check` - Check your current timer",
            "`.autotimer [minutes]` - Auto-stop timer (default: 7min)",
            "`.currenttime` - Show current time",
            "`.activetimers` - Show active timer count"
        ]
        
        embed.add_field(
            name="Available Commands",
            value="\n".join(commands_help),
            inline=False
        )
        
        embed.add_field(
            name="💡 Tips",
            value="• Timers are per-user per-channel\n• Use auto-timers for speech timing\n• Standard debate speech: 7 minutes",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TimerCommands(bot))
