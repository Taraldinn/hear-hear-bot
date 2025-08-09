"""
Timer Commands - Restored Original Functionality from pybot.py
Author: aldinn
Email: kferdoush617@gmail.com

Full restoration of the original pybot.py timer system
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import time
import logging

logger = logging.getLogger(__name__)

class Timer(commands.Cog):
    """Timer commands with original pybot.py functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        self.l = {}  # timer trigger library - format: {user_id_channel_id: status}
        self.t = {}  # reminder storage library  
        self.active_timers = {}  # track active timer messages - format: {user_id_channel_id: message_obj}
    
    async def get_language(self, guild_id):
        """Get language setting for a guild"""
        try:
            if self.bot.database and self.bot.database.db:
                collection = self.bot.database.get_collection('language')
                if collection:
                    find = collection.find_one({'_id': str(guild_id)})
                    if find:
                        return find.get('ln', 'en')
        except Exception as e:
            logger.error(f"Error getting language: {e}")
        return 'en'
    
    @commands.command(aliases=['time'])
    async def currenttime(self, ctx):
        """Get current Unix timestamp"""
        current_time = int(time.time())
        await ctx.send(f'{current_time}')
    
    @commands.command(aliases=['timekeep', 't', 'chrono'])
    async def timer(self, ctx, duration, seconds='0s'):
        """Set a visual timer with interactive buttons - Original pybot.py functionality"""
        lang = await self.get_language(ctx.guild.id)
        
        if not (duration.endswith('m') and seconds.endswith('s')):
            error_messages = {
                'en': '*Syntax error*\n*The command should contain minutes and seconds in format* **Nm Ns**\nFor example: ***7m 15s, 0m 30s***',
                'fr': '*Erreur de syntaxe*\n*La commande doit contenir le nombre de minutes et de secondes selon le format* **Nm Ns**\nPar exemple : ***7m 15s, 0m 30s***'
            }
            await ctx.send(error_messages.get(lang, error_messages['en']))
            return
        
        try:
            minutes = int(duration[:-1])
            secs = int(seconds[:-1])
            total_seconds = minutes * 60 + secs
            
            if total_seconds <= 0:
                await ctx.send("Timer duration must be greater than 0.")
                return
            
            if total_seconds > 7200:  # 2 hours limit
                await ctx.send("Timer cannot exceed 2 hours.")
                return
            
            # Create unique timer ID
            timer_id = f"{ctx.author.id}_{ctx.channel.id}"
            
            # Check if user already has a timer in this channel
            if timer_id in self.l:
                conflict_messages = {
                    'en': f'{ctx.author.mention}, you already have a timer running in this channel. Use the stop button or `.stop` to stop it first.',
                    'fr': f'{ctx.author.mention}, vous avez déjà un chronomètre en cours dans ce canal. Utilisez le bouton stop ou `.stop` pour l\'arrêter d\'abord.'
                }
                await ctx.send(conflict_messages.get(lang, conflict_messages['en']))
                return
            
            # Clean up any existing timer messages for this user/channel
            if timer_id in self.active_timers:
                try:
                    await self.active_timers[timer_id].delete()
                except:
                    pass
                del self.active_timers[timer_id]
            
            self.l[timer_id] = 0  # 0 = running, 1 = stopped, 2 = paused
            
            # Create interactive buttons
            class TimerView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=total_seconds + 30)
                    
                @discord.ui.button(label='Pause', style=discord.ButtonStyle.secondary, emoji='⏸️')
                async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message("🚫 Only the timer owner can control this timer.", ephemeral=True)
                        return
                    
                    if timer_id in outer_self.l and outer_self.l[timer_id] == 0:
                        outer_self.l[timer_id] = 2
                        button.label = 'Resume'
                        button.style = discord.ButtonStyle.success
                        button.emoji = '▶️'
                        await interaction.response.edit_message(view=self)
                    elif timer_id in outer_self.l and outer_self.l[timer_id] == 2:
                        outer_self.l[timer_id] = 0
                        button.label = 'Pause'
                        button.style = discord.ButtonStyle.secondary
                        button.emoji = '⏸️'
                        await interaction.response.edit_message(view=self)
                    else:
                        await interaction.response.send_message("❌ No timer to pause/resume.", ephemeral=True)
                
                @discord.ui.button(label='Stop', style=discord.ButtonStyle.danger, emoji='⏹️')
                async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message("🚫 Only the timer owner can control this timer.", ephemeral=True)
                        return
                    
                    if timer_id in outer_self.l:
                        outer_self.l[timer_id] = 1
                        # Disable all buttons
                        for item in self.children:
                            item.disabled = True
                        await interaction.response.edit_message(view=self)
                    else:
                        await interaction.response.send_message("❌ No timer to stop.", ephemeral=True)
                
                @discord.ui.button(label='Add 1min', style=discord.ButtonStyle.success, emoji='➕')
                async def add_time_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message("🚫 Only the timer owner can control this timer.", ephemeral=True)
                        return
                    
                    nonlocal total_seconds
                    if timer_id in outer_self.l and outer_self.l[timer_id] != 1:
                        total_seconds += 60
                        add_messages = {
                            'en': '⏰ Added 1 minute to timer! ⏱️',
                            'fr': '⏰ 1 minute ajoutée au chronomètre! ⏱️'
                        }
                        await interaction.response.send_message(add_messages.get(lang, add_messages['en']), ephemeral=True)
                    else:
                        await interaction.response.send_message("❌ Timer is not running.", ephemeral=True)
                
                @discord.ui.button(label='Notify Me', style=discord.ButtonStyle.primary, emoji='🔔')
                async def notify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message("🚫 Only the timer owner can control this timer.", ephemeral=True)
                        return
                    
                    if timer_id in outer_self.l and outer_self.l[timer_id] != 1:
                        await interaction.response.send_message("🔔 You'll be notified when the timer finishes!", ephemeral=True)
                    else:
                        await interaction.response.send_message("❌ Timer is not running.", ephemeral=True)
            
            outer_self = self
            view = TimerView()
            
            # Send only ONE timer message with buttons
            timer_embed = discord.Embed(
                title="⏰ Interactive Timer Started!",
                description=f"```\n⏱️  {minutes:02d}:{secs:02d}  ⏱️\n```",
                color=0x00ff00
            )
            timer_embed.add_field(name="👤 Timer Owner", value=ctx.author.mention, inline=True)
            timer_embed.add_field(name="🎯 Status", value="🟢 **RUNNING**", inline=True)
            timer_embed.add_field(name="📍 Channel", value=ctx.channel.mention, inline=True)
            timer_embed.set_footer(text="Use the buttons below to control your timer!")
            timer_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/755774680633016380.gif")
            
            msg = await ctx.send(embed=timer_embed, view=view)
            self.active_timers[timer_id] = msg
            
            # Animated timer countdown with rate limit protection
            last_update = 0
            while total_seconds > 0:
                if timer_id not in self.l:
                    break
                    
                if self.l[timer_id] == 1:  # Stop
                    stop_messages = {
                        'en': f"⏹️ **Timer stopped by {ctx.author.mention}!**",
                        'fr': f"⏹️ **Chronomètre arrêté par {ctx.author.mention}!**"
                    }
                    await ctx.send(stop_messages.get(lang, stop_messages['en']))
                    del self.l[timer_id]
                    if timer_id in self.active_timers:
                        del self.active_timers[timer_id]
                    break
                    
                elif self.l[timer_id] == 2:  # Pause
                    pause_embed = discord.Embed(
                        title="⏸️ Timer Paused",
                        description=f"```\n⏸️  {total_seconds // 60:02d}:{total_seconds % 60:02d}  ⏸️\n```",
                        color=0x808080
                    )
                    pause_embed.add_field(name="👤 Timer Owner", value=ctx.author.mention, inline=True)
                    pause_embed.add_field(name="🎯 Status", value="⏸️ **PAUSED**", inline=True)
                    pause_embed.add_field(name="📍 Channel", value=ctx.channel.mention, inline=True)
                    pause_embed.set_footer(text="Click Resume to continue the timer!")
                    
                    try:
                        await msg.edit(embed=pause_embed, view=view)
                    except:
                        pass
                    while self.l.get(timer_id, 1) == 2:
                        await asyncio.sleep(1)
                    continue
                
                # Update timer display with rate limit protection (every second for real-time updates)
                current_time = time.time()
                should_update = (
                    current_time - last_update >= 1 or  # Every second for real-time
                    total_seconds <= 10 or  # Last 10 seconds
                    total_seconds % 60 == 0 or  # Every minute
                    total_seconds in [300, 180, 60, 30]  # Important milestones
                )
                
                if should_update:
                    # Dynamic colors based on time remaining
                    if total_seconds > 300:  # > 5 minutes
                        color = 0x00ff00  # Green
                        status_emoji = "🟢"
                        status_text = "RUNNING"
                    elif total_seconds > 60:  # 1-5 minutes
                        color = 0xffff00  # Yellow
                        status_emoji = "🟡"
                        status_text = "RUNNING"
                    elif total_seconds > 30:  # 30s-1min
                        color = 0xff8800  # Orange
                        status_emoji = "🟠"
                        status_text = "HURRY UP!"
                    else:  # < 30 seconds
                        color = 0xff0000  # Red
                        status_emoji = "🔴"
                        status_text = "FINAL COUNTDOWN!"
                    
                    # Create simple single-line progress bar
                    total_time = minutes * 60 + secs
                    progress = max(0, (total_time - total_seconds) / total_time)
                    
                    # Single line progress bar (20 characters for clean display)
                    bar_length = 20
                    filled_blocks = int(progress * bar_length)
                    empty_blocks = bar_length - filled_blocks
                    
                    # Simple progress bar with single character
                    progress_bar = "█" * filled_blocks + "░" * empty_blocks
                    
                    timer_embed = discord.Embed(
                        title="⏰ Interactive Timer",
                        description=f"```\n⏱️  {total_seconds // 60:02d}:{total_seconds % 60:02d}  ⏱️\n```",
                        color=color
                    )
                    timer_embed.add_field(name="👤 Timer Owner", value=ctx.author.mention, inline=True)
                    timer_embed.add_field(name="🎯 Status", value=f"{status_emoji} **{status_text}**", inline=True)
                    timer_embed.add_field(name="📍 Channel", value=ctx.channel.mention, inline=True)
                    timer_embed.add_field(name="📊 Progress", value=f"{progress_bar}", inline=False)
                    
                    if total_seconds <= 30:
                        timer_embed.set_footer(text="⚡ Time is running out! ⚡")
                        timer_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/755774680633016380.gif")
                    else:
                        timer_embed.set_footer(text="Use the buttons below to control your timer!")
                    
                    try:
                        await msg.edit(embed=timer_embed, view=view)
                        last_update = current_time
                    except:
                        pass
                
                # Check for milestone notifications
                if total_seconds in [300, 180, 60, 30, 10, 5, 3, 2, 1]:
                    milestone_messages = {}
                    if total_seconds == 300:
                        milestone_messages = {
                            'en': ':yellow_circle: **5 minutes LEFT** {}',
                            'fr': ':yellow_circle: **5 minutes RESTANTES** {}'
                        }
                    elif total_seconds == 180:
                        milestone_messages = {
                            'en': ':orange_circle: **3 minutes LEFT** {}',
                            'fr': ':orange_circle: **3 minutes RESTANTES** {}'
                        }
                    elif total_seconds == 60:
                        milestone_messages = {
                            'en': ':orange_circle: **1 minute LEFT** {}',
                            'fr': ':orange_circle: **1 minute RESTANTE** {}'
                        }
                    elif total_seconds == 30:
                        milestone_messages = {
                            'en': ':red_circle: **30 seconds LEFT** {}',
                            'fr': ':red_circle: **30 secondes RESTANTES** {}'
                        }
                    elif total_seconds <= 10:
                        milestone_messages = {
                            'en': f':rotating_light: **{total_seconds} seconds LEFT** {{}}',
                            'fr': f':rotating_light: **{total_seconds} secondes RESTANTES** {{}}'
                        }
                    
                    if milestone_messages:
                        try:
                            await ctx.send(milestone_messages[lang].format(ctx.author.mention))
                        except:
                            pass
                
                await asyncio.sleep(1)
                total_seconds -= 1
            
            if total_seconds <= 0 and timer_id in self.l:
                # Disable all buttons
                for item in view.children:
                    item.disabled = True
                
                end_messages = {
                    'en': ":red_circle: **Time's UP!** {} 🎉\nhttps://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683",
                    'fr': ":red_circle: **Le temps est ÉCOULÉ!** {} 🎉\nhttps://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683"
                }
                
                try:
                    final_embed = discord.Embed(
                        title="🎉 Timer Completed!",
                        description="```\n🚨  00:00  🚨\n```",
                        color=0xff0000
                    )
                    final_embed.add_field(name="👤 Timer Owner", value=ctx.author.mention, inline=True)
                    final_embed.add_field(name="🎯 Status", value="✅ **FINISHED!**", inline=True)
                    final_embed.add_field(name="📍 Channel", value=ctx.channel.mention, inline=True)
                    final_embed.add_field(name="🎊 Result", value="**TIME'S UP!** 🎉", inline=False)
                    final_embed.set_footer(text="Timer completed successfully!")
                    final_embed.set_image(url="https://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683.gif")
                    
                    await msg.edit(embed=final_embed, view=view)
                    await ctx.send(end_messages[lang].format(ctx.author.mention))
                except:
                    pass
                
                # Clean up
                if timer_id in self.l:
                    del self.l[timer_id]
                if timer_id in self.active_timers:
                    del self.active_timers[timer_id]
                    
        except ValueError:
            error_messages = {
                'en': '*Syntax error*\n*The command should contain minutes and seconds in format* **Nm Ns**\nFor example: ***7m 15s, 0m 30s***',
                'fr': '*Erreur de syntaxe*\n*La commande doit contenir le nombre de minutes et de secondes selon le format* **Nm Ns**\nPar exemple : ***7m 15s, 0m 30s***'
            }
            await ctx.send(error_messages.get(lang, error_messages['en']))
        except Exception as e:
            logger.error(f"Timer error: {e}")
            await ctx.send("❌ An error occurred while setting up the timer.")
    
    @commands.command()
    async def stop(self, ctx):
        """Stop your active timer"""
        timer_id = f"{ctx.author.id}_{ctx.channel.id}"
        
        if timer_id in self.l:
            self.l[timer_id] = 1
            await ctx.send(f"⏹️ Timer stopped by {ctx.author.mention}!")
        else:
            await ctx.send("❌ You don't have an active timer in this channel.")
    
    @commands.command()
    async def pause(self, ctx):
        """Pause your active timer"""
        timer_id = f"{ctx.author.id}_{ctx.channel.id}"
        
        if timer_id in self.l and self.l[timer_id] == 0:
            self.l[timer_id] = 2
            await ctx.send(f"⏸️ Timer paused by {ctx.author.mention}!")
        elif timer_id in self.l and self.l[timer_id] == 2:
            await ctx.send("⏸️ Your timer is already paused.")
        else:
            await ctx.send("❌ You don't have an active timer in this channel.")
    
    @commands.command(aliases=['cleartimers'])
    async def resettimers(self, ctx):
        """Clear all active timers (Admin only)"""
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("❌ You need `Manage Messages` permission to use this command.")
            return
        
        count = len(self.l)
        self.l.clear()
        self.active_timers.clear()
        
        await ctx.send(f"🧹 Cleared {count} active timers.")

async def setup(bot):
    await bot.add_cog(Timer(bot))
