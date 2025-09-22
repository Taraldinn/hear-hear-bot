# 🚀 Quick Start Guide

Get your Hear! Hear! Bot running in 5 minutes!

## 1. Download and Setup

```bash
# Clone the bot
git clone https://github.com/Taraldinn/hear-hear-bot.git
cd hear-hear-bot

# Make scripts executable
chmod +x deploy_simple.sh
```

## 2. Deploy

```bash
# Automated setup (creates virtual environment, installs dependencies)
./deploy_simple.sh deploy
```

## 3. Configure

```bash
# Copy the example configuration
cp .env.example .env

# Edit with your bot token
nano .env
```

**Add your Discord bot token:**
```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

## 4. Start

```bash
# Start the bot
./deploy_simple.sh start

# Check if it's running
./deploy_simple.sh status
```

## 5. Access

- **Bot Status**: http://localhost:8080/
- **Documentation**: http://localhost:8080/docs
- **View Logs**: `./deploy_simple.sh logs`

## 🔧 Common Commands

```bash
./deploy_simple.sh start     # Start bot
./deploy_simple.sh stop      # Stop bot
./deploy_simple.sh restart   # Restart bot
./deploy_simple.sh status    # Check status
./deploy_simple.sh logs      # View logs
./deploy_simple.sh update    # Update bot
```

## ❓ Need Help?

- Check [Simple Deployment Guide](SIMPLE_DEPLOYMENT.md) for detailed instructions
- View [Production Checklist](PRODUCTION_CHECKLIST.md) for production setup
- See [Complete Documentation](http://localhost:8080/docs) once running

That's it! Your bot should now be running. 🎉