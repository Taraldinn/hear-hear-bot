"""
Tournament Setup System for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com

Creates tournament venues, roles, and channels for debate tournaments
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
from typing import Dict, List, Optional, Literal
from datetime import datetime

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
        tournament_type="Type of debate format (AP = Asian Parliamentary, BP = British Parliamentary)",
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

        try:
            embed = discord.Embed(
                title="🏆 Creating Tournament Setup",
                description=f"Setting up {tournament_type} tournament with {venues} venues...",
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )

            progress_msg = await interaction.followup.send(embed=embed)

            # Step 1: Create roles if requested
            roles = {}
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
                await progress_msg.edit(embed=embed)
                roles = await self.create_tournament_roles(guild)

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
            await progress_msg.edit(embed=embed)
            general_channels = await self.create_general_channels(guild, roles)

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
            await progress_msg.edit(embed=embed)
            venue_channels = await self.create_venue_channels(
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
            await progress_msg.edit(embed=embed)
            await self.setup_permissions(guild, roles, general_channels, venue_channels)

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
                await progress_msg.edit(embed=embed)
                role_assignment_msg = await self.setup_role_assignment(
                    guild, roles, general_channels
                )

            # Final success message
            success_embed = discord.Embed(
                title="✅ Tournament Setup Complete!",
                description=f"Successfully created {tournament_type} tournament with {venues} venues",
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
                    value=f"Check {general_channels.get('role_assignment', '#role-assignment')} to get your role!",
                    inline=False,
                )

            success_embed.set_footer(
                text="Tournament is ready! Good luck to all participants!"
            )

            await progress_msg.edit(embed=success_embed)

        except discord.Forbidden as e:
            logger.error(f"Permission error during tournament setup: {e}")

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
            except:
                await interaction.followup.send(embed=error_embed, ephemeral=True)

        except discord.HTTPException as e:
            logger.error(f"Discord API error during tournament setup: {e}")

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
            except:
                await interaction.followup.send(embed=error_embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Failed to create tournament: {e}")
            error_embed = discord.Embed(
                title="❌ Tournament Setup Failed",
                description=f"Error: {str(e)}",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    async def create_tournament_roles(
        self, guild: discord.Guild
    ) -> Dict[str, discord.Role]:
        """Create tournament roles if they don't exist"""
        roles = {}

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
            # Check if role already exists
            existing_role = discord.utils.get(guild.roles, name=config["name"])
            if existing_role:
                roles[role_key] = existing_role
                logger.info(f"Role {config['name']} already exists")
            else:
                # Create new role
                role = await guild.create_role(
                    name=config["name"],
                    color=config["color"],
                    permissions=config["permissions"],
                    reason="Tournament setup - creating tournament roles",
                )
                roles[role_key] = role
                logger.info(f"Created role: {config['name']}")

                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)

        return roles

    async def create_general_channels(
        self, guild: discord.Guild, roles: Dict[str, discord.Role]
    ) -> Dict[str, discord.TextChannel]:
        """Create general tournament channels"""
        channels = {}

        # Channel categories and their channels
        channel_structure = {
            "Welcome": {
                "channels": [
                    ("welcome", "Welcome to the tournament!"),
                    (
                        "instructions-for-teams",
                        "Important instructions for team members",
                    ),
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
            # Create category if it doesn't exist
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                category = await guild.create_category(
                    name=category_name,
                    reason="Tournament setup - creating general channels",
                )
                logger.info(f"Created category: {category_name}")
                await asyncio.sleep(0.5)

            # Create channels in category
            for channel_name, description in category_data["channels"]:
                existing_channel = discord.utils.get(
                    guild.text_channels, name=channel_name
                )
                if not existing_channel:
                    channel = await guild.create_text_channel(
                        name=channel_name,
                        category=category,
                        topic=description,
                        reason="Tournament setup - creating general channels",
                    )
                    channels[channel_name.replace("-", "_")] = channel
                    logger.info(f"Created channel: #{channel_name}")

                    # Set initial permissions for role-assignment channel
                    if channel_name == "role-assignment":
                        # Everyone can see and react in role-assignment channel
                        await channel.set_permissions(
                            guild.default_role,
                            read_messages=True,
                            send_messages=False,
                            add_reactions=True,
                            read_message_history=True,
                        )
                        logger.info(
                            "Set role-assignment channel permissions for everyone"
                        )
                    elif category_name == "Welcome":
                        # Welcome channels are visible to everyone but read-only
                        await channel.set_permissions(
                            guild.default_role,
                            read_messages=True,
                            send_messages=False,
                            add_reactions=False,
                        )
                        logger.info(
                            f"Set welcome channel permissions for #{channel_name}"
                        )
                    else:
                        # Other channels are hidden until user gets a role
                        await channel.set_permissions(
                            guild.default_role, read_messages=False, send_messages=False
                        )
                        logger.info(
                            f"Set hidden channel permissions for #{channel_name}"
                        )

                    await asyncio.sleep(0.5)
                    await asyncio.sleep(0.5)
                else:
                    channels[channel_name.replace("-", "_")] = existing_channel

        return channels

    async def create_venue_channels(
        self,
        guild: discord.Guild,
        tournament_type: str,
        venues: int,
        roles: Dict[str, discord.Role],
    ) -> List[Dict]:
        """Create venue-specific channels"""
        venue_channels = []

        for venue_num in range(1, venues + 1):
            venue_data = {}

            # Create venue category
            category_name = f"Venue {venue_num}"
            category = await guild.create_category(
                name=category_name,
                reason=f"Tournament setup - creating venue {venue_num}",
            )
            await asyncio.sleep(0.5)

            # Create debate text channel
            debate_text = await guild.create_text_channel(
                name=f"venue-{venue_num}-debate",
                category=category,
                topic=f"Debate discussion for venue {venue_num}",
                reason=f"Tournament setup - venue {venue_num} text channel",
            )
            venue_data["debate_text"] = debate_text
            await asyncio.sleep(0.5)

            # Create main debate voice channel
            debate_voice = await guild.create_voice_channel(
                name=f"Venue-{venue_num}-Debate",
                category=category,
                reason=f"Tournament setup - venue {venue_num} main voice",
            )
            venue_data["debate_voice"] = debate_voice
            await asyncio.sleep(0.5)

            # Create prep rooms based on tournament type
            if tournament_type == "AP":
                # Asian Parliamentary: Gov and Opp prep rooms
                prep_rooms = [
                    (f"Venue-{venue_num}-Gov-Prep", 3),
                    (f"Venue-{venue_num}-Opp-Prep", 3),
                ]
            else:  # BP
                # British Parliamentary: OG, OO, CG, CO prep rooms
                prep_rooms = [
                    (f"Venue-{venue_num}-OG-Prep", 2),
                    (f"Venue-{venue_num}-OO-Prep", 2),
                    (f"Venue-{venue_num}-CG-Prep", 2),
                    (f"Venue-{venue_num}-CO-Prep", 2),
                ]

            venue_data["prep_rooms"] = []
            for room_name, user_limit in prep_rooms:
                prep_room = await guild.create_voice_channel(
                    name=room_name,
                    category=category,
                    user_limit=user_limit,
                    reason=f"Tournament setup - {room_name}",
                )
                venue_data["prep_rooms"].append(prep_room)
                await asyncio.sleep(0.5)

            # Create result discussion room
            result_room = await guild.create_voice_channel(
                name=f"Venue-{venue_num}-Result-Discussion",
                category=category,
                reason=f"Tournament setup - venue {venue_num} result discussion",
            )
            venue_data["result_room"] = result_room
            await asyncio.sleep(0.5)

            venue_channels.append(venue_data)
            logger.info(f"Created venue {venue_num} with {len(prep_rooms)} prep rooms")

        return venue_channels

    async def setup_permissions(
        self,
        guild: discord.Guild,
        roles: Dict[str, discord.Role],
        general_channels: Dict,
        venue_channels: List[Dict],
    ):
        """Setup permissions for all channels and roles"""
        logger.info("Setting up comprehensive channel permissions...")

        if not roles:
            logger.warning("No roles provided, skipping permission setup")
            return

        debater_role = roles.get("debater")
        adjudicator_role = roles.get("adjudicator")
        spectator_role = roles.get("spectator")

        # Setup category permissions first
        welcome_categories = ["Welcome"]
        restricted_categories = ["Info Desk", "Feedback & Check-in", "Grand Auditorium"]
        
        for category in guild.categories:
            if category.name in welcome_categories:
                # Welcome categories: visible to everyone
                await category.set_permissions(
                    guild.default_role,
                    read_messages=True,
                    send_messages=False
                )
                logger.info(f"✅ Set welcome category permissions for {category.name}")
                
            elif category.name in restricted_categories:
                # Restricted categories: hidden from @everyone, visible to role holders
                await category.set_permissions(
                    guild.default_role,
                    read_messages=False
                )
                
                # Grant access to role holders
                for role in [debater_role, adjudicator_role, spectator_role]:
                    if role:
                        await category.set_permissions(
                            role,
                            read_messages=True,
                            send_messages=True
                        )
                        
                logger.info(f"✅ Set restricted category permissions for {category.name}")
                
            elif category.name and "venue" in category.name.lower():
                # Venue categories: accessible to participants
                await category.set_permissions(
                    guild.default_role,
                    view_channel=False
                )
                
                for role in [debater_role, adjudicator_role]:
                    if role:
                        await category.set_permissions(
                            role,
                            view_channel=True
                        )
                        
                if spectator_role:
                    await category.set_permissions(
                        spectator_role,
                        view_channel=True
                    )
                    
                logger.info(f"✅ Set venue category permissions for {category.name}")
            
            await asyncio.sleep(0.2)

        # Setup permissions for general channels
        for channel_key, channel in general_channels.items():
            if channel_key == "role_assignment":
                # Role assignment: Visible to everyone, reactions only
                await channel.set_permissions(
                    guild.default_role,
                    read_messages=True,
                    send_messages=False,
                    add_reactions=True,
                    read_message_history=True,
                )
                # Bot can manage the channel
                await channel.set_permissions(
                    guild.me,
                    read_messages=True,
                    send_messages=True,
                    manage_messages=True,
                    add_reactions=True,
                )
                logger.info("✅ Set role-assignment channel permissions")

            elif channel_key in [
                "welcome",
                "instructions_for_teams",
                "instructions_for_adjudicators",
                "equity_policy",
            ]:
                # Welcome channels: Everyone can read
                await channel.set_permissions(
                    guild.default_role,
                    read_messages=True,
                    send_messages=False,
                    add_reactions=False,
                )
                logger.info(f"✅ Set welcome channel permissions for {channel_key}")

            else:
                # Other channels: Hidden from @everyone, visible to role holders
                await channel.set_permissions(
                    guild.default_role, read_messages=False, send_messages=False
                )

                # Debaters get access to most channels
                if debater_role:
                    await channel.set_permissions(
                        debater_role,
                        read_messages=True,
                        send_messages=True,
                        add_reactions=True,
                    )

                # Adjudicators get access (no moderation powers)
                if adjudicator_role:
                    await channel.set_permissions(
                        adjudicator_role,
                        read_messages=True,
                        send_messages=True,
                        add_reactions=True,
                    )

                # Spectators get limited access
                if spectator_role:
                    can_send = channel_key in ["feedback_submission", "report_problems"]
                    await channel.set_permissions(
                        spectator_role,
                        read_messages=True,
                        send_messages=can_send,
                        add_reactions=True,
                    )

                logger.info(f"✅ Set permissions for {channel_key}")

            await asyncio.sleep(0.2)

        # Setup permissions for venue channels
        for i, venue_data in enumerate(venue_channels, 1):
            logger.info(f"Setting permissions for Venue {i}...")

            # Main debate text channel
            if "text_channel" in venue_data:
                text_channel = venue_data["text_channel"]
                # Hide from @everyone
                await text_channel.set_permissions(
                    guild.default_role, read_messages=False
                )

                # Tournament participants can access
                for role in [debater_role, adjudicator_role]:
                    if role:
                        await text_channel.set_permissions(
                            role,
                            read_messages=True,
                            send_messages=True,
                            add_reactions=True,
                        )

                # Spectators get read-only access
                if spectator_role:
                    await text_channel.set_permissions(
                        spectator_role,
                        read_messages=True,
                        send_messages=False,
                        add_reactions=True,
                    )

                logger.info(f"✅ Set text channel permissions for Venue {i}")
                await asyncio.sleep(0.2)

            # Main debate voice channel
            if "debate_voice" in venue_data:
                voice_channel = venue_data["debate_voice"]
                # Hide from @everyone
                await voice_channel.set_permissions(
                    guild.default_role, view_channel=False, connect=False
                )

                # Debaters can join and speak
                if debater_role:
                    await voice_channel.set_permissions(
                        debater_role,
                        view_channel=True,
                        connect=True,
                        speak=True,
                        use_voice_activation=True,
                    )

                # Adjudicators can join and speak (no moderation powers)
                if adjudicator_role:
                    await voice_channel.set_permissions(
                        adjudicator_role,
                        view_channel=True,
                        connect=True,
                        speak=True,
                        use_voice_activation=True,
                    )

                # Spectators can see but not join
                if spectator_role:
                    await voice_channel.set_permissions(
                        spectator_role, view_channel=True, connect=False
                    )

                logger.info(f"✅ Set main voice channel permissions for Venue {i}")
                await asyncio.sleep(0.2)

            # Prep rooms - debaters and adjudicators only
            prep_rooms = venue_data.get("prep_rooms", [])
            for j, prep_room in enumerate(prep_rooms, 1):
                # Hide from @everyone and spectators
                await prep_room.set_permissions(
                    guild.default_role, view_channel=False, connect=False
                )

                # Debaters can access prep rooms
                if debater_role:
                    await prep_room.set_permissions(
                        debater_role,
                        view_channel=True,
                        connect=True,
                        speak=True,
                        use_voice_activation=True,
                    )

                # Adjudicators can access prep rooms (no moderation powers)
                if adjudicator_role:
                    await prep_room.set_permissions(
                        adjudicator_role,
                        view_channel=True,
                        connect=True,
                        speak=True,
                        use_voice_activation=True,
                    )

                # Explicitly hide from spectators
                if spectator_role:
                    await prep_room.set_permissions(
                        spectator_role, view_channel=False, connect=False
                    )

                logger.info(f"✅ Set prep room {j} permissions for Venue {i}")
                await asyncio.sleep(0.2)

            # Result discussion - adjudicators only
            if "result_room" in venue_data:
                result_room = venue_data["result_room"]
                # Hide from everyone
                await result_room.set_permissions(
                    guild.default_role, view_channel=False, connect=False
                )

                # Only adjudicators can access
                if adjudicator_role:
                    await result_room.set_permissions(
                        adjudicator_role,
                        view_channel=True,
                        connect=True,
                        speak=True,
                        use_voice_activation=True,
                    )

                # Explicitly deny access to others
                for role in [debater_role, spectator_role]:
                    if role:
                        await result_room.set_permissions(
                            role, view_channel=False, connect=False
                        )

                logger.info(f"✅ Set result discussion permissions for Venue {i}")
                await asyncio.sleep(0.2)

        logger.info("🎉 All channel permissions setup completed successfully!")

    async def setup_role_assignment(
        self, guild: discord.Guild, roles: Dict[str, discord.Role], channels: Dict
    ) -> Optional[discord.Message]:
        """Setup role assignment with reactions"""

        if not roles or "role_assignment" not in channels:
            return None

        role_channel = channels["role_assignment"]

        embed = discord.Embed(
            title="🎭 Tournament Role Assignment",
            description="React with the appropriate emoji to get your tournament role!\n\n"
            "**Note:** Until you select a role, most channels will be hidden from you.",
            color=discord.Color.blue(),
        )

        role_info = []
        emoji_roles = []

        if roles.get("debater"):
            role_info.append(
                f"🥊 **Debater** - Participate in debates, access prep rooms"
            )
            emoji_roles.append(("🥊", roles["debater"]))

        if roles.get("adjudicator"):
            role_info.append(
                f"⚖️ **Adjudicator** - Judge debates, access result discussions"
            )
            emoji_roles.append(("⚖️", roles["adjudicator"]))

        if roles.get("spectator"):
            role_info.append(
                f"👀 **Spectator** - Watch the tournament, read-only access"
            )
            emoji_roles.append(("👀", roles["spectator"]))

        embed.add_field(
            name="Available Roles", value="\n".join(role_info), inline=False
        )

        embed.add_field(
            name="How to get your role",
            value="1. React with the emoji for your desired role\n"
            "2. Channels will become visible based on your role\n"
            "3. You can change your role by reacting with a different emoji",
            inline=False,
        )

        embed.set_footer(text="Role assignment powered by Hear! Hear! Bot")

        # Send the role assignment message
        role_msg = await role_channel.send(embed=embed)

        # Add reactions
        for emoji, role in emoji_roles:
            await role_msg.add_reaction(emoji)
            await asyncio.sleep(0.5)

        logger.info(
            f"Created role assignment message with {len(emoji_roles)} role options"
        )
        return role_msg

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle role assignment reactions"""
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        channel = guild.get_channel(payload.channel_id)
        if not channel or channel.name != "role-assignment":
            return

        # Define emoji to role mapping
        emoji_roles = {"🥊": "Debater", "⚖️": "Adjudicator", "👀": "Spectator"}

        emoji = str(payload.emoji)
        if emoji not in emoji_roles:
            return

        # Get the role
        role_name = emoji_roles[emoji]
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            return

        try:
            # Remove other tournament roles first
            tournament_roles = [
                discord.utils.get(guild.roles, name="Debater"),
                discord.utils.get(guild.roles, name="Adjudicator"),
                discord.utils.get(guild.roles, name="Spectator"),
            ]
            tournament_roles = [r for r in tournament_roles if r and r in member.roles]

            if tournament_roles:
                await member.remove_roles(
                    *tournament_roles, reason="Role assignment - removing old roles"
                )

            # Add new role
            await member.add_roles(
                role, reason=f"Role assignment - assigned {role_name}"
            )

            logger.info(f"Assigned {role_name} role to {member.display_name}")

            # Send welcome message to welcome channel
            await self.send_welcome_message(guild, member, role_name)

        except discord.Forbidden:
            logger.error(f"No permission to assign roles to {member.display_name}")
        except Exception as e:
            logger.error(f"Error assigning role to {member.display_name}: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Handle role removal when reaction is removed"""
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        channel = guild.get_channel(payload.channel_id)
        if not channel or channel.name != "role-assignment":
            return

        # Define emoji to role mapping
        emoji_roles = {"🥊": "Debater", "⚖️": "Adjudicator", "👀": "Spectator"}

        emoji = str(payload.emoji)
        if emoji not in emoji_roles:
            return

        # Get the role
        role_name = emoji_roles[emoji]
        role = discord.utils.get(guild.roles, name=role_name)
        if not role or role not in member.roles:
            return

        try:
            await member.remove_roles(
                role, reason=f"Role assignment - removed {role_name}"
            )
            logger.info(f"Removed {role_name} role from {member.display_name}")

        except discord.Forbidden:
            logger.error(f"No permission to remove roles from {member.display_name}")
        except Exception as e:
            logger.error(f"Error removing role from {member.display_name}: {e}")

    async def send_welcome_message(self, guild: discord.Guild, member: discord.Member, role_name: str):
        """Send welcome message to the welcome channel when user gets a role"""
        try:
            # Find the welcome channel
            welcome_channel = discord.utils.get(guild.text_channels, name="welcome")
            if not welcome_channel:
                logger.warning("Welcome channel not found for welcome message")
                return

            # Create role-specific welcome embed
            embed = discord.Embed(
                title="🎉 Welcome to the Tournament!",
                color=discord.Color.green()
            )

            # Role-specific messages
            role_messages = {
                "Debater": {
                    "description": f"Welcome {member.mention}! You've successfully registered as a **Debater**.",
                    "fields": [
                        ("🥊 What you can do:", "• Participate in debates\n• Access prep rooms\n• Submit feedback\n• Check in/out for rounds", False),
                        ("📍 Next Steps:", "• Check the schedules channel for round timings\n• Join your assigned prep room when called\n• Follow equity guidelines", False)
                    ]
                },
                "Adjudicator": {
                    "description": f"Welcome {member.mention}! You've successfully registered as an **Adjudicator**.",
                    "fields": [
                        ("⚖️ What you can do:", "• Judge debates\n• Access result discussion rooms\n• Monitor prep rooms\n• Review feedback", False),
                        ("📍 Next Steps:", "• Check the schedules channel for your assignments\n• Review adjudication guidelines\n• Join result rooms after rounds", False)
                    ]
                },
                "Spectator": {
                    "description": f"Welcome {member.mention}! You've successfully registered as a **Spectator**.",
                    "fields": [
                        ("👀 What you can do:", "• Watch debates\n• Submit feedback\n• Participate in general chat\n• Access tournament information", False),
                        ("📍 Next Steps:", "• Check the schedules channel for round timings\n• Follow tournament updates in announcements\n• Enjoy the debates!", False)
                    ]
                }
            }

            message_data = role_messages.get(role_name, {
                "description": f"Welcome {member.mention}! You've been assigned the **{role_name}** role.",
                "fields": [("📍 Next Steps:", "Check the relevant channels for more information.", False)]
            })

            embed.description = message_data["description"]
            
            for field_name, field_value, inline in message_data["fields"]:
                embed.add_field(name=field_name, value=field_value, inline=inline)

            embed.add_field(
                name="🔄 Need to change your role?",
                value="Simply react with a different emoji in the role-assignment channel!",
                inline=False
            )

            embed.add_field(
                name="👀 Can't see new channels?",
                value="• **Desktop**: Press `Ctrl+R` (Windows) or `Cmd+R` (Mac) to refresh\n• **Mobile**: Pull down to refresh or restart the app\n• New channels should appear in a few seconds!",
                inline=False
            )

            embed.set_footer(text="Good luck in the tournament! 🏆")
            embed.timestamp = discord.utils.utcnow()

            await welcome_channel.send(embed=embed)
            logger.info(f"Sent welcome message for {member.display_name} as {role_name}")

        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

    @app_commands.command()
    @app_commands.describe(confirmation="Type 'CONFIRM' to proceed with cleanup")

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
                description=f"Deleted {deleted_count} channels and {len(categories_to_delete)} categories.",
                color=discord.Color.green(),
            )

            embed.add_field(
                name="Note",
                value="Tournament roles (Debater, Adjudicator, Spectator) were preserved.\n"
                "You can delete them manually if needed.",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error during tournament cleanup: {e}")
            await interaction.followup.send(
                f"❌ Error during cleanup: {str(e)}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(TournamentSetup(bot))
