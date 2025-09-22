# 🚀 Simple Deployment Guide (No Docker)

This guide shows you how to deploy Hear! Hear! Bot without Docker, using a simple Python virtual environment and optional systemd service.

## ⚡ Quick Start

### 1. Prerequisites

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git curl

# CentOS/RHEL/Fedora
sudo yum install python3 python3-pip git curl
# or
sudo dnf install python3 python3-pip git curl

# Check Python version (requires 3.8+)
python3 --version
```

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Taraldinn/hear-hear-bot.git
cd hear-hear-bot

# Make deployment script executable
chmod +x deploy_simple.sh

# Run initial deployment
./deploy_simple.sh deploy
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the configuration (add your bot token)
nano .env
```

**Minimum required configuration:**
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

### 4. Start the Bot

```bash
# Start the bot
./deploy_simple.sh start

# Check if it's running
./deploy_simple.sh status

# View logs
./deploy_simple.sh logs
```

## 📋 Deployment Commands

| Command | Description |
|---------|-------------|
| `./deploy_simple.sh deploy` | Initial setup and deployment |
| `./deploy_simple.sh start` | Start the bot |
| `./deploy_simple.sh stop` | Stop the bot |
| `./deploy_simple.sh restart` | Restart the bot |
| `./deploy_simple.sh status` | Check bot status |
| `./deploy_simple.sh logs` | View live logs |
| `./deploy_simple.sh backup` | Create backup |
| `./deploy_simple.sh update` | Update and restart |

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Bot Manually

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Create logs directory
mkdir -p logs

# Start the bot
python main.py
```

## 🔄 Service Management (Systemd)

For production deployments, you can use systemd to manage the bot as a service:

### 1. Create Service File

```bash
# Copy the template
sudo cp hearhear-bot.service /etc/systemd/system/

# Edit the service file with your paths
sudo nano /etc/systemd/system/hearhear-bot.service
```

**Update these lines in the service file:**
```ini
User=your_username
Group=your_username
WorkingDirectory=/path/to/your/hear-hear-bot
Environment=PATH=/path/to/your/hear-hear-bot/.venv/bin
ExecStart=/path/to/your/hear-hear-bot/.venv/bin/python main.py
ReadWritePaths=/path/to/your/hear-hear-bot/logs
ReadWritePaths=/path/to/your/hear-hear-bot/data
```

### 2. Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable hearhear-bot

# Start service
sudo systemctl start hearhear-bot

# Check status
sudo systemctl status hearhear-bot
```

### 3. Service Management Commands

```bash
# Start
sudo systemctl start hearhear-bot

# Stop
sudo systemctl stop hearhear-bot

# Restart
sudo systemctl restart hearhear-bot

# View logs
sudo journalctl -u hearhear-bot -f

# Disable auto-start
sudo systemctl disable hearhear-bot
```

## 📊 Monitoring

### Check Bot Status

```bash
# Using deployment script
./deploy_simple.sh status

# Manual check
ps aux | grep "python main.py"

# Check web interface
curl http://localhost:8080/
```

### View Logs

```bash
# Live logs
./deploy_simple.sh logs

# Or manually
tail -f logs/bot.log

# Error logs
tail -f logs/errors.log

# Systemd logs (if using service)
sudo journalctl -u hearhear-bot -f
```

### Web Interface

Once the bot is running, you can access:

- **Bot Status**: http://localhost:8080/
- **Documentation**: http://localhost:8080/docs
- **Statistics**: http://localhost:8080/stats

## 🔧 Configuration Options

### Basic Configuration (.env)

```bash
# Required
DISCORD_BOT_TOKEN=your_bot_token_here

# Optional but recommended
MONGODB_CONNECTION_STRING=your_mongodb_connection
TEST_GUILD_ID=your_test_server_id

# Performance tuning
SHARD_COUNT=2
MAX_MESSAGE_CACHE=1000

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true

# Web server
PORT=8080
HOST=0.0.0.0
```

### Environment Types

```bash
# Development
ENVIRONMENT=development
DEBUG=true

# Production
ENVIRONMENT=production
DEBUG=false
```

## 🚨 Troubleshooting

### Common Issues

1. **Bot won't start**
   ```bash
   # Check Python version
   python3 --version
   
   # Check virtual environment
   source .venv/bin/activate
   pip list
   
   # Check configuration
   cat .env
   ```

2. **Permission errors**
   ```bash
   # Fix file permissions
   chmod +x deploy_simple.sh
   chmod +x start_bot.sh
   chmod +x stop_bot.sh
   chmod +x status_bot.sh
   ```

3. **Port already in use**
   ```bash
   # Check what's using port 8080
   sudo netstat -tulpn | grep 8080
   
   # Change port in .env
   echo "PORT=8081" >> .env
   ```

4. **Dependencies missing**
   ```bash
   # Reinstall dependencies
   source .venv/bin/activate
   pip install -r requirements.txt --force-reinstall
   ```

### Log Locations

- **Application logs**: `logs/bot.log`
- **Error logs**: `logs/errors.log`  
- **Web server logs**: `logs/web.log`
- **Systemd logs**: `sudo journalctl -u hearhear-bot`

## 🔄 Updates

### Update Bot

```bash
# Using deployment script (recommended)
./deploy_simple.sh update

# Manual update
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt --upgrade
./deploy_simple.sh restart
```

### Backup Before Updates

```bash
# Create backup
./deploy_simple.sh backup

# Manual backup
cp -r logs backups/logs_$(date +%Y%m%d_%H%M%S)
cp .env backups/.env_$(date +%Y%m%d_%H%M%S)
```

## 📁 File Structure

After deployment, your directory will look like:

```
hear-hear-bot/
├── .venv/                  # Python virtual environment
├── logs/                   # Application logs
├── backups/               # Automated backups
├── main.py                # Bot entry point
├── .env                   # Your configuration
├── deploy_simple.sh       # Deployment script
├── start_bot.sh          # Start script
├── stop_bot.sh           # Stop script
├── status_bot.sh         # Status script
├── hearhear-bot.service  # Systemd service template
└── requirements.txt      # Python dependencies
```

## ✅ Production Checklist

- [ ] Bot token configured in `.env`
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] Bot starts without errors
- [ ] Web interface accessible on port 8080
- [ ] Logs are being written to `logs/` directory
- [ ] Systemd service configured (optional)
- [ ] Backup strategy in place
- [ ] Monitoring and alerting set up

---

**Your bot is now ready for production! 🎉**

For additional features and configuration options, see the [complete documentation](http://localhost:8080/docs) once the bot is running.