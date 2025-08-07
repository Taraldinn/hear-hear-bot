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

l = {}      # timer trigger library
t = {}      # reminder storage library

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
    """Set a visual timer"""
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
        
        l[ctx.channel.id] = 0
        
        start_messages = {
            'en': f'**Timer set for {minutes}m {secs}s {ctx.author.mention}**\n*Use `.r` for background timer*',
            'fr': f'**Chronomètre réglé pour {minutes}m {secs}s {ctx.author.mention}**\n*Utilisez `.r` pour un chronomètre en arrière-plan*'
        }
        
        await ctx.send(start_messages.get(lang, start_messages['en']))
        
        timer_format = {
            'en': ':clock1: **Timer:** **`{:02d}:{:02d}`** {} `.pause` to pause',
            'fr': ':clock1: **Chronomètre:** **`{:02d}:{:02d}`** {} `.pause` pour mettre sur pause'
        }
        
        msg = await ctx.send(timer_format[lang].format(minutes, secs, ctx.author.mention))
        
        while total_seconds > 0:
            if ctx.channel.id not in l:
                break
                
            if l[ctx.channel.id] == 1:  # Stop
                await ctx.send("Timer stopped!")
                del l[ctx.channel.id]
                break
            elif l[ctx.channel.id] == 2:  # Pause
                pause_format = {
                    'en': ':pause_button: **Paused:** **`{:02d}:{:02d}`** {} `.resume` to resume',
                    'fr': ':pause_button: **En pause:** **`{:02d}:{:02d}`** {} `.resume` pour reprendre'
                }
                await msg.edit(content=pause_format[lang].format(total_seconds // 60, total_seconds % 60, ctx.author.mention))
                while l.get(ctx.channel.id, 0) == 2:
                    await asyncio.sleep(1)
                continue
            
            # Update timer display
            await msg.edit(content=timer_format[lang].format(total_seconds // 60, total_seconds % 60, ctx.author.mention))
            
            # Check for milestone notifications
            if total_seconds == 60:
                milestone_messages = {
                    'en': ':orange_circle: **1 minute LEFT** {}',
                    'fr': ':orange_circle: **1 minute RESTANTE** {}'
                }
                await ctx.send(milestone_messages[lang].format(ctx.author.mention))
            
            await asyncio.sleep(1)
            total_seconds -= 1
        
        if total_seconds <= 0 and ctx.channel.id in l:
            end_messages = {
                'en': ":red_circle: **Time's UP!** {} Additional 15 seconds given.",
                'fr': ":red_circle: **Le temps est ÉCOULÉ!** {} 15 secondes de grâce accordées."
            }
            await ctx.send(end_messages[lang].format(ctx.author.mention))
            await msg.edit(content=f':clock1: **Timer:** **`00:00`** {ctx.author.mention}')
            await asyncio.sleep(15)
            
            final_messages = {
                'en': "**Additional time finished!** {}",
                'fr': "**Le temps de grâce est écoulé!** {}"
            }
            await ctx.send(final_messages[lang].format(ctx.author.mention))
            
            if ctx.channel.id in l:
                del l[ctx.channel.id]
                
    except ValueError:
        await ctx.send("Invalid time format. Use format like: `5m 30s`")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@client.command()
async def pause(ctx):
    """Pause the timer"""
    if ctx.channel.id in l:
        l[ctx.channel.id] = 2
        await ctx.send("Timer paused.")
    else:
        await ctx.send("No timer running in this channel.")

@client.command()
async def resume(ctx):
    """Resume the timer"""
    if ctx.channel.id in l:
        l[ctx.channel.id] = 0
        await ctx.send("Timer resumed.")
    else:
        await ctx.send("No timer to resume in this channel.")

@client.command(aliases=['cleartimers'])
async def stop(ctx):
    """Stop the timer"""
    if ctx.channel.id in l:
        l[ctx.channel.id] = 1
        await ctx.send("Timer stopped.")
    else:
        await ctx.send("No timer running in this channel.")

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

@client.command(aliases=['r'])
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
    try:
        client.run(token)
    except Exception as e:
        print(f"Error starting bot: {e}")