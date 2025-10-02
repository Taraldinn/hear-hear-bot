# 🎙️ AldinnBot (Hear! Hear! Bot)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.4%2B-blue.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)

A comprehensive, production-ready Discord bot designed for debate tournaments and discussion management. Built with modern Python, featuring robust error handling, comprehensive logging, and scalable architecture.

> 📚 **[View Complete Documentation](./docs/INDEX.md)** | [Quick Start](./docs/QUICK_START.md) | [User Guide](./docs/guides/USER_GUIDE.md)

## ✨ Features

### 🏆 Tournament Management
- **Role Assignment**: Automated role assignment with UI-based selection
- **Channel Permissions**: Dynamic permission management based on tournament roles
- **Tabbycat Integration**: Seamless integration with Tabbycat tournament software
- **Tournament Data Sync**: Real-time synchronization with tournament databases

### ⏱️ Timer System
- **Debate Timers**: Precise timing for debate rounds with audio alerts
- **Multiple Timer Types**: Prep time, speech time, and custom timers
- **Visual Indicators**: Real-time countdown displays with progress bars
- **Timer Restoration**: Automatic timer state recovery after bot restarts

### 🗳️ Debate Features
- **Motion Management**: Automated motion distribution from Google Sheets
- **Multi-language Support**: English and Bengali motion support
- **Random Motion Selection**: Fair and random motion assignment
- **Motion History**: Track and avoid motion repetition

### 🔧 Admin Tools
- **Comprehensive Logging**: Detailed logging with file rotation
- **Error Handling**: Robust error recovery and reporting
- **Health Monitoring**: Real-time bot health and performance metrics
- **Database Management**: PostgreSQL integration with connection pooling and async support

### 🌐 Web Interface
- **Documentation Portal**: Comprehensive web-based documentation
- **Bot Statistics**: Real-time performance metrics and statistics
- **Health Dashboard**: System status and monitoring interface
- **API Endpoints**: RESTful API for external integrations

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL (local or cloud)
- Discord Bot Token
- Docker (optional, for containerized deployment)

### Installation

#### Option 1: Simple Deployment (Recommended)
```bash
# Clone the repository
git clone https://github.com/Taraldinn/hear-hear-bot.git
cd hear-hear-bot

# Run automated deployment
./deploy_simple.sh deploy

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Start the bot
./deploy_simple.sh start
```

#### Option 2: Manual Installation
```bash
# Clone the repository
git clone https://github.com/Taraldinn/hear-hear-bot.git
cd hear-hear-bot

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run the bot
python main.py
```

#### Option 3: Docker Deployment
```bash
# Clone the repository
git clone https://github.com/Taraldinn/hear-hear-bot.git
cd hear-hear-bot

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f bot
```

### Configuration

Create a `.env` file based on `.env.example` and configure the following:

```bash
# Required
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Recommended
# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://username:password@host:port/database

# Alternative: Individual PostgreSQL settings
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hearhearbot
POSTGRES_USER=botuser
POSTGRES_PASSWORD=your_password_here

# Optional
TEST_GUILD_ID=your_test_guild_id_here
TOPGG_TOKEN=your_topgg_token_here
```

## 📖 Documentation

> 📚 **Complete documentation is now organized in the [`docs/`](./docs/) folder**

### Quick Links

#### 🚀 Getting Started
- **[Quick Start Guide](./docs/QUICK_START.md)** - Get up and running in 5 minutes
- **[Quick Reference](./docs/QUICK_REFERENCE.md)** - Command reference card
- **[User Guide](./docs/guides/USER_GUIDE.md)** - Complete user manual

#### 🎨 Design & UI
- **[Web Redesign](./docs/design/WEB_REDESIGN_SUMMARY.md)** - Modern Shadcn UI theme
- **[Design System](./docs/design/SHADCN_UI_REDESIGN.md)** - Complete design documentation
- **[Visual Reference](./docs/design/SHADCN_VISUAL_REFERENCE.md)** - Color system and components

#### 🚀 Deployment
- **[Deployment Guide](./docs/deployment/DEPLOYMENT_GUIDE.md)** - Platform-specific guides
- **[Deployment Checklist](./docs/deployment/DEPLOYMENT_CHECKLIST.md)** - Pre-deployment checklist
- **[Environment Setup](./docs/deployment/ENVIRONMENT_VERIFICATION.md)** - Configuration verification

#### 🔌 Integrations
- **[Top.gg Integration](./docs/integrations/TOPGG_INTEGRATION.md)** - Bot listing integration
- **[Database Setup](./docs/database/DATABASE_FIX_SUMMARY.md)** - Database configuration

#### ⚙️ Features
- **[Commands](./docs/features/COMMANDS.md)** - All available commands
- **[Timer System](./docs/features/TIMER_RESTORATION_COMPLETE.md)** - Advanced timing features
- **[Tournament Management](./docs/features/TOURNAMENT.md)** - Tournament organization

#### 🛠️ Development
- **[Development Setup](./docs/development/SETUP.md)** - Dev environment setup
- **[Complete Docs](./docs/development/COMPLETE_DOCUMENTATION.md)** - Full technical documentation

