"""
Slash Commands - Discord Application Commands
Author: aldinn
Email: kferdoush617@gmail.com
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import random
from src.utils.language import language_manager

logger = logging.getLogger(__name__)


class SlashCommands(commands.Cog):
    """Modern slash commands for the bot"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="coinflip", description="Flip a coin for random decisions"
    )
    async def coinflip(self, interaction: discord.Interaction):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])

        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"**{result}**",
            color=discord.Color.orange(),
            timestamp=interaction.created_at,
        )

        embed.set_footer(
            text=f"Flipped by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url,
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency"""
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green(),
            timestamp=interaction.created_at,
        )

        # Bot latency
        latency = round(self.bot.latency * 1000)
        embed.add_field(name="Bot Latency", value=f"{latency}ms", inline=True)

        # Status indicator
        if latency < 100:
            status = "🟢 Excellent"
        elif latency < 200:
            status = "🟡 Good"
        else:
            status = "🔴 Poor"

        embed.add_field(name="Status", value=status, inline=True)

        await interaction.response.send_message(embed=embed)

    # Note: Help command moved to src.commands.help module to avoid conflicts


async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
