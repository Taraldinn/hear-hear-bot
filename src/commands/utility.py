"""
Utility Commands - Restored Original Functionality
Author: Tasdid Tahsin
Email: tasdidtahsin@gmail.com
"""

import discord
from discord.ext import commands
import logging
import random
from config.settings import Config

logger = logging.getLogger(__name__)

class UtilityCommands(commands.Cog):
    """General utility commands with original pybot.py functionality"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def get_language(self, guild_id):
        """Get language setting for a guild"""
        try:
            if self.bot.database and self.bot.database.db:
                collection = self.bot.database.get_collection('language')
                if collection:
                    find = collection.find_one({'_id': str(guild_id)})
                    if find:
                        return find.get('ln', 'en')
        except Exception as e:
            logger.error(f"Error getting language: {e}")
        return 'en'
    
    @commands.command()
    async def help(self, ctx, command_name=None):
        """Show help information"""
        if command_name:
            # Show specific command help
            command = self.bot.get_command(command_name)
            if not command:
                await ctx.send(f"❌ Command `{command_name}` not found.")
                return
            
            embed = discord.Embed(
                title=f"Help: {command.name}",
                description=command.help or "No description available",
                color=discord.Color.blue()
            )
            
            if command.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join(f"`{alias}`" for alias in command.aliases),
                    inline=False
                )
            
            embed.add_field(
                name="Usage",
                value=f"`{ctx.prefix}{command.name} {command.signature}`",
                inline=False
            )
            
        else:
            # Show general help
            embed = discord.Embed(
                title=f"🤖 {Config.BOT_NAME} - Help",
                description="A comprehensive debate bot with timing, motions, and tournament features",
                color=discord.Color.blue()
            )
            
            # Admin commands
            admin_cmds = [
                "`.unmute <member>` - Unmute a member",
                "`.undeafen <member>` - Undeafen a member", 
                "`.setlanguage <lang>` - Set server language",
                "`.autorole <role>` - Set auto-role for new members",
                "`.serverinfo` - Show server information"
            ]
            
            # Timer commands
            timer_cmds = [
                "`.timer start/stop/check` - Manage debate timer",
                "`.autotimer [minutes]` - Auto-stop timer",
                "`.currenttime` - Show current time",
                "`.activetimers` - Show active timer count"
            ]
            
            # Debate commands
            debate_cmds = [
                "`.randommotion [lang]` - Get random motion",
                "`.coinflip` - Flip a coin",
                "`.diceroll [sides]` - Roll a dice",
                "`.positions` - Show debate positions",
                "`.formats` - Show debate formats"
            ]
            
            # Utility commands
            utility_cmds = [
                "`.help [command]` - Show this help",
                "`.info` - Bot information",
                "`.ping` - Check bot latency",
                "`.invite` - Get bot invite link"
            ]
            
            embed.add_field(name="👑 Admin Commands", value="\n".join(admin_cmds), inline=False)
            embed.add_field(name="⏱️ Timer Commands", value="\n".join(timer_cmds), inline=False)
            embed.add_field(name="🗣️ Debate Commands", value="\n".join(debate_cmds), inline=False)
            embed.add_field(name="🔧 Utility Commands", value="\n".join(utility_cmds), inline=False)
            
            embed.add_field(
                name="💡 Need more help?",
                value="Use `.help <command>` for detailed command help\nExample: `.help timer`",
                inline=False
            )
        
        embed.set_footer(
            text=f"Bot Version {Config.BOT_VERSION} | Prefix: {ctx.prefix}",
            icon_url=self.bot.user.display_avatar.url if self.bot.user else None
        )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def info(self, ctx):
        """Show bot information"""
        embed = discord.Embed(
            title=f"🤖 {Config.BOT_NAME}",
            description="A comprehensive debate bot with timing, motions, and tournament features",
            color=discord.Color.green(),
            timestamp=ctx.message.created_at
        )
        
        # Bot stats
        total_guilds = len(self.bot.guilds)
        total_users = sum(guild.member_count for guild in self.bot.guilds)
        
        embed.add_field(name="Version", value=Config.BOT_VERSION, inline=True)
        embed.add_field(name="Servers", value=total_guilds, inline=True)
        embed.add_field(name="Users", value=total_users, inline=True)
        embed.add_field(name="Shards", value=self.bot.shard_count, inline=True)
        embed.add_field(name="Active Timers", value=self.bot.timer_manager.get_active_timers_count(), inline=True)
        
        # Developer info
        embed.add_field(
            name="👨‍💻 Developer",
            value=f"{Config.BOT_AUTHOR}\n{Config.BOT_EMAIL}",
            inline=False
        )
        
        # Links and support
        embed.add_field(
            name="🔗 Links",
            value="[Invite Bot](https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=8&scope=bot) | [Support Server](https://discord.gg/YOUR_INVITE)",
            inline=False
        )
        
        if self.bot.user and self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        embed.set_footer(
            text="Made with ❤️ for the debate community",
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def ping(self, ctx):
        """Check bot latency"""
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green(),
            timestamp=ctx.message.created_at
        )
        
        # Bot latency
        latency = round(self.bot.latency * 1000)
        embed.add_field(name="Bot Latency", value=f"{latency}ms", inline=True)
        
        # Database ping (if available)
        try:
            import time
            start_time = time.time()
            if self.bot.database.client:
                self.bot.database.client.admin.command('ping')
                db_latency = round((time.time() - start_time) * 1000)
                embed.add_field(name="Database Latency", value=f"{db_latency}ms", inline=True)
        except:
            embed.add_field(name="Database", value="❌ Offline", inline=True)
        
        # Status indicator
        if latency < 100:
            status = "🟢 Excellent"
        elif latency < 200:
            status = "🟡 Good"
        else:
            status = "🔴 Poor"
        
        embed.add_field(name="Status", value=status, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def invite(self, ctx):
        """Get bot invite link"""
        if not self.bot.user:
            await ctx.send("❌ Bot user information not available.")
            return
        
        # Create invite link with necessary permissions
        permissions = discord.Permissions(
            read_messages=True,
            send_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            add_reactions=True,
            manage_roles=True,
            mute_members=True,
            deafen_members=True,
            manage_messages=True
        )
        
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=permissions,
            scopes=('bot', 'applications.commands')
        )
        
        embed = discord.Embed(
            title="📨 Invite Bot",
            description=f"Click [here]({invite_url}) to invite {Config.BOT_NAME} to your server!",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        
        embed.add_field(
            name="🔧 Permissions Included",
            value="• Manage roles and voice\n• Send messages and embeds\n• Timer and debate features\n• Tournament management",
            inline=False
        )
        
        embed.add_field(
            name="💡 Need Help?",
            value="Use `.help` after inviting to see all available commands",
            inline=False
        )
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['about'])
    async def version(self, ctx):
        """Show bot version and changelog"""
        embed = discord.Embed(
            title=f"📋 {Config.BOT_NAME} v{Config.BOT_VERSION}",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        
        # Version info
        embed.add_field(name="Current Version", value=Config.BOT_VERSION, inline=True)
        embed.add_field(name="Release Date", value="2025-01-01", inline=True)  # Update this
        
        # Changelog
        changelog = [
            "✅ Unified bot features from multiple versions",
            "✅ Professional component-based architecture", 
            "✅ Enhanced timer functionality",
            "✅ Multi-language motion support",
            "✅ Improved error handling",
            "✅ Database optimization"
        ]
        
        embed.add_field(
            name="🆕 What's New",
            value="\n".join(changelog),
            inline=False
        )
        
        embed.set_footer(text=f"Developed by {Config.BOT_AUTHOR}")
        
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['8ball', 'test'])
    async def _8ball(self, ctx, *, question):
        """Ask the magic 8-ball a question"""
        lang = await self.get_language(ctx.guild.id)
        
        responses = {
            'en': ['Of course!', 'Yes, obviously!', 'Most likely', 'It must happen', 'Why not?', 
                   'Hear! Hear!', 'Maybe?', "Better you don't find out", 'No prediction', 
                   "Don't count on it", 'Very doubtful', 'Not so good'],
            'fr': ["Bien sûr!", "Oui, évidemment!", "Très probablement", "Tu peux compter là-dessus",
                   "Pourquoi pas ?", "Hear ! Hear !", "Peut-être ?", "Il vaut mieux ne pas le savoir",
                   "Aucune prévision", "N'y compte pas", 'Peu probable', 'Passable']
        }
        
        response = random.choice(responses.get(lang, responses['en']))
        
        format_strings = {
            'en': '*Question from {}:* {}\n*Answer:* {}',
            'fr': '*Question par {}:* {}\n*Réponse:* {}'
        }
        
        await ctx.send(format_strings[lang].format(ctx.author.mention, question, response))
    
    @commands.command(aliases=['hello', 'hi', 'hola', 'hey', 'bonjour', 'salut', 'aloha'])
    async def greetings(self, ctx):
        """Greet the user"""
        lang = await self.get_language(ctx.guild.id)
        
        greetings_list = {
            'en': ['Hey there,', 'Hello,', "What's up?"],
            'fr': ['Bonjour', 'Salut', 'Aloha', 'Hey', 'Salut toi', 'Quoi de neuf ?']
        }
        
        greeting = random.choice(greetings_list.get(lang, greetings_list['en']))
        await ctx.send(f'{greeting} {ctx.author.mention}')
    
    @commands.command()
    async def coinflip(self, ctx):
        """Flip a coin"""
        lang = await self.get_language(ctx.guild.id)
        
        coins = {
            'en': ['Head', 'Tail'],
            'fr': ['Face', 'Pile']
        }
        
        result = random.choice(coins.get(lang, coins['en']))
        await ctx.send(f"🪙 {result}!")

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))
