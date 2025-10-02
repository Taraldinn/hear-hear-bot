"""
Advanced Moderation System for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Union
import uuid

import discord
from discord import app_commands
from discord.ext import commands, tasks

from src.database.connection import database
from src.database.models import COLLECTIONS, ModerationLog, StickyRole

logger = logging.getLogger(__name__)


class ModerationSystem(commands.Cog):
    """Advanced moderation system with Carl-bot features"""

    def __init__(self, bot):
        self.bot = bot
        self.db = database  # database is already the Database instance
        self.sticky_roles_cache = {}  # Cache sticky roles
        self.temp_actions = {}  # Track temporary actions
        self.check_temp_actions.start()  # Start the cleanup task

    async def cog_load(self):
        """Load moderation data on startup"""
        # Check if database supports MongoDB operations
        if not hasattr(self.db, "__getitem__"):
            logger.warning(
                "Moderation system disabled - requires MongoDB support. "
                "Current database is PostgreSQL. This feature needs migration."
            )
            return
        await self.load_sticky_roles()
        await self.load_temporary_actions()

    async def cog_unload(self):
        """Clean up when cog unloads"""
        self.check_temp_actions.cancel()

    async def load_sticky_roles(self):
        """Load sticky roles from database"""
        if not hasattr(self.db, "__getitem__"):
            return
        try:
            # pylint: disable=unsubscriptable-object
            collection = self.db[COLLECTIONS["sticky_roles"]]  # type: ignore[index]
            sticky_roles = await collection.find().to_list(length=None)
            # pylint: enable=unsubscriptable-object
            for role_data in sticky_roles:
                guild_id = role_data["guild_id"]
                user_id = role_data["user_id"]

                if guild_id not in self.sticky_roles_cache:
                    self.sticky_roles_cache[guild_id] = {}

                self.sticky_roles_cache[guild_id][user_id] = role_data["role_ids"]

            logger.info(
                "Loaded sticky roles for %d guilds", len(self.sticky_roles_cache)
            )
        except Exception as exc:
            logger.error("Failed to load sticky roles: %s", exc)

    async def load_temporary_actions(self):
        """Load temporary actions from database"""
        if not hasattr(self.db, "__getitem__"):
            return
        try:
            # pylint: disable=unsubscriptable-object
            collection = self.db[COLLECTIONS["temporary_roles"]]  # type: ignore[index]
            temp_roles = await collection.find().to_list(length=None)
            # pylint: enable=unsubscriptable-object
            for role_data in temp_roles:
                key = f"{role_data['guild_id']}_{role_data['user_id']}_{role_data['role_id']}"
                self.temp_actions[key] = {
                    "type": "role",
                    "expires_at": role_data["expires_at"],
                    "data": role_data,
                }

            logger.info("Loaded %d temporary actions", len(self.temp_actions))
        except Exception as exc:
            logger.error("Failed to load temporary actions: %s", exc)

    @tasks.loop(minutes=1)
    async def check_temp_actions(self):
        """Check and handle expired temporary actions"""
        now = datetime.utcnow()
        expired_actions = []

        for key, action in self.temp_actions.items():
            if action["expires_at"] <= now:
                expired_actions.append((key, action))

        for key, action in expired_actions:
            try:
                if action["type"] == "role":
                    await self.handle_expired_temp_role(action["data"])

                # Remove from cache and database
                del self.temp_actions[key]
                if hasattr(self.db, "__getitem__"):
                    # pylint: disable=unsubscriptable-object
                    collection = self.db[COLLECTIONS["temporary_roles"]]  # type: ignore[index]
                    await collection.delete_one(
                        {
                            "guild_id": action["data"]["guild_id"],
                            "user_id": action["data"]["user_id"],
                            "role_id": action["data"]["role_id"],
                        }
                    )
                    # pylint: enable=unsubscriptable-object

            except Exception as exc:
                logger.error("Failed to handle expired action %s: %s", key, exc)

    @check_temp_actions.before_loop
    async def before_check_temp_actions(self):
        """Wait for bot to be ready before starting the task"""
        await self.bot.wait_until_ready()

    async def handle_expired_temp_role(self, role_data: dict):
        """Handle expired temporary role"""
        try:
            guild = self.bot.get_guild(role_data["guild_id"])
            if not guild:
                return

            member = guild.get_member(role_data["user_id"])
            if not member:
                return

            role = guild.get_role(role_data["role_id"])
            if not role or role not in member.roles:
                return

            await member.remove_roles(role, reason="Temporary role expired")
            logger.info(
                "Removed expired temporary role %s from %s", role.name, member
            )

        except Exception as exc:
            logger.error("Failed to remove expired temporary role: %s", exc)

    async def log_moderation_action(
        self,
        guild_id: int,
        action: str,
        target_user: Union[discord.User, discord.Member],
        moderator: Union[discord.User, discord.Member],
        reason: Optional[str] = None,
        duration: Optional[int] = None,
    ):
        """Log a moderation action"""
        if reason is None:
            reason = "No reason provided"
        
        try:
            case_id = str(uuid.uuid4())[:8]

            mod_log = ModerationLog(
                guild_id=guild_id,
                user_id=target_user.id,
                moderator_id=moderator.id,
                action=action,
                reason=reason,
                duration=duration,
                expires_at=(
                    datetime.utcnow() + timedelta(seconds=duration)
                    if duration
                    else None
                ),
                case_id=case_id,
            )

            if hasattr(self.db, "__getitem__"):
                # pylint: disable=unsubscriptable-object
                collection = self.db[COLLECTIONS["moderation_logs"]]  # type: ignore[index]
                await collection.insert_one(mod_log.__dict__)
                # pylint: enable=unsubscriptable-object

            # Send to moderation log channel if configured
            # ... (implement modlog channel sending)

            return case_id

        except Exception as exc:
            logger.error("Failed to log moderation action: %s", exc)
            return None

    # Moderation Commands
    @app_commands.command(
        name="mute", description="Mute a member for a specified duration"
    )
    @app_commands.describe(
        member="Member to mute",
        duration="Duration (e.g., 10m, 1h, 1d)",
        reason="Reason for the mute",
    )
    @app_commands.default_permissions(moderate_members=True)
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: Optional[str] = None,
        reason: Optional[str] = "No reason provided",
    ):
        """Mute a member"""
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        if (
            member.top_role >= interaction.user.top_role  # type: ignore[union-attr]
            and interaction.user != interaction.guild.owner
        ):
            await interaction.response.send_message(
                "❌ You cannot mute someone with a role equal or higher than yours.",
                ephemeral=True,
            )
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "❌ I cannot mute someone with a role equal or higher than mine.",
                ephemeral=True,
            )
            return

        try:
            await interaction.response.defer()

            # Parse duration
            timeout_duration = None
            if duration:
                timeout_duration = self.parse_duration(duration)
                if not timeout_duration:
                    await interaction.followup.send(
                        "❌ Invalid duration format. Use formats like: 10m, 1h, 2d",
                        ephemeral=True,
                    )
                    return

            # Apply timeout
            if timeout_duration:
                until = datetime.utcnow() + timedelta(seconds=timeout_duration)
                await member.timeout(until, reason=reason)
            else:
                # Permanent mute using timeout for 28 days (max)
                until = datetime.utcnow() + timedelta(days=28)
                await member.timeout(until, reason=reason)
                timeout_duration = 28 * 24 * 60 * 60  # 28 days in seconds

            # Log the action
            case_id = await self.log_moderation_action(
                interaction.guild.id,
                "mute",
                member,
                interaction.user,
                reason,
                timeout_duration,
            )

            embed = discord.Embed(
                title="🔇 Member Muted",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow(),
            )

            embed.add_field(
                name="👤 Member", value=f"{member} ({member.id})", inline=True
            )

            embed.add_field(
                name="👮 Moderator",
                value=f"{interaction.user} ({interaction.user.id})",
                inline=True,
            )

            if timeout_duration:
                embed.add_field(
                    name="⏰ Duration",
                    value=self.format_duration(timeout_duration),
                    inline=True,
                )

                embed.add_field(
                    name="🕒 Expires",
                    value=f"<t:{int((datetime.utcnow() + timedelta(seconds=timeout_duration)).timestamp())}:R>",
                    inline=True,
                )

            embed.add_field(name="📝 Reason", value=reason, inline=False)

            if case_id:
                embed.set_footer(text=f"Case ID: {case_id}")

            await interaction.followup.send(embed=embed)

            # Try to DM the user
            try:
                dm_embed = discord.Embed(
                    title="🔇 You've been muted",
                    description=f"You've been muted in **{interaction.guild.name}**",
                    color=discord.Color.orange(),
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                if timeout_duration:
                    dm_embed.add_field(
                        name="Duration",
                        value=self.format_duration(timeout_duration),
                        inline=False,
                    )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to mute this member.", ephemeral=True
            )
        except Exception as exc:
            logger.error("Failed to mute member: %s", exc)
            await interaction.followup.send(
                f"❌ Failed to mute member: {str(exc)}", ephemeral=True
            )

    @app_commands.command(name="unmute", description="Unmute a member")
    @app_commands.describe(member="Member to unmute", reason="Reason for unmuting")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided",
    ):
        """Unmute a member"""
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        try:
            await interaction.response.defer()

            # Remove timeout
            await member.timeout(None, reason=reason)

            # Log the action
            case_id = await self.log_moderation_action(
                interaction.guild.id, "unmute", member, interaction.user, reason
            )

            embed = discord.Embed(
                title="🔊 Member Unmuted",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )

            embed.add_field(
                name="👤 Member", value=f"{member} ({member.id})", inline=True
            )

            embed.add_field(
                name="👮 Moderator",
                value=f"{interaction.user} ({interaction.user.id})",
                inline=True,
            )

            embed.add_field(name="📝 Reason", value=reason, inline=False)

            if case_id:
                embed.set_footer(text=f"Case ID: {case_id}")

            await interaction.followup.send(embed=embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to unmute this member.", ephemeral=True
            )
        except Exception as exc:
            logger.error("Failed to unmute member: %s", exc)
            await interaction.followup.send(
                f"❌ Failed to unmute member: {str(exc)}", ephemeral=True
            )

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for the kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided",
    ):
        """Kick a member"""
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        if (
            member.top_role >= interaction.user.top_role  # type: ignore[union-attr]
            and interaction.user != interaction.guild.owner
        ):
            await interaction.response.send_message(
                "❌ You cannot kick someone with a role equal or higher than yours.",
                ephemeral=True,
            )
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "❌ I cannot kick someone with a role equal or higher than mine.",
                ephemeral=True,
            )
            return

        try:
            await interaction.response.defer()

            # Save roles for potential sticky role restoration
            await self.save_sticky_roles(member)

            # Try to DM the user first
            try:
                dm_embed = discord.Embed(
                    title="👢 You've been kicked",
                    description=f"You've been kicked from **{interaction.guild.name}**",
                    color=discord.Color.red(),
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass

            # Kick the member
            await member.kick(reason=reason)

            # Log the action
            case_id = await self.log_moderation_action(
                interaction.guild.id, "kick", member, interaction.user, reason
            )

            embed = discord.Embed(
                title="👢 Member Kicked",
                color=discord.Color.red(),
                timestamp=datetime.utcnow(),
            )

            embed.add_field(
                name="👤 Member", value=f"{member} ({member.id})", inline=True
            )

            embed.add_field(
                name="👮 Moderator",
                value=f"{interaction.user} ({interaction.user.id})",
                inline=True,
            )

            embed.add_field(name="📝 Reason", value=reason, inline=False)

            if case_id:
                embed.set_footer(text=f"Case ID: {case_id}")

            await interaction.followup.send(embed=embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to kick this member.", ephemeral=True
            )
        except Exception as exc:
            logger.error("Failed to kick member: %s", exc)
            await interaction.followup.send(
                f"❌ Failed to kick member: {str(exc)}", ephemeral=True
            )

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(
        member="Member to ban",
        duration="Duration (e.g., 1h, 1d, 7d) - leave empty for permanent",
        delete_messages="Delete messages from the last X days (0-7)",
        reason="Reason for the ban",
    )
    @app_commands.default_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: Union[discord.Member, discord.User],
        duration: Optional[str] = None,
        delete_messages: Optional[int] = 0,
        reason: Optional[str] = "No reason provided",
    ):
        """Ban a member"""
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        if isinstance(member, discord.Member):
            if (
                member.top_role >= interaction.user.top_role  # type: ignore[union-attr]
                and interaction.user != interaction.guild.owner
            ):
                await interaction.response.send_message(
                    "❌ You cannot ban someone with a role equal or higher than yours.",
                    ephemeral=True,
                )
                return

            if member.top_role >= interaction.guild.me.top_role:
                await interaction.response.send_message(
                    "❌ I cannot ban someone with a role equal or higher than mine.",
                    ephemeral=True,
                )
                return

        # Validate delete_messages parameter
        delete_days = delete_messages if delete_messages is not None else 0
        if delete_days < 0 or delete_days > 7:
            await interaction.response.send_message(
                "❌ Delete messages value must be between 0 and 7 days.", ephemeral=True
            )
            return

        try:
            await interaction.response.defer()

            # Parse duration if provided
            ban_duration = None
            if duration:
                ban_duration = self.parse_duration(duration)
                if not ban_duration:
                    await interaction.followup.send(
                        "❌ Invalid duration format. Use formats like: 1h, 2d, 7d",
                        ephemeral=True,
                    )
                    return

            # Save roles for potential sticky role restoration
            if isinstance(member, discord.Member):
                await self.save_sticky_roles(member)

            # Try to DM the user first
            try:
                dm_embed = discord.Embed(
                    title="🔨 You've been banned",
                    description=f"You've been banned from **{interaction.guild.name}**",
                    color=discord.Color.red(),
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                if ban_duration:
                    dm_embed.add_field(
                        name="Duration",
                        value=self.format_duration(ban_duration),
                        inline=False,
                    )
                await member.send(embed=dm_embed)
            except (discord.Forbidden, AttributeError):
                pass

            # Ban the member (ensure delete_messages has a value)
            delete_days = delete_messages if delete_messages is not None else 0
            await interaction.guild.ban(
                member, reason=reason, delete_message_days=delete_days
            )

            # Schedule unban if temporary
            if ban_duration:
                # Add to temporary actions tracking
                key = f"{interaction.guild.id}_{member.id}_ban"
                self.temp_actions[key] = {
                    "type": "ban",
                    "expires_at": datetime.utcnow() + timedelta(seconds=ban_duration),
                    "data": {
                        "guild_id": interaction.guild.id,
                        "user_id": member.id,
                        "reason": f"Temporary ban expired (original reason: {reason})",
                    },
                }

            # Log the action
            case_id = await self.log_moderation_action(
                interaction.guild.id,
                "ban",
                member,
                interaction.user,
                reason,
                ban_duration,
            )

            embed = discord.Embed(
                title="🔨 Member Banned",
                color=discord.Color.red(),
                timestamp=datetime.utcnow(),
            )

            embed.add_field(
                name="👤 Member", value=f"{member} ({member.id})", inline=True
            )

            embed.add_field(
                name="👮 Moderator",
                value=f"{interaction.user} ({interaction.user.id})",
                inline=True,
            )

            if ban_duration:
                embed.add_field(
                    name="⏰ Duration",
                    value=self.format_duration(ban_duration),
                    inline=True,
                )

                embed.add_field(
                    name="🕒 Expires",
                    value=f"<t:{int((datetime.utcnow() + timedelta(seconds=ban_duration)).timestamp())}:R>",
                    inline=True,
                )
            else:
                embed.add_field(name="⏰ Duration", value="Permanent", inline=True)

            if delete_days > 0:
                embed.add_field(
                    name="🗑️ Messages Deleted",
                    value=f"Last {delete_days} day(s)",
                    inline=True,
                )

            embed.add_field(name="📝 Reason", value=reason, inline=False)

            if case_id:
                embed.set_footer(text=f"Case ID: {case_id}")

            await interaction.followup.send(embed=embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to ban this member.", ephemeral=True
            )
        except Exception as exc:
            logger.error("Failed to ban member: %s", exc)
            await interaction.followup.send(
                f"❌ Failed to ban member: {str(exc)}", ephemeral=True
            )

    async def save_sticky_roles(self, member: discord.Member):
        """Save member's roles for sticky role restoration"""
        try:
            # Only save roles that aren't @everyone and aren't higher than bot's role
            roles_to_save = [
                role.id
                for role in member.roles[1:]  # Exclude @everyone
                if role < member.guild.me.top_role  # Only roles bot can manage
            ]

            if not roles_to_save:
                return

            sticky_role = StickyRole(
                guild_id=member.guild.id, user_id=member.id, role_ids=roles_to_save
            )

            # Save to database
            if hasattr(self.db, "__getitem__"):
                # pylint: disable=unsubscriptable-object
                collection = self.db[COLLECTIONS["sticky_roles"]]  # type: ignore[index]
                await collection.replace_one(
                    {"guild_id": member.guild.id, "user_id": member.id},
                    sticky_role.__dict__,
                    upsert=True,
                )
                # pylint: enable=unsubscriptable-object

            # Update cache
            if member.guild.id not in self.sticky_roles_cache:
                self.sticky_roles_cache[member.guild.id] = {}

            self.sticky_roles_cache[member.guild.id][member.id] = roles_to_save

        except Exception as exc:
            logger.error("Failed to save sticky roles for %s: %s", member, exc)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Restore sticky roles when member rejoins"""
        try:
            guild_id = member.guild.id
            user_id = member.id

            # Check if we have sticky roles for this user
            if (
                guild_id in self.sticky_roles_cache
                and user_id in self.sticky_roles_cache[guild_id]
            ):
                role_ids = self.sticky_roles_cache[guild_id][user_id]

                # Get roles that still exist
                roles_to_add = []
                for role_id in role_ids:
                    role = member.guild.get_role(role_id)
                    if role and role < member.guild.me.top_role:
                        roles_to_add.append(role)

                if roles_to_add:
                    await member.add_roles(
                        *roles_to_add, reason="Sticky roles restoration"
                    )
                    logger.info(
                        "Restored %d sticky roles to %s", len(roles_to_add), member
                    )

        except Exception as exc:
            logger.error("Failed to restore sticky roles for %s: %s", member, exc)

    def parse_duration(self, duration: str) -> Optional[int]:
        """Parse duration string into seconds"""
        try:
            duration = duration.lower().strip()

            # Extract number and unit
            import re

            match = re.match(r"(\d+)([smhd]?)", duration)
            if not match:
                return None

            amount = int(match.group(1))
            unit = match.group(2) or "s"  # Default to seconds

            multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}

            if unit not in multipliers:
                return None

            return amount * multipliers[unit]

        except (ValueError, AttributeError):
            return None

    def format_duration(self, seconds: int) -> str:
        """Format seconds into a readable duration"""
        if seconds < 60:
            return f"{seconds} second(s)"
        elif seconds < 3600:
            return f"{seconds // 60} minute(s)"
        elif seconds < 86400:
            return f"{seconds // 3600} hour(s)"
        else:
            return f"{seconds // 86400} day(s)"


async def setup(bot):
    """Load the ModerationSystem cog"""
    await bot.add_cog(ModerationSystem(bot))
