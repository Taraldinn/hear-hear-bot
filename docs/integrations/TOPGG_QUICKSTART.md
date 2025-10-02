# Top.gg Integration - Quick Start Guide

## 🎯 What Was Added

A feature that automatically posts your Discord bot's server count to top.gg every 30 minutes.

## 📦 New Files

1. **`src/utils/topgg_poster.py`** - Core integration code
2. **`TOPGG_INTEGRATION.md`** - Detailed documentation
3. **`TOPGG_IMPLEMENTATION_SUMMARY.md`** - Technical implementation details

## 🔧 Modified Files

1. **`src/bot/client.py`** - Integrated the poster into bot lifecycle
2. **`src/commands/admin.py`** - Added `/topgg` admin command
3. **`config/settings.py`** - Added `BOT_ID` config variable
4. **`.env.example`** - Documented new environment variables

## ⚙️ Setup (3 Easy Steps)

### Step 1: Get Your Credentials

**Bot ID**:
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Copy the "Application ID"

**Top.gg Token**:
1. Go to [top.gg](https://top.gg)
2. Find your bot's page
3. Go to "Edit" or "Webhooks"
4. Copy your API Token

### Step 2: Configure Environment Variables

Add to your `.env` file:

```bash
BOT_ID=123456789012345678          # Your Discord application ID
TOPGG_TOKEN=your_topgg_api_token   # Your top.gg API token
```

### Step 3: Restart Your Bot

That's it! The bot will automatically start posting to top.gg.

## ✅ Verify It's Working

### Check the Logs

You should see:
```
✅ Top.gg poster configured (bot_id: 123456789..., interval: 1800s)
🚀 Top.gg poster task started
📊 Top.gg posting loop started (interval: 1800 seconds)
✅ Posted to top.gg: 42 servers (status: 200)
```

### Use the Discord Command

In Discord, run:
```
/topgg status
```

You'll see:
- ✅ Configuration status
- ✅ Running status
- Bot ID
- Posting interval (30 minutes)
- Current server count

### Manual Post

To post immediately:
```
/topgg post
```

## 🎛️ Admin Commands

### `/topgg status`
Shows the current status of the top.gg integration:
- Configuration state
- Running state
- Bot ID (masked)
- Posting interval
- Server count

### `/topgg post`
Manually posts the server count to top.gg immediately:
- Useful for testing
- Useful for immediate updates
- Returns success or error message

**Note**: Both commands are admin-only and use ephemeral messages (only visible to you).

## 📊 How It Works

1. **Bot starts** → TopGGPoster is initialized
2. **Bot connects** → Poster is configured with your credentials
3. **Background task starts** → Posts every 30 minutes
4. **Server count changes** → Next post includes updated count
5. **Bot shuts down** → Poster stops gracefully

## 🔍 Troubleshooting

### Not Posting?

**Check your credentials**:
```bash
# In terminal
python -c "from config.settings import Config; print('BOT_ID:', bool(Config.BOT_ID), 'TOKEN:', bool(Config.TOPGG_TOKEN))"
```

### Getting API Errors?

- **401 Unauthorized**: Wrong API token
- **403 Forbidden**: Wrong bot ID or bot not listed on top.gg
- **429 Too Many Requests**: Posting too frequently (shouldn't happen with 30-min interval)

### Want More Details?

Check these files:
- `TOPGG_INTEGRATION.md` - Complete documentation
- `TOPGG_IMPLEMENTATION_SUMMARY.md` - Technical details

## 🎨 Features

- ✅ **Automatic**: Posts every 30 minutes without intervention
- ✅ **Non-blocking**: Runs in background, doesn't affect bot performance
- ✅ **Error handling**: Automatically retries on failure
- ✅ **Logging**: Comprehensive logs of all activity
- ✅ **Manual control**: Admin commands for status and manual posting
- ✅ **Graceful degradation**: Bot works fine even if top.gg is not configured
- ✅ **Security**: Tokens never exposed in logs or user-facing messages

## 📈 What Gets Posted

Every 30 minutes, the bot sends:
```json
{
  "server_count": 123
}
```

To:
```
POST https://top.gg/api/bots/{YOUR_BOT_ID}/stats
```

## 🛡️ Security Notes

- Never commit your `.env` file
- Keep your top.gg token private
- Bot ID is masked in status displays
- API token is never logged

## 💡 Tips

1. **Test it first**: Use `/topgg post` to test immediately
2. **Monitor logs**: Watch for the first successful post
3. **Wait patiently**: Changes may take 5-10 minutes to appear on top.gg
4. **Check status**: Use `/topgg status` anytime to verify it's running

## 📝 Configuration Summary

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_ID` | Yes | Discord application ID |
| `TOPGG_TOKEN` | Yes | Top.gg API token |
| Posting Interval | No | Default: 1800s (30 min) |

## 🚀 Advanced Usage

### Change Posting Interval

Edit `src/bot/client.py`, line ~126:

```python
if self.topgg_poster.setup(bot_id, Config.TOPGG_TOKEN, interval=3600):  # 1 hour
    self.topgg_poster.start()
```

### Access in Code

```python
# Get status
status = bot.topgg_poster.get_status()

# Post manually
success = await bot.topgg_poster.post_stats()

# Start/stop
bot.topgg_poster.start()
bot.topgg_poster.stop()
```

## 📚 Documentation

- **Quick Start**: This file (you are here)
- **Full Guide**: `TOPGG_INTEGRATION.md`
- **Technical Details**: `TOPGG_IMPLEMENTATION_SUMMARY.md`

## ✨ That's It!

Your bot now automatically posts to top.gg. No maintenance required!

---

**Questions?** Check `TOPGG_INTEGRATION.md` for detailed troubleshooting and advanced usage.

**Author**: aldinn (kferdoush617@gmail.com)
