"""
Tabbycat Integration Commands for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
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

            # Save to database
            collection = self.bot.database.get_collection(
                "tournaments", use_tabby_db=True
            )
            if collection:
                collection.update_one(
                    {"_id": ctx.guild.id},
                    {
                        "$set": {
                            "site": base_url,
                            "token": token,
                            "tournament": tournament_url,
                            "tournament_name": tournament["name"],
                            "tournament_slug": tournament["slug"],
                            "teams": [],
                            "adjudicators": [],
                        }
                    },
                    upsert=True,
                )

                embed = discord.Embed(
                    title="✅ Tournament Synced Successfully",
                    description=f"Connected to **{tournament['name']}**",
                    color=discord.Color.green(),
                    timestamp=ctx.message.created_at,
                )

                embed.add_field(name="Tournament URL", value=base_url, inline=False)
                embed.add_field(
                    name="Tournament Name", value=tournament["name"], inline=True
                )
                embed.add_field(name="Status", value="Connected", inline=True)

                await ctx.send(embed=embed)
                logger.info(
                    f"Synced guild {ctx.guild.id} with tournament {tournament['name']}"
                )
            else:
                await ctx.send("❌ Database connection error.")

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
            # Get tournament data
            collection = self.database.get_collection("tournaments")
            if collection is None:
                await ctx.send("❌ Database connection error.")
                return

            tournament_data = collection.find_one({"_id": ctx.guild.id})
            if not tournament_data:
                await ctx.send(
                    "❌ This server is not synced with a tournament. Contact an admin."
                )
                return

            # Check if user is already registered
            discord_id = ctx.author.id

            # Check if already registered as speaker
            existing_speaker = collection.find_one(
                {"_id": ctx.guild.id},
                {"teams": {"$elemMatch": {"speakers.url_key": key}}},
            )

            if existing_speaker and existing_speaker != {"_id": ctx.guild.id}:
                await ctx.send("❌ This key is already registered or invalid.")
                return

            # Try to fetch from API
            headers = {"Authorization": f"Token {tournament_data['token']}"}

            # First try adjudicators
            adj_url = f"{tournament_data['tournament']}adjudicators"
            adj_response = requests.get(adj_url, headers=headers)

            if adj_response.status_code == 200:
                adjudicators = adj_response.json()

                for adj in adjudicators:
                    if adj["url_key"] == key:
                        # Register as adjudicator
                        adj_info = {
                            "url": adj["url"],
                            "id": adj["id"],
                            "name": adj["name"],
                            "email": adj.get("email", ""),
                            "url_key": adj["url_key"],
                            "adj_core": adj.get("adj_core", False),
                            "discord_id": discord_id,
                        }

                        collection.update_one(
                            {"_id": ctx.guild.id},
                            {"$addToSet": {"adjudicators": adj_info}},
                        )

                        # Auto check-in
                        checkin_response = requests.put(
                            f"{adj['url']}/checkin", headers=headers
                        )

                        # Assign roles
                        try:
                            adj_role = discord.utils.get(
                                ctx.guild.roles, name="Adjudicator"
                            )
                            if not adj_role:
                                adj_role = await ctx.guild.create_role(
                                    name="Adjudicator", color=discord.Color(0x22A777)
                                )
                            await ctx.author.add_roles(adj_role)

                            if adj.get("adj_core"):
                                core_role = discord.utils.get(
                                    ctx.guild.roles, name="AdjCore"
                                )
                                if not core_role:
                                    core_role = await ctx.guild.create_role(
                                        name="AdjCore", color=discord.Color(0x34D269)
                                    )
                                await ctx.author.add_roles(core_role)
                        except Exception as role_error:
                            logger.error(f"Error assigning roles: {role_error}")

                        embed = discord.Embed(
                            title="✅ Registration Successful",
                            description=f"Welcome **{adj['name']}**! You've been registered as an adjudicator.",
                            color=discord.Color.green(),
                        )

                        embed.add_field(name="Role", value="Adjudicator", inline=True)
                        embed.add_field(
                            name="Core",
                            value="Yes" if adj.get("adj_core") else "No",
                            inline=True,
                        )
                        embed.add_field(name="Status", value="Checked In", inline=True)

                        await ctx.send(embed=embed)

                        # Send private URL
                        private_url = f"{tournament_data['site']}/privateurls/{key}/"
                        try:
                            await ctx.author.send(
                                f"🎉 Welcome **{adj['name']}**!\n"
                                f"Your private URL: {private_url}\n"
                                f"Your key: `{key}`"
                            )
                        except:
                            pass  # User might have DMs disabled

                        return

            # Try teams if not found in adjudicators
            teams_url = f"{tournament_data['tournament']}teams"
            teams_response = requests.get(teams_url, headers=headers)

            if teams_response.status_code == 200:
                teams = teams_response.json()

                for team in teams:
                    for speaker in team["speakers"]:
                        if speaker["url_key"] == key:
                            # Clean up team data
                            clean_team = {
                                "id": team["id"],
                                "url": team["url"],
                                "short_name": team["short_name"],
                                "speakers": [],
                            }

                            # Clean up speaker data
                            for spkr in team["speakers"]:
                                clean_speaker = {
                                    "name": spkr["name"],
                                    "url": spkr["url"],
                                    "url_key": spkr["url_key"],
                                }
                                if spkr["url_key"] == key:
                                    clean_speaker["discord_id"] = discord_id
                                clean_team["speakers"].append(clean_speaker)

                            # Save to database
                            collection.update_one(
                                {"_id": ctx.guild.id},
                                {"$addToSet": {"teams": clean_team}},
                            )

                            # Auto check-in
                            checkin_response = requests.put(
                                f"{speaker['url']}/checkin", headers=headers
                            )

                            # Assign debater role
                            try:
                                debater_role = discord.utils.get(
                                    ctx.guild.roles, name="Debater"
                                )
                                if not debater_role:
                                    debater_role = await ctx.guild.create_role(
                                        name="Debater", color=discord.Color(0xE6B60D)
                                    )
                                await ctx.author.add_roles(debater_role)
                            except Exception as role_error:
                                logger.error(
                                    f"Error assigning debater role: {role_error}"
                                )

                            embed = discord.Embed(
                                title="✅ Registration Successful",
                                description=f"Welcome **{speaker['name']}**! You've been registered as a debater.",
                                color=discord.Color.green(),
                            )

                            embed.add_field(name="Role", value="Debater", inline=True)
                            embed.add_field(
                                name="Team", value=team["short_name"], inline=True
                            )
                            embed.add_field(
                                name="Status", value="Checked In", inline=True
                            )

                            await ctx.send(embed=embed)

                            # Send private URL
                            private_url = (
                                f"{tournament_data['site']}/privateurls/{key}/"
                            )
                            try:
                                await ctx.author.send(
                                    f"🎉 Welcome **{speaker['name']}**!\n"
                                    f"Team: **{team['short_name']}**\n"
                                    f"Your private URL: {private_url}\n"
                                    f"Your key: `{key}`"
                                )
                            except:
                                pass

                            return

            await ctx.send("❌ Invalid registration key or key not found.")

        except Exception as e:
            await ctx.send(f"❌ Registration failed: {str(e)}")
            logger.error(f"Error in register command: {e}")

    @commands.command(aliases=["check-in"])
    async def checkin(self, ctx):
        """Check in to the tournament"""
        try:
            collection = self.bot.database.get_collection(
                "tournaments", use_tabby_db=True
            )
            if not collection:
                await ctx.send("❌ Database connection error.")
                return

            discord_id = ctx.author.id
            guild_id = ctx.guild.id

            # Check if user is registered
            user_data = collection.find_one(
                {"_id": guild_id},
                {
                    "$or": [
                        {"teams": {"$elemMatch": {"speakers.discord_id": discord_id}}},
                        {"adjudicators": {"$elemMatch": {"discord_id": discord_id}}},
                    ]
                },
            )

            if not user_data:
                await ctx.send(
                    "❌ You are not registered for this tournament. Use `.register <key>` first."
                )
                return

            tournament_data = collection.find_one({"_id": guild_id})
            headers = {"Authorization": f"Token {tournament_data['token']}"}

            # Check if adjudicator
            adj_data = collection.find_one(
                {"_id": guild_id},
                {"adjudicators": {"$elemMatch": {"discord_id": discord_id}}},
            )

            if adj_data and "adjudicators" in adj_data:
                adj = adj_data["adjudicators"][0]
                response = requests.put(f"{adj['url']}/checkin", headers=headers)

                if response.status_code == 200:
                    await ctx.send(f"✅ **{adj['name']}** checked in successfully!")
                else:
                    await ctx.send("❌ Check-in failed. Please try again.")
                return

            # Check if debater
            team_data = collection.find_one(
                {"_id": guild_id},
                {"teams": {"$elemMatch": {"speakers.discord_id": discord_id}}},
            )

            if team_data and "teams" in team_data:
                team = team_data["teams"][0]
                for speaker in team["speakers"]:
                    if speaker.get("discord_id") == discord_id:
                        response = requests.put(
                            f"{speaker['url']}/checkin", headers=headers
                        )

                        if response.status_code == 200:
                            await ctx.send(
                                f"✅ **{speaker['name']}** of **{team['short_name']}** checked in successfully!"
                            )
                        else:
                            await ctx.send("❌ Check-in failed. Please try again.")
                        return

            await ctx.send("❌ Registration data not found.")

        except Exception as e:
            await ctx.send(
                "❌ Check-in failed. Please try again or contact the tab team."
            )
            logger.error(f"Error in checkin command: {e}")

    @commands.command(aliases=["check-out"])
    async def checkout(self, ctx):
        """Check out from the tournament"""
        try:
            collection = self.bot.database.get_collection(
                "tournaments", use_tabby_db=True
            )
            if not collection:
                await ctx.send("❌ Database connection error.")
                return

            discord_id = ctx.author.id
            guild_id = ctx.guild.id

            tournament_data = collection.find_one({"_id": guild_id})
            if not tournament_data:
                await ctx.send("❌ This server is not synced with a tournament.")
                return

            headers = {"Authorization": f"Token {tournament_data['token']}"}

            # Try adjudicator first
            adj_data = collection.find_one(
                {"_id": guild_id},
                {"adjudicators": {"$elemMatch": {"discord_id": discord_id}}},
            )

            if adj_data and "adjudicators" in adj_data:
                adj = adj_data["adjudicators"][0]
                response = requests.delete(f"{adj['url']}/checkin", headers=headers)

                if response.status_code == 200:
                    await ctx.send(f"✅ **{adj['name']}** checked out successfully!")
                    try:
                        await ctx.author.send("You were successfully checked out!")
                    except:
                        pass
                else:
                    await ctx.send("❌ Check-out failed. Please try again.")
                return

            # Try debater
            team_data = collection.find_one(
                {"_id": guild_id},
                {"teams": {"$elemMatch": {"speakers.discord_id": discord_id}}},
            )

            if team_data and "teams" in team_data:
                team = team_data["teams"][0]
                for speaker in team["speakers"]:
                    if speaker.get("discord_id") == discord_id:
                        response = requests.delete(
                            f"{speaker['url']}/checkin", headers=headers
                        )

                        if response.status_code == 200:
                            await ctx.send(
                                f"✅ **{speaker['name']}** of **{team['short_name']}** checked out successfully!"
                            )
                            try:
                                await ctx.author.send(
                                    "You were successfully checked out!"
                                )
                            except:
                                pass
                        else:
                            await ctx.send("❌ Check-out failed. Please try again.")
                        return

            await ctx.send("❌ You are not registered for this tournament.")

        except Exception as e:
            await ctx.send("❌ Check-out failed. Please try again.")
            logger.error(f"Error in checkout command: {e}")

    @commands.command()
    async def status(self, ctx):
        """Show tournament status and connection info"""
        try:
            collection = self.bot.database.get_collection(
                "tournaments", use_tabby_db=True
            )
            if not collection:
                await ctx.send("❌ Database connection error.")
                return

            tournament_data = collection.find_one({"_id": ctx.guild.id})

            if not tournament_data:
                embed = discord.Embed(
                    title="❌ Not Connected",
                    description="This server is not synced with any tournament.",
                    color=discord.Color.red(),
                )
                embed.add_field(
                    name="💡 Setup Required",
                    value="Use `.tabsync <url> <token>` to connect to a tournament",
                    inline=False,
                )
            else:
                embed = discord.Embed(
                    title="✅ Tournament Connected",
                    description=f"Connected to **{tournament_data.get('tournament_name', 'Unknown Tournament')}**",
                    color=discord.Color.green(),
                    timestamp=ctx.message.created_at,
                )

                embed.add_field(
                    name="Tournament",
                    value=tournament_data.get("tournament_name", "Unknown"),
                    inline=True,
                )
                embed.add_field(
                    name="Base URL",
                    value=tournament_data.get("site", "Unknown"),
                    inline=True,
                )
                embed.add_field(
                    name="Teams Registered",
                    value=len(tournament_data.get("teams", [])),
                    inline=True,
                )
                embed.add_field(
                    name="Adjudicators Registered",
                    value=len(tournament_data.get("adjudicators", [])),
                    inline=True,
                )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("❌ Error retrieving status.")
            logger.error(f"Error in status command: {e}")

    @commands.command()
    async def motion(self, ctx, round_abbrev):
        """Get motion for a specific round

        Usage: .motion <round_abbreviation>
        Example: .motion R1
        """
        try:
            collection = self.bot.database.get_collection(
                "tournaments", use_tabby_db=True
            )
            if not collection:
                await ctx.send("❌ Database connection error.")
                return

            tournament_data = collection.find_one({"_id": ctx.guild.id})
            if not tournament_data:
                await ctx.send("❌ This server is not synced with a tournament.")
                return

            headers = {"Authorization": f"Token {tournament_data['token']}"}
            rounds_url = f"{tournament_data['tournament']}rounds"

            response = requests.get(rounds_url, headers=headers)

            if response.status_code != 200:
                await ctx.send("❌ Failed to fetch rounds data.")
                return

            rounds = response.json()

            for round_data in rounds:
                if round_data["abbreviation"].lower() == round_abbrev.lower():
                    if not round_data.get("motions_released", False):
                        await ctx.send(
                            f"🔒 The motion for **{round_abbrev}** is not released yet!"
                        )
                        return

                    motions = round_data.get("motions", [])

                    if not motions:
                        await ctx.send(f"❌ No motions found for **{round_abbrev}**")
                        return

                    for i, motion_data in enumerate(motions, 1):
                        motion_text = motion_data.get("text", "No motion text")
                        info_slide = motion_data.get("info_slide", "")

                        embed = discord.Embed(
                            title=f"🎯 Motion {i} for {round_abbrev}",
                            description=f"**{motion_text}**",
                            color=discord.Color.blue(),
                            timestamp=ctx.message.created_at,
                        )

                        if info_slide:
                            embed.add_field(
                                name="📋 Info Slide", value=info_slide, inline=False
                            )

                        embed.set_footer(
                            text=f"Tournament: {tournament_data.get('tournament_name', 'Unknown')}"
                        )

                        await ctx.send(embed=embed)

                    return

            await ctx.send(f"❌ Round **{round_abbrev}** not found.")

        except Exception as e:
            await ctx.send("❌ Error fetching motion.")
            logger.error(f"Error in motion command: {e}")

    @commands.command()
    async def feedback(
        self, ctx, round_abbrev: str, adjudicator: discord.Member, score: float
    ):
        """Submit feedback for an adjudicator

        Usage: .feedback <round> <@adjudicator> <score>
        Example: .feedback R1 @johndoe 8.5
        """
        try:
            # Remove the command message for privacy
            try:
                await ctx.message.delete()
            except:
                await ctx.send(
                    "⚠️ Please give me 'Manage Messages' permission to protect your feedback data."
                )
                return

            if not (0 <= score <= 10):
                await ctx.send("❌ Score must be between 0 and 10.", delete_after=10)
                return

            # Get tournament data from database
            collection = self.database.get_collection("tournaments")
            if collection is None:
                await ctx.send("❌ Database connection error.", delete_after=10)
                return

            tournament_data = collection.find_one({"_id": ctx.guild.id})
            if not tournament_data:
                await ctx.send(
                    "❌ No tournament synced with this server.", delete_after=10
                )
                return

            token = f"Token {tournament_data['token']}"
            headers = {"Authorization": token}

            # Find the submitter (team member)
            submitter_discord_id = ctx.author.id
            submitter_info = None

            for team in tournament_data.get("teams", []):
                for speaker in team.get("speakers", []):
                    if speaker.get("discord_id") == submitter_discord_id:
                        submitter_info = {
                            "team_url": team["url"],
                            "speaker_url": speaker["url"],
                        }
                        break
                if submitter_info:
                    break

            if not submitter_info:
                await ctx.send(
                    "❌ You are not registered for this tournament.", delete_after=10
                )
                return

            # Find the adjudicator
            adj_discord_id = adjudicator.id
            adj_info = None

            for adj in tournament_data.get("adjudicators", []):
                if adj.get("discord_id") == adj_discord_id:
                    adj_info = adj
                    break

            if not adj_info:
                await ctx.send(
                    "❌ Adjudicator not found in tournament database.", delete_after=10
                )
                return

            # Get round and debate information
            rounds_url = f"{tournament_data['tournament']}rounds"
            rounds_response = requests.get(rounds_url, headers=headers, timeout=10)

            if rounds_response.status_code != 200:
                await ctx.send("❌ Failed to fetch rounds data.", delete_after=10)
                return

            rounds = rounds_response.json()
            target_round = None

            for round_data in rounds:
                if round_data["abbreviation"] == round_abbrev:
                    target_round = round_data
                    break

            if not target_round:
                await ctx.send(
                    f"❌ Round **{round_abbrev}** not found.", delete_after=10
                )
                return

            # Get pairings for the round
            pairings_url = f"{target_round['url']}/pairings"
            pairings_response = requests.get(pairings_url, headers=headers, timeout=10)

            if pairings_response.status_code != 200:
                await ctx.send("❌ Failed to fetch pairings data.", delete_after=10)
                return

            pairings = pairings_response.json()
            debate_url = None

            # Find the debate that includes the submitter's team
            for pairing in pairings:
                for team in pairing.get("teams", []):
                    if team["team"] == submitter_info["team_url"]:
                        debate_url = pairing["url"]
                        break
                if debate_url:
                    break

            if not debate_url:
                await ctx.send(
                    "❌ No debate found for your team in this round.", delete_after=10
                )
                return

            # Submit feedback
            feedback_url = f"{tournament_data['tournament']}feedback"
            feedback_data = {
                "adjudicator": adj_info["url"],
                "source": submitter_info["team_url"],
                "debate": debate_url,
                "score": str(score),
                "answers": [],
                "ignored": False,
                "confirmed": True,
                "participant_submitter": None,
            }

            feedback_response = requests.post(
                feedback_url, json=feedback_data, headers=headers, timeout=10
            )

            if feedback_response.status_code == 201:
                # Generate feedback image if available
                try:
                    feedback_image = image_generator.create_feedback_image(
                        round_abbrev, adjudicator.display_name, score
                    )
                    if feedback_image:
                        await ctx.author.send(
                            f"✅ **Feedback submitted successfully!**\nRound: **{round_abbrev}**\nAdjudicator: **{adjudicator.display_name}**\nScore: **{score}**",
                            file=feedback_image,
                        )
                    else:
                        await ctx.author.send(
                            f"✅ **Feedback submitted successfully!**\nRound: **{round_abbrev}**\nAdjudicator: **{adjudicator.display_name}**\nScore: **{score}**"
                        )
                except:
                    await ctx.author.send(
                        f"✅ **Feedback submitted successfully!**\nRound: **{round_abbrev}**\nAdjudicator: **{adjudicator.display_name}**\nScore: **{score}**"
                    )

                await ctx.send("✅ Feedback submitted successfully!", delete_after=5)
            else:
                await ctx.send(
                    f"❌ Failed to submit feedback: {feedback_response.text}",
                    delete_after=10,
                )

        except Exception as e:
            await ctx.send(
                "❌ Error submitting feedback. Please try again.", delete_after=10
            )
            logger.error(f"Error in feedback command: {e}")

    @commands.command(name="delete-data", aliases=["delete_data"])
    @commands.has_permissions(administrator=True)
    async def delete_data(self, ctx, *, confirmation=""):
        """Delete all tournament data for this server

        Usage: .delete-data YES I AM 100% SURE
        This will permanently remove all synced tournament data.
        """
        if confirmation == "YES I AM 100% SURE":
            try:
                collection = self.database.get_collection("tournaments")
                if collection is not None:
                    collection.delete_one({"_id": ctx.guild.id})
                    await ctx.send("✅ ALL TOURNAMENT DATA WAS DELETED SUCCESSFULLY")
                else:
                    await ctx.send("❌ Database connection error.")
            except Exception as e:
                await ctx.send("❌ Error deleting data.")
                logger.error(f"Error in delete_data command: {e}")
        else:
            await ctx.send(
                "Type **YES I AM 100% SURE** after the command to confirm what you are doing"
            )

    @commands.command(name="announce")
    @commands.has_permissions(manage_messages=True)
    async def announce(self, ctx, *, text: str):
        """Send announcement to all debate channels

        Usage: .announce <message>
        Sends the message to all channels with 'debate' in the name.
        """
        try:
            debate_channels = [
                channel
                for channel in ctx.guild.text_channels
                if "debate" in channel.name.lower()
            ]

            if not debate_channels:
                await ctx.send("❌ No debate channels found.")
                return

            # Send to all debate channels
            for channel in debate_channels:
                try:
                    await channel.send(text)
                except:
                    continue

            await ctx.send(
                f"✅ Announcement sent to {len(debate_channels)} debate channels!"
            )

        except Exception as e:
            await ctx.send("❌ Error sending announcement.")
            logger.error(f"Error in announce command: {e}")

    @commands.command(name="begin-debate", aliases=["start-debate"])
    @commands.has_permissions(manage_messages=True)
    async def begin_debate(self, ctx):
        """Move people from prep rooms to debate rooms

        Requires Manage Messages permission.
        Moves all users from prep rooms to their respective debate rooms.
        """
        try:
            moved_count = 0
            venue_categories = [
                category
                for category in ctx.guild.categories
                if "venue" in category.name.lower()
            ]

            for category in venue_categories:
                # Find prep rooms and debate room in this venue
                prep_channels = [
                    channel
                    for channel in category.voice_channels
                    if "prep" in channel.name.lower()
                ]
                debate_channels = [
                    channel
                    for channel in category.voice_channels
                    if "debate" in channel.name.lower()
                ]

                if prep_channels and debate_channels:
                    debate_channel = debate_channels[0]  # Use first debate channel

                    # Move users from all prep rooms to debate room
                    for prep_channel in prep_channels:
                        for member in prep_channel.members:
                            try:
                                if member.voice.self_mute:
                                    await member.edit(voice_channel=debate_channel)
                                else:
                                    await member.edit(
                                        voice_channel=debate_channel, mute=True
                                    )
                                    await asyncio.sleep(0.5)
                                    await member.edit(mute=False)
                                moved_count += 1
                                await asyncio.sleep(0.1)
                            except:
                                continue

                await asyncio.sleep(0.2)

            if moved_count > 0:
                await ctx.send(f"✅ Moved {moved_count} participants to debate rooms!")
            else:
                await ctx.send("ℹ️ No participants found in prep rooms.")

        except Exception as e:
            await ctx.send("❌ Error moving participants.")
            logger.error(f"Error in begin_debate command: {e}")

    @commands.command(name="call-to-venue", aliases=["call-to-room"])
    @commands.has_role("Adjudicator")
    async def call_to_venue(self, ctx):
        """Move people from prep rooms to debate room in current venue

        Requires Adjudicator role.
        Works only when used in a venue category.
        """
        try:
            if not ctx.channel.category:
                await ctx.send("❌ This command must be used in a venue category.")
                return

            category = ctx.channel.category
            moved_count = 0

            # Find prep rooms and debate room in this venue
            prep_channels = [
                channel
                for channel in category.voice_channels
                if "prep" in channel.name.lower()
            ]
            debate_channels = [
                channel
                for channel in category.voice_channels
                if "debate" in channel.name.lower()
            ]

            if not debate_channels:
                await ctx.send("❌ No debate room found in this venue.")
                return

            debate_channel = debate_channels[0]

            # Move users from all prep rooms to debate room
            for prep_channel in prep_channels:
                for member in prep_channel.members:
                    try:
                        if member.voice.self_mute:
                            await member.edit(voice_channel=debate_channel)
                        else:
                            await member.edit(voice_channel=debate_channel, mute=True)
                            await asyncio.sleep(0.5)
                            await member.edit(mute=False)
                        moved_count += 1
                        await asyncio.sleep(0.1)
                    except:
                        continue

            if moved_count > 0:
                await ctx.send(
                    f"✅ Called {moved_count} participants to the debate room!"
                )
            else:
                await ctx.send("ℹ️ No participants found in prep rooms.")

        except Exception as e:
            await ctx.send("❌ Error calling participants.")
            logger.error(f"Error in call_to_venue command: {e}")


async def setup(bot):
    await bot.add_cog(TabbyCommands(bot))
