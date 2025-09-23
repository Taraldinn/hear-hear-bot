"""
UI Views for tournament role assignment.

Contains the persistent Discord UI components used by the tournament setup
module. Extracted from tournament.py to reduce module size and improve
maintainability.
"""

from __future__ import annotations

import logging
from typing import Dict

import discord

logger = logging.getLogger(__name__)


class TournamentRoleView(discord.ui.View):
    """Persistent view for tournament role assignment."""

    def __init__(self, guild_id: int) -> None:
        super().__init__(timeout=None)  # Persistent view
        self.guild_id = guild_id

        # Add the select menu
        self.add_item(TournamentRoleSelect(guild_id))


class TournamentRoleSelect(discord.ui.Select):
    """Select menu for choosing tournament roles."""

    def __init__(self, guild_id: int) -> None:
        self.guild_id = guild_id

        # Create standard options - roles will be validated dynamically
        options = [
            discord.SelectOption(
                label="Debater",
                emoji="🥊",
                value="debater",
                description="Participate in debates and access prep rooms",
            ),
            discord.SelectOption(
                label="Adjudicator",
                emoji="⚖️",
                value="adjudicator",
                description="Judge debates and access result discussions",
            ),
            discord.SelectOption(
                label="Spectator",
                emoji="👀",
                value="spectator",
                description="Watch the tournament with read-only access",
            ),
        ]

        super().__init__(
            placeholder="Choose your tournament role...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"tournament_role_select_{guild_id}",
        )

    async def callback(
        self, interaction: discord.Interaction
    ) -> None:  # pragma: no cover - interactive
        """Handle role selection."""
        try:
            await interaction.response.defer(ephemeral=True)

            guild = interaction.guild
            if not guild:
                await interaction.followup.send(
                    "❌ This command can only be used in a server.", ephemeral=True
                )
                return

            # Try to get member from cache first, then fetch if needed
            member = guild.get_member(interaction.user.id)
            if not member:
                try:
                    member = await guild.fetch_member(interaction.user.id)
                except discord.NotFound:
                    await interaction.followup.send(
                        "❌ You are not a member of this server.", ephemeral=True
                    )
                    return
                except discord.HTTPException:
                    await interaction.followup.send(
                        "❌ Failed to verify your membership. Please try again.",
                        ephemeral=True,
                    )
                    return

            selected_role_key = self.values[0]

            # Find the role dynamically based on the selection
            role_mapping: Dict[str, str] = {
                "debater": "Debater",
                "adjudicator": "Adjudicator",
                "spectator": "Spectator",
            }

            role_name = role_mapping.get(selected_role_key)
            if not role_name:
                await interaction.followup.send(
                    "❌ Invalid role selection. Please try again.", ephemeral=True
                )
                return

            selected_role = discord.utils.get(guild.roles, name=role_name)
            if not selected_role:
                await interaction.followup.send(
                    (
                        f"❌ The {role_name} role doesn't exist. "
                        "Make sure the tournament has been set up properly."
                    ),
                    ephemeral=True,
                )
                return

            # Check bot permissions
            if selected_role >= guild.me.top_role:  # type: ignore[operator]
                await interaction.followup.send(
                    (
                        f"❌ I don't have permission to assign the {role_name} role. "
                        "Please contact an administrator."
                    ),
                    ephemeral=True,
                )
                return

            # Remove other tournament roles first
            tournament_roles = [
                discord.utils.get(guild.roles, name="Debater"),
                discord.utils.get(guild.roles, name="Adjudicator"),
                discord.utils.get(guild.roles, name="Spectator"),
            ]
            tournament_roles = [r for r in tournament_roles if r and r in member.roles]

            if tournament_roles:
                await member.remove_roles(
                    *tournament_roles,
                    reason="Tournament role change - removing old roles",
                )

            # Add new role
            await member.add_roles(
                selected_role,
                reason=f"Tournament role assignment - assigned {role_name}",
            )

            logger.info("Assigned %s role to %s", role_name, member.display_name)

            # Send confirmation
            await interaction.followup.send(
                (
                    "✅ **Role assigned successfully!**\n"
                    f"You are now a **{role_name}** for this tournament.\n\n"
                    "🔄 Channels should now be visible. If you don't see them:\n"
                    "• **Desktop**: Press `Ctrl+R` (Windows) or `Cmd+R` (Mac)\n"
                    "• **Mobile**: Pull down to refresh or restart Discord\n\n"
                    "You can change your role anytime by using this menu again!"
                ),
                ephemeral=True,
            )

            # Send welcome message to welcome channel (if it exists)
            try:
                # Find the welcome channel and send a simple welcome message
                welcome_channel = discord.utils.get(guild.text_channels, name="welcome")
                if welcome_channel:
                    embed = discord.Embed(
                        title="🎉 Welcome to the Tournament!",
                        description=(
                            f"Welcome {member.mention}! You've successfully registered as a "
                            f"**{role_name}**."
                        ),
                        color=discord.Color.green(),
                    )
                    embed.add_field(
                        name="🔄 Channels should now be visible!",
                        value=(
                            "If you don't see new channels, try refreshing Discord."
                        ),
                        inline=False,
                    )
                    embed.set_footer(text="Good luck in the tournament! 🏆")
                    await welcome_channel.send(embed=embed)
            except (
                discord.HTTPException,
                discord.Forbidden,
                AttributeError,
            ) as exc:  # pragma: no cover - logging only
                logger.warning("Could not send welcome message: %s", exc)

        except discord.Forbidden:  # pragma: no cover - permission branch
            await interaction.followup.send(
                "❌ I don't have permission to assign roles. Please contact an administrator.",
                ephemeral=True,
            )
            logger.error(
                "No permission to assign roles to %s",
                getattr(interaction.user, "display_name", "unknown"),
            )
        except (
            discord.HTTPException,
            AttributeError,
            KeyError,
            TypeError,
        ) as exc:  # pragma: no cover - logging only
            await interaction.followup.send(
                (
                    "❌ An error occurred while assigning your role. "
                    "Please try again or contact an administrator."
                ),
                ephemeral=True,
            )
            logger.error(
                "Error assigning role to %s: %s",
                getattr(interaction.user, "display_name", "unknown"),
                exc,
            )
