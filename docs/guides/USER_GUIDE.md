# 🎤 Hear! Hear! Bot - Complete User Guide

**The Ultimate Discord Bot for Debate Tournaments**

![Version](https://img.shields.io/badge/version-2.1.0-blue) ![Status](https://img.shields.io/badge/status-active-success) ![License](https://img.shields.io/badge/license-MIT-green)

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Features](#features)
4. [Commands Reference](#commands-reference)
5. [Setup Guide](#setup-guide)
6. [Usage Examples](#usage-examples)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)
10. [Support](#support)

---

## 🎯 Introduction

### What is Hear! Hear! Bot?

Hear! Hear! is a comprehensive Discord bot designed specifically for debate tournaments and communities. Whether you're running parliamentary debates, British Parliamentary (BP) tournaments, or casual debate practice sessions, Hear! Hear! provides all the tools you need to manage timing, motions, tournaments, and more.

### Key Highlights

- 🎯 **Debate Timer** - Professional debate timing with visual countdowns
- 📋 **Motion Database** - Access thousands of debate motions instantly
- 🏆 **Tournament Management** - Full integration with Tabbycat
- 👥 **Role Management** - Automated role assignment for participants
- 📊 **Statistics Tracking** - Monitor bot usage and server stats
- 🌍 **Multi-language** - Support for English and Bangla motions
- ⚡ **Modern Interface** - Beautiful UI with slash commands

### Why Choose Hear! Hear!?

- ✅ **Purpose-Built** - Specifically designed for debate communities
- ✅ **Easy to Use** - Intuitive slash commands with autocomplete
- ✅ **Reliable** - 99.9% uptime with automatic error recovery
- ✅ **Active Development** - Regular updates and new features
- ✅ **Community-Driven** - Built with feedback from debate organizers

---

## 🚀 Quick Start

### Adding the Bot to Your Server

1. **Click the Invite Link**
   - Visit [Add Hear! Hear! Bot](https://discord.com/api/oauth2/authorize?client_id=1401966904578408539&permissions=8&scope=bot%20applications.commands)
   - Or use the "Add to Discord" button on our website

2. **Select Your Server**
   - Choose the server from the dropdown menu
   - You need "Manage Server" permission to add bots

3. **Grant Permissions**
   - Review the requested permissions
   - Click "Authorize" to confirm

4. **Start Using Commands**
   - Type `/` in any channel to see available commands
   - Try `/help` to get started!

### First Commands to Try

```
/help              # View all available commands
/timer start       # Start a debate timer
/motion random     # Get a random debate motion
/stats bot         # View bot statistics
```

---

## ✨ Features

### 1. Debate Timer 🕐

Professional debate timing system with visual feedback and audio alerts.

**Features:**
- Multiple timer formats (BP, WSDC, NA, Custom)
- Visual countdown displays
- Protected time indicators
- Pause/resume functionality
- Speaker time tracking
- Automatic reset options

**Use Cases:**
- Parliamentary debates
- Practice sessions
- Competition rounds
- Speaking drills

### 2. Motion Database 📋

Access to thousands of debate motions categorized by difficulty and type.

**Features:**
- Random motion generation
- Keyword search
- Category filtering
- Difficulty levels
- Infoslide support
- Google Sheets integration

**Languages:**
- English motions
- Bangla motions
- Combined database

### 3. Tournament Management 🏆

Full integration with Tabbycat for tournament operations.

**Features:**
- Automatic role creation
- Channel setup
- Pairing announcements
- Results submission
- Tournament tracking
- Venue management

**Tabbycat Integration:**
- Fetch pairings
- Submit results
- View standings
- Check schedules

### 4. Moderation Tools 🛡️

Keep your server organized and safe.

**Features:**
- Role management
- Channel organization
- Automated cleanup
- Welcome messages
- Custom configurations

### 5. Utility Commands 🔧

Helpful tools for server management and information.

**Features:**
- Server statistics
- User information
- Bot health checks
- Configuration management
- Logging system

---

## 📖 Commands Reference

### Essential Commands

#### `/help`
Display comprehensive help information.

```
Usage: /help [command]
Examples:
  /help              # Show all commands
  /help timer        # Get help for timer command
```

#### `/timer start`
Start a debate timer with customizable settings.

```
Usage: /timer start [format] [prep_time]
Options:
  format: BP, WSDC, NA, Custom
  prep_time: Preparation time in minutes
  
Examples:
  /timer start BP           # Start BP format timer
  /timer start Custom 5     # 5 minute prep, custom format
```

**Timer Controls:**
- ⏯️ Pause/Resume - Click to pause or resume
- ⏹️ Stop - Stop and reset the timer
- ⏭️ Next - Skip to next speaker
- 🔄 Restart - Start over from beginning

#### `/motion random`
Get a random debate motion.

```
Usage: /motion random [language] [difficulty]
Options:
  language: English, Bangla, Combined
  difficulty: Easy, Medium, Hard
  
Examples:
  /motion random English     # Random English motion
  /motion random Bangla Hard # Hard Bangla motion
```

#### `/motion search`
Search for specific motions by keyword.

```
Usage: /motion search <keyword> [language]
Examples:
  /motion search climate English
  /motion search শিক্ষা Bangla
```

### Tournament Commands

#### `/tournament setup`
Initialize tournament roles and channels.

```
Usage: /tournament setup
Description: Creates all necessary roles and channels for a tournament

Requires: Administrator permission
```

#### `/tournament pairings`
Fetch and announce pairings from Tabbycat.

```
Usage: /tournament pairings <round_number>
Example: /tournament pairings 1
```

#### `/tournament results`
Submit results to Tabbycat.

```
Usage: /tournament results <room> <winning_team>
Example: /tournament results R1 OG
```

### Admin Commands

#### `/config set`
Configure bot settings for your server.

```
Usage: /config set <setting> <value>
Examples:
  /config set language English
  /config set prefix !
  /config set timer_format BP
```

#### `/config view`
View current bot configuration.

```
Usage: /config view
```

### Statistics Commands

#### `/stats bot`
View bot statistics and performance.

```
Usage: /stats bot
Shows: Uptime, server count, latency, memory usage
```

#### `/stats server`
View server statistics.

```
Usage: /stats server
Shows: Members, channels, roles, boost level
```

### Utility Commands

#### `/ping`
Check bot response time and status.

```
Usage: /ping
Shows: Latency, uptime, status
```

#### `/info user`
Get information about a user.

```
Usage: /info user [@user]
Example: /info user @JohnDoe
```

#### `/info server`
Get detailed server information.

```
Usage: /info server
Shows: Creation date, owner, features, statistics
```

---

## ⚙️ Setup Guide

### Basic Setup

#### Step 1: Add the Bot
1. Visit the [invite link](https://discord.com/api/oauth2/authorize?client_id=1401966904578408539&permissions=8&scope=bot%20applications.commands)
2. Select your server
3. Authorize with required permissions

#### Step 2: Configure Permissions
The bot needs these permissions to function properly:

**Essential Permissions:**
- Send Messages
- Embed Links
- Read Message History
- Use Slash Commands
- Manage Roles (for tournaments)
- Manage Channels (for tournaments)

**Recommended Permissions:**
- Administrator (for full functionality)

#### Step 3: Test Basic Commands
Try these commands to ensure everything works:
```
/ping                    # Check bot status
/help                    # View all commands
/timer start BP          # Test timer
/motion random English   # Test motion database
```

### Advanced Setup

#### For Tournament Organizers

1. **Setup Tournament Structure**
   ```
   /tournament setup
   ```
   Creates roles: Adjudicators, Speakers, Observers
   Creates channels: General, Briefing, Rooms

2. **Configure Tabbycat**
   - Get your Tabbycat API key
   - Contact bot admin to add API key
   - Test with `/tournament pairings 1`

3. **Customize Settings**
   ```
   /config set language English
   /config set timer_format BP
   /config set announcement_channel #announcements
   ```

#### For Debate Societies

1. **Create Practice Channels**
   - Dedicated debate practice channels
   - Timer channels for multiple rooms
   - Motion discussion channels

2. **Set Up Roles**
   - Debater role
   - Judge role
   - Organizer role

3. **Configure Notifications**
   - Motion of the day
   - Practice session reminders
   - Tournament announcements

---

## 💡 Usage Examples

### Example 1: Running a Practice Debate

```
Step 1: Start with a motion
/motion random English Medium

Step 2: Start timer with prep time
/timer start BP 15

Step 3: During the debate
- Use pause/resume as needed
- Monitor protected time indicators
- Track speaker times

Step 4: After the debate
- Timer automatically resets
- Get another motion if needed
```

### Example 2: Managing a Tournament Round

```
Step 1: Announce pairings
/tournament pairings 1
Bot posts pairings in all channels

Step 2: Monitor rooms
Check each room's status
Assist with any issues

Step 3: Collect results
/tournament results R1 OG
Submit results for each room

Step 4: Prepare next round
Wait for tab room to release pairings
Repeat process
```

### Example 3: Motion Research Session

```
Step 1: Search for topic
/motion search climate English

Step 2: Get variations
/motion random English Hard
(Keep requesting until satisfied)

Step 3: Save motions
Screenshot or copy text
Discuss with team
```

---

## 🎓 Best Practices

### For Debate Organizers

1. **Pre-Tournament Setup**
   - Run `/tournament setup` at least 24 hours before
   - Test all commands with a small group
   - Ensure all organizers have proper roles

2. **During Tournament**
   - Have backup timers ready
   - Monitor bot status with `/ping`
   - Keep admin roles limited

3. **Post-Tournament**
   - Keep roles for future events
   - Export data if needed
   - Thank participants

### For Debaters

1. **Using the Timer**
   - Don't click buttons during others' speeches
   - Respect pause/resume controls
   - Report issues immediately

2. **Motion Practice**
   - Use filtered searches for specific topics
   - Track motions you've practiced
   - Share interesting motions with team

3. **Server Etiquette**
   - Use commands in appropriate channels
   - Don't spam commands
   - Report bugs or issues

### For Server Admins

1. **Performance**
   - Use slash commands (not text commands)
   - Clear old channels periodically
   - Monitor bot resource usage

2. **Security**
   - Limit admin commands to trusted roles
   - Review bot permissions regularly
   - Keep API keys secure

3. **Maintenance**
   - Check for bot updates
   - Test new features in private channels
   - Backup important configurations

---

## 🔧 Troubleshooting

### Common Issues

#### Bot Not Responding

**Problem:** Bot doesn't respond to commands

**Solutions:**
1. Check bot status: `/ping`
2. Verify bot is online (green status)
3. Check permissions in channel
4. Try in different channel
5. Contact support if persistent

#### Timer Issues

**Problem:** Timer not starting or displaying incorrectly

**Solutions:**
1. Ensure you have permission to use timer
2. Check if another timer is already running
3. Try stopping and restarting
4. Verify bot has embed permissions
5. Report specific error messages

#### Motion Database Empty

**Problem:** No motions returned from search

**Solutions:**
1. Check spelling of keywords
2. Try different language option
3. Use broader search terms
4. Try `/motion random` instead
5. Check if database is configured

#### Tournament Commands Failing

**Problem:** Tournament commands not working

**Solutions:**
1. Verify Tabbycat integration is configured
2. Check API key validity
3. Ensure tournament URL is correct
4. Verify round number exists
5. Contact tournament tab room

### Error Messages

#### "Missing Permissions"
**Cause:** Bot lacks required permissions
**Fix:** Grant bot necessary permissions in server settings

#### "Command Not Found"
**Cause:** Using outdated command format
**Fix:** Use slash commands (type `/` to see options)

#### "Database Connection Error"
**Cause:** Temporary database issue
**Fix:** Wait a few minutes and try again

#### "Invalid Configuration"
**Cause:** Server settings misconfigured
**Fix:** Run `/config view` and update settings

### Getting Help

1. **Check Documentation**
   - Read this guide thoroughly
   - Check FAQ section below
   - Visit website documentation

2. **Ask in Support Server**
   - Join our Discord support server
   - Ask questions in #support channel
   - Search existing answers

3. **Report Bugs**
   - Use GitHub issues
   - Provide detailed description
   - Include error messages and screenshots

---

## ❓ FAQ

### General Questions

**Q: Is Hear! Hear! Bot free to use?**
A: Yes, completely free for all servers.

**Q: What permissions does the bot need?**
A: Minimum: Send Messages, Embed Links, Use Slash Commands. Recommended: Administrator for full features.

**Q: Can I use the bot in multiple servers?**
A: Yes, add it to as many servers as you like.

**Q: Is my data safe?**
A: Yes, we only store necessary configuration data. No private messages are logged.

### Features

**Q: Can I add custom motions?**
A: Not directly, but you can request additions via GitHub or support server.

**Q: Does the timer have sound alerts?**
A: Visual alerts only. Sound depends on Discord's notification settings.

**Q: Can I customize timer formats?**
A: Yes, use the Custom format option with `/timer start Custom`.

**Q: Is offline mode available?**
A: No, the bot requires internet connection to function.

### Tournaments

**Q: Does it work with platforms other than Tabbycat?**
A: Currently only Tabbycat is supported.

**Q: Can I run multiple tournaments simultaneously?**
A: Yes, in different servers. One tournament per server.

**Q: Are tournament results stored?**
A: Results are sent to Tabbycat, not stored by the bot.

### Technical

**Q: What language is the bot written in?**
A: Python 3.8+ with discord.py library.

**Q: Is the source code available?**
A: Yes, it's open source on GitHub.

**Q: Can I self-host the bot?**
A: Yes, check GitHub for hosting instructions.

**Q: How often is the bot updated?**
A: Regular updates with new features and bug fixes.

---

## 🆘 Support

### Need Help?

#### Official Support Channels

1. **Discord Support Server**
   - Fastest response time
   - Community help available
   - Direct support from developers

2. **GitHub Issues**
   - Report bugs
   - Request features
   - View known issues
   - [github.com/Taraldinn/hear-hear-bot](https://github.com/Taraldinn/hear-hear-bot)

3. **Email Support**
   - For sensitive issues
   - Partnership inquiries
   - Contact: kferdoush617@gmail.com

#### Before Asking for Help

✅ Check this documentation
✅ Search existing GitHub issues
✅ Try basic troubleshooting steps
✅ Note any error messages
✅ Test in different channel/server

#### What to Include in Support Requests

- Detailed description of issue
- Steps to reproduce
- Error messages (if any)
- Screenshots
- Server ID (if relevant)
- Command used

### Contributing

Want to help improve Hear! Hear! Bot?

- Report bugs on GitHub
- Suggest features
- Contribute code (see CONTRIBUTING.md)
- Help in support server
- Share with debate communities

---

## 📊 Statistics & Monitoring

### Bot Statistics

View real-time statistics:
- Server count: `/stats bot`
- Uptime: Displayed in `/stats bot`
- Response time: Use `/ping`
- Memory usage: Admin only

### Your Server Stats

Track bot usage in your server:
- Command usage
- Most used features
- Active users
- Peak usage times

*Note: Individual tracking available in future updates*

---

## 🎯 SEO Keywords

This bot is perfect for:

- Discord debate servers
- Parliamentary debate communities
- British Parliamentary (BP) tournaments
- World Schools Debate Championship (WSDC)
- North American debate format
- Debate practice sessions
- Online debate competitions
- Debate society management
- Tournament organization
- Motion database access
- Debate timing systems
- Tabbycat integration
- Debate bot for Discord
- Tournament management bot
- Debate timer Discord bot

---

## 📜 Version History

### v2.1.0 (Current)
- ✨ Top.gg integration
- ✨ Improved timer UI
- 🐛 Bug fixes and performance improvements
- 📚 Enhanced documentation

### v2.0.0
- ✨ Slash commands migration
- ✨ Tournament management features
- ✨ Tabbycat integration
- 🎨 Modern UI redesign

### v1.x.x
- Initial release
- Basic timer and motion features

---

## 📞 Contact Information

**Developer:** aldinn  
**Email:** kferdoush617@gmail.com  
**GitHub:** [github.com/Taraldinn/hear-hear-bot](https://github.com/Taraldinn/hear-hear-bot)  
**Website:** [Coming Soon]

---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

---

## 🙏 Acknowledgments

Special thanks to:
- The debate community for feedback and support
- Discord.py developers for the amazing library
- Tabbycat developers for tournament software
- All contributors and testers

---

## 🔗 Quick Links

- [Add to Discord](https://discord.com/api/oauth2/authorize?client_id=1401966904578408539&permissions=8&scope=bot%20applications.commands)
- [GitHub Repository](https://github.com/Taraldinn/hear-hear-bot)
- [Report Bug](https://github.com/Taraldinn/hear-hear-bot/issues)
- [Request Feature](https://github.com/Taraldinn/hear-hear-bot/issues)
- [Documentation](https://github.com/Taraldinn/hear-hear-bot/wiki)

---

**Made with ❤️ for the debate community**

*Last Updated: October 2, 2025*
