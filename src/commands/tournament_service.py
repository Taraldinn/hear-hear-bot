"""
Service helpers for tournament setup.

This module contains the core logic for creating roles, channels, and
permissions for tournaments. It is imported by the TournamentSetup cog
to keep the main command module small and readable.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional

import discord

from .tournament_views import TournamentRoleView

logger = logging.getLogger(__name__)


async def create_tournament_roles(guild: discord.Guild) -> Dict[str, discord.Role]:
    """Create tournament roles if they don't exist."""
    roles: Dict[str, discord.Role] = {}

    role_configs = {
        "debater": {
            "name": "Debater",
            "color": discord.Color.blue(),
            "permissions": discord.Permissions(
                read_messages=True,
                send_messages=True,
                connect=True,
                speak=True,
                use_voice_activation=True,
            ),
        },
        "adjudicator": {
            "name": "Adjudicator",
            "color": discord.Color.gold(),
            "permissions": discord.Permissions(
                read_messages=True,
                send_messages=True,
                connect=True,
                speak=True,
                use_voice_activation=True,
                mute_members=True,
                deafen_members=True,
            ),
        },
        "spectator": {
            "name": "Spectator",
            "color": discord.Color.light_grey(),
            "permissions": discord.Permissions(
                read_messages=True, send_messages=False, connect=False, speak=False
            ),
        },
    }

    for role_key, config in role_configs.items():
        existing_role = discord.utils.get(guild.roles, name=config["name"])
        if existing_role:
            roles[role_key] = existing_role
            logger.info("Role %s already exists", config["name"])
        else:
            role = await guild.create_role(
                name=config["name"],
                color=config["color"],
                permissions=config["permissions"],
                reason="Tournament setup - creating tournament roles",
            )
            roles[role_key] = role
            logger.info("Created role: %s", config["name"])
            await asyncio.sleep(0.5)

    return roles


async def create_general_channels(
    guild: discord.Guild, _roles: Dict[str, discord.Role]
) -> Dict[str, discord.TextChannel]:
    """Create general tournament channels."""
    channels: Dict[str, discord.TextChannel] = {}

    channel_structure = {
        "Welcome": {
            "channels": [
                ("welcome", "Welcome to the tournament!"),
                ("instructions-for-teams", "Important instructions for team members"),
                ("instructions-for-adjudicators", "Guidelines for adjudicators"),
                ("equity-policy", "Tournament equity and safety policies"),
                ("report-problems", "Report any issues here"),
                ("role-assignment", "React to get your tournament role"),
            ]
        },
        "Info Desk": {
            "channels": [
                ("bot-commands", "Use bot commands here"),
                ("schedules", "Tournament schedules and timing"),
                ("tech-support", "Technical assistance"),
            ]
        },
        "Feedback & Check-in": {
            "channels": [
                ("feedback-submission", "Submit feedback and evaluations"),
                ("check-in", "Check in for rounds"),
                ("check-out", "Check out after rounds"),
            ]
        },
        "Grand Auditorium": {
            "channels": [
                ("announcements", "Official tournament announcements"),
                ("motion-clarifications", "Motion clarifications and questions"),
                ("draws-and-motion-release", "Round draws and motion releases"),
                ("equity-announcements", "Equity and safety announcements"),
                ("music-control", "Music and entertainment"),
                ("important-links", "Important links and resources"),
                ("auditorium-text", "General auditorium chat"),
            ]
        },
    }

    for category_name, category_data in channel_structure.items():
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(
                name=category_name,
                reason="Tournament setup - creating general channels",
            )
            logger.info("Created category: %s", category_name)
            await asyncio.sleep(0.5)

        for channel_name, description in category_data["channels"]:
            existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
            if not existing_channel:
                channel = await guild.create_text_channel(
                    name=channel_name,
                    category=category,
                    topic=description,
                    reason="Tournament setup - creating general channels",
                )
                channels[channel_name.replace("-", "_")] = channel
                logger.info("Created channel: #%s", channel_name)

                if channel_name == "role-assignment":
                    await channel.set_permissions(
                        guild.default_role,
                        read_messages=True,
                        send_messages=False,
                        add_reactions=True,
                        read_message_history=True,
                    )
                    logger.info("Set role-assignment channel permissions for everyone")
                elif category_name == "Welcome":
                    await channel.set_permissions(
                        guild.default_role,
                        read_messages=True,
                        send_messages=False,
                        add_reactions=False,
                    )
                    logger.info("Set welcome channel permissions for #%s", channel_name)
                else:
                    await channel.set_permissions(
                        guild.default_role, read_messages=False, send_messages=False
                    )
                    logger.info("Set hidden channel permissions for #%s", channel_name)

                await asyncio.sleep(0.5)
                await asyncio.sleep(0.5)
            else:
                channels[channel_name.replace("-", "_")] = existing_channel

    return channels


