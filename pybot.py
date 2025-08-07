#Bot Name: Hear! Hear! 
#Email: tasdidtahsin@gmail.com
#Developed by Tasdid Tahsin

import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import random
import time
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Load environment variables
load_dotenv()

# Remove the dbl import since we're not using Top.gg

intents = discord.Intents.default()
intents.message_content = True  # Required for Discord.py 2.0+

client = commands.AutoShardedBot(shard_count=2, command_prefix='.', intents=intents)

client.remove_command('help')

# Use environment variables for sensitive data
token = os.getenv('DISCORD_BOT_TOKEN')
mongoClusterKey0 = os.getenv('MONGODB_CONNECTION_STRING')

# Check if required environment variables are set
if not token:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is not set")
if not mongoClusterKey0:
    raise ValueError("MONGODB_CONNECTION_STRING environment variable is not set")

try:
    cluster0 = MongoClient(mongoClusterKey0)
    db = cluster0['hearhear-bot']
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    db = None

l = {}      # timer trigger library - format: {user_id_channel_id: status}
t = {}      # reminder storage library
active_timers = {}  # track active timer messages - format: {user_id_channel_id: message_obj}

# Simple HTTP server to satisfy Render's port requirements
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hear! Hear! Discord Bot is running!')
    
    def log_message(self, format, *args):
        pass  # Suppress HTTP server logs

def start_http_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

# Removed Top.gg/DBL client initialization since we're not using it

@client.event
async def on_ready():
    print('Bot Activated!\n')
    print(f'Logged in as {client.user.name}\n')
    print('------------------------------\n')
    
    # Start the presence update loop
    client.loop.create_task(update_presence())

async def update_presence():
    """Update bot presence every 30 minutes"""
    while True:
        try:
            act = f'debates in {len(client.guilds)} servers [.help]'
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=act))
            await asyncio.sleep(1800)  # 30 minutes
        except Exception as e:
            print(f"Error updating presence: {e}")
            await asyncio.sleep(1800)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors
    
    lang = 'en'

    try:
        if db:
            guild = str(ctx.guild.id)
            collection = db['language']
            find = collection.find_one({'_id': guild})
            if find:
                lang = find['ln']
    except Exception as e:
        print(f"Error getting language setting: {e}")

    error_messages = {
        'en': {
            'MissingPermissions': '*You are missing the basic required Permission(s)*',
            'MissingRequiredArgument': '*Command is missing required Argument*',
            'MissingRole': '*Command is missing required Role*',
            'MissingAnyRole': '*Command is missing required Role*',
            'BotMissingPermissions': '**The bot is missing required permissions. Please give the bot ADMINISTRATOR Permission to work flawlessly**'
        },
        'fr': {
            'MissingPermissions': "*Vous n'avez pas la permission nécessaire*",
            'MissingRequiredArgument': "*La commande manque l'argument nécessaire*",
            'MissingRole': '*Il manque le rôle requis pour cette commande*',
            'MissingAnyRole': '*Il manque le rôle requis pour cette commande*',
            'BotMissingPermissions': "**Il manque des permissions au bot. Veuillez donner la permission ADMINISTRATEUR au bot pour qu'il fonctionne parfaitement**"
        }
    }

    error_type = type(error).__name__
    if error_type in error_messages.get(lang, error_messages['en']):
        await ctx.send(error_messages[lang][error_type])

# Helper function to get language
async def get_language(guild_id):
    """Get the language setting for a guild"""
    try:
        if db:
            collection = db['language']
            find = collection.find_one({'_id': str(guild_id)})
            return find['ln'] if find else 'en'
    except Exception as e:
        print(f"Error getting language: {e}")
    return 'en'

#autorole
@client.event
async def on_member_join(member):
    try:
        if db:
            server = str(member.guild.id)
            collection = db['autorole']
            find = collection.find_one({'_id': server})
            
            if find:
                r = find['rol']
                role = get(member.guild.roles, name=r)
                if role:
                    await member.add_roles(role)
    except Exception as e:
        print(f"*** Error in AUTO_ROLE: {e}")

