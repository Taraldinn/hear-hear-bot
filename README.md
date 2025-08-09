# 🎤 Hear! Hear! Bot

A comprehensive Discord bot for debate tournaments, featuring debate timing, motion generation, Tabbycat integration, and tournament management tools.

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
- `.sync <url> <token>` - Connect server to Tabbycat tournament
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
