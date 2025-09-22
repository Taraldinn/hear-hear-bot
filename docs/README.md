# 📚 Hear! Hear! Bot Documentation

Welcome to the comprehensive documentation for Hear! Hear! Bot - a production-ready Discord bot for debate tournaments and discussion management.

## 📖 Quick Start

- **[Quick Start Guide](QUICK_START.md)** - Get the bot running in 5 minutes
- **[Quick Reference](QUICK_REFERENCE.md)** - Essential commands and features

## 🚀 Deployment

### Production Deployment
- **[Production Checklist](deployment/PRODUCTION_CHECKLIST.md)** - Complete production deployment guide
- **[Simple Deployment](deployment/SIMPLE_DEPLOYMENT.md)** - Streamlined deployment for smaller setups
- **[Global Deployment](deployment/GLOBAL_DEPLOYMENT.md)** - Advanced global deployment strategies

### Deployment Scripts
- **[Deploy Script](deployment/deploy.sh)** - Full production deployment automation
- **[Simple Deploy](deployment/deploy_simple.sh)** - Basic deployment script
- **[Systemd Service](deployment/hearhear-bot.service)** - Linux service configuration
- **[PostgreSQL Migration](deployment/POSTGRESQL_MIGRATION.md)** - Database migration guide

## 🛠️ Development

- **[Complete Documentation](development/COMPLETE_DOCUMENTATION.md)** - Comprehensive technical documentation
- **[Setup Guide](development/SETUP.md)** - Development environment setup
- **[Legacy README](development/README_legacy.md)** - Historical project documentation

## ✨ Features

### Core Features
- **[Commands Reference](features/COMMANDS.md)** - All available bot commands
- **[Slash Commands](features/SLASH_COMMANDS_COMPLETE.md)** - Modern Discord slash commands
- **[Tournament Management](features/TOURNAMENT.md)** - Tournament and competition features

### Advanced Features
- **[Timer System](features/TIMER_RESTORATION_COMPLETE.md)** - Debate timing functionality
- **[Google Sheets Integration](features/MOTIONS_FROM_GOOGLE_SHEETS.md)** - Motion management via Google Sheets
- **[Carl Bot Features](features/CARL_BOT_FEATURES.md)** - Additional moderation capabilities

## 🔧 Troubleshooting

- **[Permission Issues](troubleshooting/PERMISSION_FIX_GUIDE.md)** - Fix Discord permission problems
- **[MongoDB SSL Issues](troubleshooting/MONGODB_SSL_TROUBLESHOOTING.md)** - Resolve database connection problems
- **[PostgreSQL Migration](deployment/POSTGRESQL_MIGRATION.md)** - Migrate from MongoDB to PostgreSQL

## 📁 Project Structure

```
hear-hear-bot/
├── src/                     # Main source code
│   ├── bot/                 # Bot client and core functionality
│   ├── commands/            # Discord commands and interactions
│   ├── database/            # Database models and connections
│   ├── events/              # Discord event handlers
│   └── utils/               # Utility functions and helpers
├── config/                  # Configuration management
├── web/                     # Web interface (optional)
├── docs/                    # All documentation (you are here!)
│   ├── deployment/          # Deployment guides and scripts
│   ├── development/         # Development resources
│   ├── features/            # Feature documentation
│   └── troubleshooting/     # Problem-solving guides
├── assets/                  # Images and static files
├── data/                    # Data files (languages, etc.)
├── legacy/                  # Archived legacy code
└── logs/                    # Application logs
```

## 🎯 Getting Started Paths

### For Server Administrators
1. **[Quick Start Guide](QUICK_START.md)** - Basic setup
2. **[Commands Reference](features/COMMANDS.md)** - Learn available commands
3. **[Permission Guide](troubleshooting/PERMISSION_FIX_GUIDE.md)** - Set up permissions

### For Tournament Organizers
1. **[Tournament Features](features/TOURNAMENT.md)** - Tournament management
2. **[Timer System](features/TIMER_RESTORATION_COMPLETE.md)** - Debate timing
3. **[Google Sheets Integration](features/MOTIONS_FROM_GOOGLE_SHEETS.md)** - Motion management

### For Developers
1. **[Development Setup](development/SETUP.md)** - Environment setup
2. **[Complete Documentation](development/COMPLETE_DOCUMENTATION.md)** - Technical details
3. **[Production Deployment](deployment/PRODUCTION_CHECKLIST.md)** - Deploy to production

### For System Administrators
1. **[Production Checklist](deployment/PRODUCTION_CHECKLIST.md)** - Production deployment
2. **[Troubleshooting](troubleshooting/)** - Common issues and solutions
3. **[MongoDB SSL Guide](troubleshooting/MONGODB_SSL_TROUBLESHOOTING.md)** - Database setup

## 🆘 Support

- **Issues**: Report bugs on [GitHub Issues](https://github.com/Taraldinn/hear-hear-bot/issues)
- **Discussions**: Join discussions on [GitHub Discussions](https://github.com/Taraldinn/hear-hear-bot/discussions)
- **Email**: Contact the author at kferdoush617@gmail.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Last Updated**: September 23, 2025  
**Bot Version**: Latest  
**Maintained by**: [aldinn](https://github.com/Taraldinn)