# 🤖 Hear! Hear! Bot - Complete Documentation

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/Taraldinn/hear-hear-bot)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3.0-blue.svg)](https://discordpy.readthedocs.io/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Quick Start](#quick-start)
4. [Commands Reference](#commands-reference)
5. [Tournament System](#tournament-system)
6. [Carl-bot Features](#carl-bot-features)
7. [Configuration](#configuration)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)

## 🎯 Overview

**Hear! Hear! Bot** is a comprehensive Discord bot designed specifically for debate communities and tournament management. It combines traditional debate timing features with modern Discord server management capabilities, including Carl-bot style features like reaction roles, logging, and moderation.

### 🎯 Target Audience
- **Debate Societies** - Academic debate clubs and organizations
- **Tournament Organizers** - Event organizers running debate competitions
- **Educational Institutions** - Schools and universities with debate programs
- **Discord Communities** - General server management needs

### 🔧 Built With
- **Discord.py** - Modern Discord API wrapper
- **Python 3.8+** - Core programming language
- **MongoDB** - Database for persistent storage
- **AsyncIO** - Asynchronous programming for performance

## ✨ Features

### 🏆 Tournament Management
- **Automated Tournament Setup** - Create entire tournament infrastructures with one command
- **Multi-Format Support** - Asian Parliamentary (AP) and British Parliamentary (BP) formats
- **Venue Management** - Automatic creation of debate venues with proper permissions
- **Role-Based Access** - Debater, Adjudicator, and Spectator roles with appropriate permissions

### ⏰ Debate Timing System
- **Interactive Timers** - Button-controlled timers with visual feedback
- **Multiple Timer Types** - Prep time, speech time, and custom timers
- **Multi-User Support** - Individual timers for each user
- **Timer Persistence** - Timers survive bot restarts

### 🎭 Carl-bot Style Features
- **Reaction Roles** - Advanced reaction role system with multiple modes
- **Server Logging** - Comprehensive audit logs for all server activities
- **Auto-Moderation** - Automated moderation with customizable rules
- **Welcome System** - Customizable welcome messages and auto-roles

### 🎲 Debate Utilities
- **Random Motions** - Curated motion database with multi-language support
- **Coin Tossing** - Fair coin tosses for side determination
- **Dice Rolling** - Custom dice with configurable sides
- **Position Assignment** - Automatic team position allocation

### 🛠️ Server Management
- **Permission Management** - Advanced permission controls
- **Channel Organization** - Automated channel creation and organization
- **Database Integration** - Persistent storage for all configurations

## 🚀 Quick Start

### Prerequisites
```bash
# Required
Python 3.8+
Discord Bot Token
MongoDB Database (optional but recommended)
```

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/Taraldinn/hear-hear-bot.git
cd hear-hear-bot
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
# or using pipenv
pipenv install
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env file with your bot token and database connection
```

4. **Run the Bot**
```bash
python main.py
# or with pipenv
pipenv run python main.py
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# Required: Discord Bot Token
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Optional: MongoDB Connection
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/database

# Optional: Additional APIs
TOPGG_TOKEN=your_topgg_token_here
TEST_GUILD_ID=your_test_server_id_here
```

### Bot Permissions

When inviting the bot to your server, ensure it has these permissions:

#### Required Permissions
- `Send Messages` - Basic message sending
- `Use Slash Commands` - Modern command interface
- `Embed Links` - Rich message embeds
- `Read Message History` - Command context

#### Tournament Setup Permissions
- `Manage Channels` - Create/modify channels
- `Manage Roles` - Create/assign roles
- `Connect` - Join voice channels
- `Speak` - Voice channel interactions

#### Moderation Permissions (Optional)
- `Manage Messages` - Message moderation
- `Kick Members` - Member moderation
- `Ban Members` - Advanced moderation
- `Manage Nicknames` - Nickname management

## 📚 Commands Reference

### 🏆 Tournament Commands

#### `/create_tournament`
Creates a complete tournament setup with venues, roles, and channels.

**Parameters:**
- `tournament_type` - AP (Asian Parliamentary) or BP (British Parliamentary)
- `venues` - Number of venues to create (1-20)
- `setup_roles` - Create tournament roles (default: true)
- `setup_role_assignment` - Setup role assignment channel (default: true)

**Example:**
```
/create_tournament tournament_type:BP venues:5 setup_roles:true
```

**What it creates:**
- Tournament roles (Debater, Adjudicator, Spectator)
- General channels (Welcome, Info Desk, Feedback, Grand Auditorium)
- Venue-specific channels with proper permissions
- Role assignment system with reactions

### ⏰ Timer Commands

#### `/timer`
Creates an interactive debate timer with buttons.

**Parameters:**
- `duration` - Timer duration in MM:SS format
- `title` - Optional timer title
- `public` - Whether timer is visible to everyone

**Example:**
```
/timer duration:07:00 title:Government Speech public:true
```

#### `/timer-stop`, `/timer-pause`
Control your active timers.

### 🎲 Debate Utility Commands

#### `/randommotion`
Get a random debate motion from the database.

**Parameters:**
- `language` - Motion language (English, Bangla, etc.)

#### `/coinflip`, `/toss`, `/ap-toss`, `/bp-toss`
Various coin toss commands for debate format decisions.

#### `/diceroll`
Roll a dice with custom sides.

### 🎭 Carl-bot Style Commands

#### `/reactionrole`
Create a reaction role message.

**Parameters:**
- `title` - Embed title
- `description` - Embed description
- `mode` - Role assignment mode (unique, verify, reversed, binding, temporary, normal)

#### `/add-reaction-role`
Add a role to an existing reaction role message.

**Parameters:**
- `message_id` - ID of the reaction role message
- `emoji` - Emoji to use
- `role` - Role to assign

### 🛠️ Admin Commands

#### `/autorole`, `/setup-logging`, `/setup-moderation`
Server configuration commands for advanced features.

#### `/ping`, `/help`, `/about`
Basic information and utility commands.

## 🏆 Tournament System

### Tournament Formats

#### Asian Parliamentary (AP)
- **Teams per Venue:** 2 teams (Government vs Opposition)
- **Prep Rooms:** 2 per venue (Gov-Prep, Opp-Prep)
- **Capacity:** 3 members per prep room
- **Suitable for:** Smaller tournaments, school competitions

#### British Parliamentary (BP)
- **Teams per Venue:** 4 teams (OG, OO, CG, CO)
- **Prep Rooms:** 4 per venue (OG-Prep, OO-Prep, CG-Prep, CO-Prep)
- **Capacity:** 2 members per prep room
- **Suitable for:** University tournaments, major competitions

### Channel Structure

#### Per Venue (Example: Venue 1)
```
📁 Venue 1/
├── 💬 venue-1-debate (text channel)
├── 🔊 Venue-1-Debate (main voice channel)
├── 🔒 Venue-1-[Team]-Prep (prep rooms, role-restricted)
└── ⚖️ Venue-1-Result-Discussion (adjudicator only)
```

#### General Tournament Channels
```
📁 Welcome/
├── 💬 welcome
├── 💬 instructions-for-teams
├── 💬 instructions-for-adjudicators
└── 🎭 role-assignment

📁 Info Desk/
├── 💬 bot-commands
├── 💬 schedules
└── 💬 tech-support

📁 Feedback & Check-in/
├── 💬 feedback-submission
└── 💬 check-in

📁 Grand Auditorium/
├── 💬 announcements
├── 💬 motion-clarifications
├── 💬 draws-and-motion-release
└── 🔊 Grand-Auditorium (voice)
```

### Role System

#### 🥊 Debater Role
- **Access:** Prep rooms, general channels
- **Restrictions:** Cannot access result discussions
- **Voice Limits:** Prep room capacity enforced

#### ⚖️ Adjudicator Role
- **Access:** All channels including result discussions
- **Permissions:** Mute/deafen capabilities
- **Special:** Access to private adjudicator channels

#### 👀 Spectator Role
- **Access:** Read-only general channels
- **Restrictions:** Cannot join voice channels
- **Purpose:** Tournament observers, media

## 🎭 Carl-bot Features

### Reaction Roles System

#### Modes Available

**Normal Mode** - Standard reaction role behavior
**Unique Mode** - Users can only pick one role from the message
**Verify Mode** - Users must confirm their selection
**Reversed Mode** - Reactions remove roles instead of adding them
**Binding Mode** - Roles cannot be removed once assigned
**Temporary Mode** - Roles expire after a set time

### Logging System

#### Events Logged
- **Message Events:** Edit, delete, bulk delete
- **Member Events:** Join, leave, nickname changes
- **Role Events:** Role assignments, removals
- **Channel Events:** Create, delete, modify
- **Voice Events:** Join, leave, move between channels
- **Moderation Events:** Kicks, bans, mutes

### Auto-Moderation

#### Features
- **Spam Detection:** Message rate limiting
- **Link Filtering:** Block suspicious links
- **Word Filtering:** Customizable word blacklist
- **Caps Lock Detection:** Excessive capitalization
- **Raid Protection:** Mass join detection

## ⚙️ Configuration

### Database Setup

#### MongoDB Atlas (Cloud)
1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster
3. Get connection string
4. Add to `.env` file

#### Local MongoDB
```bash
# Install MongoDB Community Edition
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb/brew/mongodb-community
```

### Invite URL Template
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=8&scope=bot%20applications.commands
```

## 🌐 Deployment

### Heroku Deployment

1. **Create Heroku App**
```bash
heroku create your-bot-name
```

2. **Set Environment Variables**
```bash
heroku config:set DISCORD_BOT_TOKEN=your_token_here
heroku config:set MONGODB_CONNECTION_STRING=your_mongodb_uri
```

3. **Deploy**
```bash
git push heroku main
```

### Railway Deployment

1. **Connect Repository** to Railway
2. **Set Environment Variables** in dashboard
3. **Deploy** automatically triggers

### Self-Hosted VPS

1. **Setup Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Git
sudo apt install python3 python3-pip git -y

# Clone repository
git clone https://github.com/Taraldinn/hear-hear-bot.git
cd hear-hear-bot
```

2. **Install Dependencies**
```bash
pip3 install -r requirements.txt
```

3. **Setup Service**
```bash
# Create systemd service
sudo nano /etc/systemd/system/hear-hear-bot.service
```

4. **Service Configuration**
```ini
[Unit]
Description=Hear! Hear! Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/hear-hear-bot
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🐛 Troubleshooting

### Common Issues

#### Bot Not Responding
```bash
# Check bot status
/ping

# Verify token in logs
# Look for "logging in using static token"
```

#### Slash Commands Not Appearing
```bash
# Force sync commands
# Wait up to 1 hour for global commands
# Use test guild for immediate testing
```

#### Permission Errors
- Verify bot has required permissions
- Check role hierarchy (bot role above managed roles)
- Ensure bot has channel access

#### Database Connection Issues
```bash
# Check MongoDB connection in logs
# Verify connection string format
# Test database connectivity
```

### Error Messages

#### "Missing required environment variables"
- Check `.env` file exists and has `DISCORD_BOT_TOKEN`
- Verify environment variable names match exactly

#### "Failed to load extension"
- Check for syntax errors in command files
- Verify all imports are available
- Check database connection for database-dependent features

## 🛠️ Development

### Project Structure
```
hear-hear-bot/
├── main.py                 # Bot entry point
├── requirements.txt        # Dependencies
├── config/
│   └── settings.py        # Configuration management
├── src/
│   ├── bot/
│   │   └── client.py      # Main bot client
│   ├── commands/
│   │   ├── tournament.py  # Tournament setup
│   │   ├── timer.py       # Timer system
│   │   ├── reaction_roles.py # Reaction roles
│   │   ├── logging.py     # Logging system
│   │   └── slash_commands.py # Basic slash commands
│   ├── database/
│   │   └── connection.py  # Database connection
│   └── utils/
│       └── timer.py       # Timer utilities
└── data/
    ├── english.txt        # English motions
    └── bangla.txt         # Bangla motions
```

### Adding New Commands

1. **Create Command File**
```python
# src/commands/my_feature.py
import discord
from discord.ext import commands
from discord import app_commands

class MyFeature(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="my_command", description="My new command")
    async def my_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello from my command!")

async def setup(bot):
    await bot.add_cog(MyFeature(bot))
```

2. **Register Extension**
```python
# src/bot/client.py
extensions = [
    # ... existing extensions
    "src.commands.my_feature",
]
```

### Contributing Guidelines

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Discord.py** - Excellent Discord library
- **Carl-bot** - Inspiration for moderation features
- **Debate Community** - Feature requirements and testing

## 📞 Contact

- **Author:** aldinn
- **Email:** kferdoush617@gmail.com
- **GitHub:** [@Taraldinn](https://github.com/Taraldinn)

---

*Built with ❤️ for the debate community*

## ✨ Features

### 🕐 Timer Functions
- **Start/Stop Timers**: Individual debate timers for each user
- **Auto Timers**: Automatically stop after specified duration
- **Multi-language Support**: Timer messages in English and Bangla
- **Smart Notifications**: Warnings for approaching time limits

### 🎯 Debate Tools
- **Random Motions**: Generate random debate motions in multiple languages
- **Coin Flip & Dice**: Random decision tools
- **Position Guide**: Display debate positions and speaking order
- **Format Information**: Information about different debate formats

### 🏆 Tournament Integration
- **Tabbycat Sync**: Full integration with Tabbycat tournament software
- **Registration**: Player and adjudicator registration with private URLs
- **Check-in/Check-out**: Tournament attendance management
- **Motion Release**: Fetch and display round motions
- **Feedback System**: Submit adjudicator feedback with visual reports

### 👑 Administration
- **Voice Control**: Unmute/undeafen members
- **Auto-roles**: Automatic role assignment for new members
- **Language Settings**: Set server language preferences
- **Data Management**: Server data backup and cleanup tools

### 🌐 Multi-language Support
- **English & Bangla**: Full support for both languages
- **Expandable**: Easy to add more languages
- **Localized Messages**: All bot responses adapt to server language

### 🌍 Global Deployment
- **Multi-Server Support**: Works across ALL Discord servers simultaneously
- **Global Slash Commands**: Commands available in every server the bot joins
- **Auto-Sharding**: Optimized for handling thousands of servers
- **Scalable Architecture**: Designed for global tournament management

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB database
- Discord Bot Token
- (Optional) Tabbycat tournament instance

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hear-hear-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
DISCORD_BOT_TOKEN=your_discord_bot_token_here
MONGODB_CONNECTION_STRING=your_mongodb_connection_string_here

# Optional
TOPGG_TOKEN=your_topgg_token_here
PORT=8080
```

## 📋 Commands

### 🆕 Slash Commands (Recommended)
**Timer Commands**
- `/timer start` - Start a new debate timer
- `/timer stop` - Stop your active timer  
- `/timer check` - Check your current timer status

**Debate Commands**
- `/randommotion [language]` - Get random debate motion (English/Bangla)
- `/coinflip` - Flip a coin for decisions
- `/diceroll [sides]` - Roll a dice (default: 6 sides)

**Admin Commands** *(Requires permissions)*
- `/unmute <member>` - Unmute a voice-muted member
- `/undeafen <member>` - Undeafen a voice-deafened member

**Utility Commands**
- `/ping` - Check bot latency and status
- `/help` - Show comprehensive help information

### 📝 Prefix Commands (Legacy Support)
**Tournament Commands (Tabbycat Integration)**
- `.tabsync <url> <token>` - Connect server to Tabbycat tournament
- `.register <key>` - Register with tournament using identification key
- `.checkin` - Check in to tournament
- `.checkout` - Check out from tournament
- `.motion <round>` - Get motion for specific round
- `.status` - Show tournament connection status

**Advanced Admin Commands**
- `.setlanguage <language>` - Set server language (english/bangla)
- `.autorole <role>` - Set automatic role for new members
- `.deletedata` - Delete all server data (with confirmation)
- `.serverinfo` - Display server information and settings

**Additional Utility Commands**
- `.info` - Display bot information and statistics
- `.invite` - Get bot invite link
- `.version` - Show version and changelog

> 💡 **Tip**: Use slash commands (/) for the best experience! They provide better autocomplete, validation, and user interface.

## 🏗️ Project Structure

```
hear-hear-bot/
├── main.py                 # Bot entry point
├── config/
│   └── settings.py         # Configuration management
├── src/
│   ├── bot/
│   │   └── client.py       # Main bot client
│   ├── commands/
│   │   ├── admin.py        # Admin commands
│   │   ├── debate.py       # Debate-related commands
│   │   ├── timer.py        # Timer commands
│   │   ├── tabby.py        # Tabbycat integration
│   │   └── utility.py      # Utility commands
│   ├── events/
│   │   ├── member.py       # Member join/leave events
│   │   └── error.py        # Error handling
│   ├── utils/
│   │   ├── language.py     # Language management
│   │   ├── timer.py        # Timer utilities
│   │   └── image_generator.py # Image generation
│   └── database/
│       └── connection.py   # Database management
├── data/
│   ├── english.txt         # English motions
│   └── bangla.txt          # Bangla motions
├── assets/
│   ├── fonts/              # Font files for image generation
│   └── *.png              # Image templates
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### Bot Permissions

The bot requires the following Discord permissions:
- **Basic**: Read Messages, Send Messages, Embed Links
- **Voice**: Mute Members, Deafen Members
- **Management**: Manage Roles, Manage Messages
- **Advanced**: Add Reactions, Attach Files

### Database Schema

**Guilds Collection:**
```json
{
  "_id": "guild_id",
  "language": "english",
  "autorole": "role_id",
  "welcome_channel": "channel_id",
  "goodbye_channel": "channel_id"
}
```

**Tournaments Collection:**
```json
{
  "_id": "guild_id",
  "site": "https://tournament-site.com",
  "token": "api_token",
  "tournament": "tournament_api_url",
  "tournament_name": "Tournament Name",
  "teams": [...],
  "adjudicators": [...]
}
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### Heroku Deployment

1. Create `Procfile`:
   ```
   worker: python main.py
   ```

2. Set environment variables in Heroku dashboard

3. Deploy:
   ```bash
   git push heroku main
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Format code
black src/
```

## 📝 Changelog

### Version 2.0.0
- ✅ Unified bot features from multiple versions
- ✅ Professional component-based architecture
- ✅ Enhanced timer functionality
- ✅ Multi-language motion support
- ✅ Improved error handling
- ✅ Database optimization
- ✅ Comprehensive documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**aldinn**
- Email: kferdoush617@gmail.com
- GitHub: [https://github.com/aldinn](https://github.com/aldinn)

## 🙏 Credits

- **Project Mentor**: Étienne Beaulé [Étienne#7236]
- **Contributors**: Irhum [adorablemonk#4060] & Najib Hayder [Najib#7917]
- **Built with**: Python 3, Discord.py, Tabbycat API v1, MongoDB

## 📞 Support

- Join our [Support Server](https://discord.gg/your-invite)
- Create an [Issue](https://github.com/your-repo/issues)
- Email: kferdoush617@gmail.com

---

*Made with ❤️ for the debate community*
