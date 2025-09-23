"""
Member Events for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
"""

import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class MemberEvents(commands.Cog):
    """Events related to member join/leave"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle new member joins"""
        try:
            # Get guild settings
            collection = self.bot.database.get_collection('guilds')
            if not collection:
                return
            
            guild_data = collection.find_one({'_id': member.guild.id})
            if not guild_data:
                return
            
            # Auto-role assignment
            if 'autorole' in guild_data:
                role_id = guild_data['autorole']
                role = member.guild.get_role(role_id)
                
                if role and role < member.guild.me.top_role:
                    try:
                        await member.add_roles(role, reason="Auto-role assignment")
                        logger.info("Assigned auto-role {role.name} to {member} in {member.guild}", )
                    except discord.Forbidden:
                        logger.warning("Cannot assign auto-role {role.name} - insufficient permissions", )
                    except Exception as e:
                        logger.error("Error assigning auto-role: {e}", )
            
            # Welcome message (if configured)
            if 'welcome_channel' in guild_data:
                channel_id = guild_data['welcome_channel']
                channel = member.guild.get_channel(channel_id)
                
                if channel:
                    language = guild_data.get('language', 'english')
                    
                    if language == 'bangla':
                        welcome_msg = f"🎉 স্বাগতম {member.mention}! {member.guild.name} এ যোগ দেওয়ার জন্য ধন্যবাদ।"
                    else:
                        welcome_msg = f"🎉 Welcome {member.mention}! Thanks for joining {member.guild.name}."
                    
                    embed = discord.Embed(
                        title="👋 New Member!",
                        description=welcome_msg,
                        color=discord.Color.green(),
                        timestamp=member.joined_at
                    )
                    
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.add_field(name="Member Count", value=member.guild.member_count, inline=True)
                    
                    try:
                        await channel.send(embed=embed)
                    except discord.Forbidden:
                        logger.warning("Cannot send welcome message - no permission in {channel}", )
                    except Exception as e:
                        logger.error("Error sending welcome message: {e}", )
        
        except Exception as e:
            logger.error("Error in on_member_join: {e}", )
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Handle member leaves"""
        try:
            # Get guild settings for goodbye message
            collection = self.bot.database.get_collection('guilds')
            if not collection:
                return
            
            guild_data = collection.find_one({'_id': member.guild.id})
            if not guild_data or 'goodbye_channel' not in guild_data:
                return
            
            channel_id = guild_data['goodbye_channel']
            channel = member.guild.get_channel(channel_id)
            
            if channel:
                language = guild_data.get('language', 'english')
                
                if language == 'bangla':
                    goodbye_msg = f"👋 {member.display_name} চলে গেছেন। আমরা তাদের মিস করব!"
                else:
                    goodbye_msg = f"👋 {member.display_name} has left the server. We'll miss them!"
                
                embed = discord.Embed(
                    title="📤 Member Left",
                    description=goodbye_msg,
                    color=discord.Color.red()
                )
                
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(name="Member Count", value=member.guild.member_count, inline=True)
                
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    logger.warning("Cannot send goodbye message - no permission in {channel}", )
                except Exception as e:
                    logger.error("Error sending goodbye message: {e}", )
        
        except Exception as e:
            logger.error("Error in on_member_remove: {e}", )
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Handle bot joining new guild"""
        logger.info("Joined new guild: {guild.name} (ID: {guild.id})", )
        
        # Try to send a welcome message to the system channel or first available channel
        embed = discord.Embed(
            title=f"🎉 Thanks for adding {self.bot.user.name}!",
            description="I'm here to help with debate timing, motions, and tournament management.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="🚀 Get Started",
            value="Use `.help` to see all available commands",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Setup",
            value="• Use `.setlanguage` to set your preferred language\n• Use `.autorole` to set auto-role for new members",
            inline=False
        )
        
        # Try to send to system channel first, then any channel we can send to
        target_channel = guild.system_channel
        
        if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
            # Find first channel we can send messages to
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    target_channel = channel
                    break
        
        if target_channel:
            try:
                await target_channel.send(embed=embed)
            except Exception as e:
                logger.error("Error sending welcome message to new guild: {e}", )
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Handle bot leaving guild"""
        logger.info("Left guild: {guild.name} (ID: {guild.id})", )
        
        # Clean up guild data if needed
        try:
            collection = self.bot.database.get_collection('guilds')
            if collection:
                # Optionally remove guild data or mark as inactive
                # collection.delete_one({'_id': guild.id})
                pass
        except Exception as e:
            logger.error("Error cleaning up guild data: {e}", )

async def setup(bot):
    await bot.add_cog(MemberEvents(bot))
