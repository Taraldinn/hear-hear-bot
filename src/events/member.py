"""
Member Events for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, cast

import discord
from discord.abc import Messageable
from discord.ext import commands

from src.database.connection import database
from src.database.models import COLLECTIONS

logger = logging.getLogger(__name__)


@dataclass
class RolePromptOption:
    """Dataclass representing a role prompt option."""

    role_id: int
    label: str
    description: Optional[str] = None
    emoji: Optional[str] = None


class RolePromptSelect(discord.ui.Select):
    """Select component allowing a member to choose a tournament role."""

    def __init__(self, member: discord.Member, options: Iterable[RolePromptOption]):
        self.member = member

        select_options: list[discord.SelectOption] = []
        for option in options:
            role = member.guild.get_role(option.role_id)
            if not role:
                continue

            select_options.append(
                discord.SelectOption(
                    label=option.label,
                    description=option.description,
                    value=str(role.id),
                    emoji=option.emoji,
                )
            )

        super().__init__(
            placeholder="Select your assigned role",
            min_values=1,
            max_values=1,
            options=select_options,
        )

    async def callback(self, interaction: discord.Interaction):  # type: ignore[override]
        if interaction.user.id != self.member.id:
            await interaction.response.send_message(
                "❌ This prompt isn't for you. Please wait for your turn!",
                ephemeral=True,
            )
            return

        if not self.values:
            await interaction.response.send_message(
                "❌ Please select a role before submitting.", ephemeral=True
            )
            return

        role_id = int(self.values[0])
        role = self.member.guild.get_role(role_id)

        if not role:
            await interaction.response.send_message(
                "❌ That role is no longer available. Please contact staff.",
                ephemeral=True,
            )
            return

        if role >= self.member.guild.me.top_role:  # type: ignore[operator]
            await interaction.response.send_message(
                "❌ I don't have permission to assign that role. Please notify staff.",
                ephemeral=True,
            )
            return

        await self.member.add_roles(role, reason="Role prompt selection")
        await interaction.response.send_message(
            f"✅ Assigned {role.mention}. Welcome!", ephemeral=True
        )
        logger.info(
            "Assigned role %s to %s in %s via role prompt",
            role.id,
            self.member,
            self.member.guild,
        )
        if self.view is not None:
            self.view.stop()


class RolePromptView(discord.ui.View):
    """View container for the role prompt select menu."""

    def __init__(self, member: discord.Member, options: Iterable[RolePromptOption]):
        super().__init__(timeout=600)
        select = RolePromptSelect(member, options)
        if select.options:
            self.add_item(select)


class MemberEvents(commands.Cog):
    """Events related to member join/leave."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _fetch_guild_settings(self, guild_id: int) -> Optional[Dict[str, Any]]:
        if not await database.ensure_connected():
            return None
        collection = await database.get_collection("guilds")
        if not collection:
            return None
        return await collection.find_one({"_id": guild_id})

    async def _fetch_role_prompt(self, guild_id: int) -> Optional[Dict[str, Any]]:
        if not await database.ensure_connected():
            return None
        collection = await database.get_collection(COLLECTIONS["guild_configs"])
        if not collection:
            return None
        config = await collection.find_one({"guild_id": guild_id})
        if not config:
            return None
        return config.get("role_prompt")

    @staticmethod
    def _should_prompt_member(member: discord.Member) -> bool:
        """Return True if the member has no manageable roles yet."""
        manageable_roles = [role for role in member.roles[1:] if not role.is_default()]
        return len(manageable_roles) == 0

    @staticmethod
    def _build_prompt_options(
        guild: discord.Guild, prompt_config: Dict[str, Any]
    ) -> list[RolePromptOption]:
        options: list[RolePromptOption] = []
        for option_data in prompt_config.get("options", []):
            role = guild.get_role(option_data.get("role_id", 0))
            if not role:
                continue
            options.append(
                RolePromptOption(
                    role_id=role.id,
                    label=option_data.get("label", role.name),
                    description=option_data.get("description"),
                    emoji=option_data.get("emoji"),
                )
            )
        return options

    @staticmethod
    def _prepare_prompt_embed(
        member: discord.Member, prompt_config: Dict[str, Any]
    ) -> discord.Embed:
        title = prompt_config.get(
            "title",
            "You must only select your assigned role. Any unauthorized role will result in equity policy action",
        )
        description = prompt_config.get(
            "description",
            "Select the role that matches your tournament registration.",
        )
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blurple(),
        )
        embed.set_author(name=member.guild.name)
        embed.set_footer(text="You will receive the selected role immediately")
        return embed

    async def _send_role_prompt(
        self,
        member: discord.Member,
        guild_settings: Optional[Dict[str, Any]],
    ) -> None:
        prompt_config = await self._fetch_role_prompt(member.guild.id)
        if not prompt_config or not prompt_config.get("enabled"):
            return

        options = self._build_prompt_options(member.guild, prompt_config)
        if not options:
            logger.debug(
                "Role prompt skipped for %s - no valid options configured", member
            )
            return

        if not self._should_prompt_member(member):
            logger.debug(
                "Role prompt skipped for %s - member already has roles", member
            )
            return

        embed = self._prepare_prompt_embed(member, prompt_config)
        view = RolePromptView(member, options)

        sent = False
        try:
            await member.send(embed=embed, view=view)
            sent = True
        except discord.Forbidden:
            logger.info(
                "Could not DM role prompt to %s, attempting server channel", member
            )

        if sent:
            return

        channel: Optional[discord.abc.GuildChannel] = None
        if guild_settings and "welcome_channel" in guild_settings:
            channel = member.guild.get_channel(guild_settings["welcome_channel"])
        if not channel:
            channel = member.guild.system_channel
        if not channel:
            for candidate in member.guild.text_channels:
                if candidate.permissions_for(member.guild.me).send_messages:
                    channel = candidate
                    break

        if (
            channel
            and isinstance(channel, Messageable)
            and channel.permissions_for(member.guild.me).send_messages
        ):
            message_channel = cast(Messageable, channel)
            await message_channel.send(content=member.mention, embed=embed, view=view)
        else:
            logger.warning(
                "Unable to deliver role prompt for %s - no accessible channel",
                member,
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle new member joins."""
        try:
            guild_settings = await self._fetch_guild_settings(member.guild.id)
            if not guild_settings:
                logger.debug(
                    "No guild settings found for %s - skipping auto-role and prompts",
                    member.guild.id,
                )
                return

            role_id = guild_settings.get("autorole")
            if role_id:
                role = member.guild.get_role(role_id)
                if role and role < member.guild.me.top_role:  # type: ignore[operator]
                    try:
                        await member.add_roles(role, reason="Auto-role assignment")
                        logger.info(
                            "Assigned auto-role %s to %s in %s",
                            role.id,
                            member,
                            member.guild,
                        )
                    except discord.Forbidden:
                        logger.warning(
                            "Cannot assign auto-role %s in %s - insufficient permissions",
                            role.id,
                            member.guild,
                        )
                    except Exception as exc:  # pylint: disable=broad-exception-caught
                        logger.error("Error assigning auto-role: %s", exc)

            welcome_channel_id = guild_settings.get("welcome_channel")
            channel = (
                member.guild.get_channel(welcome_channel_id)
                if welcome_channel_id
                else None
            )
            if (
                channel
                and isinstance(channel, Messageable)
                and channel.permissions_for(member.guild.me).send_messages
            ):
                language = guild_settings.get("language", "english")
                welcome_msg = (
                    f"🎉 স্বাগতম {member.mention}! {member.guild.name} এ যোগ দেওয়ার জন্য ধন্যবাদ।"
                    if language == "bangla"
                    else f"🎉 Welcome {member.mention}! Thanks for joining {member.guild.name}."
                )
                embed = discord.Embed(
                    title="👋 New Member!",
                    description=welcome_msg,
                    color=discord.Color.green(),
                    timestamp=member.joined_at,
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(
                    name="Member Count",
                    value=member.guild.member_count,
                    inline=True,
                )

                message_channel = cast(Messageable, channel)
                try:
                    await message_channel.send(embed=embed)
                except discord.Forbidden:
                    logger.warning(
                        "Cannot send welcome message in %s - no permission",
                        message_channel,
                    )
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    logger.error("Error sending welcome message: %s", exc)

            await self._send_role_prompt(member, guild_settings)

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Error in on_member_join: %s", exc, exc_info=True)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Handle member leaves."""
        try:
            guild_settings = await self._fetch_guild_settings(member.guild.id)
            if not guild_settings or "goodbye_channel" not in guild_settings:
                return

            channel = member.guild.get_channel(guild_settings["goodbye_channel"])
            if (
                not channel
                or not isinstance(channel, Messageable)
                or not channel.permissions_for(member.guild.me).send_messages
            ):
                return

            language = guild_settings.get("language", "english")
            goodbye_msg = (
                f"👋 {member.display_name} চলে গেছেন। আমরা তাদের মিস করব!"
                if language == "bangla"
                else f"👋 {member.display_name} has left the server. We'll miss them!"
            )
            embed = discord.Embed(
                title="📤 Member Left",
                description=goodbye_msg,
                color=discord.Color.red(),
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(
                name="Member Count",
                value=member.guild.member_count,
                inline=True,
            )

            message_channel = cast(Messageable, channel)
            try:
                await message_channel.send(embed=embed)
            except discord.Forbidden:
                logger.warning(
                    "Cannot send goodbye message - no permission in %s",
                    message_channel,
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error("Error sending goodbye message: %s", exc)

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Error in on_member_remove: %s", exc, exc_info=True)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Handle bot joining a new guild."""
        logger.info("Joined new guild: %s (ID: %s)", guild.name, guild.id)

        bot_name = self.bot.user.name if self.bot.user else "Hear! Hear! Bot"
        embed = discord.Embed(
            title=f"🎉 Thanks for adding {bot_name}!",
            description="I'm here to help with debate timing, motions, and tournament management.",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="🚀 Get Started",
            value="Use `.help` to see all available commands",
            inline=False,
        )
        embed.add_field(
            name="⚙️ Setup",
            value=(
                "• Use `.setlanguage` to set your preferred language\n"
                "• Use `.autorole` to set auto-role for new members\n"
                "• Use `/roleprompt add-option` to configure the join role selector"
            ),
            inline=False,
        )

        channel = guild.system_channel
        if not channel or not isinstance(channel, Messageable):
            for candidate in guild.text_channels:
                if candidate.permissions_for(guild.me).send_messages:
                    channel = candidate
                    break

        if channel and isinstance(channel, Messageable):
            try:
                await cast(Messageable, channel).send(embed=embed)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error("Error sending welcome message to new guild: %s", exc)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Handle bot leaving a guild."""
        logger.info("Left guild: %s (ID: %s)", guild.name, guild.id)

        try:
            if await database.ensure_connected():
                collection = await database.get_collection("guilds")
                if collection:
                    await collection.update_one(
                        {"_id": guild.id},
                        {"$set": {"inactive": True}},
                        upsert=True,
                    )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Error cleaning up guild data: %s", exc)


async def setup(bot: commands.Bot):
    await bot.add_cog(MemberEvents(bot))
