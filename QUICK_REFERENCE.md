# 🎤 Hear! Hear! Bot - Quick Reference

## 🚀 Quick Start Guide

### 1. Initial Setup
```
.setup-tournament "Your Tournament Name"
```
- Creates roles, channels, and permissions
- Sets up tournament infrastructure

### 2. Tabbycat Integration (Optional)
```
.tabsync https://your-tabbycat-site.com YOUR_API_TOKEN
```
- Syncs with Tabbycat tournament software
- Enables advanced features

### 3. Role Assignment
```
.assign-roles
```
- Modern dropdown-based role selection
- Automatic permissions assignment

## 🎯 Essential Commands

### Tournament Management
| Command | Description | Permission |
|---------|-------------|------------|
| `.setup-tournament "Name"` | Complete tournament setup | Administrator |
| `.create-venues <count>` | Create debate venues | Administrator |
| `.assign-roles` | Modern role assignment UI | Administrator |
| `.tournament-info` | Display tournament stats | Anyone |

### Tabbycat Integration
| Command | Description | Permission |
|---------|-------------|------------|
| `.tabsync <url> <token>` | Sync with Tabbycat | Administrator |
| `.register <key>` | Register with key | Anyone |
| `.checkin` / `.checkout` | Check availability | Anyone |
| `.status` | Tournament status | Anyone |
| `.motion <round>` | Show round motion | Anyone |
| `.feedback <round> @adj <score>` | Submit feedback | Anyone |

### Timer System
| Command | Description | Permission |
|---------|-------------|------------|
| `.timer <duration> [type]` | Start timer | Adjudicator |
| `.timer-stop` | Stop timer | Adjudicator |
| `.timer-pause` | Pause/resume | Adjudicator |
| `.timer-status` | Check status | Anyone |

### Moderation
| Command | Description | Permission |
|---------|-------------|------------|
| `.announce <message>` | Broadcast message | Manage Messages |
| `.begin-debate` | Move all to debate rooms | Manage Messages |
| `.call-to-venue` | Move current venue participants | Adjudicator |

### Administration
| Command | Description | Permission |
|---------|-------------|------------|
| `.reload [cog]` | Reload bot components | Administrator |
| `.sync` | Sync slash commands | Administrator |
| `.logs [lines]` | View bot logs | Administrator |
| `.delete-data YES I AM 100% SURE` | Delete all data | Administrator |

## 🎪 Key Features

### ✅ Tournament Setup
- **One-command setup**: Complete tournament initialization
- **Modern UI**: Discord dropdowns and select menus
- **Role management**: Automatic role creation and assignment
- **Channel organization**: Structured categories and permissions

### ✅ Tabbycat Integration
- **Real-time sync**: Live data synchronization
- **Registration system**: Key-based participant registration
- **Check-in management**: Availability tracking
- **Feedback collection**: Adjudicator feedback system

### ✅ Advanced Timer
- **Multiple types**: Prep, speech, POI, break timers
- **Visual feedback**: Progress bars and countdowns
- **Audio alerts**: Notification sounds
- **Full control**: Pause, resume, stop functionality

### ✅ Venue Management
- **Automated movement**: Participants between prep/debate rooms
- **Smart routing**: Venue-aware processing
- **Bulk operations**: Global or venue-specific actions

## 🔐 Permission Levels

### 🏆 **Administrator**
- Complete bot access
- Tournament setup and configuration
- Data management and deletion

### 👑 **Adjudicator**
- Timer controls
- Venue management
- Check-in/checkout

### 🎭 **Debater**
- Registration and check-in
- Feedback submission
- Information viewing

### 📢 **Manage Messages**
- Announcements
- Global moderation actions

## 🌐 Web Interface

Access the full documentation at:
- **Homepage**: `http://your-bot-url/`
- **Documentation**: `http://your-bot-url/docs`
- **Commands**: `http://your-bot-url/commands`
- **Health**: `http://your-bot-url/health`
- **Stats**: `http://your-bot-url/stats`

## 🔧 Configuration

### Environment Variables
```bash
DISCORD_TOKEN=your_bot_token
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
GUILD_ID=your_server_id
COMMAND_PREFIX=.
PORT=8080
```

### Database Collections
- `tournaments`: Tournament data and sync info
- `timers`: Active timer states
- `feedback`: Adjudicator feedback records

## 🆘 Common Issues

### **Bot not responding**
1. Check bot permissions
2. Verify token validity
3. Check database connection

### **Commands not working**
1. Ensure proper permissions
2. Check command prefix
3. Try slash command alternative

### **Tabbycat sync failing**
1. Verify API token
2. Check Tabbycat URL format
3. Ensure network connectivity

### **Timer issues**
1. Check Adjudicator role
2. Verify channel permissions
3. Check for running timers

## 📞 Support

- **Email**: kferdoush617@gmail.com
- **GitHub**: https://github.com/Taraldinn/hear-hear-bot
- **Documentation**: Full web docs available at `/docs`

---
*Last Updated: September 2025 | Built with ❤️ by aldinn*