async def create_venue_channels(
    guild: discord.Guild,
    tournament_type: str,
    venues: int,
    _roles: Dict[str, discord.Role],
) -> List[Dict]:
    """Create venue-specific channels."""
    venue_channels: List[Dict[str, object]] = []

    for venue_num in range(1, venues + 1):
        venue_data: Dict[str, object] = {}

        category_name = f"Venue {venue_num}"
        category = await guild.create_category(
            name=category_name, reason=f"Tournament setup - creating venue {venue_num}"
        )
        await asyncio.sleep(0.5)

        debate_text = await guild.create_text_channel(
            name=f"venue-{venue_num}-debate",
            category=category,
            topic=f"Debate discussion for venue {venue_num}",
            reason=f"Tournament setup - venue {venue_num} text channel",
        )
        venue_data["debate_text"] = debate_text
        await asyncio.sleep(0.5)

        debate_voice = await guild.create_voice_channel(
            name=f"Venue-{venue_num}-Debate",
            category=category,
            reason=f"Tournament setup - venue {venue_num} main voice",
        )
        venue_data["debate_voice"] = debate_voice
        await asyncio.sleep(0.5)

        if tournament_type == "AP":
            prep_rooms = [
                (f"Venue-{venue_num}-Gov-Prep", 3),
                (f"Venue-{venue_num}-Opp-Prep", 3),
            ]
        else:
            prep_rooms = [
                (f"Venue-{venue_num}-OG-Prep", 2),
                (f"Venue-{venue_num}-OO-Prep", 2),
                (f"Venue-{venue_num}-CG-Prep", 2),
                (f"Venue-{venue_num}-CO-Prep", 2),
            ]

        venue_data["prep_rooms"] = []  # type: ignore[assignment]
        for room_name, user_limit in prep_rooms:
            prep_room = await guild.create_voice_channel(
                name=room_name,
                category=category,
                user_limit=user_limit,
                reason=f"Tournament setup - {room_name}",
            )
            prep_list = venue_data.get("prep_rooms")
            if isinstance(prep_list, list):
                prep_list.append(prep_room)
            else:
                venue_data["prep_rooms"] = [prep_room]
            await asyncio.sleep(0.5)

        result_room = await guild.create_voice_channel(
            name=f"Venue-{venue_num}-Result-Discussion",
            category=category,
            reason=f"Tournament setup - venue {venue_num} result discussion",
        )
        venue_data["result_room"] = result_room
        await asyncio.sleep(0.5)

        venue_channels.append(venue_data)
        logger.info("Created venue %s with %d prep rooms", venue_num, len(prep_rooms))

    return venue_channels


