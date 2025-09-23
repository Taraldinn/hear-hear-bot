"""
Tournament Setup System for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com

Creates tournament venues, roles, and channels for debate tournaments
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional, Literal

import discord
from discord import app_commands
from discord.ext import commands
from .tournament_views import TournamentRoleView
from .tournament_service import (
    create_tournament_roles,
    create_general_channels,
    create_venue_channels,
    setup_permissions,
    setup_role_assignment as setup_role_assignment_service,
)

logger = logging.getLogger(__name__)


class TournamentSetup(commands.Cog):
    """Tournament venue and role creation system"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="create_tournament",
        description="Create tournament venues and channels for debate competition",
    )
    @app_commands.describe(
        tournament_type=(
            "Type of debate format "
            "(AP = Asian Parliamentary, BP = British Parliamentary)"
        ),
        venues="Number of venues to create (1-20)",
        setup_roles="Whether to create tournament roles (Debater, Adjudicator, Spectator)",
        setup_role_assignment="Whether to setup role assignment channel with reactions",
    )
    @app_commands.choices(
        tournament_type=[
            app_commands.Choice(name="Asian Parliamentary (AP)", value="AP"),
            app_commands.Choice(name="British Parliamentary (BP)", value="BP"),
        ]
    )
    @app_commands.default_permissions(administrator=True)
    async def create_tournament(
        self,
        interaction: discord.Interaction,
        tournament_type: Literal["AP", "BP"],
        venues: int,
        setup_roles: bool = True,
        setup_role_assignment: bool = True,
    ):
        """Create tournament setup with venues, roles, and channels"""

        if not 1 <= venues <= 20:
            await interaction.response.send_message(
                "❌ Number of venues must be between 1 and 20!", ephemeral=True
            )
            return

        # Check bot permissions BEFORE starting
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server!", ephemeral=True
            )
            return

        bot_member = guild.get_member(self.bot.user.id)
        if not bot_member:
            await interaction.response.send_message(
                "❌ Bot member not found in server!", ephemeral=True
            )
            return

        # Required permissions for tournament setup
        required_permissions = [
            ("manage_channels", "Manage Channels"),
            ("manage_roles", "Manage Roles"),
            ("manage_permissions", "Manage Permissions"),
            ("send_messages", "Send Messages"),
            ("add_reactions", "Add Reactions"),
            ("read_message_history", "Read Message History"),
        ]

        missing_permissions = []
        for perm_attr, perm_name in required_permissions:
            if not getattr(bot_member.guild_permissions, perm_attr):
                missing_permissions.append(perm_name)

        if missing_permissions:
            # Create detailed permission error embed
            embed = discord.Embed(
                title="❌ Missing Required Permissions",
                description="I need the following permissions to create a tournament setup:",
                color=discord.Color.red(),
            )

            embed.add_field(
                name="🚫 Missing Permissions",
                value="\n".join([f"• {perm}" for perm in missing_permissions]),
                inline=False,
            )

            embed.add_field(
                name="🔧 How to Fix This",
                value=(
                    "**Option 1: Give Administrator Permission (Recommended)**\n"
                    "1. Go to **Server Settings** → **Roles**\n"
                    "2. Find my role (Hear! Hear! Bot)\n"
                    "3. Enable **Administrator** permission\n\n"
                    "**Option 2: Give Specific Permissions**\n"
                    "1. Go to **Server Settings** → **Roles**\n"
                    "2. Find my role and enable the missing permissions above\n"
                    "3. Make sure my role is **above** other roles in the hierarchy"
                ),
                inline=False,
            )

            embed.add_field(
                name="⚠️ Important Notes",
                value=(
                    "• My role must be **higher** than the roles I need to create\n"
                    "• I need these permissions in **all categories** I'll create\n"
                    "• Re-run this command after fixing permissions"
                ),
                inline=False,
            )

            embed.set_footer(
                text="Contact an administrator if you need help with permissions"
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        # Track progress message for updates
        progress_msg: Optional[discord.Message] = None

        try:
            embed = discord.Embed(
                title="🏆 Creating Tournament Setup",
                description=f"Setting up {tournament_type} tournament with {venues} venues...",
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )

            progress_msg = await interaction.followup.send(embed=embed)

            # Step 1: Create roles if requested
            roles: Dict[str, discord.Role] = {}
            if setup_roles:
                embed = discord.Embed(
                    title="🏆 Creating Tournament Setup",
                    description=f"Setting up {tournament_type} tournament with {venues} venues...",
                    color=discord.Color.blue(),
                    timestamp=datetime.now(),
                )
                embed.add_field(
                    name="📝 Step 1/5",
                    value="Creating tournament roles...",
                    inline=False,
                )
                if progress_msg:
                    await progress_msg.edit(embed=embed)  # type: ignore[misc]
                roles = await create_tournament_roles(guild)

            # Step 2: Create general tournament channels
            embed = discord.Embed(
                title="🏆 Creating Tournament Setup",
                description=f"Setting up {tournament_type} tournament with {venues} venues...",
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )
            embed.add_field(
                name="📁 Step 2/5", value="Creating general channels...", inline=False
            )
            if progress_msg:
                await progress_msg.edit(embed=embed)  # type: ignore[misc]
            general_channels = await create_general_channels(guild, roles)

            # Step 3: Create venue channels
            embed = discord.Embed(
                title="🏆 Creating Tournament Setup",
                description=f"Setting up {tournament_type} tournament with {venues} venues...",
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )
            embed.add_field(
                name="🏟️ Step 3/5", value=f"Creating {venues} venues...", inline=False
            )
            if progress_msg:
                await progress_msg.edit(embed=embed)  # type: ignore[misc]
            venue_channels = await create_venue_channels(
                guild, tournament_type, venues, roles
            )

            # Step 4: Setup permissions
            embed = discord.Embed(
                title="🏆 Creating Tournament Setup",
                description=f"Setting up {tournament_type} tournament with {venues} venues...",
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )
            embed.add_field(
                name="🔒 Step 4/5", value="Configuring permissions...", inline=False
            )
            if progress_msg:
                await progress_msg.edit(embed=embed)  # type: ignore[misc]
            await setup_permissions(guild, roles, general_channels, venue_channels)

            # Step 5: Setup role assignment if requested
            role_assignment_msg = None
            if setup_role_assignment and setup_roles:
                embed = discord.Embed(
                    title="🏆 Creating Tournament Setup",
                    description=f"Setting up {tournament_type} tournament with {venues} venues...",
                    color=discord.Color.blue(),
                    timestamp=datetime.now(),
                )
                embed.add_field(
                    name="🎭 Step 5/5",
                    value="Setting up role assignment...",
                    inline=False,
                )
                if progress_msg:
                    await progress_msg.edit(embed=embed)  # type: ignore[misc]
                role_assignment_msg = await setup_role_assignment_service(
                    guild, roles, general_channels
                )

            # Final success message
            success_embed = discord.Embed(
                title="✅ Tournament Setup Complete!",
                description=(
                    f"Successfully created {tournament_type} tournament "
                    f"with {venues} venues"
                ),
                color=discord.Color.green(),
                timestamp=datetime.now(),
            )

            # Build role mentions safely
            role_mentions = []
            if roles.get("debater"):
                role_mentions.append(f"• {roles['debater'].mention}")
            else:
                role_mentions.append("• Debater: Not created")

            if roles.get("adjudicator"):
                role_mentions.append(f"• {roles['adjudicator'].mention}")
            else:
                role_mentions.append("• Adjudicator: Not created")

            if roles.get("spectator"):
                role_mentions.append(f"• {roles['spectator'].mention}")
            else:
                role_mentions.append("• Spectator: Not created")

            success_embed.add_field(
                name="🎭 Roles Created",
                value="\n".join(role_mentions),
                inline=True,
            )

            success_embed.add_field(
                name="🏟️ Venues Created",
                value=f"{venues} venues with {tournament_type} format",
                inline=True,
            )

            if role_assignment_msg:
                success_embed.add_field(
                    name="📋 Role Assignment",
                    value=(
                        f"Check {general_channels.get('role_assignment', '#role-assignment')} "
                        "to get your role!"
                    ),
                    inline=False,
                )

            success_embed.set_footer(
                text="Tournament is ready! Good luck to all participants!"
            )

            if progress_msg:
                # Some type checkers think edit might return Never; it's awaitable in runtime
                await progress_msg.edit(embed=success_embed)  # type: ignore[misc]

        except discord.Forbidden as e:
            logger.error("Permission error during tournament setup: %s", e)

            # Create detailed permission error embed
            error_embed = discord.Embed(
                title="❌ Permission Error During Setup",
                description="I lost permissions while creating the tournament. This can happen if:",
                color=discord.Color.red(),
            )

            error_embed.add_field(
                name="🚫 Common Causes",
                value=(
                    "• My role was moved below other roles during setup\n"
                    "• Permissions were changed while I was working\n"
                    "• Channel category permissions conflict with my role\n"
                    "• I reached Discord's rate limits"
                ),
                inline=False,
            )

            error_embed.add_field(
                name="🔧 How to Fix This",
                value=(
                    "1. **Move my role to the TOP** of the role hierarchy\n"
                    "2. Give me **Administrator** permission (recommended)\n"
                    "3. Use `/tournament_cleanup confirmation:DELETE` to remove partial setup\n"
                    "4. Try the tournament setup command again\n"
                    "5. Create fewer venues at once if the problem persists"
                ),
                inline=False,
            )

            error_embed.add_field(
                name="📋 Technical Details",
                value=f"```Discord Error: {str(e)[:200]}```",
                inline=False,
            )

            try:
                await interaction.edit_original_response(embed=error_embed)
            except discord.HTTPException:
                await interaction.followup.send(embed=error_embed, ephemeral=True)

        except discord.HTTPException as e:
            logger.error("Discord API error during tournament setup: %s", e)

            error_embed = discord.Embed(
                title="❌ Discord API Error",
                description="A Discord API error occurred during tournament setup.",
                color=discord.Color.red(),
            )

            if "rate limited" in str(e).lower():
                error_embed.add_field(
                    name="🚦 Rate Limited",
                    value=(
                        "Discord is rate limiting the bot due to too many requests.\n"
                        "**Solution:** Wait a few minutes and try again with fewer venues."
                    ),
                    inline=False,
                )
            else:
                error_embed.add_field(
                    name="🔧 Possible Solutions",
                    value=(
                        "1. Try again with fewer venues\n"
                        "2. Check if Discord is experiencing issues\n"
                        "3. Wait a few minutes before retrying\n"
                        "4. Use `/tournament_cleanup` if partially created"
                    ),
                    inline=False,
                )

            error_embed.add_field(
                name="📋 Technical Details", value=f"```{str(e)[:500]}```", inline=False
            )

            try:
                await interaction.edit_original_response(embed=error_embed)
            except discord.HTTPException:
                await interaction.followup.send(embed=error_embed, ephemeral=True)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to create tournament: %s", e)
            error_embed = discord.Embed(
                title="❌ Tournament Setup Failed",
                description=f"Error: {str(e)}",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

            # progress messages
            if progress_msg:
                await progress_msg.edit(embed=embed)  # type: ignore[misc]

    @app_commands.command(
        name="tournament_cleanup", description="Clean up tournament channels and roles"
    )
    @app_commands.describe(
        confirm="Type 'DELETE' to confirm deletion of all tournament channels"
    )
    @app_commands.default_permissions(administrator=True)
    async def tournament_cleanup(self, interaction: discord.Interaction, confirm: str):
        """Clean up all tournament-related channels and categories"""

        if confirm.upper() != "DELETE":
            await interaction.response.send_message(
                "❌ Please type `DELETE` to confirm cleanup of tournament channels.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send(
                    "❌ This command can only be used in a server!", ephemeral=True
                )
                return

            deleted_count = 0

            # Categories to delete
            categories_to_delete = []
            for category in guild.categories:
                if category.name.startswith("Venue ") or category.name in [
                    "Welcome",
                    "Info Desk",
                    "Feedback & Check-in",
                    "Grand Auditorium",
                ]:
                    categories_to_delete.append(category)

            # Delete categories and their channels
            for category in categories_to_delete:
                for channel in category.channels:
                    await channel.delete(reason="Tournament cleanup")
                    deleted_count += 1
                    await asyncio.sleep(0.5)

                await category.delete(reason="Tournament cleanup")
                await asyncio.sleep(0.5)

            embed = discord.Embed(
                title="✅ Tournament Cleanup Complete",
                description=(
                    f"Deleted {deleted_count} channels and "
                    f"{len(categories_to_delete)} categories."
                ),
                color=discord.Color.green(),
            )

            embed.add_field(
                name="Note",
                value="Tournament roles (Debater, Adjudicator, Spectator) were preserved.\n"
                "You can delete them manually if needed.",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error during tournament cleanup: %s", e)
            await interaction.followup.send(
                f"❌ Error during cleanup: {str(e)}", ephemeral=True
            )


async def setup(bot):
    """Setup the tournament cog and persistent views."""
    # Add persistent views for tournament role assignment
    # This ensures buttons work even after bot restarts
    for guild in bot.guilds:
        # Create a basic view instance for each guild
        view = TournamentRoleView(guild.id)
        bot.add_view(view)

    await bot.add_cog(TournamentSetup(bot))
