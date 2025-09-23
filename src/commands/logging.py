"""
Comprehensive Logging System for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
"""

import logging
from datetime import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from src.database.connection import database
from src.database.models import COLLECTIONS

logger = logging.getLogger(__name__)


class LoggingSystem(commands.Cog):
    """Advanced logging system like Carl-bot"""

    def __init__(self, bot):
        self.bot = bot
        self.db = database.get_database()
        self.logging_configs = {}  # Cache guild logging configurations
        self.message_cache = {}  # Cache messages for edit/delete logging
        self.invite_cache = {}  # Cache invites for tracking

    async def cog_load(self):
        """Load logging configurations on startup"""
        await self.load_logging_configs()
        await self.cache_guild_invites()

    async def load_logging_configs(self):
        """Load all guild logging configurations"""
        # Check if database is available
        if self.db is None:
            logger.warning("Database not available - skipping logging config load")
            return

        try:
            cursor = self.db[COLLECTIONS["logging_configs"]].find()
            configs = list(cursor)
            for config in configs:
                self.logging_configs[config["guild_id"]] = config
            logger.info(
                f"Loaded logging configs for {len(self.logging_configs)} guilds"
            )
        except Exception as e:
            logger.error(
                "Failed to load logging configs: {e}",
            )

    async def cache_guild_invites(self):
        """Cache guild invites for invite tracking"""
        for guild in self.bot.guilds:
            try:
                invites = await guild.invites()
                self.invite_cache[guild.id] = {
                    invite.code: invite.uses for invite in invites
                }
            except discord.Forbidden:
                pass  # No permission to view invites

    async def get_logging_config(self, guild_id: int) -> Optional[dict]:
        """Get logging configuration for a guild"""
        # Check if database is available
        if self.db is None:
            logger.warning("Database not available - logging features disabled")
            return None

        if guild_id not in self.logging_configs:
            # Try to load from database
            try:
                config = self.db[COLLECTIONS["logging_configs"]].find_one(
                    {"guild_id": guild_id}
                )
                if config:
                    self.logging_configs[guild_id] = config
                else:
                    return None
            except Exception as e:
                logger.error(
                    "Failed to get logging config for guild {guild_id}: {e}",
                )
                return None
        return self.logging_configs.get(guild_id)

    async def should_log_event(self, guild_id: int, event_type: str, **kwargs) -> bool:
        """Check if an event should be logged based on configuration"""
        config = await self.get_logging_config(guild_id)
        if not config:
            return False

        # Check if the required channel is configured
        channel_key = f"{event_type}_logs_channel"
        if not config.get(channel_key):
            return False

        # Check ignore lists
        if kwargs.get("channel_id") in config.get("ignored_channels", []):
            return False

        if kwargs.get("user_id") in config.get("ignored_users", []):
            return False

        # Check ignored prefixes for message events
        if event_type == "message" and kwargs.get("content"):
            content = kwargs["content"]
            for prefix in config.get("ignored_prefixes", []):
                if content.startswith(prefix):
                    return False

        return True

    async def send_log(self, guild_id: int, channel_type: str, embed: discord.Embed):
        """Send a log embed to the appropriate channel"""
        config = await self.get_logging_config(guild_id)
        if not config:
            return

        channel_id = config.get(f"{channel_type}_logs_channel")
        if not channel_id:
            return

        try:
            channel = self.bot.get_channel(channel_id)
            if channel and channel.permissions_for(channel.guild.me).send_messages:
                await channel.send(embed=embed)
        except Exception as e:
            logger.error(
                "Failed to send log to {channel_type}: {e}",
            )

    # Message Logging Events
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Cache messages for edit/delete tracking"""
        if message.guild and not message.author.bot:
            # Cache the message
            self.message_cache[message.id] = {
                "content": message.content,
                "author_id": message.author.id,
                "channel_id": message.channel.id,
                "guild_id": message.guild.id,
                "created_at": message.created_at,
                "attachments": [att.url for att in message.attachments],
                "embeds": len(message.embeds),
            }

            # Keep cache size manageable (last 10,000 messages)
            if len(self.message_cache) > 10000:
                # Remove oldest 1000 messages
                oldest_keys = sorted(self.message_cache.keys())[:1000]
                for key in oldest_keys:
                    del self.message_cache[key]

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Log deleted messages"""
        if not message.guild or message.author.bot:
            return

        if not await self.should_log_event(
            message.guild.id,
            "message",
            channel_id=message.channel.id,
            user_id=message.author.id,
            content=message.content,
        ):
            return

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red(),
            timestamp=datetime.utcnow(),
        )

        embed.add_field(
            name="👤 Author",
            value=f"{message.author} ({message.author.id})",
            inline=True,
        )

        embed.add_field(
            name="📍 Channel",
            value=f"{message.channel.mention} ({message.channel.id})",
            inline=True,
        )

        embed.add_field(
            name="🕒 Created",
            value=f"<t:{int(message.created_at.timestamp())}:R>",
            inline=True,
        )

        if message.content:
            content = (
                message.content[:1024]
                if len(message.content) > 1024
                else message.content
            )
            embed.add_field(name="💬 Content", value=f"```{content}```", inline=False)

        if message.attachments:
            attachment_info = "\n".join(
                [f"[{att.filename}]({att.url})" for att in message.attachments]
            )
            embed.add_field(
                name="📎 Attachments", value=attachment_info[:1024], inline=False
            )

        if message.embeds:
            embed.add_field(
                name="📄 Embeds", value=f"{len(message.embeds)} embed(s)", inline=True
            )

        embed.set_footer(text=f"Message ID: {message.id}")
        if message.author.display_avatar:
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.display_avatar.url,
            )

        await self.send_log(message.guild.id, "message", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Log edited messages"""
        if not before.guild or before.author.bot:
            return

        # Skip if content didn't actually change
        if before.content == after.content:
            return

        if not await self.should_log_event(
            before.guild.id,
            "message",
            channel_id=before.channel.id,
            user_id=before.author.id,
            content=before.content,
        ):
            return

        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow(),
        )

        embed.add_field(
            name="👤 Author", value=f"{before.author} ({before.author.id})", inline=True
        )

        embed.add_field(
            name="📍 Channel",
            value=f"{before.channel.mention} ({before.channel.id})",
            inline=True,
        )

        embed.add_field(
            name="🔗 Jump to Message",
            value=f"[Click here]({after.jump_url})",
            inline=True,
        )

        if before.content:
            content = (
                before.content[:512] if len(before.content) > 512 else before.content
            )
            embed.add_field(name="📝 Before", value=f"```{content}```", inline=False)

        if after.content:
            content = after.content[:512] if len(after.content) > 512 else after.content
            embed.add_field(name="📝 After", value=f"```{content}```", inline=False)

        embed.set_footer(text=f"Message ID: {before.id}")
        if before.author.display_avatar:
            embed.set_author(
                name=before.author.display_name,
                icon_url=before.author.display_avatar.url,
            )

        await self.send_log(before.guild.id, "message", embed)

    # Member Logging Events
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Log member joins and track invites"""
        if not await self.should_log_event(
            member.guild.id, "join_leave", user_id=member.id
        ):
            return

        embed = discord.Embed(
            title="📥 Member Joined",
            color=discord.Color.green(),
            timestamp=datetime.utcnow(),
        )

        embed.add_field(name="👤 Member", value=f"{member} ({member.id})", inline=True)

        embed.add_field(
            name="🗓️ Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True,
        )

        embed.add_field(
            name="📊 Member Count", value=f"{member.guild.member_count}", inline=True
        )

        # Try to determine which invite was used
        config = await self.get_logging_config(member.guild.id)
        if config and config.get("invite_tracking"):
            invite_used = await self.track_invite_usage(member.guild)
            if invite_used:
                embed.add_field(
                    name="🔗 Invite Used",
                    value=f"**{invite_used['code']}** (by {invite_used['inviter']})",
                    inline=False,
                )

        embed.set_footer(text=f"User ID: {member.id}")
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)

        await self.send_log(member.guild.id, "join_leave", embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Log member leaves"""
        if not await self.should_log_event(
            member.guild.id, "join_leave", user_id=member.id
        ):
            return

        embed = discord.Embed(
            title="📤 Member Left",
            color=discord.Color.red(),
            timestamp=datetime.utcnow(),
        )

        embed.add_field(name="👤 Member", value=f"{member} ({member.id})", inline=True)

        embed.add_field(
            name="⏰ Joined",
            value=(
                f"<t:{int(member.joined_at.timestamp())}:R>"
                if member.joined_at
                else "Unknown"
            ),
            inline=True,
        )

        embed.add_field(
            name="📊 Member Count", value=f"{member.guild.member_count}", inline=True
        )

        if member.roles[1:]:  # Exclude @everyone
            roles = ", ".join([role.mention for role in member.roles[1:]][:10])
            if len(member.roles) > 11:
                roles += f" (+{len(member.roles) - 11} more)"
            embed.add_field(name="🎭 Roles", value=roles, inline=False)

        embed.set_footer(text=f"User ID: {member.id}")
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)

        await self.send_log(member.guild.id, "join_leave", embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Log member updates (roles, nickname, etc.)"""
        if not await self.should_log_event(
            before.guild.id, "member", user_id=before.id
        ):
            return

        embed = None

        # Check for role changes
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]

            if added_roles or removed_roles:
                embed = discord.Embed(
                    title="🎭 Member Roles Updated",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow(),
                )

                embed.add_field(
                    name="👤 Member", value=f"{after} ({after.id})", inline=True
                )

                if added_roles:
                    roles_text = ", ".join([role.mention for role in added_roles])
                    embed.add_field(
                        name="➕ Roles Added", value=roles_text, inline=False
                    )

                if removed_roles:
                    roles_text = ", ".join([role.mention for role in removed_roles])
                    embed.add_field(
                        name="➖ Roles Removed", value=roles_text, inline=False
                    )

        # Check for nickname changes
        elif before.nick != after.nick:
            embed = discord.Embed(
                title="📝 Nickname Changed",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow(),
            )

            embed.add_field(
                name="👤 Member", value=f"{after} ({after.id})", inline=True
            )

            embed.add_field(name="📝 Before", value=before.nick or "None", inline=True)

            embed.add_field(name="📝 After", value=after.nick or "None", inline=True)

        if embed:
            embed.set_footer(text=f"User ID: {after.id}")
            if after.display_avatar:
                embed.set_author(
                    name=after.display_name, icon_url=after.display_avatar.url
                )
            await self.send_log(after.guild.id, "member", embed)

    # Server Logging Events
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Log channel creation"""
        if not await self.should_log_event(channel.guild.id, "server"):
            return

        embed = discord.Embed(
            title="📝 Channel Created",
            color=discord.Color.green(),
            timestamp=datetime.utcnow(),
        )

        embed.add_field(
            name="📍 Channel", value=f"{channel.mention} ({channel.id})", inline=True
        )

        embed.add_field(
            name="📂 Type",
            value=str(channel.type).replace("_", " ").title(),
            inline=True,
        )

        if hasattr(channel, "category") and channel.category:
            embed.add_field(
                name="📁 Category", value=channel.category.name, inline=True
            )

        embed.set_footer(text=f"Channel ID: {channel.id}")

        await self.send_log(channel.guild.id, "server", embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Log channel deletion"""
        if not await self.should_log_event(channel.guild.id, "server"):
            return

        embed = discord.Embed(
            title="🗑️ Channel Deleted",
            color=discord.Color.red(),
            timestamp=datetime.utcnow(),
        )

        embed.add_field(
            name="📍 Channel", value=f"#{channel.name} ({channel.id})", inline=True
        )

        embed.add_field(
            name="📂 Type",
            value=str(channel.type).replace("_", " ").title(),
            inline=True,
        )

        if hasattr(channel, "category") and channel.category:
            embed.add_field(
                name="📁 Category", value=channel.category.name, inline=True
            )

        embed.set_footer(text=f"Channel ID: {channel.id}")

        await self.send_log(channel.guild.id, "server", embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Log role creation"""
        if not await self.should_log_event(role.guild.id, "server"):
            return

        embed = discord.Embed(
            title="🎭 Role Created",
            color=discord.Color.green(),
            timestamp=datetime.utcnow(),
        )

        embed.add_field(
            name="🎭 Role", value=f"{role.mention} ({role.id})", inline=True
        )

        embed.add_field(
            name="🎨 Color",
            value=f"#{role.color.value:06x}" if role.color.value else "Default",
            inline=True,
        )

        embed.add_field(name="📊 Position", value=str(role.position), inline=True)

        if role.permissions.administrator:
            embed.add_field(
                name="⚠️ Warning",
                value="This role has **Administrator** permissions!",
                inline=False,
            )

        embed.set_footer(text=f"Role ID: {role.id}")

        await self.send_log(role.guild.id, "server", embed)

    async def track_invite_usage(self, guild: discord.Guild) -> Optional[dict]:
        """Track which invite was used when someone joins"""
        try:
            current_invites = await guild.invites()
            current_uses = {invite.code: invite.uses for invite in current_invites}

            cached_uses = self.invite_cache.get(guild.id, {})

            # Find the invite with increased usage
            for code, uses in current_uses.items():
                if code in cached_uses and uses > cached_uses[code]:
                    # This invite was used
                    invite = discord.utils.get(current_invites, code=code)
                    if invite:
                        # Update cache
                        self.invite_cache[guild.id] = current_uses
                        return {"code": code, "inviter": invite.inviter, "uses": uses}

            # Update cache even if no specific invite was found
            self.invite_cache[guild.id] = current_uses

        except discord.Forbidden:
            pass  # No permission to view invites

        return None

    # Configuration Commands
    @app_commands.command(
        name="setup-logging", description="Configure logging channels for this server"
    )
    @app_commands.describe(
        message_logs="Channel for message logs (edits, deletes)",
        member_logs="Channel for member logs (roles, nicknames)",
        server_logs="Channel for server logs (channels, roles, emojis)",
        join_leave="Channel for join/leave logs",
        invite_tracking="Enable invite tracking",
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_logging(
        self,
        interaction: discord.Interaction,
        message_logs: Optional[discord.TextChannel] = None,
        member_logs: Optional[discord.TextChannel] = None,
        server_logs: Optional[discord.TextChannel] = None,
        join_leave: Optional[discord.TextChannel] = None,
        invite_tracking: Optional[bool] = False,
    ):
        """Set up logging channels for the server"""
        try:
            await interaction.response.defer()

            guild_id = interaction.guild.id

            # Get existing config or create new one
            config = await self.get_logging_config(guild_id) or {"guild_id": guild_id}

            # Update configuration
            if message_logs:
                config["message_logs_channel"] = message_logs.id
            if member_logs:
                config["member_logs_channel"] = member_logs.id
            if server_logs:
                config["server_logs_channel"] = server_logs.id
            if join_leave:
                config["join_leave_channel"] = join_leave.id
            if invite_tracking is not None:
                config["invite_tracking"] = invite_tracking

            # Save to database
            if self.db is not None:
                self.db[COLLECTIONS["logging_configs"]].replace_one(
                    {"guild_id": guild_id}, config, upsert=True
                )

            # Update cache
            self.logging_configs[guild_id] = config

            # If invite tracking is enabled, cache invites
            if invite_tracking:
                await self.cache_guild_invites()

            embed = discord.Embed(
                title="✅ Logging Configuration Updated",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )

            if message_logs:
                embed.add_field(
                    name="💬 Message Logs", value=message_logs.mention, inline=True
                )

            if member_logs:
                embed.add_field(
                    name="👤 Member Logs", value=member_logs.mention, inline=True
                )

            if server_logs:
                embed.add_field(
                    name="🏛️ Server Logs", value=server_logs.mention, inline=True
                )

            if join_leave:
                embed.add_field(
                    name="📥📤 Join/Leave Logs", value=join_leave.mention, inline=True
                )

            embed.add_field(
                name="🔗 Invite Tracking",
                value="✅ Enabled" if invite_tracking else "❌ Disabled",
                inline=True,
            )

            embed.add_field(
                name="💡 Next Steps",
                value="Use `/logging-ignore` to configure what to ignore in logs.",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(
                "Failed to setup logging: {e}",
            )
            await interaction.followup.send(
                f"❌ Failed to setup logging: {str(e)}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(LoggingSystem(bot))