@client.command()
@commands.has_permissions(manage_roles=True)
async def undeafen(ctx, member: discord.Member):
    """Undeafen a member"""
    try:
        await member.edit(deafen=False)
        await ctx.send(f"> {member.mention} was undeafened successfully")
    except discord.Forbidden:
        await ctx.send("I don't have permission to undeafen this member.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@client.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    """Unmute a member"""
    try:
        await member.edit(mute=False)
        
        lang = await get_language(ctx.guild.id)
        
        messages = {
            'en': f"> {member.mention} was unmuted successfully!",
            'fr': f"> {member.mention} a été réactivé avec succès!"
        }
        
        await ctx.send(messages.get(lang, messages['en']))
    except discord.Forbidden:
        await ctx.send("I don't have permission to unmute this member.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@client.command()
@commands.has_permissions(administrator=True)
async def setlang(ctx, language):
    """Set the server language"""
    if not db:
        await ctx.send("Database not available.")
        return
    
    language = language.lower()
    if language in ['fr', 'french', 'français']:
        language = 'fr'
    elif language in ['en', 'english', 'anglais']:
        language = 'en'
    else:
        await ctx.send('No such language in the database. Supported languages: EN, FR')
        return

    try:
        guild = str(ctx.guild.id)
        collection = db['language']
        post = {'_id': guild, 'ln': language}
        
        # Use upsert to update or insert
        collection.replace_one({'_id': guild}, post, upsert=True)
        
        messages = {
            'en': f'Default language for this server was set to ***English (EN)***',
            'fr': f'La langue par défaut pour ce serveur est réglée à : ***Français (FR)***'
        }
        
        await ctx.send(messages.get(language, messages['en']))
    except Exception as e:
        await ctx.send(f"Error setting language: {e}")

@client.command()
@commands.has_permissions(administrator=True)
async def autorole(ctx, *, role_name):
    """Set autorole for new members"""
    if not db:
        await ctx.send("Database not available.")
        return
    
    if role_name.lower() == 'disable':
        try:
            guild = str(ctx.guild.id)
            collection = db['autorole']
            collection.delete_one({'_id': guild})
            await ctx.send("Autorole disabled.")
        except Exception as e:
            await ctx.send(f"Error disabling autorole: {e}")
        return

    try:
        guild = str(ctx.guild.id)
        collection = db['autorole']
        post = {'_id': guild, 'rol': role_name}
        
        collection.replace_one({'_id': guild}, post, upsert=True)
        
        lang = await get_language(ctx.guild.id)
        
        messages = {
            'en': f'Auto-role set to **{role_name}**. To disable autorole, use `.autorole disable`',
            'fr': f"Rôle automatique défini à **{role_name}**. Pour le désactiver, saisissez `.autorole disable`"
        }
        
        await ctx.send(messages.get(lang, messages['en']))
    except Exception as e:
        await ctx.send(f"Error setting autorole: {e}")

@client.command(aliases=['time'])
async def _time(ctx):
    """Get current Unix timestamp"""
    current_time = int(time.time())
    await ctx.send(f'{current_time}')

@client.command(aliases=['timekeep', 't', 'chrono'])
async def timer(ctx, duration, seconds='0s'):
    """Set a visual timer with interactive buttons"""
    lang = await get_language(ctx.guild.id)
    
    if not (duration.endswith('m') and seconds.endswith('s')):
        error_messages = {
            'en': '*Syntax error*\n*The command should contain minutes and seconds in format* **Nm Ns**\nFor example: ***7m 15s, 0m 30s***',
            'fr': '*Erreur de syntaxe*\n*La commande doit contenir le nombre de minutes et de secondes selon le format* **Nm Ns**\nPar exemple : ***7m 15s, 0m 30s***'
        }
        await ctx.send(error_messages.get(lang, error_messages['en']))
        return
    
    try:
        minutes = int(duration[:-1])
        secs = int(seconds[:-1])
        total_seconds = minutes * 60 + secs
        
        if total_seconds <= 0:
            await ctx.send("Timer duration must be greater than 0.")
            return
        
        if total_seconds > 7200:  # 2 hours limit
            await ctx.send("Timer cannot exceed 2 hours.")
            return
        
        # Create unique timer ID
        timer_id = f"{ctx.author.id}_{ctx.channel.id}"
        
        # Check if user already has a timer in this channel
        if timer_id in l:
            conflict_messages = {
                'en': f'{ctx.author.mention}, you already have a timer running in this channel. Use the stop button or `.stop` to stop it first.',
                'fr': f'{ctx.author.mention}, vous avez déjà un chronomètre en cours dans ce canal. Utilisez le bouton stop ou `.stop` pour l\'arrêter d\'abord.'
            }
            await ctx.send(conflict_messages.get(lang, conflict_messages['en']))
            return
        
        # Clean up any existing timer messages for this user/channel
        if timer_id in active_timers:
            try:
                await active_timers[timer_id].delete()
            except:
                pass
            del active_timers[timer_id]
        
        l[timer_id] = 0  # 0 = running, 1 = stopped, 2 = paused
        
        # Create interactive buttons
        class TimerView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=total_seconds + 30)
                
            @discord.ui.button(label='Pause', style=discord.ButtonStyle.secondary, emoji='⏸️')
            async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("🚫 Only the timer owner can control this timer.", ephemeral=True)
                    return
                
                if timer_id in l and l[timer_id] == 0:
                    l[timer_id] = 2
                    button.label = 'Resume'
                    button.style = discord.ButtonStyle.success
                    button.emoji = '▶️'
                    await interaction.response.edit_message(view=self)
                elif timer_id in l and l[timer_id] == 2:
                    l[timer_id] = 0
                    button.label = 'Pause'
                    button.style = discord.ButtonStyle.secondary
                    button.emoji = '⏸️'
                    await interaction.response.edit_message(view=self)
                else:
                    await interaction.response.send_message("❌ No timer to pause/resume.", ephemeral=True)
            
            @discord.ui.button(label='Stop', style=discord.ButtonStyle.danger, emoji='⏹️')
            async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("🚫 Only the timer owner can control this timer.", ephemeral=True)
                    return
                
                if timer_id in l:
                    l[timer_id] = 1
                    # Disable all buttons
                    for item in self.children:
                        item.disabled = True
                    await interaction.response.edit_message(view=self)
                else:
                    await interaction.response.send_message("❌ No timer to stop.", ephemeral=True)
            
            @discord.ui.button(label='Add 1min', style=discord.ButtonStyle.success, emoji='➕')
            async def add_time_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("🚫 Only the timer owner can control this timer.", ephemeral=True)
                    return
                
                nonlocal total_seconds
                if timer_id in l and l[timer_id] != 1:
                    total_seconds += 60
                    add_messages = {
                        'en': '⏰ Added 1 minute to timer! ⏱️',
                        'fr': '⏰ 1 minute ajoutée au chronomètre! ⏱️'
                    }
                    await interaction.response.send_message(add_messages.get(lang, add_messages['en']), ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Timer is not running.", ephemeral=True)
            
            @discord.ui.button(label='Notify Me', style=discord.ButtonStyle.primary, emoji='🔔')
            async def notify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("🚫 Only the timer owner can control this timer.", ephemeral=True)
                    return
                
                if timer_id in l and l[timer_id] != 1:
                    await interaction.response.send_message("🔔 You'll be notified when the timer finishes!", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Timer is not running.", ephemeral=True)
        
        view = TimerView()
        
        # Send only ONE timer message with buttons
        timer_embed = discord.Embed(
            title="⏰ Interactive Timer Started!",
            description=f"```\n⏱️  {minutes:02d}:{secs:02d}  ⏱️\n```",
            color=0x00ff00
        )
        timer_embed.add_field(name="👤 Timer Owner", value=ctx.author.mention, inline=True)
        timer_embed.add_field(name="🎯 Status", value="🟢 **RUNNING**", inline=True)
        timer_embed.add_field(name="� Channel", value=ctx.channel.mention, inline=True)
        timer_embed.set_footer(text="Use the buttons below to control your timer!")
        timer_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/755774680633016380.gif")
        
        msg = await ctx.send(embed=timer_embed, view=view)
        active_timers[timer_id] = msg
        
        # Animated timer countdown with rate limit protection
        last_update = 0
        while total_seconds > 0:
            if timer_id not in l:
                break
                
            if l[timer_id] == 1:  # Stop
                stop_messages = {
                    'en': f"⏹️ **Timer stopped by {ctx.author.mention}!**",
                    'fr': f"⏹️ **Chronomètre arrêté par {ctx.author.mention}!**"
                }
                await ctx.send(stop_messages.get(lang, stop_messages['en']))
                del l[timer_id]
                if timer_id in active_timers:
                    del active_timers[timer_id]
                break
                
            elif l[timer_id] == 2:  # Pause
                pause_embed = discord.Embed(
                    title="⏸️ Timer Paused",
                    description=f"```\n⏸️  {total_seconds // 60:02d}:{total_seconds % 60:02d}  ⏸️\n```",
                    color=0x808080
                )
                pause_embed.add_field(name="👤 Timer Owner", value=ctx.author.mention, inline=True)
                pause_embed.add_field(name="🎯 Status", value="⏸️ **PAUSED**", inline=True)
                pause_embed.add_field(name="📍 Channel", value=ctx.channel.mention, inline=True)
                pause_embed.set_footer(text="Click Resume to continue the timer!")
                
                try:
                    await msg.edit(embed=pause_embed, view=view)
                except:
                    pass
                while l.get(timer_id, 1) == 2:
                    await asyncio.sleep(1)
                continue
            
            # Update timer display with rate limit protection (every second for real-time updates)
            current_time = time.time()
            should_update = (
                current_time - last_update >= 1 or  # Every second for real-time
                total_seconds <= 10 or  # Last 10 seconds
                total_seconds % 60 == 0 or  # Every minute
                total_seconds in [300, 180, 60, 30]  # Important milestones
            )
            
            if should_update:
                # Dynamic colors based on time remaining
                if total_seconds > 300:  # > 5 minutes
                    color = 0x00ff00  # Green
                    status_emoji = "�"
                    status_text = "RUNNING"
                elif total_seconds > 60:  # 1-5 minutes
                    color = 0xffff00  # Yellow
                    status_emoji = "🟡"
                    status_text = "RUNNING"
                elif total_seconds > 30:  # 30s-1min
                    color = 0xff8800  # Orange
                    status_emoji = "🟠"
                    status_text = "HURRY UP!"
                else:  # < 30 seconds
                    color = 0xff0000  # Red
                    status_emoji = "🔴"
                    status_text = "FINAL COUNTDOWN!"
                
                # Create simple single-line progress bar
                total_time = minutes * 60 + secs
                progress = max(0, (total_time - total_seconds) / total_time)
                
                # Single line progress bar (20 characters for clean display)
                bar_length = 20
                filled_blocks = int(progress * bar_length)
                empty_blocks = bar_length - filled_blocks
                
                # Simple progress bar with single character
                progress_bar = "█" * filled_blocks + "░" * empty_blocks
                
                timer_embed = discord.Embed(
                    title="⏰ Interactive Timer",
                    description=f"```\n⏱️  {total_seconds // 60:02d}:{total_seconds % 60:02d}  ⏱️\n```",
                    color=color
                )
                timer_embed.add_field(name="👤 Timer Owner", value=ctx.author.mention, inline=True)
                timer_embed.add_field(name="🎯 Status", value=f"{status_emoji} **{status_text}**", inline=True)
                timer_embed.add_field(name="📍 Channel", value=ctx.channel.mention, inline=True)
                timer_embed.add_field(name="📊 Progress", value=f"{progress_bar}", inline=False)
                
                if total_seconds <= 30:
                    timer_embed.set_footer(text="⚡ Time is running out! ⚡")
                    timer_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/755774680633016380.gif")
                else:
                    timer_embed.set_footer(text="Use the buttons below to control your timer!")
                
                try:
                    await msg.edit(embed=timer_embed, view=view)
                    last_update = current_time
                except:
                    pass
            
            # Check for milestone notifications
            if total_seconds in [300, 180, 60, 30, 10, 5, 3, 2, 1]:
                if total_seconds == 300:
                    milestone_messages = {
                        'en': ':yellow_circle: **5 minutes LEFT** {}',
                        'fr': ':yellow_circle: **5 minutes RESTANTES** {}'
                    }
                elif total_seconds == 180:
                    milestone_messages = {
                        'en': ':orange_circle: **3 minutes LEFT** {}',
                        'fr': ':orange_circle: **3 minutes RESTANTES** {}'
                    }
                elif total_seconds == 60:
                    milestone_messages = {
                        'en': ':orange_circle: **1 minute LEFT** {}',
                        'fr': ':orange_circle: **1 minute RESTANTE** {}'
                    }
                elif total_seconds == 30:
                    milestone_messages = {
                        'en': ':red_circle: **30 seconds LEFT** {}',
                        'fr': ':red_circle: **30 secondes RESTANTES** {}'
                    }
                elif total_seconds <= 10:
                    milestone_messages = {
                        'en': f':rotating_light: **{total_seconds} seconds LEFT** {{}}',
                        'fr': f':rotating_light: **{total_seconds} secondes RESTANTES** {{}}'
                    }
                
                try:
                    await ctx.send(milestone_messages[lang].format(ctx.author.mention))
                except:
                    pass
            
            await asyncio.sleep(1)
            total_seconds -= 1
        
        if total_seconds <= 0 and timer_id in l:
            # Disable all buttons
            for item in view.children:
                item.disabled = True
            
            end_messages = {
                'en': ":red_circle: **Time's UP!** {} 🎉\nhttps://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683",
                'fr': ":red_circle: **Le temps est ÉCOULÉ!** {} 🎉\nhttps://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683"
            }
            
            try:
                final_embed = discord.Embed(
                    title="🎉 Timer Completed!",
                    description="```\n🚨  00:00  🚨\n```",
                    color=0xff0000
                )
                final_embed.add_field(name="👤 Timer Owner", value=ctx.author.mention, inline=True)
                final_embed.add_field(name="🎯 Status", value="✅ **FINISHED!**", inline=True)
                final_embed.add_field(name="� Channel", value=ctx.channel.mention, inline=True)
                final_embed.add_field(name="🎊 Result", value="**TIME'S UP!** 🎉", inline=False)
                final_embed.set_footer(text="Timer completed successfully!")
                final_embed.set_image(url="https://tenor.com/view/wrap-it-up-kowalski-game-awards-finish-already-penguin-gif-9878765111777341683.gif")
                
                await msg.edit(embed=final_embed, view=view)
                await ctx.send(end_messages[lang].format(ctx.author.mention))
            except:
                pass
            
            # Cleanup
            if timer_id in l:
                del l[timer_id]
            if timer_id in active_timers:
                del active_timers[timer_id]
                
    except ValueError:
        await ctx.send("Invalid time format. Use format like: `5m 30s`")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@client.command()
async def pause(ctx):
    """Pause your timer"""
    timer_id = f"{ctx.author.id}_{ctx.channel.id}"
    lang = await get_language(ctx.guild.id)
    
    if timer_id in l and l[timer_id] == 0:
        l[timer_id] = 2
        pause_messages = {
            'en': f"⏸️ Timer paused by {ctx.author.mention}.",
            'fr': f"⏸️ Chronomètre mis en pause par {ctx.author.mention}."
        }
        await ctx.send(pause_messages.get(lang, pause_messages['en']))
    elif timer_id in l and l[timer_id] == 2:
        already_paused_messages = {
            'en': f"{ctx.author.mention}, your timer is already paused.",
            'fr': f"{ctx.author.mention}, votre chronomètre est déjà en pause."
        }
        await ctx.send(already_paused_messages.get(lang, already_paused_messages['en']))
    else:
        no_timer_messages = {
            'en': f"{ctx.author.mention}, you don't have a timer running in this channel.",
            'fr': f"{ctx.author.mention}, vous n'avez pas de chronomètre en cours dans ce canal."
        }
        await ctx.send(no_timer_messages.get(lang, no_timer_messages['en']))

@client.command()
async def resume(ctx):
    """Resume your timer"""
    timer_id = f"{ctx.author.id}_{ctx.channel.id}"
    lang = await get_language(ctx.guild.id)
    
    if timer_id in l and l[timer_id] == 2:
        l[timer_id] = 0
        resume_messages = {
            'en': f"▶️ Timer resumed by {ctx.author.mention}.",
            'fr': f"▶️ Chronomètre repris par {ctx.author.mention}."
        }
        await ctx.send(resume_messages.get(lang, resume_messages['en']))
    elif timer_id in l and l[timer_id] == 0:
        already_running_messages = {
            'en': f"{ctx.author.mention}, your timer is already running.",
            'fr': f"{ctx.author.mention}, votre chronomètre est déjà en cours."
        }
        await ctx.send(already_running_messages.get(lang, already_running_messages['en']))
    else:
        no_timer_messages = {
            'en': f"{ctx.author.mention}, you don't have a paused timer in this channel.",
            'fr': f"{ctx.author.mention}, vous n'avez pas de chronomètre en pause dans ce canal."
        }
        await ctx.send(no_timer_messages.get(lang, no_timer_messages['en']))

@client.command(aliases=['cleartimers'])
async def stop(ctx):
    """Stop your timer"""
    timer_id = f"{ctx.author.id}_{ctx.channel.id}"
    lang = await get_language(ctx.guild.id)
    
    if timer_id in l:
        l[timer_id] = 1
        stop_messages = {
            'en': f"⏹️ Timer stopped by {ctx.author.mention}.",
            'fr': f"⏹️ Chronomètre arrêté par {ctx.author.mention}."
        }
        await ctx.send(stop_messages.get(lang, stop_messages['en']))
    else:
        no_timer_messages = {
            'en': f"{ctx.author.mention}, you don't have a timer running in this channel.",
            'fr': f"{ctx.author.mention}, vous n'avez pas de chronomètre en cours dans ce canal."
        }
        await ctx.send(no_timer_messages.get(lang, no_timer_messages['en']))

@client.command(aliases=['8ball', 'test'])
async def _8ball(ctx, *, question):
    """Ask the magic 8-ball a question"""
    lang = await get_language(ctx.guild.id)
    
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

@client.command(aliases=['hello', 'hi', 'hola', 'hey', 'bonjour', 'salut', 'aloha'])
async def greetings(ctx):
    """Greet the user"""
    lang = await get_language(ctx.guild.id)
    
    greetings_list = {
        'en': ['Hey there,', 'Hello,', "What's up?"],
        'fr': ['Bonjour', 'Salut', 'Aloha', 'Hey', 'Salut toi', 'Quoi de neuf ?']
    }
    
    greeting = random.choice(greetings_list.get(lang, greetings_list['en']))
    await ctx.send(f'{greeting} {ctx.author.mention}')

@client.command()
async def coinflip(ctx):
    """Flip a coin"""
    lang = await get_language(ctx.guild.id)
    
    coins = {
        'en': ['Head', 'Tail'],
        'fr': ['Face', 'Pile']
    }
    
    result = random.choice(coins.get(lang, coins['en']))
    
    format_strings = {
        'en': 'The coin shows **{}!**',
        'fr': 'La pièce montre **{}!**'
    }
    
    await ctx.send(format_strings[lang].format(result))

@client.command()
async def ping(ctx):
    """Check bot latency"""
    await ctx.send(f'Ping: ***{round(client.latency*1000)}*** ms')

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 0):
    """Clear messages from channel"""
    lang = await get_language(ctx.guild.id)
    
    if amount < 0:
        await ctx.send("Amount must be positive.")
        return
    
    if amount > 100:
        await ctx.send("Cannot delete more than 100 messages at once.")
        return
    
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 for the command message
        count = len(deleted) - 1  # -1 for the command message
        
        messages = {
            'en': f'Cleared **{count}** message(s) by {ctx.author.mention}' if count > 0 else '*No messages were cleared. Provide a number!*',
            'fr': f'**{count}** message(s) effacé(s) par {ctx.author.mention}' if count > 0 else "*Aucun message effacé. Fournissez un nombre!*"
        }
        
        await ctx.send(messages.get(lang, messages['en']), delete_after=5)
    except discord.Forbidden:
        await ctx.send("I don't have permission to delete messages.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@client.command(aliases=['commands', 'HELP'])
async def help(ctx):
    """Show help message"""
    lang = await get_language(ctx.guild.id)
    
    if lang == 'fr':
        help_text = """**Toutes les commandes de Hear! Hear! :**

**Débat**
```
~ getmotion   : obtenir une motion aléatoire
~ addmotion   : ajouter une motion à la base de données
~ matchup     : .matchup AP | .toss BP - obtenir un appariement
```

**Chronométrage**
```
~ timer       : .t | .timer - régler un chronomètre à l'écran
~ reminder    : .reminder - régler un rappel en arrière-plan
~ pause       : mettre le chronomètre sur pause
~ resume      : reprendre le chronomètre
~ stop        : arrêter le chronomètre
```

**Utilitaire**
```
~ setlang     : .setlang fr | .setlang en
~ coinflip    : pile ou face
~ ping        : voir la latence du bot
~ time        : afficher le temps Unix
```

**Modération**
```
~ clear       : supprimer le nombre spécifié de messages
~ unmute      : .unmute @mention
~ undeafen    : .undeafen @mention
```

**Amusement**
```
~ greetings   : .hello | .hi | .hola
~ 8ball       : poser une question à la boule magique
```

***Veuillez utiliser un point `.` avant les commandes***"""
    else:
        help_text = """**Hear! Hear! bot all commands:**

**Debate**
```
~ getmotion   : get a random motion
~ addmotion   : add a motion to the database
~ matchup     : .matchup AP | .toss BP - get matchup
```

**Time Keeping**
```
~ timer       : .t | .timer - set an on-screen timer
~ reminder    : .reminder - set a background reminder
~ pause       : pause the timer
~ resume      : resume the timer
~ stop        : stop the timer
```

**Utility**
```
~ setlang     : .setlang en | .setlang fr
~ coinflip    : heads or tails
~ ping        : see bot latency
~ time        : show Unix time
```

**Moderation**
```
~ clear       : delete specified number of messages
~ unmute      : .unmute @mention
~ undeafen    : .undeafen @mention
```

**Fun**
```
~ greetings   : .hello | .hi | .hola
~ 8ball       : ask the magic 8-ball a question
```

***Please use a dot `.` before commands***"""
    
    await ctx.send(help_text)

@client.command()
async def getmotion(ctx):
    """Get a random debate motion"""
    if not db:
        await ctx.send("Database not available.")
        return
    
    lang = await get_language(ctx.guild.id)
    
    try:
        collection = db['motions']
        motions = list(collection.find())
        
        if not motions:
            no_motions_messages = {
                'en': 'No motions found in database. Use `.addmotion` to add some!',
                'fr': 'Aucune motion trouvée dans la base de données. Utilisez `.addmotion` pour en ajouter!'
            }
            await ctx.send(no_motions_messages.get(lang, no_motions_messages['en']))
            return
        
        motion = random.choice(motions)
        
        format_messages = {
            'en': f'**Random Motion:** {motion["text"]}',
            'fr': f'**Motion Aléatoire:** {motion["text"]}'
        }
        
        await ctx.send(format_messages.get(lang, format_messages['en']))
        
    except Exception as e:
        await ctx.send(f"Error getting motion: {e}")

@client.command()
async def addmotion(ctx, *, motion_text):
    """Add a motion to the database"""
    if not db:
        await ctx.send("Database not available.")
        return
    
    lang = await get_language(ctx.guild.id)
    
    if len(motion_text) < 10:
        error_messages = {
            'en': 'Motion too short. Please provide a detailed motion.',
            'fr': 'Motion trop courte. Veuillez fournir une motion détaillée.'
        }
        await ctx.send(error_messages.get(lang, error_messages['en']))
        return
    
    try:
        collection = db['motions']
        
        # Check if motion already exists
        existing = collection.find_one({'text': motion_text})
        if existing:
            duplicate_messages = {
                'en': 'This motion already exists in the database!',
                'fr': 'Cette motion existe déjà dans la base de données!'
            }
            await ctx.send(duplicate_messages.get(lang, duplicate_messages['en']))
            return
        
        # Add new motion
        motion_doc = {
            'text': motion_text,
            'added_by': str(ctx.author.id),
            'added_at': time.time(),
            'guild_id': str(ctx.guild.id)
        }
        
        collection.insert_one(motion_doc)
        
        success_messages = {
            'en': f'Motion added successfully: **{motion_text}**',
            'fr': f'Motion ajoutée avec succès: **{motion_text}**'
        }
        
        await ctx.send(success_messages.get(lang, success_messages['en']))
        
    except Exception as e:
        await ctx.send(f"Error adding motion: {e}")

@client.command()
async def matchup(ctx, position=None):
    """Get a debate matchup"""
    lang = await get_language(ctx.guild.id)
    
    teams = {
        'en': {
            'AP': 'Affirmative (Pro)',
            'BP': 'Negative (Con)', 
            'sides': ['Affirmative (Pro)', 'Negative (Con)']
        },
        'fr': {
            'AP': 'Affirmatif (Pour)',
            'BP': 'Négatif (Contre)',
            'sides': ['Affirmatif (Pour)', 'Négatif (Contre)']
        }
    }
    
    if position and position.upper() in ['AP', 'BP']:
        side = teams[lang][position.upper()]
        result_messages = {
            'en': f'**Your assigned position:** {side}',
            'fr': f'**Votre position assignée:** {side}'
        }
        await ctx.send(result_messages.get(lang, result_messages['en']))
    else:
        side = random.choice(teams[lang]['sides'])
        result_messages = {
            'en': f'**Random matchup for {ctx.author.mention}:** {side}',
            'fr': f'**Appariement aléatoire pour {ctx.author.mention}:** {side}'
        }
        await ctx.send(result_messages.get(lang, result_messages['en']))

@client.command()
async def toss(ctx, position=None):
    """Coin toss for debate position"""
    lang = await get_language(ctx.guild.id)
    
    teams = {
        'en': ['Affirmative (Pro)', 'Negative (Con)'],
        'fr': ['Affirmatif (Pour)', 'Négatif (Contre)']
    }
    
    result = random.choice(teams[lang])
    
    if position and position.upper() == 'BP':
        toss_messages = {
            'en': f'**Coin toss result for {ctx.author.mention}:** {result}',
            'fr': f'**Résultat du tirage pour {ctx.author.mention}:** {result}'
        }
    else:
        toss_messages = {
            'en': f'**Coin toss result for {ctx.author.mention}:** {result}',
            'fr': f'**Résultat du tirage pour {ctx.author.mention}:** {result}'
        }
    
    await ctx.send(toss_messages.get(lang, toss_messages['en']))

@client.command()
async def reminder(ctx, duration, seconds='0s', *, message='Timer finished!'):
    """Set a background reminder"""
    lang = await get_language(ctx.guild.id)
    
    if not (duration.endswith('m') and seconds.endswith('s')):
        error_messages = {
            'en': '*Syntax error*\n*The command should contain minutes and seconds in format* **Nm Ns**\nFor example: ***7m 15s "Your message here"***',
            'fr': '*Erreur de syntaxe*\n*La commande doit contenir le nombre de minutes et de secondes selon le format* **Nm Ns**\nPar exemple : ***7m 15s "Votre message ici"***'
        }
        await ctx.send(error_messages.get(lang, error_messages['en']))
        return
    
    try:
        minutes = int(duration[:-1])
        secs = int(seconds[:-1])
        total_seconds = minutes * 60 + secs
        
        if total_seconds <= 0:
            await ctx.send("Reminder duration must be greater than 0.")
            return
        
        if total_seconds > 86400:  # 24 hours limit
            await ctx.send("Reminder cannot exceed 24 hours.")
            return
        
        start_messages = {
            'en': f'**Background reminder set for {minutes}m {secs}s** ⏰',
            'fr': f'**Rappel en arrière-plan réglé pour {minutes}m {secs}s** ⏰'
        }
        
        await ctx.send(start_messages.get(lang, start_messages['en']))
        
        # Store reminder info
        reminder_id = f"{ctx.author.id}_{int(time.time())}"
        t[reminder_id] = {
            'user': ctx.author,
            'channel': ctx.channel,
            'message': message,
            'lang': lang
        }
        
        # Wait for the specified time
        await asyncio.sleep(total_seconds)
        
        # Send reminder
        if reminder_id in t:
            reminder_messages = {
                'en': f'⏰ **Reminder for {ctx.author.mention}:** {message}',
                'fr': f'⏰ **Rappel pour {ctx.author.mention}:** {message}'
            }
            await ctx.send(reminder_messages.get(lang, reminder_messages['en']))
            del t[reminder_id]
                
    except ValueError:
        await ctx.send("Invalid time format. Use format like: `5m 30s Your message`")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@client.command()
async def about(ctx):
    """Show information about the bot"""
    lang = await get_language(ctx.guild.id)
    
    if lang == 'fr':
        about_text = """```Ceci est un bot utilitaire dédié aux débatteurs. Ce bot permet de chronométrer vos débats à l'aide d'un affichage de chronomètre et d'alertes.

Développé par         : Tasdid Tahsin
Avatar                : Sharaf Ahmed
Traduction française  : Victor Babin, Étienne Beaulé, Thierry Jean, Nuzaba Tasannum
Support communautaire : Bangla Online Debate Platform

</> Programmé en Python3 utilisant Discord.py & pymongo```"""
    else:
        about_text = """```This is a productivity bot dedicated to debaters. This bot can time your debates with on-screen timer and give you reminders.

Developed by       : Tasdid Tahsin
Avatar             : Sharaf Ahmed  
French Translation : Victor Babin, Étienne Beaulé, Thierry Jean, Nuzaba Tasannum
Community Support  : Bangla Online Debate Platform

</> Coded in Python3 using Discord.py & pymongo```"""
    
    await ctx.send(about_text)

if __name__ == "__main__":
    # Start HTTP server in background thread for Render
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    print("HTTP server started for Render compatibility")
    
    try:
        client.run(token)
    except Exception as e:
        print(f"Error starting bot: {e}")