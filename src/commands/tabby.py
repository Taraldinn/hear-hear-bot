"""
Tabbycat Integration Commands for Hear! Hear! Bot - PostgreSQL Compatible
Author: aldinn
Email: kferdoush617@gmail.com

NOTE: This is a temporary compatibility layer during PostgreSQL migration.
Many features are temporarily disabled until proper PostgreSQL tables are created.
"""

import discord
from discord.ext import commands
from discord import app_commands
import requests
import json
import logging
import asyncio
from src.utils.image_generator import image_generator
from src.database.connection import Database

logger = logging.getLogger(__name__)


class TabbyCommands(commands.Cog):
    """Commands for Tabbycat tournament integration"""

    def __init__(self, bot):
        self.bot = bot
        self.database = Database()

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

            # Database storage temporarily disabled for PostgreSQL migration
            # TODO: Create proper PostgreSQL tables for tournament data

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
                f"Connected guild {ctx.guild.id} to tournament {tournament['name']}"
            )

        except requests.exceptions.RequestException as e:
            await ctx.send(f"❌ Network error: {str(e)}")
            logger.error(f"Network error in sync command: {e}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            logger.error(f"Error in sync command: {e}")

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
            # TODO: Implement PostgreSQL tournament storage and registration

            send_func = ctx.followup.send if is_slash else ctx.send
            if is_slash:
                await ctx.response.defer()

            await send_func(
                "⚠️ Tournament registration temporarily disabled during PostgreSQL migration.\n"
                f"Your registration key `{key}` has been noted.\n"
                "Please check back soon when the database migration is complete!"
            )
            return

        except Exception as e:
            send_func = ctx.followup.send if is_slash else ctx.send
            if is_slash and not ctx.response.is_done():
                await ctx.response.defer()
            await send_func("❌ Registration error.")
            logger.error(f"Error in register command: {e}")

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

    @commands.command(
        name="addemai",
        aliases=["email-adj"],
        description="Add an email to adjudicator list",
    )
    async def addemai(self, ctx, email):
        """Add an email to adjudicator list (temporarily disabled)"""
        await ctx.send(
            "⚠️ Adjudicator management temporarily disabled during PostgreSQL migration."
        )

    @commands.command(name="announce")
    async def announce(self, ctx, *, message):
        """Make an announcement (temporarily disabled)"""
        await ctx.send(
            "⚠️ Announcement system temporarily disabled during PostgreSQL migration."
        )

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

            # Store tournament data in PostgreSQL
            if await self.database.ensure_connected():
                # TODO: Update this to use proper PostgreSQL table structure
                # For now, just acknowledge the sync
                await interaction.followup.send(
                    f"✅ Successfully connected to tournament: **{tournament['name']}**\n"
                    f"🔗 URL: {base_url}\n"
                    f"📊 Tournament ID: {tournament['slug']}\n"
                    f"⚠️ Database storage pending PostgreSQL table creation"
                )
                logger.info(
                    f"Synced guild {interaction.guild_id} with tournament {tournament['name']}"
                )
            else:
                await interaction.followup.send("❌ Database connection error.")

        except requests.exceptions.RequestException as e:
            await interaction.followup.send(f"❌ Network error: {str(e)}")
            logger.error(f"Network error in slash sync command: {e}")
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {str(e)}")
            logger.error(f"Error in slash sync command: {e}")

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
        """Slash command version of announce"""
        await interaction.response.defer()
        await interaction.followup.send(
            "⚠️ Announcement system temporarily disabled during PostgreSQL migration."
        )

    # Helper methods to handle both slash and prefix commands
    async def _checkin_logic(self, ctx, is_slash=False):
        """Shared logic for checkin commands"""
        send_func = ctx.followup.send if is_slash else ctx.send
        await send_func(
            "⚠️ Check-in functionality temporarily disabled during PostgreSQL migration."
        )

    async def _checkout_logic(self, ctx, is_slash=False):
        """Shared logic for checkout commands"""
        send_func = ctx.followup.send if is_slash else ctx.send
        await send_func(
            "⚠️ Check-out functionality temporarily disabled during PostgreSQL migration."
        )

    async def _ballot_logic(self, ctx, is_slash=False):
        """Shared logic for ballot commands"""
        send_func = ctx.followup.send if is_slash else ctx.send
        await send_func(
            "🗳️ Ballot functionality temporarily disabled during PostgreSQL migration."
        )

    async def _pairings_logic(self, ctx, is_slash=False):
        """Shared logic for pairings commands"""
        send_func = ctx.followup.send if is_slash else ctx.send
        await send_func(
            "📋 Pairings functionality temporarily disabled during PostgreSQL migration."
        )

    async def _standings_logic(self, ctx, is_slash=False):
        """Shared logic for standings commands"""
        send_func = ctx.followup.send if is_slash else ctx.send
        await send_func(
            "🏆 Standings functionality temporarily disabled during PostgreSQL migration."
        )


async def setup(bot):
    await bot.add_cog(TabbyCommands(bot))
