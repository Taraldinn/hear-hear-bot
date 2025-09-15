"""
Debate Commands for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
"""

import discord
from discord.ext import commands
from discord import app_commands
import random
import logging
from src.utils.language import language_manager

logger = logging.getLogger(__name__)


class DebateCommands(commands.Cog):
    """Commands related to debate activities"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def randommotion(self, ctx, language=None):
        """Get a random debate motion

        Usage: .randommotion [language]
        Languages: english, bangla
        """
        # Get guild language if not specified
        if not language:
            language = await self.bot.get_language(ctx.guild.id)
        else:
            language = language.lower()

        # Validate language
        if language not in language_manager.get_available_languages():
            available = ", ".join(language_manager.get_available_languages())
            await ctx.send(f"❌ Language not supported. Available: {available}")
            return

        # Get random motion (with optional info slide)
        entry = language_manager.get_random_motion_entry(language)
        if not entry:
            await ctx.send("No motions available for this language.")
            return
        motion = entry.get("text")
        info = entry.get("info")

        # Create embed
        embed = discord.Embed(
            title="🎯 Random Debate Motion",
            description=motion,
            color=discord.Color.gold(),
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="Language", value=language.title(), inline=True)
        embed.add_field(
            name="Total Motions",
            value=language_manager.get_motion_count(language),
            inline=True,
        )

        # Include Info Slide if present
        if info:
            embed.add_field(name="Info Slide", value=info, inline=False)

        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @app_commands.command(name="randommotion", description="Get a random debate motion")
    @app_commands.describe(language="Language for the motion (english/bangla)")
    @app_commands.choices(
        language=[
            app_commands.Choice(name="English", value="english"),
            app_commands.Choice(name="Bangla", value="bangla"),
        ]
    )
    async def slash_randommotion(
        self, interaction: discord.Interaction, language: str = "english"
    ):
        """Slash command version of randommotion"""
        # Defer to avoid interaction timeout and allow time for data fetch/processing
        # Try to defer; if token already expired (cold start) use channel fallback
        deferred = False
        use_channel_fallback = False
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(thinking=True)
                deferred = True
            except discord.NotFound:
                # Unknown interaction (token expired). We'll fallback to channel send.
                use_channel_fallback = True
        # Get guild language if not specified
        if not language:
            language = await self.bot.get_language(interaction.guild.id)
        else:
            language = language.lower()

        # Validate language
        if language not in language_manager.get_available_languages():
            available = ", ".join(language_manager.get_available_languages())
            error_msg = f"❌ Language not supported. Available: {available}"
            sent = False
            if use_channel_fallback:
                await interaction.channel.send(error_msg)
                sent = True
            else:
                if deferred:
                    try:
                        await interaction.followup.send(error_msg, ephemeral=True)
                        sent = True
                    except discord.NotFound:
                        await interaction.channel.send(error_msg)
                        sent = True
                else:
                    try:
                        await interaction.response.send_message(
                            error_msg, ephemeral=True
                        )
                        sent = True
                    except discord.NotFound:
                        await interaction.channel.send(error_msg)
                        sent = True
            if sent:
                return

        # Get random motion (with optional info slide)
        entry = language_manager.get_random_motion_entry(language)
        if not entry:
            msg = "No motions available for this language."
            sent = False
            if use_channel_fallback:
                await interaction.channel.send(msg)
                sent = True
            else:
                if deferred:
                    try:
                        await interaction.followup.send(msg, ephemeral=True)
                        sent = True
                    except discord.NotFound:
                        await interaction.channel.send(msg)
                        sent = True
                else:
                    try:
                        await interaction.response.send_message(msg, ephemeral=True)
                        sent = True
                    except discord.NotFound:
                        await interaction.channel.send(msg)
                        sent = True
            if sent:
                return
        motion = entry.get("text")
        info = entry.get("info")

        # Create embed
        embed = discord.Embed(
            title="🎯 Random Debate Motion",
            description=motion,
            color=discord.Color.gold(),
            timestamp=interaction.created_at,
        )

        embed.add_field(name="Language", value=language.title(), inline=True)
        embed.add_field(
            name="Total Motions",
            value=language_manager.get_motion_count(language),
            inline=True,
        )

        # Include Info Slide if present (truncate if too long for Discord)
        if info:
            # Discord embed field values have a 1024 character limit
            info_text = info if len(info) <= 1020 else info[:1017] + "..."
            embed.add_field(name="Info Slide", value=info_text, inline=False)

        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url,
        )

        sent = False
        if use_channel_fallback:
            await interaction.channel.send(embed=embed)
            sent = True
        else:
            if deferred:
                try:
                    await interaction.followup.send(embed=embed)
                    sent = True
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)
                    sent = True
            else:
                try:
                    await interaction.response.send_message(embed=embed)
                    sent = True
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)
                    sent = True

    @commands.command(aliases=["dice", "roll"])
    async def diceroll(self, ctx, sides: int = 6):
        """Roll a dice with specified number of sides (default: 6)"""
        if sides < 2 or sides > 100:
            await ctx.send("❌ Dice must have between 2 and 100 sides.")
            return

        result = random.randint(1, sides)

        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"**{result}** (out of {sides})",
            color=discord.Color.purple(),
            timestamp=ctx.message.created_at,
        )

        embed.set_footer(
            text=f"Rolled by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def toss(self, ctx, *options):
        """Toss to decide between options or determine who goes first

        Usage:
        .toss - Simple heads/tails
        .toss @user1 @user2 - Pick between users
        .toss option1 option2 option3 - Pick between custom options
        """
        if not options:
            # Simple coin toss
            result = random.choice(["Heads", "Tails"])
            embed = discord.Embed(
                title="🪙 Coin Toss",
                description=f"**{result}**",
                color=discord.Color.orange(),
                timestamp=ctx.message.created_at,
            )
            embed.set_footer(
                text=f"Tossed by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url,
            )
        else:
            # Toss between options
            # Handle mentions vs text options
            if ctx.message.mentions:
                # Use mentioned users
                chosen = random.choice(ctx.message.mentions)
                embed = discord.Embed(
                    title="🎯 Toss Result",
                    description=f"**{chosen.mention} goes first!**",
                    color=discord.Color.gold(),
                    timestamp=ctx.message.created_at,
                )
                embed.add_field(
                    name="Participants",
                    value=" vs ".join([user.mention for user in ctx.message.mentions]),
                    inline=False,
                )
            else:
                # Use text options
                chosen = random.choice(options)
                embed = discord.Embed(
                    title="🎯 Toss Result",
                    description=f"**{chosen}**",
                    color=discord.Color.gold(),
                    timestamp=ctx.message.created_at,
                )
                embed.add_field(
                    name="Options", value=" vs ".join(options), inline=False
                )

            embed.set_footer(
                text=f"Tossed by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url,
            )

        await ctx.send(embed=embed)

    @app_commands.command(
        name="toss",
        description="Toss to decide between options or determine who goes first",
    )
    @app_commands.describe(
        option1="First option or user",
        option2="Second option or user (optional for coin toss)",
        option3="Third option (optional)",
        option4="Fourth option (optional)",
    )
    async def slash_toss(
        self,
        interaction: discord.Interaction,
        option1: str | None = None,
        option2: str | None = None,
        option3: str | None = None,
        option4: str | None = None,
    ):
        """Slash command version of toss"""
        # Handle interaction token expiry
        deferred = False
        use_channel_fallback = False
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(thinking=True)
                deferred = True
            except discord.NotFound:
                use_channel_fallback = True

        # Collect non-None options
        options = [opt for opt in [option1, option2, option3, option4] if opt]

        if not options:
            # Simple coin toss
            result = random.choice(["Heads", "Tails"])
            embed = discord.Embed(
                title="🪙 Coin Toss",
                description=f"**{result}**",
                color=discord.Color.orange(),
                timestamp=interaction.created_at,
            )
            embed.set_footer(
                text=f"Tossed by {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url,
            )
        else:
            # Toss between options
            chosen = random.choice(options)
            embed = discord.Embed(
                title="🎯 Toss Result",
                description=f"**{chosen}**",
                color=discord.Color.gold(),
                timestamp=interaction.created_at,
            )
            embed.add_field(name="Options", value=" vs ".join(options), inline=False)
            embed.set_footer(
                text=f"Tossed by {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url,
            )

        # Send response with fallback handling
        if use_channel_fallback:
            await interaction.channel.send(embed=embed)
        else:
            if deferred:
                try:
                    await interaction.followup.send(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)
            else:
                try:
                    await interaction.response.send_message(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)

    @commands.command(aliases=["ap-toss", "aptoss"])
    async def ap_toss(self, ctx, team1: str = "Team 1", team2: str = "Team 2"):
        """Asian Parliamentary toss for 2 teams and Gov/Opp sides

        Usage: .ap_toss [team1] [team2]
        """
        # Randomly assign teams to sides
        teams = [team1, team2]
        sides = ["Government", "Opposition"]

        # Shuffle teams to randomize assignment
        random.shuffle(teams)

        embed = discord.Embed(
            title="🏛️ Asian Parliamentary Toss",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="🏛️ Government Side", value=f"**{teams[0]}**", inline=True)

        embed.add_field(name="⚖️ Opposition Side", value=f"**{teams[1]}**", inline=True)

        embed.add_field(
            name="🎯 Format", value="Asian Parliamentary (2 teams)", inline=False
        )

        embed.set_footer(
            text=f"Tossed by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["bp-toss", "bptoss"])
    async def bp_toss(
        self,
        ctx,
        team1: str = "Team 1",
        team2: str = "Team 2",
        team3: str = "Team 3",
        team4: str = "Team 4",
    ):
        """British Parliamentary toss for 4 teams and OG/OO/CG/CO sides

        Usage: .bp_toss [team1] [team2] [team3] [team4]
        """
        # Randomly assign teams to sides
        teams = [team1, team2, team3, team4]
        sides = [
            "Opening Government (OG)",
            "Opening Opposition (OO)",
            "Closing Government (CG)",
            "Closing Opposition (CO)",
        ]

        # Shuffle teams to randomize assignment
        random.shuffle(teams)

        embed = discord.Embed(
            title="🏆 British Parliamentary Toss",
            color=discord.Color.gold(),
            timestamp=ctx.message.created_at,
        )

        embed.add_field(
            name="🏛️ Opening Government (OG)", value=f"**{teams[0]}**", inline=True
        )

        embed.add_field(
            name="⚖️ Opening Opposition (OO)", value=f"**{teams[1]}**", inline=True
        )

        embed.add_field(
            name="📊 Room Layout", value="OG ↔️ OO\n⬇️      ⬇️\nCG ↔️ CO", inline=False
        )

        embed.add_field(
            name="🏛️ Closing Government (CG)", value=f"**{teams[2]}**", inline=True
        )

        embed.add_field(
            name="⚖️ Closing Opposition (CO)", value=f"**{teams[3]}**", inline=True
        )

        embed.add_field(
            name="🎯 Format", value="British Parliamentary (4 teams)", inline=False
        )

        embed.set_footer(
            text=f"Tossed by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    # Slash command versions for AP and BP toss
    @app_commands.command(
        name="ap-toss", description="Asian Parliamentary toss for 2 teams (Gov/Opp)"
    )
    @app_commands.describe(team1="First team name", team2="Second team name")
    async def slash_ap_toss(
        self,
        interaction: discord.Interaction,
        team1: str = "Team 1",
        team2: str = "Team 2",
    ):
        """Slash command version of AP toss"""
        # Handle interaction token expiry
        deferred = False
        use_channel_fallback = False
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(thinking=True)
                deferred = True
            except discord.NotFound:
                use_channel_fallback = True

        # Randomly assign teams to sides
        teams = [team1, team2]
        random.shuffle(teams)

        embed = discord.Embed(
            title="🏛️ Asian Parliamentary Toss",
            color=discord.Color.blue(),
            timestamp=interaction.created_at,
        )

        embed.add_field(name="🏛️ Government Side", value=f"**{teams[0]}**", inline=True)

        embed.add_field(name="⚖️ Opposition Side", value=f"**{teams[1]}**", inline=True)

        embed.add_field(
            name="🎯 Format", value="Asian Parliamentary (2 teams)", inline=False
        )

        embed.set_footer(
            text=f"Tossed by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url,
        )

        # Send response with fallback handling
        if use_channel_fallback:
            await interaction.channel.send(embed=embed)
        else:
            if deferred:
                try:
                    await interaction.followup.send(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)
            else:
                try:
                    await interaction.response.send_message(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)

    @app_commands.command(
        name="bp-toss",
        description="British Parliamentary toss for 4 teams (OG/OO/CG/CO)",
    )
    @app_commands.describe(
        team1="First team name",
        team2="Second team name",
        team3="Third team name",
        team4="Fourth team name",
    )
    async def slash_bp_toss(
        self,
        interaction: discord.Interaction,
        team1: str = "Team 1",
        team2: str = "Team 2",
        team3: str = "Team 3",
        team4: str = "Team 4",
    ):
        """Slash command version of BP toss"""
        # Handle interaction token expiry
        deferred = False
        use_channel_fallback = False
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(thinking=True)
                deferred = True
            except discord.NotFound:
                use_channel_fallback = True

        # Randomly assign teams to sides
        teams = [team1, team2, team3, team4]
        random.shuffle(teams)

        embed = discord.Embed(
            title="🏆 British Parliamentary Toss",
            color=discord.Color.gold(),
            timestamp=interaction.created_at,
        )

        embed.add_field(
            name="🏛️ Opening Government (OG)", value=f"**{teams[0]}**", inline=True
        )

        embed.add_field(
            name="⚖️ Opening Opposition (OO)", value=f"**{teams[1]}**", inline=True
        )

        embed.add_field(
            name="📊 Room Layout", value="OG ↔️ OO\n⬇️      ⬇️\nCG ↔️ CO", inline=False
        )

        embed.add_field(
            name="🏛️ Closing Government (CG)", value=f"**{teams[2]}**", inline=True
        )

        embed.add_field(
            name="⚖️ Closing Opposition (CO)", value=f"**{teams[3]}**", inline=True
        )

        embed.add_field(
            name="🎯 Format", value="British Parliamentary (4 teams)", inline=False
        )

        embed.set_footer(
            text=f"Tossed by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url,
        )

        # Send response with fallback handling
        if use_channel_fallback:
            await interaction.channel.send(embed=embed)
        else:
            if deferred:
                try:
                    await interaction.followup.send(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)
            else:
                try:
                    await interaction.response.send_message(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)

    @commands.command()
    async def positions(self, ctx):
        """Show debate positions and speaking order"""
        embed = discord.Embed(
            title="📋 Debate Positions & Speaking Order",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at,
        )

        # Government positions
        gov_positions = [
            "**Prime Minister (PM)** - Opening government case",
            "**Deputy Prime Minister (DPM)** - Extending government case",
            "**Member of Government (MG)** - Extending government case",
            "**Government Whip (GW)** - Rebuttal and summary",
        ]

        # Opposition positions
        opp_positions = [
            "**Leader of Opposition (LO)** - Opening opposition case",
            "**Deputy Leader of Opposition (DLO)** - Extending opposition case",
            "**Member of Opposition (MO)** - Extending opposition case",
            "**Opposition Whip (OW)** - Rebuttal and summary",
        ]

        embed.add_field(
            name="🏛️ Government Side", value="\n".join(gov_positions), inline=False
        )

        embed.add_field(
            name="⚖️ Opposition Side", value="\n".join(opp_positions), inline=False
        )

        embed.add_field(
            name="⏱️ Speaking Order",
            value="PM → LO → DPM → DLO → MG → MO → OW → GW",
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def formats(self, ctx):
        """Show different debate formats"""
        embed = discord.Embed(
            title="🗣️ Debate Formats",
            color=discord.Color.green(),
            timestamp=ctx.message.created_at,
        )

        formats = [
            "**British Parliamentary (BP)** - 4 teams, 8 speakers",
            "**Asian Parliamentary** - 2 teams, 6 speakers",
            "**World Schools** - 2 teams, 6 speakers + POI",
            "**Public Forum** - 2 teams, 4 speakers",
            "**Policy Debate** - 2 teams, 4 speakers",
        ]

        embed.add_field(name="Common Formats", value="\n".join(formats), inline=False)

        embed.add_field(
            name="💡 Tip",
            value="Use `.positions` to see BP speaking order and positions",
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["stats"])
    async def motionstats(self, ctx):
        """Show motion statistics"""
        stats = {}
        total_motions = 0

        for language in language_manager.get_available_languages():
            count = language_manager.get_motion_count(language)
            stats[language] = count
            total_motions += count

        embed = discord.Embed(
            title="📊 Motion Statistics",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at,
        )

        for language, count in stats.items():
            embed.add_field(
                name=f"{language.title()} Motions",
                value=f"{count} motions",
                inline=True,
            )

        embed.add_field(
            name="Total Motions", value=f"{total_motions} motions", inline=False
        )

        embed.set_footer(text="Use .randommotion [language] to get a random motion")

        await ctx.send(embed=embed)

    # Slash command versions for remaining commands
    @app_commands.command(
        name="diceroll", description="Roll a dice with specified number of sides"
    )
    @app_commands.describe(sides="Number of sides on the dice (2-100, default: 6)")
    async def slash_diceroll(self, interaction: discord.Interaction, sides: int = 6):
        """Slash command version of diceroll"""
        # Handle interaction token expiry
        deferred = False
        use_channel_fallback = False
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(thinking=True)
                deferred = True
            except discord.NotFound:
                use_channel_fallback = True

        if sides < 2 or sides > 100:
            error_msg = "❌ Dice must have between 2 and 100 sides."
            if use_channel_fallback:
                await interaction.channel.send(error_msg)
            else:
                if deferred:
                    try:
                        await interaction.followup.send(error_msg, ephemeral=True)
                    except discord.NotFound:
                        await interaction.channel.send(error_msg)
                else:
                    try:
                        await interaction.response.send_message(
                            error_msg, ephemeral=True
                        )
                    except discord.NotFound:
                        await interaction.channel.send(error_msg)
            return

        result = random.randint(1, sides)

        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"**{result}** (out of {sides})",
            color=discord.Color.purple(),
            timestamp=interaction.created_at,
        )

        embed.set_footer(
            text=f"Rolled by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url,
        )

        # Send response with fallback handling
        if use_channel_fallback:
            await interaction.channel.send(embed=embed)
        else:
            if deferred:
                try:
                    await interaction.followup.send(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)
            else:
                try:
                    await interaction.response.send_message(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)

    @app_commands.command(
        name="positions", description="Show debate positions and speaking order"
    )
    async def slash_positions(self, interaction: discord.Interaction):
        """Slash command version of positions"""
        # Handle interaction token expiry
        deferred = False
        use_channel_fallback = False
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(thinking=True)
                deferred = True
            except discord.NotFound:
                use_channel_fallback = True

        embed = discord.Embed(
            title="📋 Debate Positions & Speaking Order",
            color=discord.Color.blue(),
            timestamp=interaction.created_at,
        )

        # Government positions
        gov_positions = [
            "**Prime Minister (PM)** - Opening government case",
            "**Deputy Prime Minister (DPM)** - Extending government case",
            "**Member of Government (MG)** - Extending government case",
            "**Government Whip (GW)** - Rebuttal and summary",
        ]

        # Opposition positions
        opp_positions = [
            "**Leader of Opposition (LO)** - Opening opposition case",
            "**Deputy Leader of Opposition (DLO)** - Extending opposition case",
            "**Member of Opposition (MO)** - Extending opposition case",
            "**Opposition Whip (OW)** - Rebuttal and summary",
        ]

        embed.add_field(
            name="🏛️ Government Side", value="\n".join(gov_positions), inline=False
        )

        embed.add_field(
            name="⚖️ Opposition Side", value="\n".join(opp_positions), inline=False
        )

        embed.add_field(
            name="⏱️ Speaking Order",
            value="PM → LO → DPM → DLO → MG → MO → OW → GW",
            inline=False,
        )

        # Send response with fallback handling
        if use_channel_fallback:
            await interaction.channel.send(embed=embed)
        else:
            if deferred:
                try:
                    await interaction.followup.send(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)
            else:
                try:
                    await interaction.response.send_message(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)

    @app_commands.command(name="formats", description="Show different debate formats")
    async def slash_formats(self, interaction: discord.Interaction):
        """Slash command version of formats"""
        # Handle interaction token expiry
        deferred = False
        use_channel_fallback = False
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(thinking=True)
                deferred = True
            except discord.NotFound:
                use_channel_fallback = True

        embed = discord.Embed(
            title="🗣️ Debate Formats",
            color=discord.Color.green(),
            timestamp=interaction.created_at,
        )

        formats = [
            "**British Parliamentary (BP)** - 4 teams, 8 speakers",
            "**Asian Parliamentary** - 2 teams, 6 speakers",
            "**World Schools** - 2 teams, 6 speakers + POI",
            "**Public Forum** - 2 teams, 4 speakers",
            "**Policy Debate** - 2 teams, 4 speakers",
        ]

        embed.add_field(name="Common Formats", value="\n".join(formats), inline=False)

        embed.add_field(
            name="💡 Tip",
            value="Use `/positions` to see BP speaking order and positions",
            inline=False,
        )

        # Send response with fallback handling
        if use_channel_fallback:
            await interaction.channel.send(embed=embed)
        else:
            if deferred:
                try:
                    await interaction.followup.send(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)
            else:
                try:
                    await interaction.response.send_message(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)

    @app_commands.command(name="motionstats", description="Show motion statistics")
    async def slash_motionstats(self, interaction: discord.Interaction):
        """Slash command version of motionstats"""
        # Handle interaction token expiry
        deferred = False
        use_channel_fallback = False
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(thinking=True)
                deferred = True
            except discord.NotFound:
                use_channel_fallback = True

        stats = {}
        total_motions = 0

        for language in language_manager.get_available_languages():
            count = language_manager.get_motion_count(language)
            stats[language] = count
            total_motions += count

        embed = discord.Embed(
            title="📊 Motion Statistics",
            color=discord.Color.blue(),
            timestamp=interaction.created_at,
        )

        for language, count in stats.items():
            embed.add_field(
                name=f"{language.title()} Motions",
                value=f"{count} motions",
                inline=True,
            )

        embed.add_field(
            name="Total Motions", value=f"{total_motions} motions", inline=False
        )

        embed.set_footer(text="Use /randommotion to get a random motion")

        # Send response with fallback handling
        if use_channel_fallback:
            await interaction.channel.send(embed=embed)
        else:
            if deferred:
                try:
                    await interaction.followup.send(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)
            else:
                try:
                    await interaction.response.send_message(embed=embed)
                except discord.NotFound:
                    await interaction.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DebateCommands(bot))