async def setup_permissions(
    guild: discord.Guild,
    roles: Dict[str, discord.Role],
    general_channels: Dict,
    venue_channels: List[Dict],
) -> None:
    """Setup permissions for all channels and roles."""
    logger.info("Setting up comprehensive channel permissions...")

    if not roles:
        logger.warning("No roles provided, skipping permission setup")
        return

    debater_role = roles.get("debater")
    adjudicator_role = roles.get("adjudicator")
    spectator_role = roles.get("spectator")

    welcome_categories = ["Welcome"]
    grand_auditorium_categories = ["Grand Auditorium"]
    restricted_categories = ["Info Desk", "Feedback & Check-in"]

    for category in guild.categories:
        if category.name in welcome_categories:
            await category.set_permissions(
                guild.default_role, read_messages=True, send_messages=False
            )
            logger.info("✅ Set welcome category permissions for %s", category.name)
        elif category.name in grand_auditorium_categories:
            await category.set_permissions(guild.default_role, read_messages=False)
            for role in [debater_role, adjudicator_role, spectator_role]:
                if role:
                    await category.set_permissions(
                        role, read_messages=True, send_messages=True
                    )
            logger.info(
                "✅ Set Grand Auditorium permissions (open for all role holders)"
            )
        elif category.name in restricted_categories:
            await category.set_permissions(guild.default_role, read_messages=False)
            for role in [debater_role, adjudicator_role, spectator_role]:
                if role:
                    await category.set_permissions(
                        role, read_messages=True, send_messages=True
                    )
            logger.info("✅ Set restricted category permissions for %s", category.name)
        elif category.name and "venue" in category.name.lower():
            await category.set_permissions(guild.default_role, view_channel=False)
            for role in [debater_role, adjudicator_role, spectator_role]:
                if role:
                    await category.set_permissions(role, view_channel=True)
            logger.info("✅ Set venue category permissions for %s", category.name)

        await asyncio.sleep(0.2)

    for channel_key, channel in general_channels.items():
        if channel_key == "role_assignment":
            await channel.set_permissions(
                guild.default_role,
                read_messages=True,
                send_messages=False,
                add_reactions=True,
                read_message_history=True,
            )
            await channel.set_permissions(
                guild.me,
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                add_reactions=True,
            )
            logger.info("✅ Set role-assignment channel permissions")
        elif channel_key in (
            "welcome",
            "instructions_for_teams",
            "instructions_for_adjudicators",
            "equity_policy",
        ):
            await channel.set_permissions(
                guild.default_role,
                read_messages=True,
                send_messages=False,
                add_reactions=False,
            )
            logger.info("✅ Set welcome channel permissions for %s", channel_key)
        else:
            await channel.set_permissions(
                guild.default_role, read_messages=False, send_messages=False
            )
            for role in [debater_role, adjudicator_role, spectator_role]:
                if role:
                    can_send = True
                    if role == spectator_role:
                        can_send = channel_key in [
                            "feedback_submission",
                            "report_problems",
                            "general",
                            "announcements",
                        ]
                    await channel.set_permissions(
                        role,
                        read_messages=True,
                        send_messages=can_send,
                        add_reactions=True,
                    )
            logger.info(
                "✅ Set permissions for %s (open for all role holders)", channel_key
            )

        await asyncio.sleep(0.2)

    for i, venue_data in enumerate(venue_channels, 1):
        logger.info("Setting permissions for Venue %s...", i)

        if "text_channel" in venue_data:
            text_channel = venue_data["text_channel"]
            await text_channel.set_permissions(guild.default_role, read_messages=False)
            for role in [debater_role, adjudicator_role, spectator_role]:
                if role:
                    can_send = role != spectator_role
                    await text_channel.set_permissions(
                        role,
                        read_messages=True,
                        send_messages=can_send,
                        add_reactions=True,
                    )
            logger.info(
                "✅ Set text channel permissions for Venue %s (open for all)", i
            )
            await asyncio.sleep(0.2)

        if "debate_voice" in venue_data:
            voice_channel = venue_data["debate_voice"]
            await voice_channel.set_permissions(
                guild.default_role, view_channel=False, connect=False
            )
            for role in [debater_role, adjudicator_role]:
                if role:
                    await voice_channel.set_permissions(
                        role,
                        view_channel=True,
                        connect=True,
                        speak=True,
                        use_voice_activation=True,
                    )
            if spectator_role:
                await voice_channel.set_permissions(
                    spectator_role, view_channel=True, connect=True, speak=False
                )
            logger.info(
                "✅ Set main voice channel permissions for Venue %s (open for all)", i
            )
            await asyncio.sleep(0.2)

        prep_rooms = venue_data.get("prep_rooms", [])
        for j, prep_room in enumerate(prep_rooms, 1):
            await prep_room.set_permissions(
                guild.default_role, view_channel=False, connect=False
            )
            if debater_role:
                await prep_room.set_permissions(
                    debater_role,
                    view_channel=True,
                    connect=True,
                    speak=True,
                    use_voice_activation=True,
                )
            for role in [adjudicator_role, spectator_role]:
                if role:
                    await prep_room.set_permissions(
                        role, view_channel=False, connect=False
                    )
            logger.info(
                "✅ Set prep room %s permissions for Venue %s (debaters only)", j, i
            )
            await asyncio.sleep(0.2)

        if "result_room" in venue_data:
            result_room = venue_data["result_room"]
            await result_room.set_permissions(
                guild.default_role, view_channel=False, connect=False
            )
            if adjudicator_role:
                await result_room.set_permissions(
                    adjudicator_role,
                    view_channel=True,
                    connect=True,
                    speak=True,
                    use_voice_activation=True,
                )
            for role in [debater_role, spectator_role]:
                if role:
                    await result_room.set_permissions(
                        role, view_channel=False, connect=False
                    )
            logger.info("✅ Set result discussion permissions for Venue %s", i)
            await asyncio.sleep(0.2)

    logger.info("🎉 All channel permissions setup completed successfully!")


