"""
Admin Commands for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    """Administrative commands for server management"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmute a member in voice chat"""
        try:
            await member.edit(mute=False)
            await ctx.send(f"> {member.mention} was unmuted successfully")
            logger.info(f"Unmuted {member} in {ctx.guild}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unmute members.")
        except Exception as e:
            await ctx.send(f"❌ Error unmuting member: {str(e)}")
            logger.error(f"Error unmuting {member}: {e}")
    
    @app_commands.command(name="unmute", description="Unmute a member in voice chat")
    @app_commands.describe(member="The member to unmute")
    @app_commands.default_permissions(manage_roles=True)
    async def slash_unmute(self, interaction: discord.Interaction, member: discord.Member):
        """Slash command version of unmute"""
        try:
            await member.edit(mute=False)
            await interaction.response.send_message(f"> {member.mention} was unmuted successfully")
            logger.info(f"Unmuted {member} in {interaction.guild}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to unmute members.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error unmuting member: {str(e)}", ephemeral=True)
            logger.error(f"Error unmuting {member}: {e}")
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def undeafen(self, ctx, member: discord.Member):
        """Undeafen a member in voice chat"""
        try:
            await member.edit(deafen=False)
            await ctx.send(f"> {member.mention} was undeafened successfully")
            logger.info(f"Undeafened {member} in {ctx.guild}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to undeafen members.")
        except Exception as e:
            await ctx.send(f"❌ Error undeafening member: {str(e)}")
            logger.error(f"Error undeafening {member}: {e}")
    
    @app_commands.command(name="undeafen", description="Undeafen a member in voice chat")
    @app_commands.describe(member="The member to undeafen")
    @app_commands.default_permissions(manage_roles=True)
    async def slash_undeafen(self, interaction: discord.Interaction, member: discord.Member):
        """Slash command version of undeafen"""
        try:
            await member.edit(deafen=False)
            await interaction.response.send_message(f"> {member.mention} was undeafened successfully")
            logger.info(f"Undeafened {member} in {interaction.guild}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to undeafen members.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error undeafening member: {str(e)}", ephemeral=True)
            logger.error(f"Error undeafening {member}: {e}")
    
    @commands.command(aliases=['setlang'])
    @commands.has_permissions(administrator=True)
    async def setlanguage(self, ctx, language):
        """Set the language for this server (english/bangla)"""
        language = language.lower()
        
        if language not in ['english', 'bangla']:
            await ctx.send("❌ Supported languages: `english`, `bangla`")
            return
        
        success = await self.bot.set_language(ctx.guild.id, language)
        
        if success:
            if language == 'english':
                await ctx.send("✅ Language set to English for this server")
            else:
                await ctx.send("✅ এই সার্ভারের জন্য ভাষা বাংলায় সেট করা হয়েছে")
        else:
            await ctx.send("❌ Failed to set language. Please try again.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, *, role_name):
        """Set up automatic role assignment for new members"""
        # Find the role
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        
        if not role:
            await ctx.send(f"❌ Role '{role_name}' not found.")
            return
        
        # Check if bot can assign this role
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send("❌ I cannot assign this role as it's higher than my highest role.")
            return
        
        # Save to database
        try:
            collection = self.bot.database.get_collection('guilds')
            if collection:
                collection.update_one(
                    {'_id': ctx.guild.id},
                    {'$set': {'autorole': role.id}},
                    upsert=True
                )
                await ctx.send(f"✅ Auto-role set to **{role.name}**")
            else:
                await ctx.send("❌ Database connection error.")
        except Exception as e:
            await ctx.send("❌ Failed to set auto-role.")
            logger.error(f"Error setting autorole: {e}")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removeautorole(self, ctx):
        """Remove automatic role assignment"""
        try:
            collection = self.bot.database.get_collection('guilds')
            if collection:
                collection.update_one(
                    {'_id': ctx.guild.id},
                    {'$unset': {'autorole': ''}},
                    upsert=True
                )
                await ctx.send("✅ Auto-role removed")
            else:
                await ctx.send("❌ Database connection error.")
        except Exception as e:
            await ctx.send("❌ Failed to remove auto-role.")
            logger.error(f"Error removing autorole: {e}")
    
    @commands.command(aliases=['delete-data'])
    @commands.has_permissions(administrator=True)
    async def deletedata(self, ctx, *, confirmation=''):
        """Delete all data associated with this server"""
        if confirmation != 'YES I AM 100% SURE':
            await ctx.send(
                "⚠️ **WARNING**: This will delete ALL data for this server!\n"
                "Type `YES I AM 100% SURE` after the command to confirm."
            )
            return
        
        try:
            # Delete from both databases
            main_collection = self.bot.database.get_collection('guilds')
            tabby_collection = self.bot.database.get_collection('tournaments', use_tabby_db=True)
            
            if main_collection:
                main_collection.delete_one({'_id': ctx.guild.id})
            
            if tabby_collection:
                tabby_collection.delete_one({'_id': ctx.guild.id})
            
            await ctx.send("✅ ALL DATA FOR THIS SERVER WAS DELETED SUCCESSFULLY")
            logger.warning(f"All data deleted for guild {ctx.guild.id} by {ctx.author}")
            
        except Exception as e:
            await ctx.send("❌ Error deleting data.")
            logger.error(f"Error deleting data for guild {ctx.guild.id}: {e}")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def serverinfo(self, ctx):
        """Display server information and bot settings"""
        guild = ctx.guild
        
        # Get language setting
        language = await self.bot.get_language(guild.id)
        
        # Get autorole setting
        try:
            collection = self.bot.database.get_collection('guilds')
            guild_data = collection.find_one({'_id': guild.id}) if collection else None
            autorole_id = guild_data.get('autorole') if guild_data else None
            autorole = guild.get_role(autorole_id) if autorole_id else None
        except:
            autorole = None
        
        embed = discord.Embed(
            title=f"Server Information - {guild.name}",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Member Count", value=guild.member_count, inline=True)
        embed.add_field(name="Language", value=language.title(), inline=True)
        embed.add_field(name="Auto-role", value=autorole.name if autorole else "None", inline=True)
        embed.add_field(name="Active Timers", value=self.bot.timer_manager.get_active_timers_count(), inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
