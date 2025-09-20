"""
Enhanced Help System for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class HelpSystem(commands.Cog):
    """Enhanced help system showcasing all bot features"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help", description="Show comprehensive bot help and features"
    )
    @app_commands.describe(category="Specific category to get help for")
    @app_commands.choices(
        category=[
            app_commands.Choice(name="🎯 Debate Commands", value="debate"),
            app_commands.Choice(name="⏱️ Timer Commands", value="timer"),
            app_commands.Choice(name="🎭 Reaction Roles", value="reaction_roles"),
            app_commands.Choice(name="📊 Logging System", value="logging"),
            app_commands.Choice(name="🛡️ Moderation", value="moderation"),
            app_commands.Choice(name="⚙️ Configuration", value="config"),
            app_commands.Choice(name="🔧 Admin Commands", value="admin"),
            app_commands.Choice(name="🛠️ Utility Commands", value="utility"),
        ]
    )
    async def help_command(
        self, interaction: discord.Interaction, category: Optional[str] = None
    ):
        """Comprehensive help command"""
        try:
            await interaction.response.defer()

            if category:
                embed = await self.get_category_help(category)
            else:
                embed = await self.get_main_help()

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Failed to send help: {e}")
            await interaction.followup.send(
                "❌ Failed to load help information.", ephemeral=True
            )

    async def get_main_help(self) -> discord.Embed:
        """Get main help embed with overview"""
        embed = discord.Embed(
            title="🎯 Hear! Hear! Bot - Complete Feature Guide",
            description="**A comprehensive debate and server management bot with Carl-bot level features!**",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )

        embed.add_field(
            name="🎯 **Debate Features**",
            value=(
                "• **Motion System**: Load from Google Sheets/CSV with info slides\n"
                "• **Random Motions**: Get debate motions in English/Bangla\n"
                "• **Toss Commands**: Regular, AP (Asian Parliamentary), BP (British Parliamentary)\n"
                "• **Position Tools**: Show debate positions and formats\n"
                "• **Motion Stats**: Track motion usage and popularity"
            ),
            inline=False,
        )

        embed.add_field(
            name="⏱️ **Timer System**",
            value=(
                "• **Speech Timers**: Customizable debate speech timing\n"
                "• **Visual Indicators**: Color-coded progress bars\n"
                "• **Multiple Timers**: Run several timers simultaneously\n"
                "• **Pause/Resume**: Full timer control\n"
                "• **Auto Cleanup**: Automatic timer management"
            ),
            inline=False,
        )

        embed.add_field(
            name="🎭 **Advanced Reaction Roles**",
            value=(
                "• **Multiple Modes**: Unique, verify, reversed, binding, temporary\n"
                "• **High Limits**: Support for 250+ roles per message\n"
                "• **Any Emoji**: Use custom emojis from any server\n"
                "• **Self-Destruct**: Messages that auto-delete\n"
                "• **Role Limits**: Max users per role\n"
                "• **Whitelist/Blacklist**: Control who can use roles"
            ),
            inline=False,
        )

        embed.add_field(
            name="📊 **Comprehensive Logging**",
            value=(
                "• **Message Logs**: Track edits, deletes, and purges\n"
                "• **Member Logs**: Role changes, nickname updates\n"
                "• **Join/Leave Tracking**: With invite usage detection\n"
                "• **Server Logs**: Channel, role, and emoji changes\n"
                "• **Flexible Setup**: Split logs into different channels\n"
                "• **Smart Filtering**: Ignore specific channels, users, or prefixes"
            ),
            inline=False,
        )

        embed.add_field(
            name="🛡️ **Advanced Moderation**",
            value=(
                "• **Timed Actions**: Mute, ban with automatic expiry\n"
                "• **Sticky Roles**: Roles persist when users rejoin\n"
                "• **Moderation Logs**: Full audit trail with case IDs\n"
                "• **Bulk Management**: Mass role operations\n"
                "• **Infraction History**: Track user violations\n"
                "• **Drama Channel**: Highlight rule violations for mods"
            ),
            inline=False,
        )

        embed.add_field(
            name="⚙️ **Server Configuration**",
            value=(
                "• **Custom Prefixes**: Multiple command prefixes\n"
                "• **Auto Roles**: Automatic role assignment for new members\n"
                "• **Welcome/Farewell**: Customizable member messages\n"
                "• **Language Support**: English and Bangla\n"
                "• **Timezone Settings**: Server-specific time zones"
            ),
            inline=False,
        )

        embed.add_field(
            name="🚀 **Quick Start Commands**",
            value=(
                "`/help [category]` - Get specific help\n"
                "`/config` - View server configuration\n"
                "`/setup-logging` - Configure log channels\n"
                "`/reactionrole` - Create reaction roles\n"
                "`/timer start` - Start a debate timer\n"
                "`/randommotion` - Get a random motion"
            ),
            inline=False,
        )

        embed.add_field(
            name="💡 **Pro Tips**",
            value=(
                "• Use `/guild_sync` for instant slash command access\n"
                "• Set up logging before moderation for full tracking\n"
                "• Configure reaction roles with verify mode for important roles\n"
                "• Use sticky roles to prevent role loss on rejoin\n"
                "• Load motions from Google Sheets for easy management"
            ),
            inline=False,
        )

        embed.set_footer(
            text="Made for the debate community ❤️ | Use /help [category] for detailed help"
        )

        return embed

    async def get_category_help(self, category: str) -> discord.Embed:
        """Get help for a specific category"""
        category_helps = {
            "debate": self.get_debate_help(),
            "timer": self.get_timer_help(),
            "reaction_roles": self.get_reaction_roles_help(),
            "logging": self.get_logging_help(),
            "moderation": self.get_moderation_help(),
            "config": self.get_config_help(),
            "admin": self.get_admin_help(),
            "utility": self.get_utility_help(),
        }

        return category_helps.get(category, await self.get_main_help())

    def get_debate_help(self) -> discord.Embed:
        """Get debate commands help"""
        embed = discord.Embed(
            title="🎯 Debate Commands",
            description="Complete debate tournament and practice tools",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="📋 **Motion Commands**",
            value=(
                "`/randommotion [language]` - Get a random debate motion\n"
                "`/motionstats` - View motion usage statistics\n"
                "• Loads from Google Sheets, CSV, or text files\n"
                "• Supports info slides for complex motions\n"
                "• Tracks motion popularity and usage"
            ),
            inline=False,
        )

        embed.add_field(
            name="🎲 **Toss Commands**",
            value=(
                "`/toss [user1] [user2] ...` - General coin toss with options\n"
                "`/ap-toss [team1] [team2]` - Asian Parliamentary toss (Gov/Opp)\n"
                "`/bp-toss [team1] [team2] [team3] [team4]` - British Parliamentary toss (OG/OO/CG/CO)\n"
                "• Randomly assigns teams to sides\n"
                "• Format-specific positioning\n"
                "• Mentions users in results"
            ),
            inline=False,
        )

        embed.add_field(
            name="🎯 **Format Commands**",
            value=(
                "`/positions` - Show all debate positions and roles\n"
                "`/formats` - List supported debate formats\n"
                "`/diceroll [sides] [count]` - Roll dice for random decisions\n"
                "• Comprehensive format coverage\n"
                "• Educational position explanations"
            ),
            inline=False,
        )

        embed.add_field(
            name="💡 **Pro Tips**",
            value=(
                "• Load motions from Google Sheets URL for easy updates\n"
                "• Use AP/BP toss for tournament-style random assignment\n"
                "• Info slides provide context for complex motions\n"
                "• Motion stats help track popular topics"
            ),
            inline=False,
        )

        return embed

    def get_timer_help(self) -> discord.Embed:
        """Get timer commands help"""
        embed = discord.Embed(
            title="⏱️ Timer System",
            description="Advanced debate timing with visual progress",
            color=discord.Color.orange(),
        )

        embed.add_field(
            name="🎮 **Timer Controls**",
            value=(
                "`/timer start [duration] [title]` - Start a new timer\n"
                "`/timer pause` - Pause the current timer\n"
                "`/timer resume` - Resume a paused timer\n"
                "`/timer stop` - Stop and clean up timer\n"
                "`/timer status` - Check current timer status"
            ),
            inline=False,
        )

        embed.add_field(
            name="🎨 **Visual Features**",
            value=(
                "• **Color-coded progress bars**: Green → Yellow → Red\n"
                "• **Live updates**: Real-time progress display\n"
                "• **Custom titles**: Name your timers\n"
                "• **Automatic cleanup**: No manual intervention needed\n"
                "• **Multiple timers**: Run several simultaneously"
            ),
            inline=False,
        )

        embed.add_field(
            name="⚙️ **Timer Formats**",
            value=(
                "• **Seconds**: `30s` or `30`\n"
                "• **Minutes**: `5m` or `5:00`\n"
                "• **Hours**: `1h` or `1:00:00`\n"
                "• **Mixed**: `1h30m` or `1:30:00`\n"
                "• **Common presets**: Quick access to standard times"
            ),
            inline=False,
        )

        return embed

    def get_reaction_roles_help(self) -> discord.Embed:
        """Get reaction roles help"""
        embed = discord.Embed(
            title="🎭 Advanced Reaction Roles",
            description="Carl-bot level reaction role system with advanced features",
            color=discord.Color.purple(),
        )

        embed.add_field(
            name="🎯 **Setup Commands**",
            value=(
                "`/reactionrole` - Create a new reaction role message\n"
                "`/add-reaction-role` - Add roles to existing messages\n"
                "• Choose from 6 different modes\n"
                "• Set self-destruct timers\n"
                "• Configure role limits and restrictions"
            ),
            inline=False,
        )

        embed.add_field(
            name="⚙️ **Available Modes**",
            value=(
                "**Normal**: Standard reaction role behavior\n"
                "**Unique**: Users can only pick one role\n"
                "**Verify**: Users must confirm role selection\n"
                "**Reversed**: Reactions remove roles instead\n"
                "**Binding**: Roles cannot be removed once assigned\n"
                "**Temporary**: Roles expire after a set time"
            ),
            inline=False,
        )

        embed.add_field(
            name="🚀 **Advanced Features**",
            value=(
                "• **High Limits**: 250+ roles per message\n"
                "• **Any Emoji**: Use emojis from any server\n"
                "• **Self-Destruct**: Messages auto-delete\n"
                "• **Role Whitelist/Blacklist**: Control access\n"
                "• **Max Uses**: Limit users per role\n"
                "• **Rich Embeds**: Beautiful, informative displays"
            ),
            inline=False,
        )

        return embed

    def get_logging_help(self) -> discord.Embed:
        """Get logging system help"""
        embed = discord.Embed(
            title="📊 Comprehensive Logging",
            description="Track everything happening in your server",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="🎯 **Setup Command**",
            value=(
                "`/setup-logging` - Configure all logging channels\n"
                "• **Message Logs**: Edits, deletes, purges\n"
                "• **Member Logs**: Roles, nicknames, avatars\n"
                "• **Server Logs**: Channels, roles, emojis\n"
                "• **Join/Leave**: Member activity with invite tracking\n"
                "• **Invite Tracking**: See which invite was used"
            ),
            inline=False,
        )

        embed.add_field(
            name="🔍 **What Gets Logged**",
            value=(
                "**Messages**: Content, attachments, embeds, reactions\n"
                "**Members**: Role changes, nickname updates, avatar changes\n"
                "**Server**: Channel creation/deletion, role management\n"
                "**Moderation**: All mod actions with case IDs\n"
                "**Invites**: Track invite usage and creators"
            ),
            inline=False,
        )

        embed.add_field(
            name="⚙️ **Smart Filtering**",
            value=(
                "• **Ignored Channels**: Skip logging for specific channels\n"
                "• **Ignored Users**: Don't log certain users (like bots)\n"
                "• **Ignored Prefixes**: Skip messages starting with specific text\n"
                "• **Channel Splitting**: Separate logs by type for organization"
            ),
            inline=False,
        )

        return embed

    def get_moderation_help(self) -> discord.Embed:
        """Get moderation commands help"""
        embed = discord.Embed(
            title="🛡️ Advanced Moderation",
            description="Powerful moderation tools with full audit trails",
            color=discord.Color.red(),
        )

        embed.add_field(
            name="⚔️ **Moderation Commands**",
            value=(
                "`/mute [user] [duration] [reason]` - Mute with auto-expiry\n"
                "`/unmute [user] [reason]` - Remove mute from user\n"
                "`/kick [user] [reason]` - Kick user (saves sticky roles)\n"
                "`/ban [user] [duration] [reason]` - Ban with optional time limit\n"
                "• All actions generate case IDs for tracking\n"
                "• Full moderation log integration"
            ),
            inline=False,
        )

        embed.add_field(
            name="🏷️ **Advanced Features**",
            value=(
                "**Sticky Roles**: Roles persist when users rejoin\n"
                "**Timed Actions**: Auto-expiry for mutes and bans\n"
                "**Case IDs**: Track all moderation actions\n"
                "**DM Notifications**: Users get notified of actions\n"
                "**Infraction History**: Full audit trail per user\n"
                "**Drama Channel**: Alert mods to rule violations"
            ),
            inline=False,
        )

        embed.add_field(
            name="⏰ **Duration Formats**",
            value=(
                "• **Minutes**: `10m`, `30m`\n"
                "• **Hours**: `2h`, `12h`\n"
                "• **Days**: `1d`, `7d`\n"
                "• **Mixed**: `1d12h30m`\n"
                "• **Permanent**: Leave duration empty"
            ),
            inline=False,
        )

        return embed

    def get_config_help(self) -> discord.Embed:
        """Get configuration commands help"""
        embed = discord.Embed(
            title="⚙️ Server Configuration",
            description="Customize bot behavior for your server",
            color=discord.Color.gold(),
        )

        embed.add_field(
            name="🎛️ **Configuration Commands**",
            value=(
                "`/config` - View current server settings\n"
                "`/setup-moderation` - Configure moderation settings\n"
                "`/setup-welcome` - Set welcome/farewell channels\n"
                "`/autorole` - Manage automatic role assignment\n"
                "`/prefix` - Manage command prefixes"
            ),
            inline=False,
        )

        embed.add_field(
            name="🎯 **Available Settings**",
            value=(
                "**Language**: English or Bangla for motions\n"
                "**Timezone**: Server timezone for timestamps\n"
                "**Prefixes**: Custom command prefixes\n"
                "**Mute Role**: Role used for muting members\n"
                "**Drama Channel**: Moderation alerts channel\n"
                "**Auto Roles**: Roles given to new members"
            ),
            inline=False,
        )

        return embed

    def get_admin_help(self) -> discord.Embed:
        """Get admin commands help"""
        embed = discord.Embed(
            title="🔧 Admin Commands",
            description="Administrative tools and bot management",
            color=discord.Color.dark_red(),
        )

        embed.add_field(
            name="🌍 **Command Sync**",
            value=(
                "`/sync` - Sync slash commands globally (1 hour delay)\n"
                "`/guild_sync` - Sync commands to this server (instant)\n"
                "• Use guild sync for testing new commands\n"
                "• Global sync makes commands available everywhere"
            ),
            inline=False,
        )

        embed.add_field(
            name="🎮 **Server Management**",
            value=(
                "`.unmute [user]` - Voice unmute members\n"
                "`.undeafen [user]` - Voice undeafen members\n"
                "`.setlanguage [lang]` - Set server language\n"
                "• Prefix commands for quick admin actions\n"
                "• Voice channel management tools"
            ),
            inline=False,
        )

        return embed

    def get_utility_help(self) -> discord.Embed:
        """Get utility commands help"""
        embed = discord.Embed(
            title="🛠️ Utility Commands",
            description="General utility and fun commands",
            color=discord.Color.teal(),
        )

        embed.add_field(
            name="🎲 **Fun Commands**",
            value=(
                "`/coinflip` - Flip a coin\n"
                "`/ping` - Check bot latency\n"
                "• Simple utility commands\n"
                "• Quick response tools"
            ),
            inline=False,
        )

        return embed


async def setup(bot):
    await bot.add_cog(HelpSystem(bot))
