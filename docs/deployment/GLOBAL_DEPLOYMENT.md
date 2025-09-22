# 🌍 Global Deployment Guide

This guide explains how to deploy the Hear! Hear! Bot for global use across multiple Discord servers.

## ✅ Bot is Already Configured for Global Use

The bot is **already optimized for global deployment** with the following configurations:

### 🌍 Global Command Registration
- **Slash Commands**: Registered globally using `await self.tree.sync()` (no guild parameter)
- **Command Clearing**: Uses `self.tree.clear_commands(guild=None)` for global scope
- **Auto-Sharding**: Configured with `SHARD_COUNT = 2` for handling multiple servers

### 🚀 Performance Optimizations
- **Minimal Member Caching**: `member_cache_flags=discord.MemberCacheFlags.none()`
- **No Guild Chunking**: `chunk_guilds_at_startup=False` for better startup performance
- **Database per Server**: Uses `guild_id` for server-specific data storage

## 🔧 Deployment Steps

### 1. Environment Variables
Set these environment variables for global deployment:

```bash
# Required
DISCORD_BOT_TOKEN=your_bot_token_here

# Optional (for full functionality)
MONGODB_CONNECTION_STRING=your_mongodb_connection_string
PORT=8080  # For web server
```

### 2. Bot Permissions
When inviting the bot to servers, ensure it has:
- ✅ `applications.commands` scope (for global slash commands)
- ✅ `bot` scope
- ✅ Required permissions for commands (Admin, Manage Roles, etc.)

### 3. Deploy to Render.com
The bot is configured for Render.com deployment:

```yaml
# Procfile
web: python main.py
```

The bot will:
- Start the Discord bot
- Start the web server on the specified PORT
- Sync commands globally across all servers

## 🌍 How Global Deployment Works

### Command Propagation
1. **Initial Sync**: Commands are registered globally when bot starts
2. **Propagation Time**: Takes up to 1 hour to appear in all servers
3. **Manual Sync**: Use `.sync` command to force immediate sync

### Server-Specific Data
- **Language Settings**: Stored per server using `guild_id`
- **Tournament Data**: Each server can sync with different Tabbycat instances
- **Timer Data**: User timers are isolated per channel/server

### Scaling Features
- **Auto-Sharding**: Bot automatically handles multiple servers
- **Minimal Memory Usage**: Optimized for global deployment
- **Database Efficiency**: Server-specific collections for data isolation

## 🎯 Usage Across Servers

### For Server Administrators
1. **Invite Bot**: Use the bot invite link with proper permissions
2. **Set Language**: Use `.setlanguage english` or `.setlanguage bangla`
3. **Sync Commands**: Use `.sync` to force command update if needed

### For Tournament Organizers
1. **Connect Tabbycat**: Use `.tabsync <url> <token>` in each server
2. **Register Participants**: Use `.register <key>` for tournament registration
3. **Manage Attendance**: Use `.checkin`/`.checkout` for participant management

### For Users
1. **Use Slash Commands**: All `/` commands work in every server
2. **Timer Functions**: Each user can run timers independently
3. **Motion Generation**: Get random motions in server language

## 🔍 Monitoring Global Deployment

### Logs to Watch
```
Successfully synced X GLOBAL slash commands
🌍 Commands will be available in ALL servers within 1 hour
Verified X commands are registered globally
```

### Health Checks
- **Command Count**: Should show 20 slash commands registered
- **Server Count**: Monitor `len(self.guilds)` for connected servers
- **Database**: Check per-server data isolation

## 🚨 Troubleshooting

### Commands Not Appearing
1. **Check Scope**: Ensure bot has `applications.commands` scope
2. **Wait for Propagation**: Commands take up to 1 hour to appear globally
3. **Manual Sync**: Use `.sync` command to force immediate sync

### Performance Issues
1. **Monitor Memory**: Bot uses minimal member caching for global scale
2. **Database Load**: Each server's data is isolated
3. **Shard Distribution**: Auto-sharding handles server distribution

### Server-Specific Issues
1. **Permissions**: Check bot permissions in each server
2. **Language Settings**: Verify server language configuration
3. **Tournament Data**: Ensure Tabbycat sync is server-specific

## 📊 Global Deployment Benefits

✅ **Single Bot Instance**: One bot serves all servers
✅ **Consistent Experience**: Same commands across all servers
✅ **Efficient Resource Usage**: Optimized for global scale
✅ **Easy Management**: Centralized command updates
✅ **Server Isolation**: Data remains separate per server
✅ **Automatic Scaling**: Auto-sharding handles growth

## 🎉 Ready for Global Use!

Your Hear! Hear! Bot is now configured and ready for global deployment across multiple Discord servers. Simply deploy it and invite it to as many servers as needed!
