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
        
        # Get random motion
        motion = language_manager.get_random_motion(language)
        
        # Create embed
        embed = discord.Embed(
            title="🎯 Random Debate Motion",
            description=motion,
            color=discord.Color.gold(),
            timestamp=ctx.message.created_at
        )
        
        embed.add_field(name="Language", value=language.title(), inline=True)
        embed.add_field(
            name="Total Motions", 
            value=language_manager.get_motion_count(language), 
            inline=True
        )
        
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}", 
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.send(embed=embed)
    
    @app_commands.command(name="randommotion", description="Get a random debate motion")
    @app_commands.describe(language="Language for the motion (english/bangla)")
    @app_commands.choices(language=[
        app_commands.Choice(name="English", value="english"),
        app_commands.Choice(name="Bangla", value="bangla")
    ])
    async def slash_randommotion(self, interaction: discord.Interaction, language: str = "english"):
        """Slash command version of randommotion"""
        # Get guild language if not specified
        if not language:
            language = await self.bot.get_language(interaction.guild.id)
        else:
            language = language.lower()
        
        # Validate language
        if language not in language_manager.get_available_languages():
            available = ", ".join(language_manager.get_available_languages())
            await interaction.response.send_message(f"❌ Language not supported. Available: {available}", ephemeral=True)
            return
        
        # Get random motion
        motion = language_manager.get_random_motion(language)
        
        # Create embed
        embed = discord.Embed(
            title="🎯 Random Debate Motion",
            description=motion,
            color=discord.Color.gold(),
            timestamp=interaction.created_at
        )
        
        embed.add_field(name="Language", value=language.title(), inline=True)
        embed.add_field(
            name="Total Motions", 
            value=language_manager.get_motion_count(language), 
            inline=True
        )
        
        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}", 
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)
    
    @commands.command(aliases=['flip', 'coin'])
    async def coinflip(self, ctx):
        """Flip a coin for random decisions"""
        result = random.choice(['Heads', 'Tails'])
        
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"**{result}**",
            color=discord.Color.orange(),
            timestamp=ctx.message.created_at
        )
        
        embed.set_footer(
            text=f"Flipped by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['dice', 'roll'])
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
            timestamp=ctx.message.created_at
        )
        
        embed.set_footer(
            text=f"Rolled by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def positions(self, ctx):
        """Show debate positions and speaking order"""
        embed = discord.Embed(
            title="📋 Debate Positions & Speaking Order",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        
        # Government positions
        gov_positions = [
            "**Prime Minister (PM)** - Opening government case",
            "**Deputy Prime Minister (DPM)** - Extending government case",
            "**Member of Government (MG)** - Extending government case", 
            "**Government Whip (GW)** - Rebuttal and summary"
        ]
        
        # Opposition positions
        opp_positions = [
            "**Leader of Opposition (LO)** - Opening opposition case",
            "**Deputy Leader of Opposition (DLO)** - Extending opposition case",
            "**Member of Opposition (MO)** - Extending opposition case",
            "**Opposition Whip (OW)** - Rebuttal and summary"
        ]
        
        embed.add_field(
            name="🏛️ Government Side",
            value="\n".join(gov_positions),
            inline=False
        )
        
        embed.add_field(
            name="⚖️ Opposition Side", 
            value="\n".join(opp_positions),
            inline=False
        )
        
        embed.add_field(
            name="⏱️ Speaking Order",
            value="PM → LO → DPM → DLO → MG → MO → OW → GW",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def formats(self, ctx):
        """Show different debate formats"""
        embed = discord.Embed(
            title="🗣️ Debate Formats",
            color=discord.Color.green(),
            timestamp=ctx.message.created_at
        )
        
        formats = [
            "**British Parliamentary (BP)** - 4 teams, 8 speakers",
            "**Asian Parliamentary** - 2 teams, 6 speakers", 
            "**World Schools** - 2 teams, 6 speakers + POI",
            "**Public Forum** - 2 teams, 4 speakers",
            "**Policy Debate** - 2 teams, 4 speakers"
        ]
        
        embed.add_field(
            name="Common Formats",
            value="\n".join(formats),
            inline=False
        )
        
        embed.add_field(
            name="💡 Tip",
            value="Use `.positions` to see BP speaking order and positions",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['stats'])
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
            timestamp=ctx.message.created_at
        )
        
        for language, count in stats.items():
            embed.add_field(
                name=f"{language.title()} Motions",
                value=f"{count} motions",
                inline=True
            )
        
        embed.add_field(
            name="Total Motions",
            value=f"{total_motions} motions",
            inline=False
        )
        
        embed.set_footer(
            text="Use .randommotion [language] to get a random motion"
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DebateCommands(bot))
