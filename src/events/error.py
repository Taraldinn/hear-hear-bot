"""
Error Handling Events for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
"""

import discord
from discord.ext import commands
import logging
import traceback

logger = logging.getLogger(__name__)

class ErrorEvents(commands.Cog):
    """Events for error handling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        
        # Ignore command not found errors
        if isinstance(error, commands.CommandNotFound):
            return
        
        # Extract original error if it's wrapped
        error = getattr(error, 'original', error)
        
        # Create base embed for error messages
        embed = discord.Embed(color=discord.Color.red(), timestamp=ctx.message.created_at)
        embed.set_footer(text=f"Error in {ctx.command}", icon_url=ctx.author.display_avatar.url)
        
        # Handle specific error types
        if isinstance(error, commands.MissingPermissions):
            embed.title = "❌ Missing Permissions"
            embed.description = f"You need the following permissions to use this command:\n" + \
                              "\n".join(f"• `{perm.replace('_', ' ').title()}`" for perm in error.missing_permissions)
            
        elif isinstance(error, commands.BotMissingPermissions):
            embed.title = "❌ Bot Missing Permissions"
            embed.description = f"I need the following permissions to execute this command:\n" + \
                              "\n".join(f"• `{perm.replace('_', ' ').title()}`" for perm in error.missing_permissions)
            embed.add_field(
                name="💡 Solution",
                value="Please give me the necessary permissions or contact an administrator.",
                inline=False
            )
            
        elif isinstance(error, commands.MissingRequiredArgument):
            embed.title = "❌ Missing Required Argument"
            embed.description = f"The `{error.param.name}` argument is required for this command."
            embed.add_field(
                name="💡 Usage",
                value=f"`{ctx.prefix}{ctx.command} {ctx.command.signature}`",
                inline=False
            )
            
        elif isinstance(error, commands.BadArgument):
            embed.title = "❌ Invalid Argument"
            embed.description = "One or more arguments provided are invalid."
            embed.add_field(
                name="💡 Usage",
                value=f"`{ctx.prefix}{ctx.command} {ctx.command.signature}`",
                inline=False
            )
            
        elif isinstance(error, commands.MissingRole):
            embed.title = "❌ Missing Role"
            embed.description = f"You need the `{error.missing_role}` role to use this command."
            
        elif isinstance(error, commands.MissingAnyRole):
            embed.title = "❌ Missing Required Role"
            embed.description = f"You need one of the following roles:\n" + \
                              "\n".join(f"• `{role}`" for role in error.missing_roles)
            
        elif isinstance(error, commands.CommandOnCooldown):
            embed.title = "⏰ Command on Cooldown"
            embed.description = f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
            
        elif isinstance(error, commands.DisabledCommand):
            embed.title = "❌ Command Disabled"
            embed.description = "This command has been temporarily disabled."
            
        elif isinstance(error, commands.NoPrivateMessage):
            embed.title = "❌ Server Only Command"
            embed.description = "This command can only be used in servers, not in DMs."
            
        elif isinstance(error, commands.PrivateMessageOnly):
            embed.title = "❌ DM Only Command"
            embed.description = "This command can only be used in direct messages."
            
        elif isinstance(error, discord.Forbidden):
            embed.title = "❌ Permission Denied"
            embed.description = "I don't have permission to perform this action."
            embed.add_field(
                name="💡 Solution",
                value="Please check my role permissions and try again.",
                inline=False
            )
            
        elif isinstance(error, discord.NotFound):
            embed.title = "❌ Not Found"
            embed.description = "The requested resource could not be found."
            
        elif isinstance(error, discord.HTTPException):
            embed.title = "❌ Discord API Error"
            embed.description = "There was an error communicating with Discord. Please try again later."
            
        else:
            # Log unexpected errors
            logger.error("Unexpected error in command {ctx.command}: {error}", )
            logger.error(traceback.format_exc())
            
            embed.title = "❌ Unexpected Error"
            embed.description = "An unexpected error occurred. This has been logged for investigation."
            embed.add_field(
                name="💡 Support",
                value="If this error persists, please contact the bot developer.",
                inline=False
            )
        
        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            # If we can't send embeds, try sending a plain text message
            try:
                await ctx.send(f"❌ Error: {embed.description}")
            except:
                # If we can't send messages at all, there's nothing we can do
                pass
        except Exception as send_error:
            logger.error("Error sending error message: {send_error}", )
    
    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        """Handle general bot errors"""
        logger.error("Error in event {event}", )
        logger.error(traceback.format_exc())
    
    @commands.Cog.listener()
    async def on_application_command_error(self, interaction, error):
        """Handle application command (slash command) errors"""
        error = getattr(error, 'original', error)
        
        embed = discord.Embed(
            title="❌ Command Error",
            color=discord.Color.red(),
            timestamp=interaction.created_at
        )
        
        if isinstance(error, discord.Forbidden):
            embed.description = "I don't have permission to perform this action."
        elif isinstance(error, discord.NotFound):
            embed.description = "The requested resource could not be found."
        else:
            embed.description = "An error occurred while processing this command."
            logger.error("Application command error: {error}", )
            logger.error(traceback.format_exc())
        
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as send_error:
            logger.error("Error sending application command error message: {send_error}", )

async def setup(bot):
    await bot.add_cog(ErrorEvents(bot))
