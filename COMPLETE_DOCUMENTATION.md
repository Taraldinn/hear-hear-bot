# 🎤 Hear! Hear! Bot - Complete Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Web Documentation](#web-documentation)
4. [Command Reference](#command-reference)
5. [Features](#features)
6. [Architecture](#architecture)
7. [API Reference](#api-reference)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**Hear! Hear! Bot** is a comprehensive Discord bot specifically designed for debate tournaments and parliamentary-style debating communities. It provides seamless integration with Tabbycat tournament management software and offers a complete suite of tools for tournament administrators, adjudicators, and debaters.

### 🌟 Key Highlights

- **Modern Discord Integration**: Built with Discord.py 2.3+ using latest UI components
- **Tabbycat Integration**: Full synchronization with Tabbycat tournament software
- **Tournament Management**: Complete tournament setup and administration
- **Advanced Timer System**: Professional debate timing with multiple modes
- **Role-Based Permissions**: Granular access control for different user types
- **Web Documentation**: Comprehensive web-based documentation and API

---

## ⚙️ Installation & Setup

### 📋 Prerequisites

- **Python 3.10+**
- **Discord Bot Token**
- **MongoDB Database** (local or cloud)
- **Tabbycat Instance** (optional, for advanced features)

### 🔧 Quick Installation

```bash
# Clone the repository
git clone https://github.com/Taraldinn/hear-hear-bot.git
cd hear-hear-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run the bot
python main.py
```

### 🔐 Environment Configuration

```bash
# Discord Configuration
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_server_id
COMMAND_PREFIX=.

# Database Configuration
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
DATABASE_NAME=hear_hear_bot

# Web Server Configuration
PORT=8080
HOST=0.0.0.0

# Optional: Tabbycat Integration
TABBYCAT_URL=https://your-tabbycat-instance.com
TABBYCAT_TOKEN=your_api_token
```

---

## 🌐 Web Documentation

The bot includes a comprehensive web interface accessible at:

### 📚 Available Endpoints

- **`/`** - Homepage with bot overview and statistics
- **`/docs`** - Complete documentation (this comprehensive guide)
- **`/commands`** - Interactive command reference
- **`/health`** - Health check and status
- **`/api/stats`** - JSON API for bot statistics
- **`/invite`** - Bot invitation link

### 🎨 Features

- **Responsive Design**: Mobile-friendly interface
- **Dark/Light Mode**: Theme toggle support
- **Interactive Navigation**: Smooth scrolling and anchors
- **Real-time Stats**: Live bot statistics
- **Modern UI**: Beautiful, professional design

---

## 🤖 Command Reference

### 🏆 Tournament Management

#### `.setup-tournament "Tournament Name"`
- **Permission**: Administrator
- **Description**: Complete tournament initialization
- **Features**:
  - Creates all necessary roles (Debater, Adjudicator, AdjCore, etc.)
  - Sets up channel categories and permissions
  - Generates onboarding message with role assignment UI

#### `.create-venues <count> [prefix]`
- **Permission**: Administrator
- **Description**: Create debate venues with prep rooms and debate channels
- **Example**: `.create-venues 8 "Room"`

#### `.assign-roles`
- **Permission**: Administrator
- **Description**: Modern UI-based role assignment system
- **Features**:
  - Dropdown role selection
  - Duplicate registration prevention
  - Automatic permission assignment

### 📊 Tabbycat Integration

#### `.tabsync <TABBYCAT_URL> <API_TOKEN>`
- **Permission**: Administrator
- **Description**: Synchronize server with Tabbycat tournament
- **Features**:
  - Full tournament data import
  - Participant and adjudicator sync
  - Round and motion synchronization

#### `.register <key>`
- **Permission**: Anyone
- **Description**: Register for tournament using registration key
- **Supports**: Both debaters and adjudicators
- **Features**:
  - Automatic role assignment
  - Tabbycat check-in
  - Registration confirmation

#### `.checkin` / `.checkout`
- **Permission**: Anyone
- **Description**: Check in/out for tournament rounds
- **Updates**: Tabbycat availability status

#### `.status`
- **Permission**: Anyone
- **Description**: View tournament status and information
- **Shows**: Next round, participant counts, tournament details

#### `.motion <round_abbreviation>`
- **Permission**: Anyone
- **Description**: Display motion for specified round
- **Example**: `.motion R1`

#### `.feedback <round> <@adjudicator> <score>`
- **Permission**: Anyone (must be registered debater)
- **Description**: Submit feedback for adjudicators
- **Features**:
  - Privacy protection (deletes command message)
  - Score validation (0-10 range)
  - Optional feedback image generation
- **Example**: `.feedback R1 @johndoe 8.5`

### ⏰ Timer System

#### `.timer <duration> [type]`
- **Permission**: Adjudicator
- **Description**: Start debate timer
- **Types**: prep, speech, poi, break
- **Example**: `.timer 8 speech`
- **Features**:
  - Visual progress bars
  - Audio notifications
  - Real-time updates

#### `.timer-stop`
- **Permission**: Adjudicator
- **Description**: Stop current running timer

#### `.timer-pause`
- **Permission**: Adjudicator
- **Description**: Pause/resume current timer

#### `.timer-status`
- **Permission**: Anyone
- **Description**: Check current timer status

### 🛡️ Moderation & Venue Management

#### `.announce <message>`
- **Permission**: Manage Messages
- **Description**: Send announcements to all debate channels
- **Targets**: All channels with 'debate' in the name

#### `.begin-debate`
- **Permission**: Manage Messages
- **Description**: Move all participants from prep rooms to debate rooms
- **Features**:
  - Global participant movement
  - Automatic mute/unmute handling
  - Venue-aware processing

#### `.call-to-venue`
- **Permission**: Adjudicator
- **Description**: Move participants in current venue to debate room
- **Scope**: Works only within venue categories

### 👑 Administrative Commands

#### `.reload [cog_name]`
- **Permission**: Administrator
- **Description**: Reload bot cogs and extensions

#### `.sync`
- **Permission**: Administrator
- **Description**: Synchronize slash commands with Discord

#### `.logs [lines]`
- **Permission**: Administrator
- **Description**: View recent bot logs

#### `.delete-data YES I AM 100% SURE`
- **Permission**: Administrator
- **Description**: Safely delete all tournament data
- **Warning**: Irreversible action with confirmation required

### 🔧 Utility Commands

#### `.help [command]`
- **Permission**: Anyone
- **Description**: Display help information

#### `.ping`
- **Permission**: Anyone
- **Description**: Check bot latency and status

#### `.about`
- **Permission**: Anyone
- **Description**: Bot information and statistics

---

## ✨ Features

### 🎪 Tournament Management
- **Automated Setup**: One-command tournament initialization
- **Role Management**: Automatic role creation and assignment
- **Channel Creation**: Organized channel structure with proper permissions
- **Venue Management**: Automated prep and debate room creation
- **Permission System**: Granular permission control per role

### 📊 Tabbycat Integration
- **Real-time Sync**: Live synchronization with Tabbycat
- **Participant Registration**: Seamless key-based registration
- **Check-in System**: Availability tracking and updates
- **Motion Display**: Round-specific motion sharing
- **Feedback Collection**: Adjudicator feedback submission
- **Data Management**: Secure data handling and deletion

### ⏰ Advanced Timer System
- **Multiple Timer Types**: Prep, speech, POI, and break timers
- **Visual Feedback**: Real-time timer displays with progress bars
- **Audio Alerts**: Customizable notification sounds
- **Pause/Resume**: Full timer control capabilities
- **Auto-cleanup**: Automatic message management

### 🎨 Modern User Interface
- **Discord UI Components**: Dropdowns, buttons, and select menus
- **Interactive Registration**: User-friendly role selection
- **Rich Embeds**: Beautiful information displays
- **Responsive Design**: Optimized for all device types
- **Accessibility**: Screen reader friendly interfaces

### 🛡️ Security & Privacy
- **Permission Validation**: Strict command access control
- **Data Encryption**: Secure database storage
- **Privacy Protection**: Automatic sensitive message deletion
- **Audit Logging**: Comprehensive action tracking
- **Rate Limiting**: Abuse prevention mechanisms

---

## 🏗️ Architecture

### 💻 Technology Stack

- **Backend**: Python 3.10+, discord.py 2.3+, asyncio
- **Database**: MongoDB with pymongo
- **Web Server**: aiohttp with Jinja2 templates
- **Integration**: Tabbycat REST API
- **Deployment**: Docker, Gunicorn, Environment Variables

### 📁 Project Structure

```
hear-hear-bot/
├── src/
│   ├── bot/              # Bot client and core functionality
│   ├── commands/         # Command modules (cogs)
│   ├── database/         # Database connection and models
│   ├── events/           # Event handlers
│   └── utils/            # Utility functions
├── web/
│   ├── server.py         # Web server
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, assets
├── config/               # Configuration settings
├── data/                 # Data files
├── assets/               # Bot assets
└── main.py              # Application entry point
```

### 🔄 Data Flow

1. **Command Processing**: Discord message → Command parser → Cog handler
2. **Database Operations**: Handler → Database layer → MongoDB
3. **Tabbycat Sync**: API calls → Data processing → Database update
4. **Response Generation**: Data → Template rendering → Discord response
5. **Error Handling**: Exception → Logger → User feedback

---

## 📡 API Reference

### 🌐 Web Endpoints

- **`GET /`** - Bot homepage and status
- **`GET /docs`** - Complete documentation
- **`GET /commands`** - Interactive command list
- **`GET /health`** - Health check endpoint
- **`GET /api/stats`** - JSON statistics API

### 🔗 Tabbycat Integration

The bot integrates with Tabbycat API endpoints:
- Tournaments, institutions, teams, speakers
- Adjudicators, rounds, motions, pairings
- Feedback, check-in/check-out functionality

### 🔐 Authentication

```python
# Tabbycat API Authentication
headers = {
    "Authorization": f"Token {api_token}",
    "Content-Type": "application/json"
}
```

### 📝 Database Schema

```json
{
  "tournaments": {
    "_id": "guild_id",
    "tournament": "tournament_url",
    "token": "api_token",
    "name": "tournament_name",
    "teams": [...],
    "adjudicators": [...],
    "rounds": [...]
  },
  "timers": {
    "_id": "timer_id",
    "guild_id": "guild_id",
    "channel_id": "channel_id",
    "duration": 480,
    "timer_type": "speech",
    "status": "running"
  }
}
```

---

## 🚀 Deployment

### 🐳 Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "main.py"]
```

### ☁️ Cloud Platforms

#### Heroku
```bash
heroku create your-bot-name
heroku config:set DISCORD_TOKEN=your_token
git push heroku main
```

#### Railway
```bash
railway login
railway init
railway up
```

### 🔧 Production Configuration

- Use environment variables for secrets
- Enable MongoDB authentication
- Configure firewall rules
- Set up SSL/TLS certificates
- Enable comprehensive logging
- Implement backup procedures

---

## 🆘 Troubleshooting

### Common Issues

#### **Bot Not Responding**
1. Verify Discord token validity
2. Check bot permissions in server
3. Confirm database connectivity
4. Review bot status in Discord Developer Portal

#### **Commands Not Working**
1. Ensure user has required permissions
2. Verify command prefix setting
3. Check for typing errors in commands
4. Try slash command alternatives

#### **Tabbycat Sync Failing**
1. Verify API token permissions
2. Check Tabbycat URL format (include https://)
3. Ensure network connectivity to Tabbycat instance
4. Review Tabbycat API rate limits

#### **Timer Issues**
1. Confirm user has Adjudicator role
2. Check channel permissions for bot
3. Verify no conflicting timers running
4. Review timer type spelling

#### **Database Connection Problems**
1. Verify MongoDB connection string
2. Check database server status
3. Confirm network connectivity
4. Review authentication credentials

### Debugging Tips

1. **Enable Debug Logging**: Set `LOG_LEVEL=DEBUG` in environment
2. **Check Bot Logs**: Use `.logs` command or review log files
3. **Test Permissions**: Use Discord's permission calculator
4. **Verify Configuration**: Double-check all environment variables
5. **Monitor Resources**: Check memory and CPU usage

---

## 📞 Support & Contact

- **Developer**: aldinn
- **Email**: kferdoush617@gmail.com
- **GitHub**: https://github.com/Taraldinn/hear-hear-bot
- **Documentation**: Available at `/docs` endpoint

---

## 📝 License & Credits

Built with ❤️ by aldinn for the debate community.

**Technologies Used:**
- Discord.py - Discord API wrapper
- MongoDB - Database storage
- aiohttp - Async web framework
- Jinja2 - Template engine
- Tabbycat - Tournament management integration

---

*Last Updated: September 2025*
*Version: 2.0 - Complete Integration Edition*