async def setup_role_assignment(
    guild: discord.Guild, roles: Dict[str, discord.Role], channels: Dict
) -> Optional[discord.Message]:
    """Setup role assignment with interactive buttons."""

    if not roles or "role_assignment" not in channels:
        return None

    role_channel: discord.TextChannel = channels["role_assignment"]

    embed = discord.Embed(
        title="🎭 Tournament Role Assignment",
        description=(
            "Click the button below to select your tournament role!\n\n"
            "**Note:** Until you select a role, most channels will be hidden from you."
        ),
        color=discord.Color.blue(),
    )

    role_info: List[str] = []
    available_roles: List[str] = []

    if roles.get("debater"):
        role_info.append("🥊 **Debater** - Participate in debates, access prep rooms")
        available_roles.append("debater")

    if roles.get("adjudicator"):
        role_info.append("⚖️ **Adjudicator** - Judge debates, access result discussions")
        available_roles.append("adjudicator")

    if roles.get("spectator"):
        role_info.append("👀 **Spectator** - Watch the tournament, read-only access")
        available_roles.append("spectator")

    embed.add_field(name="Available Roles", value="\n".join(role_info), inline=False)
    embed.add_field(
        name="How to get your role",
        value=(
            "1. Click the **Select Role** button below\n"
            "2. Choose your desired role from the dropdown\n"
            "3. Channels will become visible based on your role\n"
            "4. You can change your role anytime by clicking the button again"
        ),
        inline=False,
    )
    embed.set_footer(text="Role assignment powered by Hear! Hear! Bot")

    view = TournamentRoleView(guild.id)
    role_msg = await role_channel.send(embed=embed, view=view)

    logger.info(
        "Created role assignment message with %d role options", len(available_roles)
    )
    return role_msg


async def send_welcome_message(
    guild: discord.Guild, member: discord.Member, role_name: str
) -> None:
    """Send welcome message to the welcome channel when user gets a role."""
    try:
        welcome_channel = discord.utils.get(guild.text_channels, name="welcome")
        if not welcome_channel:
            logger.warning("Welcome channel not found for welcome message")
            return

        embed = discord.Embed(
            title="🎉 Welcome to the Tournament!", color=discord.Color.green()
        )

        role_messages = {
            "Debater": {
                "description": (
                    f"Welcome {member.mention}! You've successfully registered as a "
                    f"**Debater**."
                ),
                "fields": [
                    (
                        "🥊 What you can do:",
                        (
                            "• Participate in debates\n• Access prep rooms\n"
                            "• Submit feedback\n• Check in/out for rounds"
                        ),
                        False,
                    ),
                    (
                        "📍 Next Steps:",
                        (
                            "• Check the schedules channel for round timings\n"
                            "• Join your assigned prep room when called\n"
                            "• Follow equity guidelines"
                        ),
                        False,
                    ),
                ],
            },
            "Adjudicator": {
                "description": (
                    f"Welcome {member.mention}! You've successfully registered as an "
                    f"**Adjudicator**."
                ),
                "fields": [
                    (
                        "⚖️ What you can do:",
                        (
                            "• Judge debates\n• Access result discussion rooms\n"
                            "• Monitor prep rooms\n• Review feedback"
                        ),
                        False,
                    ),
                    (
                        "📍 Next Steps:",
                        (
                            "• Check the schedules channel for your assignments\n"
                            "• Review adjudication guidelines\n"
                            "• Join result rooms after rounds"
                        ),
                        False,
                    ),
                ],
            },
            "Spectator": {
                "description": (
                    f"Welcome {member.mention}! You've successfully registered as a "
                    f"**Spectator**."
                ),
                "fields": [
                    (
                        "👀 What you can do:",
                        (
                            "• Watch debates\n• Submit feedback\n"
                            "• Participate in general chat\n• Access tournament information"
                        ),
                        False,
                    ),
                    (
                        "📍 Next Steps:",
                        (
                            "• Check the schedules channel for round timings\n"
                            "• Follow tournament updates in announcements\n"
                            "• Enjoy the debates!"
                        ),
                        False,
                    ),
                ],
            },
        }

        message_data = role_messages.get(
            role_name,
            {
                "description": (
                    f"Welcome {member.mention}! You've been assigned the **{role_name}** role."
                ),
                "fields": [
                    (
                        "📍 Next Steps:",
                        "Check the relevant channels for more information.",
                        False,
                    )
                ],
            },
        )

        embed.description = message_data["description"]
        for field_name, field_value, inline in message_data["fields"]:
            embed.add_field(name=field_name, value=field_value, inline=inline)

        embed.add_field(
            name="🔄 Need to change your role?",
            value="Simply react with a different emoji in the role-assignment channel!",
            inline=False,
        )
        embed.add_field(
            name="👀 Can't see new channels?",
            value=(
                "• **Desktop**: Press `Ctrl+R` (Windows) or `Cmd+R` (Mac) to refresh\n"
                "• **Mobile**: Pull down to refresh or restart the app\n"
                "• New channels should appear in a few seconds!"
            ),
            inline=False,
        )

        embed.set_footer(text="Good luck in the tournament! 🏆")
        embed.timestamp = discord.utils.utcnow()
        await welcome_channel.send(embed=embed)
        logger.info("Sent welcome message for %s as %s", member.display_name, role_name)
    except discord.HTTPException as exc:  # pragma: no cover - logging only
        logger.error("Error sending welcome message: %s", exc)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Unexpected error sending welcome message: %s", exc)
