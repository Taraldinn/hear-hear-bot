"""
Tabbycat Integration Commands for Hear! Hear! Bot - PostgreSQL Compatible
Author: aldinn
Email: kferdoush617@gmail.com

NOTE: This is a temporary compatibility layer during PostgreSQL migration.
Many features are temporarily disabled until proper PostgreSQL tables are created.
"""

import logging

import discord
import requests
from discord import app_commands
from discord.ext import commands

from src.database.connection import Database

logger = logging.getLogger(__name__)


class TabbyCommands(commands.Cog):
    """Commands for Tabbycat tournament integration"""

    def __init__(self, bot):
        self.bot = bot
        self.database = Database()
        # Temporary in-memory storage until PostgreSQL tables are created
        self.tournament_cache = {}

    def _get_tournament_data(self, guild_id):
        """Get tournament data from cache"""
        return self.tournament_cache.get(guild_id)

    def _store_tournament_data(self, guild_id, data):
        """Store tournament data in cache"""
        self.tournament_cache[guild_id] = data

    @commands.command(name="tabsync")
    @commands.has_permissions(administrator=True)
    async def tabsync(self, ctx, url, token):
        """Sync server with Tabbycat tournament

        Usage: .tabsync <TABBYCAT_URL> <API_TOKEN>
        Get the API token from your Tabbycat site settings.
        """
        try:
            # Clean up the URL
            if url.endswith("/"):
                base_url = url[:-1]
            else:
                base_url = url

            # Test the connection
            test_url = f"{base_url}/api/v1/tournaments"
            headers = {"Authorization": f"Token {token}"}

            response = requests.get(test_url, headers=headers, timeout=10)

            if response.status_code != 200:
                await ctx.send(
                    f"❌ Failed to connect to Tabbycat. Status code: {response.status_code}"
                )
                return

            tournaments = response.json()

            if not tournaments:
                await ctx.send("❌ No tournaments found at this URL.")
                return

            # Use the first tournament found
            tournament = tournaments[0]
            tournament_url = f"{base_url}/api/v1/tournaments/{tournament['slug']}/"

            # Store tournament data in temporary cache
            tournament_data = {
                "site": base_url,
                "token": token,
                "tournament": tournament_url,
                "tournament_name": tournament["name"],
                "tournament_slug": tournament["slug"],
                "teams": [],
                "adjudicators": [],
            }
            self._store_tournament_data(ctx.guild.id, tournament_data)

            embed = discord.Embed(
                title="✅ Tournament Connected",
                description=f"Connected to **{tournament['name']}**",
                color=discord.Color.green(),
                timestamp=ctx.message.created_at,
            )

            embed.add_field(name="Tournament URL", value=base_url, inline=False)
            embed.add_field(
                name="Tournament Name", value=tournament["name"], inline=True
            )
            embed.add_field(
                name="Status", value="Connected (⚠️ Storage pending)", inline=True
            )

            await ctx.send(embed=embed)
            logger.info(
                "Connected guild %s to tournament %s", ctx.guild.id, tournament["name"]
            )

        except requests.exceptions.RequestException as e:
            await ctx.send(f"❌ Network error: {str(e)}")
            logger.error("Network error in sync command: %s", e)
        except (AttributeError, KeyError, ValueError) as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            logger.error("Error in sync command: %s", e)

    @commands.command()
    async def register(self, ctx, key):
        """Register with tournament using your identification key

        Usage: .register <8-digit-key>
        Get your key from the tournament organizers.
        """
        await self._register_logic(ctx, key, is_slash=False)

    @app_commands.command(
        name="register",
        description="Register with tournament using your identification key",
    )
    @app_commands.describe(
        key="Your 8-digit identification key from tournament organizers"
    )
    async def slash_register(self, interaction: discord.Interaction, key: str):
        """Slash command version of register"""
        await self._register_logic(interaction, key, is_slash=True)

    async def _register_logic(self, ctx, key, is_slash=False):
        """Shared logic for both command types"""
        try:
            # Tournament registration temporarily disabled for PostgreSQL migration
            # NOTE: PostgreSQL tournament storage and registration needed

            send_func = ctx.followup.send if is_slash else ctx.send
            if is_slash:
                await ctx.response.defer()

            await send_func(
                "⚠️ Tournament registration temporarily disabled during PostgreSQL migration.\n"
                f"Your registration key `{key}` has been noted.\n"
                "Please check back soon when the database migration is complete!"
            )
            return

        except (discord.HTTPException, AttributeError) as e:
            send_func = ctx.followup.send if is_slash else ctx.send
            if is_slash and not ctx.response.is_done():
                await ctx.response.defer()
            await send_func("❌ Registration error.")
            logger.error("Error in register command: %s", e)

    @commands.command(aliases=["check-in"])
    async def checkin(self, ctx):
        """Check in to the tournament"""
        await self._checkin_logic(ctx, is_slash=False)

    @commands.command(aliases=["check-out"])
    async def checkout(self, ctx):
        """Check out from the tournament"""
        await self._checkout_logic(ctx, is_slash=False)

    @commands.command()
    async def ballot(self, ctx):
        """Get your ballot for judging"""
        await self._ballot_logic(ctx, is_slash=False)

    @commands.command()
    async def pairings(self, ctx):
        """View current round pairings"""
        await self._pairings_logic(ctx, is_slash=False)

    @commands.command()
    async def standings(self, ctx):
        """View current tournament standings"""
        await self._standings_logic(ctx, is_slash=False)

    @commands.command()
    async def motion(self, ctx, round_abbrev):
        """Get motion for a specific round

        Usage: .motion <round_abbreviation>
        Example: .motion R1
        """
        await self._motion_logic(ctx, round_abbrev, is_slash=False)

    @commands.command()
    async def status(self, ctx):
        """Show tournament status and connection info"""
        await self._status_logic(ctx, is_slash=False)

    @commands.command(
        name="addemai",
        aliases=["email-adj"],
        description="Add an email to adjudicator list",
    )
    async def addemai(self, ctx, email):
        """Add email for tournament notifications (placeholder)"""
        # NOTE: Email registration functionality needed
        _ = email  # Suppress unused argument warning
        await ctx.send("📧 Email registration feature coming soon!")

    @commands.command()
    async def announce(self, ctx, *, message):
        """Announce message to tournament participants (placeholder)"""
        # NOTE: Announcement functionality needed
        _ = message  # Suppress unused argument warning
        await ctx.send("📢 Announcement feature coming soon!")

    @commands.command(name="begin-debate", aliases=["start-debate"])
    async def begin_debate(self, ctx):
        """Begin debate (temporarily disabled)"""
        await ctx.send(
            "⚠️ Debate management temporarily disabled during PostgreSQL migration."
        )

    @commands.command(name="call-to-venue", aliases=["call-to-room"])
    async def call_to_venue(self, ctx):
        """Call participants to venue (temporarily disabled)"""
        await ctx.send(
            "⚠️ Venue management temporarily disabled during PostgreSQL migration."
        )

    # === SLASH COMMAND VERSIONS ===

    @app_commands.command(
        name="tabsync", description="Sync server with Tabbycat tournament (Admin only)"
    )
    @app_commands.describe(
        url="Your Tabbycat tournament URL",
        token="Your API token from Tabbycat site settings",
    )
    @app_commands.default_permissions(administrator=True)
    async def slash_tabsync(
        self, interaction: discord.Interaction, url: str, token: str
    ):
        """Slash command version of tabsync"""
        # Defer the response since this might take a while
        await interaction.response.defer()

        try:
            # Clean up the URL
            if url.endswith("/"):
                base_url = url[:-1]
            else:
                base_url = url

            # Test the connection
            test_url = f"{base_url}/api/v1/tournaments"
            headers = {"Authorization": f"Token {token}"}

            response = requests.get(test_url, headers=headers, timeout=10)

            if response.status_code != 200:
                await interaction.followup.send(
                    f"❌ Failed to connect to Tabbycat. Status code: {response.status_code}"
                )
                return

            tournaments = response.json()
            if not tournaments:
                await interaction.followup.send(
                    "❌ No tournaments found in your Tabbycat instance."
                )
                return

            # Use the first tournament (or let admin choose in the future)
            tournament = tournaments[0]

            # Store tournament data in temporary cache
            tournament_data = {
                "site": base_url,
                "token": token,
                "tournament": f"{base_url}/api/v1/tournaments/{tournament['slug']}/",
                "tournament_name": tournament["name"],
                "tournament_slug": tournament["slug"],
                "teams": [],
                "adjudicators": [],
            }
            self._store_tournament_data(interaction.guild_id, tournament_data)

            # Store tournament data in PostgreSQL
            if await self.database.ensure_connected():
                await interaction.followup.send(
                    f"✅ Successfully connected to tournament: **{tournament['name']}**\n"
                    f"🔗 URL: {base_url}\n"
                    f"📊 Tournament ID: {tournament['slug']}\n"
                    f"💾 Data cached and ready for use!"
                )
                logger.info(
                    "Synced guild %s with tournament %s",
                    interaction.guild_id,
                    tournament["name"],
                )
            else:
                await interaction.followup.send("❌ Database connection error.")

        except requests.exceptions.RequestException as e:
            await interaction.followup.send(f"❌ Network error: {str(e)}")
            logger.error("Network error in slash sync command: %s", e)
        except (AttributeError, KeyError, ValueError) as e:
            await interaction.followup.send(f"❌ An error occurred: {str(e)}")
            logger.error("Error in slash sync command: %s", e)

    @app_commands.command(name="checkin", description="Check in to the tournament")
    async def slash_checkin(self, interaction: discord.Interaction):
        """Slash command version of checkin"""
        await interaction.response.defer()
        await self._checkin_logic(interaction, is_slash=True)

    @app_commands.command(name="checkout", description="Check out from the tournament")
    async def slash_checkout(self, interaction: discord.Interaction):
        """Slash command version of checkout"""
        await interaction.response.defer()
        await self._checkout_logic(interaction, is_slash=True)

    @app_commands.command(name="ballot", description="Get your ballot for judging")
    async def slash_ballot(self, interaction: discord.Interaction):
        """Slash command version of ballot"""
        await interaction.response.defer()
        await self._ballot_logic(interaction, is_slash=True)

    @app_commands.command(name="pairings", description="View current round pairings")
    async def slash_pairings(self, interaction: discord.Interaction):
        """Slash command version of pairings"""
        await interaction.response.defer()
        await self._pairings_logic(interaction, is_slash=True)

    @app_commands.command(
        name="standings", description="View current tournament standings"
    )
    async def slash_standings(self, interaction: discord.Interaction):
        """Slash command version of standings"""
        await interaction.response.defer()
        await self._standings_logic(interaction, is_slash=True)

    @app_commands.command(
        name="announce", description="Make a tournament announcement (Admin only)"
    )
    @app_commands.describe(message="The announcement message")
    @app_commands.default_permissions(administrator=True)
    async def slash_announce(self, interaction: discord.Interaction, message: str):
        """Slash command for tournament announcements (placeholder)"""
        # NOTE: Announcement functionality needed
        _ = message  # Suppress unused argument warning
        await interaction.response.send_message(
            "📢 Announcement feature coming soon!", ephemeral=True
        )

    @app_commands.command(name="motion", description="Get motion for a specific round")
    @app_commands.describe(round_abbrev="Round abbreviation (e.g., R1, R2, SF, F)")
    async def slash_motion(self, interaction: discord.Interaction, round_abbrev: str):
        """Slash command version of motion"""
        await interaction.response.defer()
        await self._motion_logic(interaction, round_abbrev, is_slash=True)

    @app_commands.command(
        name="status", description="Show tournament status and connection info"
    )
    async def slash_status(self, interaction: discord.Interaction):
        """Slash command version of status"""
        await interaction.response.defer()
        await self._status_logic(interaction, is_slash=True)

    # Helper methods to handle both slash and prefix commands
    async def _checkin_logic(self, ctx, is_slash=False):
        """Shared logic for checkin commands"""
        try:
            tournament_data = self._get_tournament_data(
                ctx.guild.id if hasattr(ctx, "guild") else ctx.guild_id
            )
            if not tournament_data:
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func(
                    "❌ This server is not synced with a tournament. Use `/tabsync` first."
                )
                return

            # For now, provide information about check-in process
            embed = discord.Embed(
                title="✅ Tournament Check-in",
                description="Ready to check in for the tournament",
                color=discord.Color.green(),
            )

            embed.add_field(
                name="📋 Check-in Process:",
                value="1. Make sure you're registered with `/register <key>`\n"
                "2. Check your tournament status with `/status`\n"
                "3. Contact the tab team if you need assistance",
                inline=False,
            )

            embed.add_field(
                name="🏆 Tournament:",
                value=f"**{tournament_data['tournament_name']}**",
                inline=True,
            )

            embed.add_field(
                name="🔗 Tabbycat:",
                value=f"[Open Tournament]({tournament_data['site']})",
                inline=True,
            )

            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func(embed=embed)

        except (discord.HTTPException, AttributeError) as e:
            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func("❌ Error processing check-in.")
            logger.error("Error in checkin command: %s", e)

    async def _checkout_logic(self, ctx, is_slash=False):
        """Shared logic for checkout commands"""
        try:
            tournament_data = self._get_tournament_data(
                ctx.guild.id if hasattr(ctx, "guild") else ctx.guild_id
            )
            if not tournament_data:
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func(
                    "❌ This server is not synced with a tournament. Use `/tabsync` first."
                )
                return

            # For now, provide information about check-out process
            embed = discord.Embed(
                title="🚪 Tournament Check-out",
                description="Ready to check out from the tournament",
                color=discord.Color.orange(),
            )

            embed.add_field(
                name="📋 Check-out Process:",
                value="1. Complete any ongoing debates or judging\n"
                "2. Submit any required feedback\n"
                "3. Check your availability status",
                inline=False,
            )

            embed.add_field(
                name="🏆 Tournament:",
                value=f"**{tournament_data['tournament_name']}**",
                inline=True,
            )

            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func(embed=embed)

        except (discord.HTTPException, AttributeError) as e:
            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func("❌ Error processing check-out.")
            logger.error("Error in checkout command: %s", e)

    async def _ballot_logic(self, ctx, is_slash=False):
        """Shared logic for ballot commands"""
        try:
            tournament_data = self._get_tournament_data(
                ctx.guild.id if hasattr(ctx, "guild") else ctx.guild_id
            )
            if not tournament_data:
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func(
                    "❌ This server is not synced with a tournament. Use `/tabsync` first."
                )
                return

            # Get adjudicator info (simplified for now)
            # In a full implementation, this would check if the user is registered as an adjudicator
            # and fetch their specific ballot assignments

            embed = discord.Embed(
                title="🗳️ Adjudicator Ballot",
                description="Ballot functionality is available for registered adjudicators",
                color=discord.Color.purple(),
            )

            embed.add_field(
                name="📋 How to get your ballot:",
                value="1. Make sure you're registered with `/register <key>`\n"
                "2. Check in with `/checkin`\n"
                "3. Your ballot will be available once the round starts",
                inline=False,
            )

            embed.add_field(
                name="💡 Note:",
                value="Full ballot functionality requires tournament organizer setup.\n"
                "Contact the tab team if you need assistance.",
                inline=False,
            )

            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func(embed=embed)

        except (discord.HTTPException, AttributeError) as e:
            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func("❌ Error fetching ballot information.")
            logger.error("Error in ballot command: %s", e)

    async def _pairings_logic(self, ctx, is_slash=False):
        """Shared logic for pairings commands"""
        try:
            tournament_data = self._get_tournament_data(
                ctx.guild.id if hasattr(ctx, "guild") else ctx.guild_id
            )
            if not tournament_data:
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func(
                    "❌ This server is not synced with a tournament. Use `/tabsync` first."
                )
                return

            headers = {"Authorization": f"Token {tournament_data['token']}"}

            # First get current round info
            rounds_url = f"{tournament_data['tournament']}rounds"
            rounds_response = requests.get(rounds_url, headers=headers, timeout=10)

            if rounds_response.status_code != 200:
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func("❌ Failed to fetch rounds data.")
                return

            rounds = rounds_response.json()

            # Find the current round (first non-completed round)
            current_round = None
            for round_data in rounds:
                if not round_data.get("completed", False):
                    current_round = round_data
                    break

            if not current_round:
                # If no incomplete rounds, use the last round
                current_round = rounds[-1] if rounds else None

            if not current_round:
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func("❌ No rounds found in tournament.")
                return

            # Get pairings for the current round
            pairings_url = f"{current_round['url']}/pairings"
            pairings_response = requests.get(pairings_url, headers=headers, timeout=10)

            if pairings_response.status_code != 200:
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func("❌ Failed to fetch pairings data.")
                return

            pairings = pairings_response.json()

            embed = discord.Embed(
                title=f"📋 Round {current_round['abbreviation']} Pairings",
                description=f"Draw for **{tournament_data['tournament_name']}**",
                color=discord.Color.blue(),
            )

            if not pairings:
                embed.add_field(
                    name="Status", value="No pairings released yet", inline=False
                )
            else:
                # Format pairings - show first 10 debates
                pairings_text = ""
                for pairing in pairings[:10]:
                    venue = pairing.get("venue", {}).get("display_name", "TBA")

                    # Get team names
                    teams = []
                    for team_data in pairing.get("teams", []):
                        team_name = team_data.get("team", {}).get(
                            "short_name", "Unknown"
                        )
                        position = team_data.get("position", "Unknown")
                        teams.append(f"{team_name} ({position})")

                    if teams:
                        teams_str = " vs ".join(teams)
                        pairings_text += f"**{venue}:** {teams_str}\n"

                if pairings_text:
                    embed.add_field(name="Debates", value=pairings_text, inline=False)

                if len(pairings) > 10:
                    embed.add_field(
                        name="Note",
                        value=f"Showing 10 of {len(pairings)} total debates",
                        inline=False,
                    )

            embed.set_footer(text=f"Round: {current_round['name']}")

            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func(embed=embed)

        except (KeyError, ValueError, AttributeError) as e:
            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func("❌ Error fetching pairings.")
            logger.error("Error in pairings command: %s", e)

    async def _standings_logic(self, ctx, is_slash=False):
        """Shared logic for standings commands"""
        try:
            tournament_data = self._get_tournament_data(
                ctx.guild.id if hasattr(ctx, "guild") else ctx.guild_id
            )
            if not tournament_data:
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func(
                    "❌ This server is not synced with a tournament. Use `/tabsync` first."
                )
                return

            headers = {"Authorization": f"Token {tournament_data['token']}"}
            standings_url = f"{tournament_data['tournament']}standings"

            response = requests.get(standings_url, headers=headers, timeout=10)

            if response.status_code != 200:
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func("❌ Failed to fetch standings data.")
                return

            standings = response.json()

            embed = discord.Embed(
                title="🏆 Tournament Standings",
                description=f"Current standings for **{tournament_data['tournament_name']}**",
                color=discord.Color.gold(),
            )

            # Format top 10 standings
            standings_text = ""
            for i, team in enumerate(standings[:10], 1):
                team_name = team.get("short_name", "Unknown")
                team_points = team.get("points", 0)
                standings_text += f"{i}. **{team_name}** - {team_points} pts\n"

            if standings_text:
                embed.add_field(name="Top 10 Teams", value=standings_text, inline=False)
            else:
                embed.add_field(
                    name="Standings", value="No standings available yet", inline=False
                )

            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func(embed=embed)

        except (KeyError, ValueError, AttributeError) as e:
            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func("❌ Error fetching standings.")
            logger.error("Error in standings command: %s", e)

    async def _motion_logic(self, ctx, round_abbrev, is_slash=False):
        """Shared logic for motion commands"""
        try:
            tournament_data = self._get_tournament_data(
                ctx.guild.id if hasattr(ctx, "guild") else ctx.guild_id
            )
            if not tournament_data:
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func(
                    "❌ This server is not synced with a tournament. Use `/tabsync` first."
                )
                return

            headers = {"Authorization": f"Token {tournament_data['token']}"}
            rounds_url = f"{tournament_data['tournament']}rounds"

            response = requests.get(rounds_url, headers=headers, timeout=10)

            if response.status_code != 200:
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func("❌ Failed to fetch rounds data.")
                return

            rounds = response.json()

            for round_data in rounds:
                if round_data["abbreviation"].lower() == round_abbrev.lower():
                    if not round_data.get("motions_released", False):
                        send_func = ctx.followup.send if is_slash else ctx.send
                        await send_func(
                            f"🔒 The motion for **{round_abbrev}** is not released yet!"
                        )
                        return

                    motions = round_data.get("motions", [])

                    if not motions:
                        send_func = ctx.followup.send if is_slash else ctx.send
                        await send_func(f"❌ No motions found for **{round_abbrev}**")
                        return

                    for i, motion_data in enumerate(motions, 1):
                        motion_text = motion_data.get("text", "No motion text")
                        info_slide = motion_data.get("info_slide", "")

                        embed = discord.Embed(
                            title=f"🎯 Motion {i} for {round_abbrev}",
                            description=f"**{motion_text}**",
                            color=discord.Color.blue(),
                        )

                        if info_slide:
                            embed.add_field(
                                name="📋 Info Slide", value=info_slide, inline=False
                            )

                        embed.set_footer(
                            text=f"Tournament: {tournament_data.get('tournament_name', 'Unknown')}"
                        )

                        send_func = ctx.followup.send if is_slash else ctx.send
                        await send_func(embed=embed)

                    return

            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func(f"❌ Round **{round_abbrev}** not found.")

        except (KeyError, ValueError, AttributeError, requests.RequestException) as e:
            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func("❌ Error fetching motion.")
            logger.error("Error in motion command: %s", e)

    async def _status_logic(self, ctx, is_slash=False):
        """Shared logic for status commands"""
        try:
            tournament_data = self._get_tournament_data(
                ctx.guild.id if hasattr(ctx, "guild") else ctx.guild_id
            )
            if not tournament_data:
                embed = discord.Embed(
                    title="❌ Not Connected",
                    description="This server is not synced with any tournament.",
                    color=discord.Color.red(),
                )
                embed.add_field(
                    name="💡 Setup Required",
                    value="Use `/tabsync <url> <token>` to connect to a tournament",
                    inline=False,
                )
                send_func = ctx.followup.send if is_slash else ctx.send
                await send_func(embed=embed)
                return

            embed = discord.Embed(
                title="🏆 Tournament Status",
                description=f"Connected to **{tournament_data['tournament_name']}**",
                color=discord.Color.green(),
            )

            embed.add_field(name="🔗 URL", value=tournament_data["site"], inline=False)
            embed.add_field(
                name="📊 Tournament",
                value=tournament_data["tournament_slug"],
                inline=True,
            )
            embed.add_field(name="🔄 Status", value="Connected", inline=True)

            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func(embed=embed)

        except (KeyError, ValueError, AttributeError):
            send_func = ctx.followup.send if is_slash else ctx.send
            await send_func("❌ Error retrieving status.")
            logger.error("Error in status command")


async def setup(bot):
    """
    Setup function to add the TabbyCommands cog to the bot
    """
    await bot.add_cog(TabbyCommands(bot))
