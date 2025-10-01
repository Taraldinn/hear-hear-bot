# 🚀 Production Deployment Guide

## Overview

This guide will help you deploy Hear! Hear! Bot to production with the proper environment configuration.

---

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ Discord Bot Token (from Discord Developer Portal)
- ✅ Discord Application ID
- ✅ PostgreSQL Database (Neon, Supabase, Railway, etc.)
- ✅ Python 3.8+ installed
- ✅ Git repository access

---

## 🔐 Environment Configuration

### Step 1: Copy Production Template

```bash
# Copy the production template
cp .env.production .env

# Or for specific environments
cp .env.production .env.production.local
```

### Step 2: Configure Required Variables

Open `.env` and set these **REQUIRED** variables:

```bash
# Discord Configuration
DISCORD_BOT_TOKEN=MTxxxxxx.xxxxxx.xxxxxxxxxxxx
BOT_ID=1234567890123456789

# Database Configuration
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

### Step 3: Configure Optional Variables

Set these based on your needs:

```bash
# Top.gg Integration (recommended)
TOPGG_TOKEN=your_topgg_token_here

# Google Sheets (if using motion sync)
MOTIONS_CSV_URL_ENGLISH=https://docs.google.com/spreadsheets/...

# Tabbycat Integration (if using tournaments)
TABBYCAT_URL=https://your-tabby.com
TABBYCAT_API_KEY=your_api_key
```

---

## 🌐 Deployment Platforms

### Option 1: Heroku

#### Setup

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-bot-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set DISCORD_BOT_TOKEN=your_token
heroku config:set BOT_ID=your_bot_id

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

#### Procfile (already exists)
```
web: python main.py
```

### Option 2: Railway

#### Setup

1. **Connect Repository**
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub"
   - Select your repository

2. **Add PostgreSQL**
   - Click "New" → "Database" → "PostgreSQL"
   - Copy the connection string

3. **Configure Environment**
   - Go to "Variables" tab
   - Add all required variables from `.env.production`
   - Paste PostgreSQL URL as `DATABASE_URL`

4. **Deploy**
   - Railway automatically deploys on push
   - Check "Deployments" tab for status

### Option 3: Render

#### Setup

1. **Create Web Service**
   - Go to https://render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   ```
   Name: hear-hear-bot
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   ```

3. **Add PostgreSQL**
   - Click "New" → "PostgreSQL"
   - Copy connection string

4. **Set Environment Variables**
   - Add all required variables
   - Use the PostgreSQL connection string

### Option 4: DigitalOcean App Platform

#### Setup

```bash
# Install doctl CLI
brew install doctl  # macOS
# or download from: https://docs.digitalocean.com/reference/doctl/

# Login
doctl auth init

# Create app spec (app.yaml)
# Then deploy
doctl apps create --spec app.yaml
```

### Option 5: VPS (Ubuntu/Debian)

#### Setup

```bash
# SSH into your server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip -y

# Install PostgreSQL client
sudo apt install postgresql-client -y

# Clone repository
git clone https://github.com/yourusername/hear-hear-bot.git
cd hear-hear-bot

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
nano .env
# Paste your configuration

# Test run
python main.py

# Setup systemd service (see below)
```

#### Systemd Service (VPS)

Create `/etc/systemd/system/hear-hear-bot.service`:

```ini
[Unit]
Description=Hear! Hear! Discord Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/hear-hear-bot
Environment="PATH=/home/your-username/hear-hear-bot/venv/bin"
ExecStart=/home/your-username/hear-hear-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hear-hear-bot
sudo systemctl start hear-hear-bot
sudo systemctl status hear-hear-bot
```

### Option 6: Docker

#### Dockerfile (create if needed)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run bot
CMD ["python", "main.py"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  bot:
    build: .
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      - db
    
  db:
    image: postgres:14-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: hearbot
      POSTGRES_USER: hearbot
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Deploy:

```bash
docker-compose up -d
docker-compose logs -f bot
```

---

## 🗄️ Database Setup

### Option 1: Neon (Recommended - Serverless)

1. Go to https://neon.tech
2. Sign up and create a project
3. Create a database
4. Copy the connection string
5. Add to `.env` as `DATABASE_URL`

**Example:**
```
DATABASE_URL=postgresql://user:pass@ep-example-123456.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### Option 2: Supabase

1. Go to https://supabase.com
2. Create a new project
3. Go to Settings → Database
4. Copy the connection string (URI format)
5. Add to `.env` as `DATABASE_URL`

### Option 3: Railway PostgreSQL

1. In Railway dashboard, click "New" → "Database"
2. Select "PostgreSQL"
3. Copy the `DATABASE_URL` from variables
4. Add to your bot's environment variables

### Option 4: Self-Hosted PostgreSQL

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE hearbot;
CREATE USER hearbot WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hearbot TO hearbot;
\q

