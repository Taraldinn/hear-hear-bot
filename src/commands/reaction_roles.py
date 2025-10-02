"""
Reaction Roles System for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import re
from src.database.connection import database
from src.database.models import ReactionRoleConfig, ReactionRole, COLLECTIONS

logger = logging.getLogger(__name__)


class ReactionRolesSystem(commands.Cog):
    """Advanced reaction roles system with Carl-bot features"""

    def __init__(self, bot):
        self.bot = bot
        self.db = database  # database is already the Database instance
        self.reaction_roles_cache = {}  # Cache for active reaction role messages
        self.self_destruct_tasks = {}  # Track self-destructing messages

    async def cog_load(self):
        """Load existing reaction role configurations on startup"""
        # Check if database supports MongoDB operations
        if not hasattr(self.db, '__getitem__'):
            logger.warning(
                "Reaction roles system disabled - requires MongoDB support. "
                "Current database is PostgreSQL. This feature needs migration."
            )
            return
        await self.load_reaction_roles()

    async def load_reaction_roles(self):
        """Load all reaction role configurations from database"""
        try:
            configs = (
                await self.db[COLLECTIONS["reaction_role_configs"]]
                .find()
                .to_list(length=None)
            )
            roles = (
                await self.db[COLLECTIONS["reaction_roles"]].find().to_list(length=None)
            )

            # Group roles by message ID
            roles_by_message = {}
            for role in roles:
                msg_id = role["message_id"]
                if msg_id not in roles_by_message:
                    roles_by_message[msg_id] = []
                roles_by_message[msg_id].append(role)

            # Build cache
            for config in configs:
                msg_id = config["message_id"]
                self.reaction_roles_cache[msg_id] = {
                    "config": config,
                    "roles": roles_by_message.get(msg_id, []),
                }

                # Set up self-destruct if needed
                if config.get("self_destruct"):
                    await self.schedule_self_destruct(msg_id, config["self_destruct"])

            logger.info(
                f"Loaded {len(self.reaction_roles_cache)} reaction role messages"
            )

        except Exception as e:
            logger.error("Failed to load reaction roles: {e}", )

    async def schedule_self_destruct(self, message_id: int, delay: int):
        """Schedule a message for self-destruction"""

        async def self_destruct():
            await asyncio.sleep(delay)
            try:
                # Get the message and delete it
                for guild in self.bot.guilds:
                    for channel in guild.text_channels:
                        try:
                            message = await channel.fetch_message(message_id)
                            await message.delete()
                            logger.info(
                                f"Self-destructed reaction role message {message_id}"
                            )
                            break
                        except discord.NotFound:
                            continue
                        except discord.Forbidden:
                            continue

                # Clean up from database and cache
                await self.remove_reaction_role_message(message_id)

            except Exception as e:
                logger.error("Failed to self-destruct message {message_id}: {e}", )
            finally:
                # Clean up task reference
                if message_id in self.self_destruct_tasks:
                    del self.self_destruct_tasks[message_id]

        # Cancel existing task if any
        if message_id in self.self_destruct_tasks:
            self.self_destruct_tasks[message_id].cancel()

        # Schedule new task
        task = asyncio.create_task(self_destruct())
        self.self_destruct_tasks[message_id] = task

    @app_commands.command(
        name="reactionrole", description="Create a reaction role message"
    )
    @app_commands.describe(
        title="Title for the reaction role embed",
        description="Description for the reaction role embed",
        mode="Mode: unique (one role), verify (confirm), reversed (remove), binding (permanent), temporary",
        self_destruct="Self-destruct after X minutes (optional)",
        channel="Channel to send the message (defaults to current)",
    )
    @app_commands.choices(
        mode=[
            app_commands.Choice(
                name="Unique (users can only pick one role)", value="unique"
            ),
            app_commands.Choice(
                name="Verify (users must confirm selection)", value="verify"
            ),
            app_commands.Choice(
                name="Reversed (reactions remove roles)", value="reversed"
            ),
            app_commands.Choice(
                name="Binding (roles can't be removed)", value="binding"
            ),
            app_commands.Choice(name="Temporary (roles expire)", value="temporary"),
            app_commands.Choice(name="Normal (standard behavior)", value="normal"),
        ]
    )
    @app_commands.default_permissions(manage_roles=True)
    async def create_reaction_role(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        mode: str = "normal",
        self_destruct: Optional[int] = None,
        channel: Optional[discord.TextChannel] = None,
    ):
        """Create a new reaction role message"""
        if not channel:
            channel = interaction.channel

        # Check permissions
        if not channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(
                "❌ I don't have permission to send messages in that channel.",
                ephemeral=True,
            )
            return

        if not channel.permissions_for(interaction.guild.me).add_reactions:
            await interaction.response.send_message(
                "❌ I don't have permission to add reactions in that channel.",
                ephemeral=True,
            )
            return

        try:
            await interaction.response.defer()

            # Create embed
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.blue(),
                timestamp=datetime.utcnow(),
            )

            # Add mode information
            mode_descriptions = {
                "unique": "👤 You can only pick **one role** from this message",
                "verify": "✅ You'll need to **confirm** your role selection",
                "reversed": "🔄 Reacting **removes** the role instead of adding it",
                "binding": "🔒 Roles from this message **cannot be removed**",
                "temporary": "⏰ Roles from this message are **temporary**",
                "normal": "⚙️ Standard reaction role behavior",
            }

            embed.add_field(
                name="🎯 Mode",
                value=mode_descriptions.get(mode, "Standard behavior"),
                inline=False,
            )

            if self_destruct:
                embed.add_field(
                    name="💥 Self-Destruct",
                    value=f"This message will self-destruct in **{self_destruct} minutes**",
                    inline=False,
                )

            embed.add_field(
                name="📝 Setup Instructions",
                value="Use `/add-reaction-role` to add roles to this message.\nReact with emojis to assign roles!",
                inline=False,
            )

            embed.set_footer(
                text=f"Created by {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url,
            )

            # Send the message
            message = await channel.send(embed=embed)

            # Save configuration to database
            config = ReactionRoleConfig(
                message_id=message.id,
                channel_id=channel.id,
                guild_id=interaction.guild.id,
                title=title,
                description=description,
                mode=mode,
                self_destruct=(
                    self_destruct * 60 if self_destruct else None
                ),  # Convert to seconds
                created_by=interaction.user.id,
            )

            await self.db[COLLECTIONS["reaction_role_configs"]].insert_one(
                config.__dict__
            )

            # Add to cache
            self.reaction_roles_cache[message.id] = {
                "config": config.__dict__,
                "roles": [],
            }

            # Schedule self-destruct if needed
            if self_destruct:
                await self.schedule_self_destruct(message.id, self_destruct * 60)

            await interaction.followup.send(
                f"✅ **Reaction role message created!**\n"
                f"📍 **Channel:** {channel.mention}\n"
                f"🆔 **Message ID:** `{message.id}`\n"
                f"⚙️ **Mode:** {mode}\n"
                f"📝 Use `/add-reaction-role message_id:{message.id}` to add roles!"
            )

        except Exception as e:
            logger.error("Failed to create reaction role message: {e}", )
            await interaction.followup.send(
                f"❌ Failed to create reaction role message: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="add-reaction-role", description="Add a role to a reaction role message"
    )
    @app_commands.describe(
        message_id="ID of the reaction role message",
        emoji="Emoji to react with (can be custom)",
        role="Role to assign when reacted",
        description="Description for this role (optional)",
        max_uses="Maximum number of people who can have this role (optional)",
    )
    @app_commands.default_permissions(manage_roles=True)
    async def add_reaction_role(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
        role: discord.Role,
        description: Optional[str] = None,
        max_uses: Optional[int] = None,
    ):
        """Add a reaction role to an existing message"""
        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid message ID. Please provide a valid number.", ephemeral=True
            )
            return

        # Check if message exists in cache
        if msg_id not in self.reaction_roles_cache:
            await interaction.response.send_message(
                "❌ Reaction role message not found. Make sure you're using the correct message ID.",
                ephemeral=True,
            )
            return

        # Check if role is higher than bot's highest role
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                f"❌ I can't assign the role **{role.name}** because it's higher than my highest role.\n"
                f"Please move my role above **{role.name}** in the server settings.",
                ephemeral=True,
            )
            return

        # Check if role is already assigned to this emoji
        existing_roles = self.reaction_roles_cache[msg_id]["roles"]
        for existing_role in existing_roles:
            if existing_role["emoji"] == emoji:
                await interaction.response.send_message(
                    f"❌ The emoji {emoji} is already assigned to role **{existing_role['role_name']}**.",
                    ephemeral=True,
                )
                return

        try:
            await interaction.response.defer()

            # Get the message and add reaction
            config = self.reaction_roles_cache[msg_id]["config"]
            channel = self.bot.get_channel(config["channel_id"])
            if not channel:
                await interaction.followup.send(
                    "❌ Could not find the channel for this reaction role message.",
                    ephemeral=True,
                )
                return

            try:
                message = await channel.fetch_message(msg_id)
            except discord.NotFound:
                await interaction.followup.send(
                    "❌ Could not find the reaction role message. It may have been deleted.",
                    ephemeral=True,
                )
                return

            # Add reaction to message
            try:
                await message.add_reaction(emoji)
            except discord.HTTPException as e:
                await interaction.followup.send(
                    f"❌ Failed to add reaction {emoji}: {str(e)}\n"
                    f"Make sure the emoji is valid and I have permission to use it.",
                    ephemeral=True,
                )
                return

            # Create reaction role entry
            reaction_role = ReactionRole(
                message_id=msg_id,
                emoji=emoji,
                role_id=role.id,
                role_name=role.name,
                description=description,
                max_uses=max_uses,
            )

            # Save to database
            await self.db[COLLECTIONS["reaction_roles"]].insert_one(
                reaction_role.__dict__
            )

            # Add to cache
            self.reaction_roles_cache[msg_id]["roles"].append(reaction_role.__dict__)

            # Update the embed to show the new role
            await self.update_reaction_role_embed(message)

            await interaction.followup.send(
                f"✅ **Reaction role added successfully!**\n"
                f"🎭 **Emoji:** {emoji}\n"
                f"🎯 **Role:** {role.mention}\n"
                f"📝 **Description:** {description or 'None'}\n"
                f"👥 **Max Uses:** {max_uses or 'Unlimited'}"
            )

        except Exception as e:
            logger.error("Failed to add reaction role: {e}", )
            await interaction.followup.send(
                f"❌ Failed to add reaction role: {str(e)}", ephemeral=True
            )

    async def update_reaction_role_embed(self, message: discord.Message):
        """Update the reaction role embed to show current roles"""
        try:
            msg_id = message.id
            if msg_id not in self.reaction_roles_cache:
                return

            data = self.reaction_roles_cache[msg_id]
            config = data["config"]
            roles = data["roles"]

            # Get original embed
            embed = message.embeds[0] if message.embeds else discord.Embed()

            # Remove old role fields
            embed.clear_fields()

            # Add mode information
            mode_descriptions = {
                "unique": "👤 You can only pick **one role** from this message",
                "verify": "✅ You'll need to **confirm** your role selection",
                "reversed": "🔄 Reacting **removes** the role instead of adding it",
                "binding": "🔒 Roles from this message **cannot be removed**",
                "temporary": "⏰ Roles from this message are **temporary**",
                "normal": "⚙️ Standard reaction role behavior",
            }

            embed.add_field(
                name="🎯 Mode",
                value=mode_descriptions.get(config["mode"], "Standard behavior"),
                inline=False,
            )

            # Add self-destruct info if applicable
            if config.get("self_destruct"):
                embed.add_field(
                    name="💥 Self-Destruct",
                    value=f"This message will self-destruct in **{config['self_destruct'] // 60} minutes**",
                    inline=False,
                )

            # Add roles
            if roles:
                role_text = []
                for role_data in roles:
                    role_line = f"{role_data['emoji']} **{role_data['role_name']}**"
                    if role_data.get("description"):
                        role_line += f" - {role_data['description']}"
                    if role_data.get("max_uses"):
                        role_line += f" (Max: {role_data['max_uses']})"
                    role_text.append(role_line)

                # Split into multiple fields if too long
                role_text_str = "\n".join(role_text)
                if len(role_text_str) > 1024:
                    # Split into chunks
                    chunks = []
                    current_chunk = []
                    current_length = 0

                    for line in role_text:
                        if current_length + len(line) + 1 > 1024:
                            chunks.append("\n".join(current_chunk))
                            current_chunk = [line]
                            current_length = len(line)
                        else:
                            current_chunk.append(line)
                            current_length += len(line) + 1

                    if current_chunk:
                        chunks.append("\n".join(current_chunk))

                    for i, chunk in enumerate(chunks):
                        field_name = (
                            "🎭 Available Roles"
                            if i == 0
                            else f"🎭 Available Roles (continued {i+1})"
                        )
                        embed.add_field(name=field_name, value=chunk, inline=False)
                else:
                    embed.add_field(
                        name="🎭 Available Roles", value=role_text_str, inline=False
                    )
            else:
                embed.add_field(
                    name="📝 Setup Instructions",
                    value="Use `/add-reaction-role` to add roles to this message.\nReact with emojis to assign roles!",
                    inline=False,
                )

            await message.edit(embed=embed)

        except Exception as e:
            logger.error("Failed to update reaction role embed: {e}", )

    async def remove_reaction_role_message(self, message_id: int):
        """Remove a reaction role message from database and cache"""
        try:
            # Remove from database
            await self.db[COLLECTIONS["reaction_role_configs"]].delete_one(
                {"message_id": message_id}
            )
            await self.db[COLLECTIONS["reaction_roles"]].delete_many(
                {"message_id": message_id}
            )

            # Remove from cache
            if message_id in self.reaction_roles_cache:
                del self.reaction_roles_cache[message_id]

            # Cancel self-destruct task if any
            if message_id in self.self_destruct_tasks:
                self.self_destruct_tasks[message_id].cancel()
                del self.self_destruct_tasks[message_id]

        except Exception as e:
            logger.error("Failed to remove reaction role message {message_id}: {e}", )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle when someone adds a reaction to a reaction role message"""
        await self.handle_reaction(payload, added=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Handle when someone removes a reaction from a reaction role message"""
        await self.handle_reaction(payload, added=False)

    async def handle_reaction(
        self, payload: discord.RawReactionActionEvent, added: bool
    ):
        """Handle reaction add/remove for reaction roles"""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return

        # Check if this is a reaction role message
        msg_id = payload.message_id
        if msg_id not in self.reaction_roles_cache:
            return

        try:
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return

            member = guild.get_member(payload.user_id)
            if not member:
                return

            data = self.reaction_roles_cache[msg_id]
            config = data["config"]
            roles = data["roles"]

            # Find the role for this emoji
            target_role_data = None
            for role_data in roles:
                if role_data["emoji"] == str(payload.emoji):
                    target_role_data = role_data
                    break

            if not target_role_data:
                return

            role = guild.get_role(target_role_data["role_id"])
            if not role:
                logger.warning(
                    f"Role {target_role_data['role_id']} not found for reaction role"
                )
                return

            # Check permissions and restrictions
            if not await self.check_reaction_role_permissions(member, config, role):
                return

            # Handle different modes
            mode = config["mode"]

            if mode == "reversed":
                # Reversed mode: reactions remove roles instead of adding
                added = not added

            if added:
                await self.add_role_to_member(member, role, target_role_data, config)
            else:
                await self.remove_role_from_member(
                    member, role, target_role_data, config
                )

        except Exception as e:
            logger.error("Error handling reaction role: {e}", )

    async def check_reaction_role_permissions(
        self, member: discord.Member, config: dict, role: discord.Role
    ) -> bool:
        """Check if a member can use this reaction role"""
        # Check whitelist
        if config.get("whitelist_roles"):
            member_role_ids = [r.id for r in member.roles]
            if not any(
                role_id in member_role_ids for role_id in config["whitelist_roles"]
            ):
                return False

        # Check blacklist
        if config.get("blacklist_roles"):
            member_role_ids = [r.id for r in member.roles]
            if any(role_id in member_role_ids for role_id in config["blacklist_roles"]):
                return False

        # Check if bot can manage the role
        if role >= member.guild.me.top_role:
            return False

        return True

    async def add_role_to_member(
        self, member: discord.Member, role: discord.Role, role_data: dict, config: dict
    ):
        """Add a role to a member with mode-specific logic"""
        mode = config["mode"]

        # Check if member already has the role
        if role in member.roles:
            return

        # Check max uses
        if role_data.get("max_uses"):
            current_uses = len([m for m in member.guild.members if role in m.roles])
            if current_uses >= role_data["max_uses"]:
                # Send ephemeral message about limit reached
                try:
                    await member.send(
                        f"❌ The role **{role.name}** has reached its maximum limit of {role_data['max_uses']} users."
                    )
                except discord.Forbidden:
                    pass
                return

        # Handle unique mode - remove other roles from this message
        if mode == "unique":
            data = self.reaction_roles_cache[config["message_id"]]
            other_roles = [
                member.guild.get_role(r["role_id"])
                for r in data["roles"]
                if r["role_id"] != role.id
            ]
            other_roles = [r for r in other_roles if r and r in member.roles]

            if other_roles:
                await member.remove_roles(
                    *other_roles, reason="Reaction role (unique mode)"
                )

        # Handle verify mode - ask for confirmation
        if mode == "verify":
            try:
                embed = discord.Embed(
                    title="🔍 Confirm Role Assignment",
                    description=f"Are you sure you want the **{role.name}** role?",
                    color=discord.Color.orange(),
                )
                embed.add_field(
                    name="React with",
                    value="✅ to confirm or ❌ to cancel",
                    inline=False,
                )

                confirm_msg = await member.send(embed=embed)
                await confirm_msg.add_reaction("✅")
                await confirm_msg.add_reaction("❌")

                def check(reaction, user):
                    return (
                        user == member
                        and str(reaction.emoji) in ["✅", "❌"]
                        and reaction.message.id == confirm_msg.id
                    )

                try:
                    reaction, user = await self.bot.wait_for(
                        "reaction_add", timeout=60.0, check=check
                    )

                    if str(reaction.emoji) == "❌":
                        await confirm_msg.edit(
                            embed=discord.Embed(
                                title="❌ Role Assignment Cancelled",
                                description=f"You chose not to get the **{role.name}** role.",
                                color=discord.Color.red(),
                            )
                        )
                        return

                except asyncio.TimeoutError:
                    await confirm_msg.edit(
                        embed=discord.Embed(
                            title="⏰ Confirmation Timeout",
                            description=f"You didn't respond in time. Role assignment for **{role.name}** was cancelled.",
                            color=discord.Color.orange(),
                        )
                    )
                    return

            except discord.Forbidden:
                # Can't DM user, proceed without confirmation
                pass

        # Add the role
        try:
            await member.add_roles(role, reason=f"Reaction role ({mode} mode)")
            logger.info("Added role {role.name} to {member} via reaction role", )

            # Send confirmation DM if possible
            try:
                embed = discord.Embed(
                    title="✅ Role Added",
                    description=f"You've been given the **{role.name}** role in **{member.guild.name}**!",
                    color=discord.Color.green(),
                )
                if role_data.get("description"):
                    embed.add_field(
                        name="Description", value=role_data["description"], inline=False
                    )
                await member.send(embed=embed)
            except discord.Forbidden:
                pass

        except discord.Forbidden:
            logger.error(
                f"Failed to add role {role.name} to {member}: Missing permissions"
            )
        except Exception as e:
            logger.error("Failed to add role {role.name} to {member}: {e}", )

    async def remove_role_from_member(
        self, member: discord.Member, role: discord.Role, role_data: dict, config: dict
    ):
        """Remove a role from a member with mode-specific logic"""
        mode = config["mode"]

        # Check if member has the role
        if role not in member.roles:
            return

        # Handle binding mode - roles can't be removed
        if mode == "binding":
            try:
                embed = discord.Embed(
                    title="🔒 Role is Binding",
                    description=f"The **{role.name}** role cannot be removed once assigned.",
                    color=discord.Color.orange(),
                )
                await member.send(embed=embed)
            except discord.Forbidden:
                pass
            return

        # Remove the role
        try:
            await member.remove_roles(
                role, reason=f"Reaction role removal ({mode} mode)"
            )
            logger.info("Removed role {role.name} from {member} via reaction role", )

            # Send confirmation DM if possible
            try:
                embed = discord.Embed(
                    title="✅ Role Removed",
                    description=f"The **{role.name}** role has been removed from you in **{member.guild.name}**.",
                    color=discord.Color.blue(),
                )
                await member.send(embed=embed)
            except discord.Forbidden:
                pass

        except discord.Forbidden:
            logger.error(
                f"Failed to remove role {role.name} from {member}: Missing permissions"
            )
        except Exception as e:
            logger.error("Failed to remove role {role.name} from {member}: {e}", )


async def setup(bot):
    await bot.add_cog(ReactionRolesSystem(bot))
