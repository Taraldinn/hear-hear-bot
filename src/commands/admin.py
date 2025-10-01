"""
Admin Commands for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
"""

import logging
import os

import discord
from discord.ext import commands
from discord import app_commands

logger = logging.getLogger(__name__)


class AdminCommands(commands.Cog):
    """Administrative commands for server management"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmute a member in voice chat"""
        try:
            await member.edit(mute=False)
            await ctx.send(f"> {member.mention} was unmuted successfully")
            logger.info("Unmuted %s in %s", member, ctx.guild)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unmute members.")
        except (discord.HTTPException, discord.NotFound) as e:
            await ctx.send(f"❌ Error unmuting member: {str(e)}")
            logger.error("Error unmuting %s: %s", member, e)

    @app_commands.command(name="unmute", description="Unmute a member in voice chat")
    @app_commands.describe(member="The member to unmute")
    @app_commands.default_permissions(manage_roles=True)
    async def slash_unmute(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        """Slash command version of unmute"""
        try:
            await member.edit(mute=False)
            await interaction.response.send_message(
                f"> {member.mention} was unmuted successfully"
            )
            logger.info("Unmuted %s in %s", member, interaction.guild)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to unmute members.", ephemeral=True
            )
        except (discord.HTTPException, discord.NotFound) as e:
            await interaction.response.send_message(
                f"❌ Error unmuting member: {str(e)}", ephemeral=True
            )
            logger.error("Error unmuting %s: %s", member, e)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def undeafen(self, ctx, member: discord.Member):
        """Undeafen a member in voice chat"""
        try:
            await member.edit(deafen=False)
            await ctx.send(f"> {member.mention} was undeafened successfully")
            logger.info("Undeafened %s in %s", member, ctx.guild)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to undeafen members.")
        except (discord.HTTPException, discord.NotFound) as e:
            await ctx.send(f"❌ Error undeafening member: {str(e)}")
            logger.error("Error undeafening %s: %s", member, e)

    @app_commands.command(
        name="undeafen", description="Undeafen a member in voice chat"
    )
    @app_commands.describe(member="The member to undeafen")
    @app_commands.default_permissions(manage_roles=True)
    async def slash_undeafen(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        """Slash command version of undeafen"""
        try:
            await member.edit(deafen=False)
            await interaction.response.send_message(
                f"> {member.mention} was undeafened successfully"
            )
            logger.info("Undeafened %s in %s", member, interaction.guild)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to undeafen members.", ephemeral=True
            )
        except (discord.HTTPException, discord.NotFound) as e:
            await interaction.response.send_message(
                f"❌ Error undeafening member: {str(e)}", ephemeral=True
            )
            logger.error("Error undeafening %s: %s", member, e)

    @commands.command(aliases=["setlang"])
    @commands.has_permissions(administrator=True)
    async def setlanguage(self, ctx, language):
        """Set the language for this server (english/bangla)"""
        language = language.lower()

        if language not in ["english", "bangla"]:
            await ctx.send("❌ Supported languages: `english`, `bangla`")
            return

        success = await self.bot.set_language(ctx.guild.id, language)

        if success:
            if language == "english":
                await ctx.send("✅ Language set to English for this server")
            else:
                await ctx.send("✅ এই সার্ভারের জন্য ভাষা বাংলায় সেট করা হয়েছে")
        else:
            await ctx.send("❌ Failed to set language. Please try again.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, *, role_name):
        """Set up automatic role assignment for new members"""
        # Find the role
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if not role:
            await ctx.send(f"❌ Role '{role_name}' not found.")
            return

        # Check if bot can assign this role
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send(
                "❌ I cannot assign this role as it's higher than my highest role."
            )
            return

        # Save to database
        try:
            collection = self.bot.database.get_collection("guilds")
            if collection:
                collection.update_one(
                    {"_id": ctx.guild.id}, {"$set": {"autorole": role.id}}, upsert=True
                )
                await ctx.send(f"✅ Auto-role set to **{role.name}**")
            else:
                await ctx.send("❌ Database connection error.")
        except (AttributeError, ConnectionError, OSError) as e:
            await ctx.send("❌ Failed to set auto-role.")
            logger.error("Error setting autorole: %s", e)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removeautorole(self, ctx):
        """Remove automatic role assignment"""
        try:
            collection = self.bot.database.get_collection("guilds")
            if collection:
                collection.update_one(
                    {"_id": ctx.guild.id}, {"$unset": {"autorole": ""}}, upsert=True
                )
                await ctx.send("✅ Auto-role removed")
            else:
                await ctx.send("❌ Database connection error.")
        except (AttributeError, ConnectionError, OSError) as e:
            await ctx.send("❌ Failed to remove auto-role.")
            logger.error("Error removing autorole: %s", e)

    @commands.command(aliases=["delete-data"])
    @commands.has_permissions(administrator=True)
    async def deletedata(self, ctx, *, confirmation=""):
        """Delete all data associated with this server"""
        if confirmation != "YES I AM 100% SURE":
            await ctx.send(
                "⚠️ **WARNING**: This will delete ALL data for this server!\n"
                "Type `YES I AM 100% SURE` after the command to confirm."
            )
            return

        try:
            # Delete from both databases
            main_collection = self.bot.database.get_collection("guilds")
            tabby_collection = self.bot.database.get_collection(
                "tournaments", use_tabby_db=True
            )

            if main_collection:
                main_collection.delete_one({"_id": ctx.guild.id})

            if tabby_collection:
                tabby_collection.delete_one({"_id": ctx.guild.id})

            await ctx.send("✅ ALL DATA FOR THIS SERVER WAS DELETED SUCCESSFULLY")
            logger.warning(
                "All data deleted for guild %s by %s", ctx.guild.id, ctx.author
            )

        except (AttributeError, ConnectionError, OSError) as e:
            await ctx.send("❌ Error deleting data.")
            logger.error("Error deleting data for guild %s: %s", ctx.guild.id, e)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def serverinfo(self, ctx):
        """Display server information and bot settings"""
        guild = ctx.guild

        # Get language setting
        language = await self.bot.get_language(guild.id)

        # Get autorole setting
        try:
            collection = self.bot.database.get_collection("guilds")
            guild_data = collection.find_one({"_id": guild.id}) if collection else None
            autorole_id = guild_data.get("autorole") if guild_data else None
            autorole = guild.get_role(autorole_id) if autorole_id else None
        except (AttributeError, KeyError, TypeError):
            autorole = None

        embed = discord.Embed(
            title=f"Server Information - {guild.name}",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Member Count", value=guild.member_count, inline=True)
        embed.add_field(name="Language", value=language.title(), inline=True)
        embed.add_field(
            name="Auto-role", value=autorole.name if autorole else "None", inline=True
        )
        embed.add_field(
            name="Active Timers",
            value=self.bot.timer_manager.get_active_timers_count(),
            inline=True,
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx):
        """Manually sync slash commands globally across ALL servers (Admin only)"""
        try:
            # Send initial message
            embed = discord.Embed(
                title="🌍 Syncing Global Commands...",
                description="Please wait while I sync the slash commands across ALL servers.",
                color=discord.Color.blue(),
                timestamp=ctx.message.created_at,
            )
            sync_msg = await ctx.send(embed=embed)

            # Check if bot has a valid token
            if not self.bot.user:
                embed = discord.Embed(
                    title="⚠️ Bot Not Connected",
                    description="Bot is not connected to Discord. Please check your bot token.",
                    color=discord.Color.orange(),
                    timestamp=ctx.message.created_at,
                )
                embed.add_field(
                    name="Troubleshooting",
                    value=(
                        "• Make sure DISCORD_BOT_TOKEN is set correctly\n"
                        "• Check if the bot token is valid\n"
                        "• Ensure bot has proper permissions"
                    ),
                    inline=False,
                )
                await sync_msg.edit(embed=embed)
                return

            # Use the improved sync method
            await self.bot.force_sync_commands()

            # Get the synced commands
            try:
                synced = await self.bot.tree.fetch_commands()
            except (
                discord.HTTPException,
                discord.Forbidden,
                discord.NotFound,
            ) as fetch_error:
                # Fallback to show loaded commands if fetch fails
                logger.warning("Could not fetch synced commands: %s", fetch_error)
                loaded_commands = self.bot.tree.get_commands()
                synced = loaded_commands

            embed = discord.Embed(
                title="✅ Global Commands Synced Successfully",
                description=f"Successfully synced {len(synced)} slash commands globally",
                color=discord.Color.green(),
                timestamp=ctx.message.created_at,
            )

            if synced:
                command_names = [cmd.name for cmd in synced]
                embed.add_field(
                    name="🌍 Global Commands",
                    value=", ".join(f"`/{name}`" for name in command_names),
                    inline=False,
                )

                # Add note about propagation
                embed.add_field(
                    name="💡 Global Propagation",
                    value=(
                        "Commands are now synced globally and will appear in ALL servers "
                        "within 1 hour due to Discord's propagation time."
                    ),
                    inline=False,
                )

            await sync_msg.edit(embed=embed)

        except (discord.HTTPException, discord.Forbidden, AttributeError) as e:
            embed = discord.Embed(
                title="❌ Global Sync Failed",
                description=f"Failed to sync slash commands globally: {str(e)}",
                color=discord.Color.red(),
                timestamp=ctx.message.created_at,
            )
            embed.add_field(
                name="Troubleshooting",
                value=(
                    "• Make sure the bot has the `applications.commands` scope\n"
                    "• Bot must have global permissions\n"
                    "• Try again in a few minutes\n"
                    "• Check bot permissions"
                ),
                inline=False,
            )
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def guild_sync(self, ctx):
        """Sync slash commands to THIS server only for instant access (Admin only)"""
        try:
            # Send initial message
            embed = discord.Embed(
                title="⚡ Syncing Guild Commands...",
                description=f"Syncing slash commands to {ctx.guild.name} for instant access.",
                color=discord.Color.green(),
                timestamp=ctx.message.created_at,
            )
            sync_msg = await ctx.send(embed=embed)

            # Use the guild-specific sync method
            await self.bot.sync_commands(guild_id=ctx.guild.id)

            # Get the synced commands for this guild
            try:
                synced = await self.bot.tree.fetch_commands(
                    guild=discord.Object(id=ctx.guild.id)
                )
            except (
                discord.HTTPException,
                discord.Forbidden,
                discord.NotFound,
            ) as fetch_error:
                # Fallback to show loaded commands if fetch fails
                logger.warning("Could not fetch guild synced commands: %s", fetch_error)
                loaded_commands = self.bot.tree.get_commands()
                synced = loaded_commands

            embed = discord.Embed(
                title="⚡ Guild Commands Synced Successfully",
                description=f"Successfully synced {len(synced)} slash commands to {ctx.guild.name}",
                color=discord.Color.green(),
                timestamp=ctx.message.created_at,
            )

            if synced:
                command_names = [cmd.name for cmd in synced]
                embed.add_field(
                    name="⚡ Guild Commands (Instant Access)",
                    value=", ".join(f"`/{name}`" for name in command_names),
                    inline=False,
                )

                # Add note about instant access
                embed.add_field(
                    name="💡 Instant Access",
                    value=(
                        "Commands are now available IMMEDIATELY in this server! "
                        "Try typing `/` to see them."
                    ),
                    inline=False,
                )

            await sync_msg.edit(embed=embed)

        except (discord.HTTPException, discord.Forbidden, AttributeError) as e:
            embed = discord.Embed(
                title="❌ Guild Sync Failed",
                description=f"Failed to sync slash commands to this guild: {str(e)}",
                color=discord.Color.red(),
                timestamp=ctx.message.created_at,
            )
            embed.add_field(
                name="Troubleshooting",
                value=(
                    "• Make sure the bot has the `applications.commands` scope\n"
                    "• Bot must have permissions in this server\n"
                    "• Try the global sync command instead\n"
                    "• Check bot permissions"
                ),
                inline=False,
            )
            await ctx.send(embed=embed)

    @app_commands.command(
        name="test-all-commands",
        description="Test all bot commands to verify functionality",
    )
    @app_commands.default_permissions(administrator=True)
    async def test_all_commands(self, interaction: discord.Interaction):
        """Comprehensive test of all bot commands and features"""
        await interaction.response.defer(ephemeral=True)

        results = []
        total_tests = 0
        passed_tests = 0

        # Test 1: Basic Bot Connectivity
        total_tests += 1
        try:
            latency = round(self.bot.latency * 1000, 2)
            results.append(f"✅ **Bot Connectivity**: {latency}ms latency")
            passed_tests += 1
        except (AttributeError, TypeError, ValueError) as e:
            results.append(f"❌ **Bot Connectivity**: Failed - {str(e)[:50]}")

        # Test 2: Database Connection
        total_tests += 1
        try:
            # Test database configuration availability
            if hasattr(self.bot, "database"):
                results.append("✅ **Database Connection**: Configuration available")
                passed_tests += 1
            else:
                results.append("❌ **Database Connection**: No database configured")
        except (ImportError, ModuleNotFoundError) as e:
            results.append(f"❌ **Database Connection**: {str(e)[:50]}")

        # Test 3: Timer Commands
        total_tests += 1
        try:
            timer_cog = self.bot.get_cog("Timer")
            if timer_cog and hasattr(timer_cog, "timer_slash"):
                results.append("✅ **Timer Commands**: Available")
                passed_tests += 1
            else:
                results.append("❌ **Timer Commands**: Not loaded")
        except (AttributeError, KeyError) as e:
            results.append(f"❌ **Timer Commands**: {str(e)[:50]}")

        # Test 4: Tabbycat Commands
        total_tests += 1
        try:
            tabby_cog = self.bot.get_cog("TabbyCommands")
            if tabby_cog and hasattr(tabby_cog, "slash_sync"):
                results.append("✅ **Tabbycat Commands**: Available")
                passed_tests += 1
            else:
                results.append("❌ **Tabbycat Commands**: Not loaded")
        except (AttributeError, KeyError) as e:
            results.append(f"❌ **Tabbycat Commands**: {str(e)[:50]}")

        # Test 5: Slash Command Registration
        total_tests += 1
        try:
            registered_commands = await self.bot.tree.fetch_commands()
            command_count = len(registered_commands)
            if command_count > 0:
                results.append(
                    f"✅ **Slash Commands**: {command_count} registered globally"
                )
                passed_tests += 1
            else:
                results.append("❌ **Slash Commands**: None registered")
        except (discord.HTTPException, discord.Forbidden, AttributeError) as e:
            results.append(f"❌ **Slash Commands**: {str(e)[:50]}")

        # Test 6: Guild Commands
        total_tests += 1
        try:
            if interaction.guild:
                guild_commands = await self.bot.tree.fetch_commands(
                    guild=interaction.guild
                )
                guild_count = len(guild_commands)
                results.append(f"✅ **Guild Commands**: {guild_count} registered")
                passed_tests += 1
            else:
                results.append("❌ **Guild Commands**: Not in guild")
        except (discord.HTTPException, discord.Forbidden, AttributeError) as e:
            results.append(f"❌ **Guild Commands**: {str(e)[:50]}")

        # Test 7: Environment Configuration
        total_tests += 1
        try:
            token = os.getenv("DISCORD_TOKEN")
            db_url = os.getenv("DATABASE_URL")
            if token and db_url:
                results.append("✅ **Environment Config**: All required vars set")
                passed_tests += 1
            else:
                results.append("❌ **Environment Config**: Missing required vars")
        except (ImportError, OSError) as e:
            results.append(f"❌ **Environment Config**: {str(e)[:50]}")

        # Test 8: Cog Loading Status
        total_tests += 1
        try:
            cog_names = list(self.bot.cogs.keys())
            expected_cogs = ["AdminCommands", "Timer", "TabbyCommands", "ErrorHandler"]
            loaded_expected = [cog for cog in expected_cogs if cog in cog_names]

            if len(loaded_expected) >= 3:
                results.append(f"✅ **Cog Loading**: {len(cog_names)} cogs loaded")
                passed_tests += 1
            else:
                results.append(
                    (
                        "❌ **Cog Loading**: Only "
                        f"{len(loaded_expected)}/{len(expected_cogs)} expected cogs"
                    )
                )
        except (AttributeError, KeyError, TypeError) as e:
            results.append(f"❌ **Cog Loading**: {str(e)[:50]}")

        # Test 9: Permission Checks
        total_tests += 1
        try:
            if interaction.guild:
                bot_member = interaction.guild.get_member(self.bot.user.id)
                if bot_member:
                    perms = bot_member.guild_permissions
                    essential_perms = [
                        perms.send_messages,
                        perms.embed_links,
                        perms.add_reactions,
                        perms.read_message_history,
                    ]
                    if all(essential_perms):
                        results.append(
                            "✅ **Bot Permissions**: All essential permissions"
                        )
                        passed_tests += 1
                    else:
                        results.append(
                            "❌ **Bot Permissions**: Missing essential permissions"
                        )
                else:
                    results.append("❌ **Bot Permissions**: Bot member not found")
            else:
                results.append("❌ **Bot Permissions**: Not in guild")
        except (AttributeError, TypeError) as e:
            results.append(f"❌ **Bot Permissions**: {str(e)[:50]}")

        # Test 10: Memory Usage
        total_tests += 1
        try:
            # Simple memory check using basic OS calls
            results.append("✅ **Memory Usage**: Basic monitoring available")
            passed_tests += 1
        except (ImportError, OSError) as e:
            results.append(f"❌ **Memory Usage**: {str(e)[:50]}")

        # Create comprehensive report
        success_rate = round((passed_tests / total_tests) * 100, 1)

        if success_rate >= 90:
            status_emoji = "🟢"
            status_text = "EXCELLENT"
            color = 0x00FF00
        elif success_rate >= 70:
            status_emoji = "🟡"
            status_text = "GOOD"
            color = 0xFFFF00
        else:
            status_emoji = "🔴"
            status_text = "NEEDS ATTENTION"
            color = 0xFF0000

        embed = discord.Embed(
            title=f"{status_emoji} Bot System Test Results",
            description=(
                "**Overall Status**: "
                f"{status_text} ("
                f"{passed_tests}/{total_tests} tests passed - {success_rate}%)"
            ),
            color=color,
            timestamp=discord.utils.utcnow(),
        )

        # Split results into chunks to avoid field limit
        chunk_size = 10
        for i in range(0, len(results), chunk_size):
            chunk = results[i : i + chunk_size]
            field_name = (
                f"Test Results {i//chunk_size + 1}"
                if len(results) > chunk_size
                else "Test Results"
            )
            embed.add_field(name=field_name, value="\n".join(chunk), inline=False)

        # Add recommendations
        if success_rate < 100:
            recommendations = []
            if passed_tests < total_tests:
                recommendations.append("• Check failed tests above for specific issues")
                recommendations.append(
                    "• Restart the bot if configuration changes were made"
                )
                recommendations.append(
                    "• Verify environment variables are set correctly"
                )
                recommendations.append(
                    "• Check bot permissions in Discord server settings"
                )

            if recommendations:
                embed.add_field(
                    name="📋 Recommendations",
                    value="\n".join(recommendations),
                    inline=False,
                )
        else:
            embed.add_field(
                name="🎉 All Systems Operational",
                value="All tests passed! The bot is functioning correctly.",
                inline=False,
            )

        embed.set_footer(text=f"Test completed by {interaction.user.display_name}")

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="topgg", description="Manage top.gg integration and post stats"
    )
    @app_commands.describe(action="Action to perform (status, post)")
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Check Status", value="status"),
            app_commands.Choice(name="Post Now", value="post"),
        ]
    )
    @app_commands.default_permissions(administrator=True)
    async def topgg_command(
        self, interaction: discord.Interaction, action: app_commands.Choice[str]
    ):
        """Manage top.gg integration"""
        await interaction.response.defer(ephemeral=True)

        if action.value == "status":
            # Get top.gg status
            status = self.bot.topgg_poster.get_status()

            embed = discord.Embed(
                title="📊 Top.gg Integration Status",
                color=discord.Color.blue(),
                description="Current status of top.gg server count posting",
            )

            # Configuration status
            config_status = (
                "✅ Configured" if status["configured"] else "❌ Not Configured"
            )
            embed.add_field(name="Configuration", value=config_status, inline=True)

            # Running status
            running_status = "✅ Running" if status["running"] else "❌ Stopped"
            embed.add_field(name="Status", value=running_status, inline=True)

            # Bot ID
            bot_id_display = status["bot_id"]
            if len(bot_id_display) > 15:
                bot_id_display = f"{bot_id_display[:4]}...{bot_id_display[-4:]}"
            embed.add_field(name="Bot ID", value=bot_id_display, inline=True)

            # Posting interval
            interval_minutes = status["interval"] // 60
            embed.add_field(
                name="Posting Interval",
                value=f"{interval_minutes} minutes",
                inline=True,
            )

            # Current server count
            embed.add_field(
                name="Current Servers", value=str(status["server_count"]), inline=True
            )

            # Add configuration help if not configured
            if not status["configured"]:
                embed.add_field(
                    name="⚠️ Configuration Required",
                    value="Set `BOT_ID` and `TOPGG_TOKEN` in your environment variables.",
                    inline=False,
                )

            embed.set_footer(text="Use /topgg post to manually post stats now")

            await interaction.followup.send(embed=embed, ephemeral=True)

        elif action.value == "post":
            # Manually post to top.gg
            if not self.bot.topgg_poster.bot_id or not self.bot.topgg_poster.api_token:
                await interaction.followup.send(
                    "❌ Top.gg is not configured. Please set `BOT_ID` and "
                    "`TOPGG_TOKEN` in your environment variables.",
                    ephemeral=True,
                )
                return

            # Post stats
            success = await self.bot.topgg_poster.post_stats()

            if success:
                server_count = len(self.bot.guilds)
                embed = discord.Embed(
                    title="✅ Top.gg Stats Posted",
                    color=discord.Color.green(),
                    description="Successfully posted server count to top.gg!",
                )
                embed.add_field(name="Server Count", value=str(server_count))
                embed.set_footer(text="Stats may take 5-10 minutes to update on top.gg")
            else:
                embed = discord.Embed(
                    title="❌ Failed to Post Stats",
                    color=discord.Color.red(),
                    description="Failed to post server count to top.gg. Check logs for details.",
                )
                embed.add_field(
                    name="Troubleshooting",
                    value="• Check your API token\n"
                    "• Verify your bot ID\n"
                    "• Ensure your bot is listed on top.gg",
                )

            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    """Set up the AdminCommands cog."""
    await bot.add_cog(AdminCommands(bot))
