# 🎤 Hear! Hear! - The Ultimate Discord Debate Bot

<div align="center">

![Hear! Hear! Bot Logo](https://img.shields.io/badge/Hear!_Hear!-Discord_Bot-5865F2?style=for-the-badge&logo=discord&logoColor=white)

**The most comprehensive Discord bot for debate tournaments and communities**

[![Version](https://img.shields.io/badge/version-2.1.0-blue?style=flat-square)](https://github.com/Taraldinn/hear-hear-bot)
[![Python](https://img.shields.io/badge/python-3.8+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.4.0+-blue?style=flat-square)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success?style=flat-square)](https://github.com/Taraldinn/hear-hear-bot)

[Add to Discord](https://discord.com/api/oauth2/authorize?client_id=1401966904578408539&permissions=8&scope=bot%20applications.commands) • [Documentation](USER_GUIDE.md) • [Support Server](#support) • [Report Bug](https://github.com/Taraldinn/hear-hear-bot/issues)

</div>

---

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

---

## 🎯 About

**Hear! Hear!** is a comprehensive Discord bot specifically designed for debate tournaments and communities. Whether you're organizing parliamentary debates, British Parliamentary (BP) tournaments, or running a debate society, Hear! Hear! provides all the essential tools in one powerful package.

### Why Hear! Hear!?

- 🎯 **Purpose-Built** - Specifically designed for debate communities
- ⚡ **Modern Technology** - Built with Python 3.8+ and discord.py 2.4+
- 🎨 **Beautiful UI** - Intuitive slash commands with rich embeds
- 🏆 **Tournament Ready** - Full Tabbycat integration
- 🌍 **Multi-Language** - Support for English and Bangla motions
- 📊 **Reliable** - 99.9% uptime with automatic error recovery
- 🔒 **Secure** - Modern security practices and data protection
- 📈 **Active Development** - Regular updates and new features

### Key Statistics

- 🌟 **1000+** Debate motions in database
- ⚡ **<50ms** Average response time
- 🏆 **Multiple** Tournament formats supported
- 👥 **Active** Community-driven development

---

## ✨ Features

### 🕐 Professional Debate Timer

The most advanced debate timing system for Discord:

- ✅ **Multiple Formats** - BP, WSDC, NA, Custom
- ✅ **Visual Countdown** - Real-time countdown displays
- ✅ **Protected Time** - Clear indicators for protected speaking time
- ✅ **Pause/Resume** - Full timer control
- ✅ **Speaker Tracking** - Individual speaker time tracking
- ✅ **Audio Alerts** - Optional sound notifications
- ✅ **Auto-Reset** - Automatic reset after completion

**Perfect for:**
- Parliamentary debates
- Practice sessions
- Competition rounds
- Speaking drills
- Training exercises

### 📋 Comprehensive Motion Database

Access thousands of debate motions instantly:

- ✅ **1000+ Motions** - Extensive database
- ✅ **Keyword Search** - Find specific topics quickly
- ✅ **Category Filters** - Browse by theme
- ✅ **Difficulty Levels** - Easy, Medium, Hard
- ✅ **Multi-Language** - English and Bangla
- ✅ **Infoslides** - Contextual information included
- ✅ **Google Sheets Integration** - Easy updates

**Languages Supported:**
- 🇬🇧 English motions
- 🇧🇩 Bangla motions
- 🌍 Combined database

### 🏆 Tournament Management

Full-featured tournament administration:

- ✅ **Tabbycat Integration** - Direct API connection
- ✅ **Auto Role Creation** - Automatic role assignment
- ✅ **Channel Setup** - Organized tournament channels
- ✅ **Pairing Announcements** - Automated pairing posts
- ✅ **Results Submission** - Quick result reporting
- ✅ **Standings** - Real-time rankings
- ✅ **Venue Management** - Room organization

**Tournament Features:**
- Fetch pairings
- Submit results
- View standings
- Check schedules
- Manage venues
- Track progress

### 🛡️ Moderation & Utilities

Keep your server organized:

- ✅ **Role Management** - Automated role assignment
- ✅ **Channel Organization** - Structured channels
- ✅ **Automated Cleanup** - Maintenance tools
- ✅ **Welcome Messages** - Customizable greetings
- ✅ **Server Statistics** - Detailed analytics
- ✅ **User Information** - Member details
- ✅ **Bot Health Checks** - Status monitoring

### 📊 Statistics & Analytics

Track your bot usage:

- ✅ **Server Count** - Monitor growth
- ✅ **Uptime Tracking** - Reliability metrics
- ✅ **Response Time** - Performance monitoring
- ✅ **Command Usage** - Activity statistics
- ✅ **Memory Usage** - Resource tracking
- ✅ **Top.gg Integration** - Bot list statistics

---

## 🚀 Quick Start

### For Server Owners

1. **Invite the Bot**

   Click this link to add Hear! Hear! to your server:
   
   👉 [Add to Discord](https://discord.com/api/oauth2/authorize?client_id=1401966904578408539&permissions=8&scope=bot%20applications.commands)

2. **Grant Permissions**

   The bot needs these permissions:
   - Send Messages
   - Embed Links
   - Use Slash Commands
   - Manage Roles (for tournaments)
   - Manage Channels (for tournaments)

3. **Start Using Commands**

   Type `/` in any channel to see available commands:
   ```
   /help              # View all commands
   /timer start BP    # Start a debate timer
   /motion random     # Get a random motion
   /stats bot         # View bot statistics
   ```

### For Self-Hosting

See [Installation](#installation) section below.

---

## 📖 Commands

### Essential Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show all available commands | `/help timer` |
| `/timer start` | Start a debate timer | `/timer start BP` |
| `/motion random` | Get a random debate motion | `/motion random English` |
| `/motion search` | Search for specific motions | `/motion search climate` |
| `/stats bot` | View bot statistics | `/stats bot` |
| `/ping` | Check bot latency | `/ping` |

### Tournament Commands

| Command | Description | Requires |
|---------|-------------|----------|
| `/tournament setup` | Create tournament structure | Admin |
| `/tournament pairings` | Fetch round pairings | Admin |
| `/tournament results` | Submit results | Judge Role |
| `/tournament standings` | View current standings | Anyone |

### Admin Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/config set` | Configure bot settings | Admin |
| `/config view` | View current configuration | Admin |
| `/topgg status` | Check Top.gg integration | Admin |
| `/topgg post` | Manually post stats | Admin |

For a complete command reference, see [USER_GUIDE.md](USER_GUIDE.md).

---

## 💻 Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Discord Bot Token
- Git

### Setup Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Taraldinn/hear-hear-bot.git
   cd hear-hear-bot
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**

   Copy `.env.example` to `.env.local`:
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` with your credentials:
   ```env
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   BOT_ID=your_bot_application_id_here
   DATABASE_URL=your_postgresql_database_url_here
   TOPGG_TOKEN=your_topgg_api_token_here
   ```

4. **Verify Configuration**

   ```bash
   python check_config.py
   ```

5. **Start the Bot**

   ```bash
   python main.py
   ```

### Docker Installation

Coming soon! Docker support is planned for future releases.

---

## ⚙️ Configuration

### Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_BOT_TOKEN` | Your Discord bot token | Yes |
| `BOT_ID` | Discord application ID | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TOPGG_TOKEN` | Top.gg API token | None |
| `BOT_INVITE_URL` | Custom invite URL | Auto-generated |
| `MOTIONS_CSV_URL_ENGLISH` | Google Sheets URL for motions | None |
| `TABBYCAT_API_KEY` | Tabbycat API key | None |
| `LOG_LEVEL` | Logging level | INFO |
| `WEB_SERVER_PORT` | Web server port | 8080 |

### Configuration Files

- `.env.local` - Local environment variables (not committed)
- `.env` - Template with defaults
- `config/settings.py` - Application configuration
- `permissions.json` - Role permissions

For detailed configuration, see [Configuration Guide](docs/CONFIGURATION.md).

---

## 💡 Usage Examples

### Example 1: Running a Practice Debate

```python
# 1. Get a motion
/motion random English Medium

# 2. Start timer with prep time
/timer start BP 15

# 3. During debate
- Monitor protected time indicators
- Use pause/resume as needed
- Track individual speaker times

# 4. After debate
- Timer auto-resets
- Request another motion
```

### Example 2: Managing a Tournament

```python
# 1. Initial setup
/tournament setup

# 2. Announce pairings
/tournament pairings 1

# 3. Submit results
/tournament results R1 OG

# 4. Check standings
/tournament standings
```

### Example 3: Server Configuration

```python
# Set language preference
/config set language English

# Set timer format
/config set timer_format BP

# Set announcement channel
/config set announcement_channel #announcements

# View current config
/config view
```

For more examples, see [USER_GUIDE.md](USER_GUIDE.md#usage-examples).

---

## 🛠️ Development

### Project Structure

```
hear-hear-bot/
├── src/
│   ├── bot/           # Bot client and core logic
│   ├── commands/      # Command implementations
│   ├── events/        # Event handlers
│   ├── utils/         # Utility functions
│   └── database/      # Database models
├── config/            # Configuration files
├── web/               # Web server
│   ├── templates/     # HTML templates
│   └── static/        # Static assets
├── data/              # Motion databases
├── logs/              # Log files
└── docs/              # Documentation

```

### Tech Stack

- **Language:** Python 3.8+
- **Framework:** discord.py 2.4+
- **Database:** PostgreSQL with asyncpg
- **Web Server:** aiohttp
- **Templates:** Jinja2
- **Styling:** Tailwind CSS

### Development Setup

1. **Fork the Repository**

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dev Dependencies**
   ```bash
   pip install -r requirements/dev.txt
   ```

4. **Run Tests**
   ```bash
   python -m pytest tests/
   ```

5. **Code Quality**
   ```bash
   # Linting
   pylint src/
   
   # Type checking
   mypy src/
   
   # Formatting
   black src/
   ```

### Testing

```bash
# Run all tests
python test_topgg.py

# Check configuration
python check_config.py

# Run specific tests
python -m pytest tests/test_timer.py
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

- 🐛 **Report Bugs** - Create detailed issue reports
- 💡 **Suggest Features** - Share your ideas
- 📝 **Improve Documentation** - Help others understand
- 💻 **Submit Code** - Fix bugs or add features
- 🌍 **Translate** - Add language support
- 🎨 **Design** - Improve UI/UX

### Contribution Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Add docstrings to functions
- Write unit tests for new features
- Update documentation as needed
- Keep commits atomic and descriptive

For detailed guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📞 Support

### Need Help?

- 📚 **Documentation** - [USER_GUIDE.md](USER_GUIDE.md)
- 💬 **Discord Server** - [Join our community](#)
- 🐛 **Bug Reports** - [GitHub Issues](https://github.com/Taraldinn/hear-hear-bot/issues)
- 📧 **Email** - kferdoush617@gmail.com

### Community

- Star ⭐ this repository to show support
- Follow for updates and announcements
- Share with debate communities
- Join our Discord for discussions

---

## 📊 Project Status

### Current Status: **Active Development** 🟢

- ✅ Core features complete
- ✅ Production ready
- ✅ Regular updates
- ✅ Community-driven

### Roadmap

#### Version 2.2.0 (Planned)
- [ ] Advanced analytics dashboard
- [ ] Custom motion categories
- [ ] Multi-tournament support
- [ ] Enhanced role management
- [ ] Webhook integrations

#### Version 3.0.0 (Future)
- [ ] Web dashboard
- [ ] Mobile app
- [ ] AI-powered features
- [ ] Advanced tournament analytics

### Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

## 🏆 Acknowledgments

### Special Thanks

- **Debate Community** - For invaluable feedback
- **Discord.py Team** - For the amazing library
- **Tabbycat Developers** - For tournament software
- **Contributors** - For code and suggestions
- **Users** - For choosing Hear! Hear!

### Built With

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [aiohttp](https://github.com/aio-libs/aiohttp) - Async HTTP
- [asyncpg](https://github.com/MagicStack/asyncpg) - PostgreSQL driver
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [PostgreSQL](https://www.postgresql.org/) - Database

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 aldinn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🔗 Links

### Official Links
- [Add to Discord](https://discord.com/api/oauth2/authorize?client_id=1401966904578408539&permissions=8&scope=bot%20applications.commands)
- [GitHub Repository](https://github.com/Taraldinn/hear-hear-bot)
- [Documentation](USER_GUIDE.md)
- [Top.gg Page](#)

### Resources
- [Discord.py Docs](https://discordpy.readthedocs.io/)
- [Tabbycat](https://tabbycat-debate.readthedocs.io/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

## 📈 SEO & Keywords

**Primary Keywords:**
- Discord debate bot
- Debate timer Discord
- Tournament management bot
- Parliamentary debate bot
- Tabbycat Discord integration

**Secondary Keywords:**
- British Parliamentary bot
- Debate motion database
- Discord timer bot
- Tournament organization bot
- Debate practice bot
- Motion search bot
- Debate tournament software
- Discord debate tools

**Long-tail Keywords:**
- How to use debate bot Discord
- Best Discord bot for debate tournaments
- Parliamentary debate timer Discord
- Tabbycat integration Discord bot
- Free debate bot for Discord servers

---

<div align="center">

**Made with ❤️ for the debate community**

[![GitHub stars](https://img.shields.io/github/stars/Taraldinn/hear-hear-bot?style=social)](https://github.com/Taraldinn/hear-hear-bot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Taraldinn/hear-hear-bot?style=social)](https://github.com/Taraldinn/hear-hear-bot/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/Taraldinn/hear-hear-bot?style=social)](https://github.com/Taraldinn/hear-hear-bot/watchers)

*Last Updated: October 2, 2025*

[⬆ Back to Top](#-hear-hear---the-ultimate-discord-debate-bot)

</div>