#### ❗ Troubleshooting
- **[Common Issues](./docs/troubleshooting/)** - Solutions to common problems
- **[Permission Guide](./docs/troubleshooting/PERMISSION_FIX_GUIDE.md)** - Permission fixes

### 📑 Full Documentation Index
**→ [View Complete Documentation Index](./docs/INDEX.md)**

---

## 📖 Command Reference

#### Slash Commands
- `/timer` - Start debate timers with various presets
- `/randommotion` - Get random debate motions
- `/help` - Display help information
- `/ping` - Check bot latency and status

#### Admin Commands
- `/sync` - Synchronize slash commands
- `/reload` - Reload bot extensions
- `/stats` - View bot statistics

### Web Interface

Access the web interface at `http://localhost:8080` (or your configured port):

- **Documentation**: `/docs` - Complete feature documentation
- **Health Check**: `/` - Bot status and health
- **Statistics**: `/stats` - Performance metrics

## 🏗️ Architecture

### Project Structure
```
hear-hear-bot/
├── main.py                 # Application entry point
├── config/
│   └── settings.py         # Configuration management
├── src/
│   ├── bot/
│   │   └── client.py       # Enhanced bot client
│   ├── commands/           # Command modules
│   ├── database/           # Database management
│   ├── events/            # Event handlers
│   └── utils/             # Utility functions
├── web/
│   ├── server.py          # Web server
│   └── templates/         # HTML templates
├── logs/                  # Application logs
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-service deployment
└── requirements.txt       # Python dependencies
```

### Key Components

- **Enhanced Bot Client**: Production-ready Discord bot with auto-sharding
- **Database Manager**: Robust PostgreSQL integration with async connection pooling
- **Web Server**: aiohttp-based web interface with comprehensive documentation
- **Logging System**: Multi-level logging with file rotation
- **Error Handling**: Comprehensive error recovery and reporting

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/Taraldinn/hear-hear-bot.git
cd hear-hear-bot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Set up pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and start services
docker-compose up -d --build

# Scale bot instances
docker-compose up -d --scale bot=2

# View logs
docker-compose logs -f

# Update deployment
docker-compose pull
docker-compose up -d --force-recreate
```

### Development with Docker

Create `docker-compose.override.yml`:

```yaml
version: '3.8'
services:
  bot:
    build:
      target: development
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
    volumes:
      - .:/app
```

## 📊 Monitoring

### Health Checks

- **HTTP Health Check**: `GET /` returns bot status
- **Docker Health Check**: Built-in container health monitoring
- **Database Health**: Automatic connection monitoring and recovery

### Logging

- **Application Logs**: `logs/bot.log`
- **Error Logs**: `logs/errors.log`
- **Web Server Logs**: `logs/web.log`

### Metrics

Access real-time metrics at `/stats`:
- Bot uptime and latency
- Command usage statistics
- Database connection status
- Memory and resource usage

## 🛠️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | ✅ | - | Discord bot token |
| `DATABASE_URL` | ⚠️ | - | PostgreSQL connection URL |
| `POSTGRES_HOST` | ⚠️ | localhost | PostgreSQL host |
| `POSTGRES_PORT` | ⚠️ | 5432 | PostgreSQL port |  
| `POSTGRES_DB` | ⚠️ | hearhearbot | PostgreSQL database name |
| `POSTGRES_USER` | ⚠️ | - | PostgreSQL username |
| `POSTGRES_PASSWORD` | ⚠️ | - | PostgreSQL password |
| `TEST_GUILD_ID` | ❌ | - | Guild ID for instant command testing |
| `PORT` | ❌ | 8080 | Web server port |
| `ENVIRONMENT` | ❌ | production | Environment type |
| `LOG_LEVEL` | ❌ | INFO | Logging level |

### Database Configuration

The bot supports PostgreSQL with automatic connection management:

```env
# Option 1: Full connection URL
DATABASE_URL=postgresql://username:password@host:port/database

# Option 2: Individual settings
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hearhearbot
POSTGRES_USER=botuser
POSTGRES_PASSWORD=your_password
```

**Migration Note**: If migrating from MongoDB, see [PostgreSQL Migration Guide](docs/deployment/POSTGRESQL_MIGRATION.md).

- **Connection Pooling**: Optimized for production workloads
- **Auto-Reconnection**: Automatic recovery from connection failures
- **Health Monitoring**: Continuous connection health checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for changes
- Use type hints where appropriate
- Ensure all tests pass before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**aldinn** - [GitHub](https://github.com/Taraldinn) - kferdoush617@gmail.com

## 🙏 Acknowledgments

- [discord.py](https://discordpy.readthedocs.io/) - Python Discord API wrapper
- [PostgreSQL](https://postgresql.org/) - Relational database with JSON support
- [aiohttp](https://docs.aiohttp.org/) - Async HTTP client/server
- [Tabbycat](https://tabbycat-debate.readthedocs.io/) - Debate tournament software

## 📈 Roadmap

- [ ] Advanced tournament bracket management
- [ ] Real-time notifications for tournament updates
- [ ] Enhanced analytics and reporting
- [ ] Multi-server tournament support
- [ ] Integration with additional tournament platforms
- [ ] Mobile-responsive web interface

---

**Built with ❤️ for the debate community**