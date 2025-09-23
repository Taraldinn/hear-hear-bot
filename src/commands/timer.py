"""
Timer Commands - Restored Original Functionality from pybot.py
Author: aldinn
Email: kferdoush617@gmail.com

Full restoration of the original pybot.py timer system
"""

import asyncio
import logging
import time

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class Timer(commands.Cog):
    """Timer commands with original pybot.py functionality"""

    def __init__(self, bot):
        self.bot = bot
        self.l = {}  # timer trigger library - format: {user_id_channel_id: status}
        self.t = {}  # reminder storage library
        self.active_timers = (
            {}
        )  # track active timer messages - format: {user_id_channel_id: message_obj}

    async def get_language(self, guild_id):
        """Get language setting for a guild"""
        try:
            if self.bot.database and self.bot.database.db:
                collection = self.bot.database.get_collection("language")
                if collection:
                    find = collection.find_one({"_id": str(guild_id)})
                    if find:
                        return find.get("ln", "en")
        except (AttributeError, KeyError, TypeError) as e:
            logger.error("Error getting language: %s", e)
        return "en"

    @commands.command(aliases=["time"])
    async def currenttime(self, ctx):
        """Get current Unix timestamp"""
        current_time = int(time.time())
        await ctx.send(f"{current_time}")

    @commands.command(aliases=["timekeep", "t", "chrono"])
    async def timer(self, ctx, duration, seconds="0s"):
        """Set a visual timer with interactive buttons - Original pybot.py functionality"""
        lang = await self.get_language(ctx.guild.id)

        if not (duration.endswith("m") and seconds.endswith("s")):
            error_messages = {
                "en": (
                    "*Syntax error*\n*The command should contain minutes and seconds "
                    "in format* **Nm Ns**\nFor example: ***7m 15s, 0m 30s***"
                ),
                "fr": (
                    "*Erreur de syntaxe*\n*La commande doit contenir le nombre de minutes "
                    "et de secondes selon le format* **Nm Ns**\nPar exemple : ***7m 15s, 0m 30s***"
                ),
            }
            await ctx.send(error_messages.get(lang, error_messages["en"]))
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
                    "en": (
                        f"{ctx.author.mention}, you already have a timer running in this channel. "
                        "Use the stop button or `.stop` to stop it first."
                    ),
                    "fr": (
                        f"{ctx.author.mention}, vous avez déjà un chronomètre en cours dans ce canal. "
                        "Utilisez le bouton stop ou `.stop` pour l'arrêter d'abord."
                    ),
                }
                await ctx.send(conflict_messages.get(lang, conflict_messages["en"]))
                return

            # Clean up any existing timer messages for this user/channel
            if timer_id in self.active_timers:
                try:
                    await self.active_timers[timer_id].delete()
                except (discord.NotFound, discord.HTTPException):
                    pass
                del self.active_timers[timer_id]

            self.l[timer_id] = 0  # 0 = running, 1 = stopped, 2 = paused

            # Create interactive buttons
            class TimerView(discord.ui.View):
                """Interactive view for timer controls."""

                def __init__(self):
                    super().__init__(timeout=total_seconds + 30)

                @discord.ui.button(
                    label="Pause", style=discord.ButtonStyle.secondary, emoji="⏸️"
                )
                async def pause_button(
                    self, interaction: discord.Interaction, button: discord.ui.Button
                ):  # pylint: disable=unused-argument
                    """Handle pause/resume button clicks."""
                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message(
                            "🚫 Only the timer owner can control this timer.",
                            ephemeral=True,
                        )
                        return

                    if timer_id in outer_self.l and outer_self.l[timer_id] == 0:
                        outer_self.l[timer_id] = 2
                        button.label = "Resume"
                        button.style = discord.ButtonStyle.success
                        button.emoji = "▶️"
                        await interaction.response.edit_message(view=self)
                    elif timer_id in outer_self.l and outer_self.l[timer_id] == 2:
                        outer_self.l[timer_id] = 0
                        button.label = "Pause"
                        button.style = discord.ButtonStyle.secondary
                        button.emoji = "⏸️"
                        await interaction.response.edit_message(view=self)
                    else:
                        await interaction.response.send_message(
                            "❌ No timer to pause/resume.", ephemeral=True
                        )

                @discord.ui.button(
                    label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️"
                )
                async def stop_button(
                    self, interaction: discord.Interaction, button: discord.ui.Button
                ):  # pylint: disable=unused-argument
                    """Handle stop button clicks."""
                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message(
                            "🚫 Only the timer owner can control this timer.",
                            ephemeral=True,
                        )
                        return

                    if timer_id in outer_self.l:
                        outer_self.l[timer_id] = 1
                        # Disable all buttons by clearing view
                        self.clear_items()
                        await interaction.response.edit_message(view=self)
                    else:
                        await interaction.response.send_message(
                            "❌ No timer to stop.", ephemeral=True
                        )

                @discord.ui.button(
                    label="Add 1min", style=discord.ButtonStyle.success, emoji="➕"
                )
                async def add_time_button(
                    self, interaction: discord.Interaction, button: discord.ui.Button
                ):  # pylint: disable=unused-argument
                    """Handle add time button clicks."""
                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message(
                            "🚫 Only the timer owner can control this timer.",
                            ephemeral=True,
                        )
                        return

                    nonlocal total_seconds
                    if timer_id in outer_self.l and outer_self.l[timer_id] != 1:
                        total_seconds += 60
                        add_messages = {
                            "en": "⏰ Added 1 minute to timer! ⏱️",
                            "fr": "⏰ 1 minute ajoutée au chronomètre! ⏱️",
                        }
                        await interaction.response.send_message(
                            add_messages.get(lang, add_messages["en"]), ephemeral=True
                        )
                    else:
                        await interaction.response.send_message(
                            "❌ Timer is not running.", ephemeral=True
                        )

                @discord.ui.button(
                    label="Notify Me", style=discord.ButtonStyle.primary, emoji="🔔"
                )
                async def notify_button(
                    self, interaction: discord.Interaction, button: discord.ui.Button
                ):  # pylint: disable=unused-argument
                    """Handle notify button clicks."""
                    if interaction.user.id != ctx.author.id:
                        await interaction.response.send_message(
                            "🚫 Only the timer owner can control this timer.",
                            ephemeral=True,
                        )
                        return

                    if timer_id in outer_self.l and outer_self.l[timer_id] != 1:
                        await interaction.response.send_message(
                            "🔔 You'll be notified when the timer finishes!",
                            ephemeral=True,
                        )
                    else:
                        await interaction.response.send_message(
                            "❌ Timer is not running.", ephemeral=True
                        )

            outer_self = self
            view = TimerView()

            # Send only ONE timer message with buttons
            timer_embed = discord.Embed(
                title="⏰ Interactive Timer Started!",
                description=f"```\n⏱️  {minutes:02d}:{secs:02d}  ⏱️\n```",
                color=0x00FF00,
            )
            timer_embed.add_field(
                name="👤 Timer Owner", value=ctx.author.mention, inline=True
            )
            timer_embed.add_field(name="🎯 Status", value="🟢 **RUNNING**", inline=True)
            timer_embed.add_field(
                name="📍 Channel", value=ctx.channel.mention, inline=True
            )
            timer_embed.set_footer(text="Use the buttons below to control your timer!")
            timer_embed.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/755774680633016380.gif"
            )

            msg = await ctx.send(embed=timer_embed, view=view)
            self.active_timers[timer_id] = msg

            # Animated timer countdown with rate limit protection
            last_update = 0
            while total_seconds > 0:
                if timer_id not in self.l:
                    break

                if self.l[timer_id] == 1:  # Stop
                    stop_messages = {
                        "en": f"⏹️ **Timer stopped by {ctx.author.mention}!**",
                        "fr": f"⏹️ **Chronomètre arrêté par {ctx.author.mention}!**",
                    }
                    await ctx.send(stop_messages.get(lang, stop_messages["en"]))
                    del self.l[timer_id]
                    if timer_id in self.active_timers:
                        del self.active_timers[timer_id]
                    break

                elif self.l[timer_id] == 2:  # Pause
                    pause_embed = discord.Embed(
                        title="⏸️ Timer Paused",
                        description=f"```\n⏸️  {total_seconds // 60:02d}:{total_seconds % 60:02d}  ⏸️\n```",
                        color=0x808080,
                    )
                    pause_embed.add_field(
                        name="👤 Timer Owner", value=ctx.author.mention, inline=True
                    )
                    pause_embed.add_field(
                        name="🎯 Status", value="⏸️ **PAUSED**", inline=True
                    )
                    pause_embed.add_field(
                        name="📍 Channel", value=ctx.channel.mention, inline=True
                    )
                    pause_embed.set_footer(text="Click Resume to continue the timer!")

                    try:
                        await msg.edit(embed=pause_embed, view=view)
                    except (discord.NotFound, discord.HTTPException):
                        pass
                    while self.l.get(timer_id, 1) == 2:
                        await asyncio.sleep(1)
                    continue

                # Update timer display with rate limit protection (every second for real-time updates)
                current_time = time.time()
                should_update = (
                    current_time - last_update >= 1  # Every second for real-time
                    or total_seconds <= 10  # Last 10 seconds
                    or total_seconds % 60 == 0  # Every minute
                    or total_seconds in [300, 180, 60, 30]  # Important milestones
                )

                if should_update:
                    # Dynamic colors based on time remaining
                    if total_seconds > 300:  # > 5 minutes
                        color = 0x00FF00  # Green
                        status_emoji = "🟢"
                        status_text = "RUNNING"
                    elif total_seconds > 60:  # 1-5 minutes
                        color = 0xFFFF00  # Yellow
                        status_emoji = "🟡"
                        status_text = "RUNNING"
                    elif total_seconds > 30:  # 30s-1min
                        color = 0xFF8800  # Orange
                        status_emoji = "🟠"
                        status_text = "HURRY UP!"
                    else:  # < 30 seconds
                        color = 0xFF0000  # Red
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
                        color=color,
                    )
                    timer_embed.add_field(
                        name="👤 Timer Owner", value=ctx.author.mention, inline=True
                    )
                    timer_embed.add_field(
                        name="🎯 Status",
                        value=f"{status_emoji} **{status_text}**",
                        inline=True,
                    )
                    timer_embed.add_field(
                        name="📍 Channel", value=ctx.channel.mention, inline=True
                    )
                    timer_embed.add_field(
                        name="📊 Progress", value=f"{progress_bar}", inline=False
                    )

                    if total_seconds <= 30:
                        timer_embed.set_footer(text="⚡ Time is running out! ⚡")
                        timer_embed.set_thumbnail(
                            url="https://cdn.discordapp.com/emojis/755774680633016380.gif"
                        )
                    else:
                        timer_embed.set_footer(
                            text="Use the buttons below to control your timer!"
                        )

                    try:
                        await msg.edit(embed=timer_embed, view=view)
                        last_update = current_time
                    except (discord.NotFound, discord.HTTPException):
                        pass

                # Check for milestone notifications
                if total_seconds in [300, 180, 60, 30, 10, 5, 3, 2, 1]:
                    milestone_messages = {}
                    if total_seconds == 300:
                        milestone_messages = {
                            "en": ":yellow_circle: **5 minutes LEFT** {}",
                            "fr": ":yellow_circle: **5 minutes RESTANTES** {}",
                        }
                    elif total_seconds == 180:
                        milestone_messages = {
                            "en": ":orange_circle: **3 minutes LEFT** {}",
                            "fr": ":orange_circle: **3 minutes RESTANTES** {}",
                        }
                    elif total_seconds == 60:
                        milestone_messages = {
                            "en": ":orange_circle: **1 minute LEFT** {}",
                            "fr": ":orange_circle: **1 minute RESTANTE** {}",
                        }
                    elif total_seconds == 30:
                        milestone_messages = {
                            "en": ":red_circle: **30 seconds LEFT** {}",
                            "fr": ":red_circle: **30 secondes RESTANTES** {}",
                        }
                    elif total_seconds <= 10:
                        milestone_messages = {
                            "en": f":rotating_light: **{total_seconds} seconds LEFT** {{}}",
                            "fr": f":rotating_light: **{total_seconds} secondes RESTANTES** {{}}",
                        }

                    if milestone_messages:
                        try:
                            await ctx.send(
                                milestone_messages[lang].format(ctx.author.mention)
                            )
                        except (discord.HTTPException, KeyError):
                            pass

                await asyncio.sleep(1)
                total_seconds -= 1

            if total_seconds <= 0 and timer_id in self.l:
                # Disable all buttons by clearing the view
                view.clear_items()

                end_messages = {
                    "en": ":red_circle: **Time's UP!** {} 🎉\nhttps://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683",
                    "fr": ":red_circle: **Le temps est ÉCOULÉ!** {} 🎉\nhttps://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683",
                }

                try:
                    final_embed = discord.Embed(
                        title="🎉 Timer Completed!",
                        description="```\n🚨  00:00  🚨\n```",
                        color=0xFF0000,
                    )
                    final_embed.add_field(
                        name="👤 Timer Owner", value=ctx.author.mention, inline=True
                    )
                    final_embed.add_field(
                        name="🎯 Status", value="✅ **FINISHED!**", inline=True
                    )
                    final_embed.add_field(
                        name="📍 Channel", value=ctx.channel.mention, inline=True
                    )
                    final_embed.add_field(
                        name="🎊 Result", value="**TIME'S UP!** 🎉", inline=False
                    )
                    final_embed.set_footer(text="Timer completed successfully!")
                    final_embed.set_image(
                        url="https://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683.gif"
                    )

                    await msg.edit(embed=final_embed, view=view)
                    await ctx.send(end_messages[lang].format(ctx.author.mention))
                except (discord.HTTPException, KeyError):
                    pass

                # Clean up
                if timer_id in self.l:
                    del self.l[timer_id]
                if timer_id in self.active_timers:
                    del self.active_timers[timer_id]

        except ValueError:
            error_messages = {
                "en": "*Syntax error*\n*The command should contain minutes and seconds in format* **Nm Ns**\nFor example: ***7m 15s, 0m 30s***",
                "fr": "*Erreur de syntaxe*\n*La commande doit contenir le nombre de minutes et de secondes selon le format* **Nm Ns**\nPar exemple : ***7m 15s, 0m 30s***",
            }
            await ctx.send(error_messages.get(lang, error_messages["en"]))
        except (discord.HTTPException, asyncio.TimeoutError) as e:
            logger.error("Timer error: %s", e)
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

    @commands.command()
    async def resume(self, ctx):
        """Resume your paused timer"""
        timer_id = f"{ctx.author.id}_{ctx.channel.id}"

        if timer_id in self.l and self.l[timer_id] == 2:
            self.l[timer_id] = 0
            await ctx.send(f"▶️ Timer resumed by {ctx.author.mention}!")
        elif timer_id in self.l and self.l[timer_id] == 0:
            await ctx.send("⏸️ Your timer is already running.")
        else:
            await ctx.send("❌ You don't have a paused timer in this channel.")

    @commands.command(aliases=["cleartimers"])
    async def resettimers(self, ctx):
        """Clear all active timers (Admin only)"""
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send(
                "❌ You need `Manage Messages` permission to use this command."
            )
            return

        count = len(self.l)
        self.l.clear()
        self.active_timers.clear()

        await ctx.send(f"🧹 Cleared {count} active timers.")

    # ========================================
    # SLASH COMMAND VERSIONS
    # ========================================

    @app_commands.command(
        name="timer", description="Set a visual timer with interactive buttons"
    )
    @app_commands.describe(
        minutes="Number of minutes (0-120)", seconds="Number of seconds (0-59)"
    )
    async def timer_slash(
        self, interaction: discord.Interaction, minutes: int, seconds: int = 0
    ):
        """Slash command version of timer"""
        # Validate input
        if not (0 <= minutes <= 120 and 0 <= seconds <= 59):
            await interaction.response.send_message(
                "❌ Invalid time range. Minutes: 0-120, Seconds: 0-59", ephemeral=True
            )
            return

        if minutes == 0 and seconds == 0:
            await interaction.response.send_message(
                "❌ Timer duration must be greater than 0.", ephemeral=True
            )
            return

        # Ensure we have guild and channel
        if not interaction.guild or not interaction.channel:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        # Convert to expected format and call the timer logic directly
        lang = await self.get_language(interaction.guild.id)
        total_seconds = minutes * 60 + seconds

        if total_seconds > 7200:  # 2 hours limit
            await interaction.response.send_message(
                "❌ Timer cannot exceed 2 hours.", ephemeral=True
            )
            return

        # Create unique timer ID
        timer_id = f"{interaction.user.id}_{interaction.channel.id}"

        # Check if user already has a timer in this channel
        if timer_id in self.l:
            conflict_messages = {
                "en": f"{interaction.user.mention}, you already have a timer running in this channel. Use `/timer-stop` to stop it first.",
                "fr": f"{interaction.user.mention}, vous avez déjà un chronomètre en cours dans ce canal. Utilisez `/timer-stop` pour l'arrêter d'abord.",
            }
            await interaction.response.send_message(
                conflict_messages.get(lang, conflict_messages["en"]), ephemeral=True
            )
            return

        # Clean up any existing timer messages for this user/channel
        if timer_id in self.active_timers:
            try:
                await self.active_timers[timer_id].delete()
            except (discord.NotFound, discord.HTTPException):
                pass
            del self.active_timers[timer_id]

        self.l[timer_id] = 0  # 0 = running, 1 = stopped, 2 = paused

        # Get channel mention safely
        channel_mention = "DM"
        if interaction.channel:
            try:
                if isinstance(interaction.channel, discord.TextChannel):
                    channel_mention = interaction.channel.mention
                elif isinstance(
                    interaction.channel,
                    (
                        discord.VoiceChannel,
                        discord.ForumChannel,
                        discord.CategoryChannel,
                    ),
                ):
                    channel_mention = interaction.channel.mention
                else:
                    channel_mention = str(interaction.channel)
            except (AttributeError, TypeError):
                channel_mention = "DM"

        # Create interactive buttons (same as prefix command)
        class TimerView(discord.ui.View):
            """Interactive view for slash command timer controls."""

            def __init__(self):
                super().__init__(timeout=total_seconds + 30)

            @discord.ui.button(
                label="Pause", style=discord.ButtonStyle.secondary, emoji="⏸️"
            )
            async def pause_button(
                self, button_interaction: discord.Interaction, button: discord.ui.Button
            ):  # pylint: disable=unused-argument
                """Handle pause/resume button clicks for slash command."""
                if button_interaction.user.id != interaction.user.id:
                    await button_interaction.response.send_message(
                        "🚫 Only the timer owner can control this timer.",
                        ephemeral=True,
                    )
                    return

                if timer_id in outer_self.l and outer_self.l[timer_id] == 0:
                    outer_self.l[timer_id] = 2
                    button.label = "Resume"
                    button.style = discord.ButtonStyle.success
                    button.emoji = "▶️"
                    await button_interaction.response.edit_message(view=self)
                elif timer_id in outer_self.l and outer_self.l[timer_id] == 2:
                    outer_self.l[timer_id] = 0
                    button.label = "Pause"
                    button.style = discord.ButtonStyle.secondary
                    button.emoji = "⏸️"
                    await button_interaction.response.edit_message(view=self)
                else:
                    await button_interaction.response.send_message(
                        "❌ No timer to pause/resume.", ephemeral=True
                    )

            @discord.ui.button(
                label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️"
            )
            async def stop_button(
                self, button_interaction: discord.Interaction, button: discord.ui.Button
            ):  # pylint: disable=unused-argument
                """Handle stop button clicks for slash command."""
                if button_interaction.user.id != interaction.user.id:
                    await button_interaction.response.send_message(
                        "🚫 Only the timer owner can control this timer.",
                        ephemeral=True,
                    )
                    return

                if timer_id in outer_self.l:
                    outer_self.l[timer_id] = 1
                    self.clear_items()
                    await button_interaction.response.edit_message(view=self)
                else:
                    await button_interaction.response.send_message(
                        "❌ No timer to stop.", ephemeral=True
                    )

            @discord.ui.button(
                label="Add 1min", style=discord.ButtonStyle.success, emoji="➕"
            )
            async def add_time_button(
                self, button_interaction: discord.Interaction, button: discord.ui.Button
            ):  # pylint: disable=unused-argument
                """Handle add time button clicks for slash command."""
                if button_interaction.user.id != interaction.user.id:
                    await button_interaction.response.send_message(
                        "🚫 Only the timer owner can control this timer.",
                        ephemeral=True,
                    )
                    return

                nonlocal total_seconds
                if timer_id in outer_self.l and outer_self.l[timer_id] != 1:
                    total_seconds += 60
                    add_messages = {
                        "en": "⏰ Added 1 minute to timer! ⏱️",
                        "fr": "⏰ 1 minute ajoutée au chronomètre! ⏱️",
                    }
                    await button_interaction.response.send_message(
                        add_messages.get(lang, add_messages["en"]), ephemeral=True
                    )
                else:
                    await button_interaction.response.send_message(
                        "❌ Timer is not running.", ephemeral=True
                    )

            @discord.ui.button(
                label="Notify Me", style=discord.ButtonStyle.primary, emoji="🔔"
            )
            async def notify_button(
                self, button_interaction: discord.Interaction, button: discord.ui.Button
            ):  # pylint: disable=unused-argument
                """Handle notify button clicks for slash command."""
                if button_interaction.user.id != interaction.user.id:
                    await button_interaction.response.send_message(
                        "🚫 Only the timer owner can control this timer.",
                        ephemeral=True,
                    )
                    return

                if timer_id in outer_self.l and outer_self.l[timer_id] != 1:
                    await button_interaction.response.send_message(
                        "🔔 You'll be notified when the timer finishes!", ephemeral=True
                    )
                else:
                    await button_interaction.response.send_message(
                        "❌ Timer is not running.", ephemeral=True
                    )

        outer_self = self
        view = TimerView()

        # Send timer message with buttons
        timer_embed = discord.Embed(
            title="⏰ Interactive Timer Started!",
            description=f"```\n⏱️  {minutes:02d}:{seconds:02d}  ⏱️\n```",
            color=0x00FF00,
        )
        timer_embed.add_field(
            name="👤 Timer Owner", value=interaction.user.mention, inline=True
        )
        timer_embed.add_field(name="🎯 Status", value="🟢 **RUNNING**", inline=True)
        timer_embed.add_field(name="📍 Channel", value=channel_mention, inline=True)
        timer_embed.set_footer(text="Use the buttons below to control your timer!")
        timer_embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/755774680633016380.gif"
        )

        await interaction.response.send_message(embed=timer_embed, view=view)
        msg = await interaction.original_response()
        self.active_timers[timer_id] = msg

        # Start the countdown logic (same as prefix command)
        last_update = 0
        while total_seconds > 0:
            if timer_id not in self.l:
                break

            if self.l[timer_id] == 1:  # Stop
                stop_messages = {
                    "en": f"⏹️ **Timer stopped by {interaction.user.mention}!**",
                    "fr": f"⏹️ **Chronomètre arrêté par {interaction.user.mention}!**",
                }
                await interaction.followup.send(
                    stop_messages.get(lang, stop_messages["en"])
                )
                del self.l[timer_id]
                if timer_id in self.active_timers:
                    del self.active_timers[timer_id]
                break

            elif self.l[timer_id] == 2:  # Pause
                pause_embed = discord.Embed(
                    title="⏸️ Timer Paused",
                    description=f"```\n⏸️  {total_seconds // 60:02d}:{total_seconds % 60:02d}  ⏸️\n```",
                    color=0x808080,
                )
                pause_embed.add_field(
                    name="👤 Timer Owner", value=interaction.user.mention, inline=True
                )
                pause_embed.add_field(
                    name="🎯 Status", value="⏸️ **PAUSED**", inline=True
                )
                pause_embed.add_field(
                    name="📍 Channel", value=channel_mention, inline=True
                )
                pause_embed.set_footer(text="Click Resume to continue the timer!")

                try:
                    await msg.edit(embed=pause_embed, view=view)
                except (discord.NotFound, discord.HTTPException):
                    pass
                while self.l.get(timer_id, 1) == 2:
                    await asyncio.sleep(1)
                continue

            # Update timer display (same logic as prefix command)
            current_time = time.time()
            should_update = (
                current_time - last_update >= 1
                or total_seconds <= 10
                or total_seconds % 60 == 0
                or total_seconds in [300, 180, 60, 30]
            )

            if should_update:
                # Dynamic colors based on time remaining
                if total_seconds > 300:
                    color = 0x00FF00
                    status_emoji = "🟢"
                    status_text = "RUNNING"
                elif total_seconds > 60:
                    color = 0xFFFF00
                    status_emoji = "🟡"
                    status_text = "RUNNING"
                elif total_seconds > 30:
                    color = 0xFF8800
                    status_emoji = "🟠"
                    status_text = "HURRY UP!"
                else:
                    color = 0xFF0000
                    status_emoji = "🔴"
                    status_text = "FINAL COUNTDOWN!"

                # Progress bar
                total_time = minutes * 60 + seconds
                progress = max(0, (total_time - total_seconds) / total_time)
                bar_length = 20
                filled_blocks = int(progress * bar_length)
                empty_blocks = bar_length - filled_blocks
                progress_bar = "█" * filled_blocks + "░" * empty_blocks

                timer_embed = discord.Embed(
                    title="⏰ Interactive Timer",
                    description=f"```\n⏱️  {total_seconds // 60:02d}:{total_seconds % 60:02d}  ⏱️\n```",
                    color=color,
                )
                timer_embed.add_field(
                    name="👤 Timer Owner", value=interaction.user.mention, inline=True
                )
                timer_embed.add_field(
                    name="🎯 Status",
                    value=f"{status_emoji} **{status_text}**",
                    inline=True,
                )
                timer_embed.add_field(
                    name="📍 Channel", value=channel_mention, inline=True
                )
                timer_embed.add_field(
                    name="📊 Progress", value=f"{progress_bar}", inline=False
                )

                if total_seconds <= 30:
                    timer_embed.set_footer(text="⚡ Time is running out! ⚡")
                    timer_embed.set_thumbnail(
                        url="https://cdn.discordapp.com/emojis/755774680633016380.gif"
                    )
                else:
                    timer_embed.set_footer(
                        text="Use the buttons below to control your timer!"
                    )

                try:
                    await msg.edit(embed=timer_embed, view=view)
                    last_update = current_time
                except (discord.NotFound, discord.HTTPException):
                    pass

            # Milestone notifications
            if total_seconds in [300, 180, 60, 30, 10, 5, 3, 2, 1]:
                milestone_messages = {}
                if total_seconds == 300:
                    milestone_messages = {
                        "en": ":yellow_circle: **5 minutes LEFT** {}",
                        "fr": ":yellow_circle: **5 minutes RESTANTES** {}",
                    }
                elif total_seconds == 180:
                    milestone_messages = {
                        "en": ":orange_circle: **3 minutes LEFT** {}",
                        "fr": ":orange_circle: **3 minutes RESTANTES** {}",
                    }
                elif total_seconds == 60:
                    milestone_messages = {
                        "en": ":orange_circle: **1 minute LEFT** {}",
                        "fr": ":orange_circle: **1 minute RESTANTE** {}",
                    }
                elif total_seconds == 30:
                    milestone_messages = {
                        "en": ":red_circle: **30 seconds LEFT** {}",
                        "fr": ":red_circle: **30 secondes RESTANTES** {}",
                    }
                elif total_seconds <= 10:
                    milestone_messages = {
                        "en": f":rotating_light: **{total_seconds} seconds LEFT** {{}}",
                        "fr": f":rotating_light: **{total_seconds} secondes RESTANTES** {{}}",
                    }

                if milestone_messages:
                    try:
                        await interaction.followup.send(
                            milestone_messages[lang].format(interaction.user.mention)
                        )
                    except (discord.HTTPException, KeyError):
                        pass

            await asyncio.sleep(1)
            total_seconds -= 1

        # Timer completion
        if total_seconds <= 0 and timer_id in self.l:
            view.clear_items()

            end_messages = {
                "en": ":red_circle: **Time's UP!** {} 🎉\nhttps://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683",
                "fr": ":red_circle: **Le temps est ÉCOULÉ!** {} 🎉\nhttps://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683",
            }

            try:
                final_embed = discord.Embed(
                    title="🎉 Timer Completed!",
                    description="```\n🚨  00:00  🚨\n```",
                    color=0xFF0000,
                )
                final_embed.add_field(
                    name="👤 Timer Owner", value=interaction.user.mention, inline=True
                )
                final_embed.add_field(
                    name="🎯 Status", value="✅ **FINISHED!**", inline=True
                )
                final_embed.add_field(
                    name="📍 Channel", value=channel_mention, inline=True
                )
                final_embed.add_field(
                    name="🎊 Result", value="**TIME'S UP!** 🎉", inline=False
                )
                final_embed.set_footer(text="Timer completed successfully!")
                final_embed.set_image(
                    url="https://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683.gif"
                )

                await msg.edit(embed=final_embed, view=view)
                await interaction.followup.send(
                    end_messages[lang].format(interaction.user.mention)
                )
            except (discord.HTTPException, KeyError):
                pass

            # Clean up
            if timer_id in self.l:
                del self.l[timer_id]
            if timer_id in self.active_timers:
                del self.active_timers[timer_id]

    @app_commands.command(name="currenttime", description="Get current Unix timestamp")
    async def currenttime_slash(self, interaction: discord.Interaction):
        """Slash command version of currenttime"""
        current_time = int(time.time())
        await interaction.response.send_message(
            f"**Current Unix Timestamp:** `{current_time}`"
        )

    @app_commands.command(name="timer-stop", description="Stop your active timer")
    async def stop_slash(self, interaction: discord.Interaction):
        """Slash command version of stop"""
        if not interaction.channel:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        timer_id = f"{interaction.user.id}_{interaction.channel.id}"

        if timer_id in self.l:
            self.l[timer_id] = 1
            await interaction.response.send_message(
                f"⏹️ Timer stopped by {interaction.user.mention}!"
            )
        else:
            await interaction.response.send_message(
                "❌ You don't have an active timer in this channel.", ephemeral=True
            )

    @app_commands.command(name="timer-pause", description="Pause your active timer")
    async def pause_slash(self, interaction: discord.Interaction):
        """Slash command version of pause"""
        if not interaction.channel:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        timer_id = f"{interaction.user.id}_{interaction.channel.id}"

        if timer_id in self.l and self.l[timer_id] == 0:
            self.l[timer_id] = 2
            await interaction.response.send_message(
                f"⏸️ Timer paused by {interaction.user.mention}!"
            )
        elif timer_id in self.l and self.l[timer_id] == 2:
            await interaction.response.send_message(
                "⏸️ Your timer is already paused.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ You don't have an active timer in this channel.", ephemeral=True
            )

    @app_commands.command(name="timer-resume", description="Resume your paused timer")
    async def resume_slash(self, interaction: discord.Interaction):
        """Slash command version of resume"""
        if not interaction.channel:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        timer_id = f"{interaction.user.id}_{interaction.channel.id}"

        if timer_id in self.l and self.l[timer_id] == 2:
            self.l[timer_id] = 0
            await interaction.response.send_message(
                f"▶️ Timer resumed by {interaction.user.mention}!"
            )
        elif timer_id in self.l and self.l[timer_id] == 0:
            await interaction.response.send_message(
                "⏸️ Your timer is already running.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ You don't have a paused timer in this channel.", ephemeral=True
            )

    @app_commands.command(
        name="reset-timers", description="Clear all active timers (Admin only)"
    )
    async def resettimers_slash(self, interaction: discord.Interaction):
        """Slash command version of resettimers"""
        # Check permissions properly for different member types
        has_permission = False
        if interaction.guild and interaction.user:
            member = interaction.guild.get_member(interaction.user.id)
            if member and hasattr(member, "guild_permissions"):
                has_permission = member.guild_permissions.manage_messages

        if not has_permission:
            await interaction.response.send_message(
                "❌ You need `Manage Messages` permission to use this command.",
                ephemeral=True,
            )
            return

        count = len(self.l)
        self.l.clear()
        self.active_timers.clear()

        await interaction.response.send_message(f"🧹 Cleared {count} active timers.")


async def setup(bot):
    """Set up the Timer cog."""
    await bot.add_cog(Timer(bot))
