"""
Configuration Commands for Hear! Hear! Bot
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


class ConfigurationCommands(commands.Cog):
    """Advanced configuration commands for server management"""

    def __init__(self, bot):
        self.bot = bot
        self.db = database  # database is already the Database instance
        self.guild_configs = {}  # Cache guild configurations

    async def cog_load(self):
        """Load guild configurations on startup"""
        # Check if database supports MongoDB operations
        if not hasattr(self.db, "__getitem__"):
            logger.warning(
                "Configuration system disabled - requires MongoDB support. "
                "Current database is PostgreSQL. This feature needs migration."
            )
            return
        try:
            await self.load_guild_configs()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Failed to load guild configs: %s", exc)

    async def load_guild_configs(self):
        """Load all guild configurations"""
        if not hasattr(self.db, "__getitem__"):
            return
        try:
            # Type guard for MongoDB-style database
            # pylint: disable=unsubscriptable-object
            collection = self.db[COLLECTIONS["guild_configs"]]  # type: ignore[index]
            configs = await collection.find().to_list(length=None)
            # pylint: enable=unsubscriptable-object
            for config in configs:
                self.guild_configs[config["guild_id"]] = config
            logger.info(
                "Loaded configurations for %d guilds",
                len(self.guild_configs),
            )
        except Exception:  # pylint: disable=broad-exception-caught
            # Already logged in cog_load
            pass

    async def get_guild_config(self, guild_id: int) -> dict:
        """Get or create guild configuration"""
        if guild_id not in self.guild_configs:
            # Create default config
            default_config = {
                "guild_id": guild_id,
                "prefix": [".", "?"],
                "language": "english",
                "timezone": "UTC",
                "mute_role_id": None,
                "drama_channel_id": None,
                "welcome_channel_id": None,
                "farewell_channel_id": None,
                "autorole_ids": [],
            }

            # Save to database
            if hasattr(self.db, "__getitem__"):
                # pylint: disable=unsubscriptable-object
                collection = self.db[COLLECTIONS["guild_configs"]]  # type: ignore[index]
                await collection.insert_one(default_config)
                # pylint: enable=unsubscriptable-object
            self.guild_configs[guild_id] = default_config

        return self.guild_configs[guild_id]

    async def update_guild_config(self, guild_id: int, updates: dict):
        """Update guild configuration"""
        config = await self.get_guild_config(guild_id)
        config.update(updates)

        # Save to database
        if hasattr(self.db, "__getitem__"):
            # pylint: disable=unsubscriptable-object
            collection = self.db[COLLECTIONS["guild_configs"]]  # type: ignore[index]
            await collection.replace_one({"guild_id": guild_id}, config, upsert=True)
            # pylint: enable=unsubscriptable-object

        # Update cache
        self.guild_configs[guild_id] = config

    @app_commands.command(name="config", description="View server configuration")
    @app_commands.default_permissions(administrator=True)
    async def view_config(self, interaction: discord.Interaction):
        """View current server configuration"""
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        try:
            await interaction.response.defer()

            config = await self.get_guild_config(interaction.guild.id)

            embed = discord.Embed(
                title="⚙️ Server Configuration",
                description=f"Configuration for **{interaction.guild.name}**",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow(),
            )

            # Basic settings
            embed.add_field(
                name="🔤 Language",
                value=config.get("language", "english").title(),
                inline=True,
            )

            embed.add_field(
                name="🌍 Timezone", value=config.get("timezone", "UTC"), inline=True
            )

            embed.add_field(
                name="📝 Prefixes",
                value=", ".join(f"`{p}`" for p in config.get("prefix", [".", "?"])),
                inline=True,
            )

            # Moderation settings
            mute_role_id = config.get("mute_role_id")
            mute_role = (
                interaction.guild.get_role(mute_role_id)
                if mute_role_id is not None
                else None
            )
            embed.add_field(
                name="🔇 Mute Role",
                value=mute_role.mention if mute_role else "Not set",
                inline=True,
            )

            drama_channel_id = config.get("drama_channel_id")
            drama_channel = (
                interaction.guild.get_channel(drama_channel_id)
                if drama_channel_id is not None
                else None
            )
            embed.add_field(
                name="🎭 Drama Channel",
                value=drama_channel.mention if drama_channel else "Not set",
                inline=True,
            )

            # Welcome/Farewell
            welcome_channel_id = config.get("welcome_channel_id")
            welcome_channel = (
                interaction.guild.get_channel(welcome_channel_id)
                if welcome_channel_id is not None
                else None
            )
            embed.add_field(
                name="👋 Welcome Channel",
                value=welcome_channel.mention if welcome_channel else "Not set",
                inline=True,
            )

            farewell_channel_id = config.get("farewell_channel_id")
            farewell_channel = (
                interaction.guild.get_channel(farewell_channel_id)
                if farewell_channel_id is not None
                else None
            )
            embed.add_field(
                name="👋 Farewell Channel",
                value=farewell_channel.mention if farewell_channel else "Not set",
                inline=True,
            )

            # Auto roles
            autoroles = []
            for role_id in config.get("autorole_ids", []):
                role = interaction.guild.get_role(role_id)
                if role:
                    autoroles.append(role.mention)

            embed.add_field(
                name="🎭 Auto Roles",
                value=", ".join(autoroles) if autoroles else "None",
                inline=False,
            )

            embed.set_footer(text="Use the setup commands to configure these settings")

            await interaction.followup.send(embed=embed)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to view config: {e}",
            )
            await interaction.followup.send(
                f"❌ Failed to view configuration: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="setup-moderation", description="Configure moderation settings"
    )
    @app_commands.describe(
        mute_role="Role to assign for mutes",
        drama_channel="Channel for moderation alerts and rule violations",
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_moderation(
        self,
        interaction: discord.Interaction,
        mute_role: Optional[discord.Role] = None,
        drama_channel: Optional[discord.TextChannel] = None,
    ):
        """Set up moderation settings"""
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        try:
            await interaction.response.defer()

            updates = {}

            if mute_role:
                # Check if bot can manage this role
                if mute_role >= interaction.guild.me.top_role:
                    await interaction.followup.send(
                        f"❌ I cannot manage the role **{mute_role.name}** "
                        f"because it's higher than my highest role.\n"
                        f"Please move my role above **{mute_role.name}** "
                        f"in the server settings.",
                        ephemeral=True,
                    )
                    return

                updates["mute_role_id"] = mute_role.id

            if drama_channel:
                # Check if bot can send messages in this channel
                if not drama_channel.permissions_for(
                    interaction.guild.me
                ).send_messages:
                    await interaction.followup.send(
                        f"❌ I don't have permission to send messages in {drama_channel.mention}.",
                        ephemeral=True,
                    )
                    return

                updates["drama_channel_id"] = drama_channel.id

            if updates:
                await self.update_guild_config(interaction.guild.id, updates)

            embed = discord.Embed(
                title="✅ Moderation Setup Complete",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )

            if mute_role:
                embed.add_field(
                    name="🔇 Mute Role", value=mute_role.mention, inline=True
                )

            if drama_channel:
                embed.add_field(
                    name="🎭 Drama Channel", value=drama_channel.mention, inline=True
                )

            embed.add_field(
                name="💡 Next Steps",
                value="Use `/setup-logging` to configure log channels.",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to setup moderation: {e}",
            )
            await interaction.followup.send(
                f"❌ Failed to setup moderation: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="setup-welcome", description="Configure welcome and farewell messages"
    )
    @app_commands.describe(
        welcome_channel="Channel for welcome messages",
        farewell_channel="Channel for farewell messages",
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_welcome(
        self,
        interaction: discord.Interaction,
        welcome_channel: Optional[discord.TextChannel] = None,
        farewell_channel: Optional[discord.TextChannel] = None,
    ):
        """Set up welcome and farewell channels"""
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        try:
            await interaction.response.defer()

            updates = {}

            if welcome_channel:
                perms = welcome_channel.permissions_for(interaction.guild.me)
                if not perms.send_messages:
                    await interaction.followup.send(
                        f"❌ I don't have permission to send messages in "
                        f"{welcome_channel.mention}.",
                        ephemeral=True,
                    )
                    return
                updates["welcome_channel_id"] = welcome_channel.id

            if farewell_channel:
                perms = farewell_channel.permissions_for(interaction.guild.me)
                if not perms.send_messages:
                    await interaction.followup.send(
                        f"❌ I don't have permission to send messages in "
                        f"{farewell_channel.mention}.",
                        ephemeral=True,
                    )
                    return
                updates["farewell_channel_id"] = farewell_channel.id

            if updates:
                await self.update_guild_config(interaction.guild.id, updates)

            embed = discord.Embed(
                title="✅ Welcome Setup Complete",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )

            if welcome_channel:
                embed.add_field(
                    name="👋 Welcome Channel",
                    value=welcome_channel.mention,
                    inline=True,
                )

            if farewell_channel:
                embed.add_field(
                    name="👋 Farewell Channel",
                    value=farewell_channel.mention,
                    inline=True,
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to setup welcome: {e}",
            )
            await interaction.followup.send(
                f"❌ Failed to setup welcome: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="autorole", description="Manage auto roles for new members"
    )
    @app_commands.describe(
        action="Action to perform", role="Role to add/remove from auto roles"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Add role to auto roles", value="add"),
            app_commands.Choice(name="Remove role from auto roles", value="remove"),
            app_commands.Choice(name="List current auto roles", value="list"),
            app_commands.Choice(name="Clear all auto roles", value="clear"),
        ]
    )
    @app_commands.default_permissions(administrator=True)
    async def autorole(
        self,
        interaction: discord.Interaction,
        action: str,
        role: Optional[discord.Role] = None,
    ):
        """Manage auto roles for new members"""
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        try:
            await interaction.response.defer()

            config = await self.get_guild_config(interaction.guild.id)
            autorole_ids = config.get("autorole_ids", [])

            if action == "add":
                if not role:
                    await interaction.followup.send(
                        "❌ You must specify a role to add.", ephemeral=True
                    )
                    return

                if role.id in autorole_ids:
                    await interaction.followup.send(
                        f"❌ **{role.name}** is already an auto role.", ephemeral=True
                    )
                    return

                if role >= interaction.guild.me.top_role:
                    await interaction.followup.send(
                        f"❌ I cannot manage the role **{role.name}** "
                        f"because it's higher than my highest role.",
                        ephemeral=True,
                    )
                    return

                autorole_ids.append(role.id)
                await self.update_guild_config(
                    interaction.guild.id, {"autorole_ids": autorole_ids}
                )

                embed = discord.Embed(
                    title="✅ Auto Role Added",
                    description=(
                        f"**{role.name}** will now be given to new members "
                        f"automatically."
                    ),
                    color=discord.Color.green(),
                )

            elif action == "remove":
                if not role:
                    await interaction.followup.send(
                        "❌ You must specify a role to remove.", ephemeral=True
                    )
                    return

                if role.id not in autorole_ids:
                    await interaction.followup.send(
                        f"❌ **{role.name}** is not an auto role.", ephemeral=True
                    )
                    return

                autorole_ids.remove(role.id)
                await self.update_guild_config(
                    interaction.guild.id, {"autorole_ids": autorole_ids}
                )

                embed = discord.Embed(
                    title="✅ Auto Role Removed",
                    description=(
                        f"**{role.name}** will no longer be given to new "
                        f"members automatically."
                    ),
                    color=discord.Color.orange(),
                )

            elif action == "list":
                embed = discord.Embed(title="🎭 Auto Roles", color=discord.Color.blue())

                if autorole_ids:
                    roles_text = []
                    for role_id in autorole_ids:
                        role_obj = interaction.guild.get_role(role_id)
                        if role_obj:
                            roles_text.append(role_obj.mention)
                        else:
                            # Clean up invalid role IDs
                            autorole_ids.remove(role_id)

                    if roles_text:
                        embed.description = "\n".join(roles_text)
                        # Update config if we cleaned up invalid roles
                        if len(roles_text) != len(autorole_ids):
                            await self.update_guild_config(
                                interaction.guild.id, {"autorole_ids": autorole_ids}
                            )
                    else:
                        embed.description = "No auto roles configured."
                else:
                    embed.description = "No auto roles configured."

            elif action == "clear":
                if not autorole_ids:
                    await interaction.followup.send(
                        "❌ There are no auto roles to clear.", ephemeral=True
                    )
                    return

                await self.update_guild_config(
                    interaction.guild.id, {"autorole_ids": []}
                )

                embed = discord.Embed(
                    title="🗑️ Auto Roles Cleared",
                    description=(
                        "All auto roles have been removed. New members will no "
                        "longer receive automatic roles."
                    ),
                    color=discord.Color.red(),
                )
            else:
                # Should never reach here, but initialize embed for type safety
                embed = discord.Embed(
                    title="❌ Unknown Action",
                    description="Invalid action specified.",
                    color=discord.Color.red(),
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to manage autorole: {e}",
            )
            await interaction.followup.send(
                f"❌ Failed to manage auto role: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="prefix", description="Manage server command prefixes")
    @app_commands.describe(action="Action to perform", prefix="Prefix to add/remove")
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Add prefix", value="add"),
            app_commands.Choice(name="Remove prefix", value="remove"),
            app_commands.Choice(name="List prefixes", value="list"),
            app_commands.Choice(name="Reset to default", value="reset"),
        ]
    )
    @app_commands.default_permissions(administrator=True)
    async def prefix_management(
        self,
        interaction: discord.Interaction,
        action: str,
        prefix: Optional[str] = None,
    ):
        """Manage command prefixes for this server"""
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        try:
            await interaction.response.defer()

            config = await self.get_guild_config(interaction.guild.id)
            prefixes = config.get("prefix", [".", "?"])

            if action == "add":
                if not prefix:
                    await interaction.followup.send(
                        "❌ You must specify a prefix to add.", ephemeral=True
                    )
                    return

                if len(prefix) > 5:
                    await interaction.followup.send(
                        "❌ Prefixes cannot be longer than 5 characters.",
                        ephemeral=True,
                    )
                    return

                if prefix in prefixes:
                    await interaction.followup.send(
                        f"❌ `{prefix}` is already a prefix for this server.",
                        ephemeral=True,
                    )
                    return

                prefixes.append(prefix)
                await self.update_guild_config(
                    interaction.guild.id, {"prefix": prefixes}
                )

                embed = discord.Embed(
                    title="✅ Prefix Added",
                    description=f"Added `{prefix}` as a command prefix for this server.",
                    color=discord.Color.green(),
                )

            elif action == "remove":
                if not prefix:
                    await interaction.followup.send(
                        "❌ You must specify a prefix to remove.", ephemeral=True
                    )
                    return

                if prefix not in prefixes:
                    await interaction.followup.send(
                        f"❌ `{prefix}` is not a prefix for this server.",
                        ephemeral=True,
                    )
                    return

                if len(prefixes) == 1:
                    await interaction.followup.send(
                        "❌ Cannot remove the last prefix. Add another prefix first.",
                        ephemeral=True,
                    )
                    return

                prefixes.remove(prefix)
                await self.update_guild_config(
                    interaction.guild.id, {"prefix": prefixes}
                )

                embed = discord.Embed(
                    title="✅ Prefix Removed",
                    description=f"Removed `{prefix}` from command prefixes for this server.",
                    color=discord.Color.orange(),
                )

            elif action == "list":
                embed = discord.Embed(
                    title="🔤 Server Prefixes",
                    description=", ".join(f"`{p}`" for p in prefixes),
                    color=discord.Color.blue(),
                )

            elif action == "reset":
                await self.update_guild_config(
                    interaction.guild.id, {"prefix": [".", "?"]}
                )

                embed = discord.Embed(
                    title="🔄 Prefixes Reset",
                    description="Server prefixes have been reset to default: `.` and `?`",
                    color=discord.Color.blue(),
                )
            else:
                # Should never reach here, but initialize embed for type safety
                embed = discord.Embed(
                    title="❌ Unknown Action",
                    description="Invalid action specified.",
                    color=discord.Color.red(),
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to manage prefixes: {e}",
            )
            await interaction.followup.send(
                f"❌ Failed to manage prefixes: {str(e)}", ephemeral=True
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle new member auto roles"""
        try:
            config = await self.get_guild_config(member.guild.id)
            autorole_ids = config.get("autorole_ids", [])

            if not autorole_ids:
                return

            # Get roles that still exist and bot can manage
            roles_to_add = []
            for role_id in autorole_ids:
                role = member.guild.get_role(role_id)
                if role and role < member.guild.me.top_role:
                    roles_to_add.append(role)

            if roles_to_add:
                await member.add_roles(*roles_to_add, reason="Auto role assignment")
                logger.info(
                    "Added {len(roles_to_add)} auto roles to {member}",
                )

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to assign auto roles to %s: %s",
                member,
                exc,
            )


async def setup(bot):
    """Load the ConfigurationCommands cog"""
    await bot.add_cog(ConfigurationCommands(bot))