# Connection string
DATABASE_URL=postgresql://hearbot:your_password@localhost:5432/hearbot
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] All sensitive credentials in `.env` file
- [ ] `.env` is in `.gitignore`
- [ ] Database has SSL enabled (`sslmode=require`)
- [ ] Bot token is valid and not exposed
- [ ] Owner IDs are configured
- [ ] Admin roles are properly named
- [ ] Rate limiting is enabled
- [ ] Error logging is configured
- [ ] Backup system is in place (optional)

---

## 🧪 Testing Before Production

```bash
# 1. Test configuration
python check_config.py

# 2. Test database connection
python -c "from src.database.connection import DatabaseManager; import asyncio; asyncio.run(DatabaseManager.initialize())"

# 3. Dry run
python main.py

# 4. Check logs
tail -f logs/bot.log

# 5. Test commands in Discord
# Send: /help
# Send: /ping
# Send: /stats bot
```

---

## 📊 Monitoring & Maintenance

### Log Management

```bash
# View logs
tail -f logs/bot.log

# Rotate logs (add to crontab)
0 0 * * * find /path/to/logs -name "*.log" -mtime +7 -delete
```

### Health Checks

The bot provides these endpoints:

```bash
# Health check
curl http://localhost:8080/health

# Bot stats
curl http://localhost:8080/api/stats

# Homepage
curl http://localhost:8080/
```

### Uptime Monitoring

Use these services to monitor your bot:

- **UptimeRobot** (https://uptimerobot.com)
- **StatusCake** (https://www.statuscake.com)
- **Pingdom** (https://www.pingdom.com)

Configure HTTP checks on:
- `http://your-bot-url/health`

### Error Tracking

Configure Sentry for error tracking:

```bash
# In .env
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

---

## 🔄 Updates & Deployment

### Update Process

```bash
# 1. Pull latest changes
git pull origin main

# 2. Update dependencies
pip install -r requirements.txt --upgrade

# 3. Run migrations (if any)
# python migrate.py

# 4. Restart bot
# Heroku: git push heroku main
# Railway: git push (auto-deploys)
# VPS: sudo systemctl restart hear-hear-bot
# Docker: docker-compose restart bot
```

### Rollback

```bash
# Heroku
heroku releases
heroku rollback v123

# Railway
# Use Railway dashboard → Deployments → Redeploy previous

# VPS/Docker
git checkout previous-commit
sudo systemctl restart hear-hear-bot
```

---

## 🚨 Troubleshooting

### Bot Not Starting

```bash
# Check logs
heroku logs --tail  # Heroku
railway logs        # Railway
sudo journalctl -u hear-hear-bot -f  # VPS

# Common issues:
# - Invalid bot token
# - Database connection failed
# - Missing dependencies
```

### Database Connection Issues

```bash
# Test connection
python -c "
import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect('YOUR_DATABASE_URL')
    print('Connected!')
    await conn.close()

asyncio.run(test())
"
```

### Port Issues

```bash
# Check if port is in use
lsof -i :8080  # Linux/Mac
netstat -ano | findstr :8080  # Windows

# Kill process
kill -9 PID  # Linux/Mac
taskkill /PID PID /F  # Windows
```

---

## 📈 Scaling

### Horizontal Scaling

For high-traffic bots:

1. **Add Redis for Caching**
   ```bash
   REDIS_URL=redis://username:password@host:port
   ```

2. **Use Multiple Workers** (Railway/Render)
   - Configure in dashboard
   - Set min/max instances

3. **Implement Rate Limiting**
   ```python
   # Already configured in .env
   RATE_LIMIT_PER_USER=5
   RATE_LIMIT_WINDOW=60
   ```

### Vertical Scaling

Increase resources:
- Heroku: Upgrade dyno size
- Railway: Adjust memory/CPU in settings
- VPS: Upgrade instance size

---

## 📝 Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_BOT_TOKEN` | Discord bot token | `MTxxxxx.xxxxx.xxxxx` |
| `BOT_ID` | Discord application ID | `123456789012345678` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TOPGG_TOKEN` | Top.gg API token | Empty (disabled) |
| `BOT_NAME` | Bot display name | `Hear! Hear! Bot` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `WEB_SERVER_PORT` | Web server port | `8080` |

See `.env.production` for complete list.

---

## 🎯 Production Checklist

Before going live:

- [ ] Environment variables configured
- [ ] Database created and accessible
- [ ] Bot invited to test server
- [ ] All commands tested
- [ ] Web server accessible
- [ ] Logging working
- [ ] Error handling tested
- [ ] Rate limiting enabled
- [ ] Health checks configured
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Documentation updated

---

## 📞 Support

If you need help with deployment:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review logs for error messages
3. Verify environment variables
4. Test database connection
5. Check Discord bot permissions

---

## 🎉 Success!

Once deployed, your bot should be:

- ✅ Online and responding to commands
- ✅ Accessible via web interface
- ✅ Posting stats to Top.gg (if configured)
- ✅ Logging events properly
- ✅ Auto-restarting on errors

**Your production deployment is complete!** 🚀

---

**Last Updated:** October 2, 2025  
**Version:** 2.1.0
