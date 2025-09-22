# 🛠️ Installation & Setup Guide

This guide walks you through the complete setup process for the Hear! Hear! Discord Bot.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Discord Bot Setup](#discord-bot-setup)
3. [Local Development Setup](#local-development-setup)
4. [Database Configuration](#database-configuration)
5. [Environment Configuration](#environment-configuration)
6. [Running the Bot](#running-the-bot)
7. [Production Deployment](#production-deployment)
8. [Verification & Testing](#verification--testing)
9. [Troubleshooting](#troubleshooting)

## ✅ Prerequisites

### System Requirements
- **Python 3.8 or higher**
- **Git** (for cloning the repository)
- **Discord Account** (for bot creation)
- **MongoDB Database** (optional but recommended)

### Knowledge Requirements
- Basic familiarity with Discord
- Basic command line usage
- Understanding of environment variables

### Account Requirements
- **Discord Developer Account** (free)
- **MongoDB Atlas Account** (free tier available)
- **Hosting Service Account** (for production deployment)

## 🤖 Discord Bot Setup

### Step 1: Create Discord Application

1. **Visit Discord Developer Portal**
   - Go to [https://discord.com/developers/applications](https://discord.com/developers/applications)
   - Log in with your Discord account

2. **Create New Application**
   - Click "New Application"
   - Enter bot name: "Hear! Hear! Bot" (or your preferred name)
   - Click "Create"

3. **Configure Application**
   - Add description: "Tournament management and debate utility bot"
   - Upload bot avatar (optional)
   - Save changes

### Step 2: Create Bot User

1. **Navigate to Bot Section**
   - In the left sidebar, click "Bot"
   - Click "Add Bot" → "Yes, do it!"

2. **Configure Bot Settings**
   - **Username:** Set your preferred bot username
   - **Icon:** Upload bot avatar image
   - **Public Bot:** Turn OFF (recommended for private use)
   - **Requires OAuth2 Code Grant:** Keep OFF
   - **Presence Intent:** Turn ON
   - **Server Members Intent:** Turn ON
   - **Message Content Intent:** Turn ON

3. **Copy Bot Token**
   - Click "Copy" under the Token section
   - **⚠️ IMPORTANT:** Save this token securely - you'll need it later
   - **⚠️ WARNING:** Never share this token publicly

### Step 3: Set Bot Permissions

1. **Navigate to OAuth2 → URL Generator**
   - Select **Scopes:**
     - ☑️ `bot`
     - ☑️ `applications.commands`

2. **Select **Bot Permissions:**
   - **General Permissions:**
     - ☑️ `Manage Roles`
     - ☑️ `Manage Channels`
     - ☑️ `View Channels`
     - ☑️ `Send Messages`
     - ☑️ `Manage Messages`
     - ☑️ `Embed Links`
     - ☑️ `Read Message History`
     - ☑️ `Add Reactions`
     - ☑️ `Use Slash Commands`
   
   - **Voice Permissions:**
     - ☑️ `Connect`
     - ☑️ `Speak`
     - ☑️ `Mute Members`
     - ☑️ `Deafen Members`
     - ☑️ `Move Members`

3. **Copy Generated URL**
   - Copy the generated URL at the bottom
   - Use this to invite the bot to your server

### Step 4: Invite Bot to Server

1. **Open Invite URL**
   - Paste the copied URL in your browser
   - Select your Discord server
   - Click "Authorize"

2. **Verify Bot Presence**
   - Check that the bot appears in your server member list
   - The bot should be offline until you run the code

## 💻 Local Development Setup

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/Taraldinn/hear-hear-bot.git

# Navigate to project directory
cd hear-hear-bot

# Verify contents
ls -la
```

### Step 2: Python Environment Setup

#### Option A: Using pip (Recommended for beginners)
```bash
# Ensure you have Python 3.8+
python3 --version

# Install dependencies
pip3 install -r requirements.txt
```

#### Option B: Using pipenv (Recommended for development)
```bash
# Install pipenv if not already installed
pip install pipenv

# Install dependencies and create virtual environment
pipenv install

# Activate virtual environment
pipenv shell
```

#### Option C: Using venv (Alternative)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
# Check if key packages are installed
python3 -c "import discord; print(f'discord.py version: {discord.__version__}')"
python3 -c "import pymongo; print('MongoDB driver installed')"
```

## 🗄️ Database Configuration

### Option A: MongoDB Atlas (Cloud - Recommended)

1. **Create MongoDB Atlas Account**
   - Visit [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up for free account
   - Verify email address

2. **Create a Cluster**
   - Choose "Build a Database"
   - Select "FREE" tier (M0 Sandbox)
   - Choose cloud provider and region (closest to you)
   - Name your cluster (e.g., "hear-hear-bot")
   - Click "Create Cluster"

3. **Configure Database Access**
   - **Database Access:**
     - Click "Database Access" in left sidebar
     - Click "Add New Database User"
     - Choose "Password" authentication
     - Username: `bot_user` (or your choice)
     - Generate secure password
     - Database User Privileges: "Read and write to any database"
     - Click "Add User"

   - **Network Access:**
     - Click "Network Access" in left sidebar
     - Click "Add IP Address"
     - Choose "Allow Access from Anywhere" (0.0.0.0/0)
     - Or add your specific IP address for security
     - Click "Confirm"

4. **Get Connection String**
   - Click "Database" in left sidebar
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Select "Python" and version "3.6 or later"
   - Copy the connection string
   - Replace `<password>` with your database user password

### Option B: Local MongoDB (Development)

1. **Install MongoDB Community Edition**

   **Ubuntu/Debian:**
   ```bash
   wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
   sudo apt-get update
   sudo apt-get install -y mongodb-org
   ```

   **macOS (using Homebrew):**
   ```bash
   brew tap mongodb/brew
   brew install mongodb-community@6.0
   ```

   **Windows:**
   - Download installer from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Run installer with default settings

2. **Start MongoDB Service**

   **Ubuntu/Debian:**
   ```bash
   sudo systemctl start mongod
   sudo systemctl enable mongod
   ```

   **macOS:**
   ```bash
   brew services start mongodb/brew/mongodb-community@6.0
   ```

   **Windows:**
   - MongoDB should start automatically as a service

3. **Verify Installation**
   ```bash
   # Connect to MongoDB shell
   mongosh

   # Should see MongoDB connection message
   # Type 'exit' to quit
   ```

4. **Connection String for Local MongoDB**
   ```
   mongodb://localhost:27017/hear_hear_bot
   ```

## ⚙️ Environment Configuration

### Step 1: Create Environment File

1. **Copy Example File**
   ```bash
   cp .env.example .env
   ```

   If `.env.example` doesn't exist, create `.env` manually:
   ```bash
   touch .env
   ```

### Step 2: Configure Environment Variables

Edit the `.env` file with your favorite text editor:

```env
# Required: Discord Bot Token
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Required for database features: MongoDB Connection
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/database

# Optional: Test server for development
TEST_GUILD_ID=your_test_server_id_here

# Optional: Web server configuration
PORT=8080

# Optional: Additional APIs
TOPGG_TOKEN=your_topgg_token_here
```

### Step 3: Fill in Your Values

1. **DISCORD_BOT_TOKEN**
   - Paste the bot token you copied from Discord Developer Portal
   - Remove any quotes around the token

2. **MONGODB_CONNECTION_STRING**
   - If using MongoDB Atlas: Use the connection string from Atlas
   - If using local MongoDB: Use `mongodb://localhost:27017/hear_hear_bot`
   - Replace username/password with your actual credentials

3. **TEST_GUILD_ID** (Optional but recommended)
   - Right-click on your Discord server name
   - Select "Copy ID" (requires Developer Mode enabled)
   - Paste the ID here for faster command sync during development

### Step 4: Secure Your Environment File

```bash
# Make sure .env is in .gitignore (should already be there)
echo ".env" >> .gitignore

# Set appropriate permissions (Linux/Mac)
chmod 600 .env
```

## 🚀 Running the Bot

### Step 1: Start the Bot

#### Using Python directly:
```bash
python3 main.py
```

#### Using pipenv:
```bash
pipenv run python main.py
```

### Step 2: Verify Bot Startup

Look for these messages in the console:

```
✅ Bot is starting up...
✅ Database connected successfully (if using MongoDB)
✅ Loading extensions...
   ├── src.commands.slash_commands
   ├── src.commands.timer
   ├── src.commands.tournament
   ├── src.commands.reaction_roles
   ├── src.commands.logging
   ├── src.commands.admin
   └── src.events.member
✅ All extensions loaded successfully
✅ Bot logged in as: Hear! Hear! Bot#1234
✅ Command sync completed: 30 global commands
🎯 Bot is ready to use!
```

### Step 3: Test Basic Functionality

In your Discord server, try these commands:
```
/ping          # Should respond with latency
/help          # Should show help message
/about         # Should show bot information
```

## 🌐 Production Deployment

### Option A: Heroku Deployment

1. **Install Heroku CLI**
   - Download from [https://devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-bot-name
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set DISCORD_BOT_TOKEN=your_token_here
   heroku config:set MONGODB_CONNECTION_STRING=your_mongodb_uri
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

6. **Scale Worker**
   ```bash
   heroku ps:scale worker=1
   ```

### Option B: Railway Deployment

1. **Connect Repository**
   - Visit [Railway.app](https://railway.app)
   - Connect your GitHub repository

2. **Set Environment Variables**
   - In Railway dashboard, go to Variables
   - Add all your environment variables

3. **Deploy**
   - Railway automatically deploys on push to main branch

### Option C: VPS/Self-Hosted

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

3. **Create Service File**
   ```bash
   sudo nano /etc/systemd/system/hear-hear-bot.service
   ```

   **Service Configuration:**
   ```ini
   [Unit]
   Description=Hear! Hear! Discord Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/hear-hear-bot
   Environment=PATH=/usr/bin:/usr/local/bin
   EnvironmentFile=/home/ubuntu/hear-hear-bot/.env
   ExecStart=/usr/bin/python3 main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable hear-hear-bot
   sudo systemctl start hear-hear-bot
   
   # Check status
   sudo systemctl status hear-hear-bot
   ```

## ✅ Verification & Testing

### Step 1: Basic Commands Test

Test these commands in your Discord server:

```bash
/ping                    # Check bot responsiveness
/help                    # Verify help system
/about                   # Check bot information
/randommotion language:English  # Test motion database
/coinflip               # Test utility commands
```

### Step 2: Timer System Test

```bash
/timer duration:01:00 title:Test Timer public:true
# Verify timer appears with buttons
# Test start, pause, stop buttons
```

### Step 3: Tournament System Test

**⚠️ Test in a test server first!**

```bash
/create_tournament tournament_type:AP venues:1 setup_roles:true setup_role_assignment:true
# Verify channels are created
# Test role assignment reactions
```

### Step 4: Database Features Test (if using MongoDB)

```bash
/reactionrole title:"Test Roles" description:"Test reaction roles" mode:normal
# Add some reaction roles
# Test that they work
```

### Step 5: Performance Test

```bash
# Check memory usage
ps aux | grep python

# Check logs for errors
tail -f logs/bot.log  # if logging to file
```

## 🐛 Troubleshooting

### Bot Won't Start

#### "Missing required environment variables"
- Check `.env` file exists in root directory
- Verify `DISCORD_BOT_TOKEN` is set correctly
- Ensure no extra quotes around token

#### "discord.errors.LoginFailure: Improper token has been passed"
- Verify bot token is correct
- Check for extra spaces or characters
- Regenerate token in Discord Developer Portal if needed

#### "ModuleNotFoundError"
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python3 --version`
- Verify virtual environment is activated

### Bot Online But Commands Don't Work

#### Slash commands not appearing
- Wait up to 1 hour for global command sync
- Use `TEST_GUILD_ID` for immediate testing
- Check bot has `applications.commands` scope

#### Permission errors
- Verify bot role is above managed roles
- Check bot has required permissions in server
- Ensure bot can see channels where commands are used

### Database Issues

#### "ServerSelectionTimeoutError"
- Check MongoDB connection string
- Verify network access (whitelist IP in Atlas)
- Test database connectivity independently

#### "OperationFailure: Authentication failed"
- Check username/password in connection string
- Verify database user permissions
- Ensure user has access to correct database

### Performance Issues

#### High memory usage
- Monitor memory with `htop` or similar
- Check for memory leaks in logs
- Consider reducing concurrent operations

#### Slow response times
- Check network connectivity
- Monitor database performance
- Verify server resources

### Getting Help

1. **Check Logs**
   - Look for error messages in console output
   - Enable debug logging if needed

2. **Verify Setup**
   - Double-check all configuration steps
   - Test with minimal setup first

3. **Community Support**
   - GitHub Issues: [Report bugs or issues](https://github.com/Taraldinn/hear-hear-bot/issues)
   - Email: kferdoush617@gmail.com

4. **Debug Information to Include**
   - Python version (`python3 --version`)
   - Discord.py version
   - Operating system
   - Error messages (full traceback)
   - Steps to reproduce the issue

---

*Once you've completed the setup, refer to the [Commands Reference](COMMANDS.md) to learn about all available features.*