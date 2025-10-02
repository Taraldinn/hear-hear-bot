# Top.gg Integration Guide

This document explains how to set up and use the automatic top.gg server count posting feature for the Hear! Hear! Discord bot.

## Overview

The top.gg integration automatically posts your Discord bot's current server count to [top.gg](https://top.gg) at regular intervals (default: every 30 minutes). This keeps your bot's statistics up-to-date on the bot list without manual intervention.

## Features

- **Automatic Posting**: Posts server count every 30 minutes (configurable)
- **Error Handling**: Graceful error handling with retry logic
- **Logging**: Comprehensive logging of all posting activities
- **Status Monitoring**: Includes top.gg status in bot statistics endpoint
- **Background Task**: Runs as a non-blocking background task
- **Graceful Shutdown**: Properly stops when bot shuts down

## Setup Instructions

### 1. Get Your Bot ID

Your bot ID is the unique Discord application ID:

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your bot application
3. Copy the "Application ID" from the General Information page

### 2. Get Your Top.gg API Token

1. Go to [top.gg](https://top.gg) and log in
2. Navigate to your bot's page (or add your bot if not already listed)
3. Go to the "Edit" or "Webhooks" section
4. Copy your API Token

### 3. Configure Environment Variables

Add the following to your `.env` file:

```bash
# Discord Bot ID (required for top.gg)
BOT_ID=your_bot_id_here

# Top.gg API Token (required for posting stats)
TOPGG_TOKEN=your_topgg_api_token_here
```

**Note**: If you don't set these variables, the bot will still run normally but won't post to top.gg.

### 4. Restart Your Bot

The integration will automatically start when the bot connects to Discord.

## How It Works

### Automatic Startup

The top.gg poster is automatically initialized and started when the bot connects:

1. **On Bot Startup** (`setup_hook`):
   - Initializes the TopGGPoster instance
   - Configures it with BOT_ID and TOPGG_TOKEN from environment variables
   - Starts the background posting task if credentials are valid

2. **On Bot Ready** (`on_ready`):
   - Ensures the poster is running (fallback if not started in setup_hook)
   - Uses the actual bot user ID if BOT_ID environment variable isn't set

### Background Task

The background task runs continuously:

1. Waits for the bot to be fully ready
2. Posts the current server count to top.gg API
3. Logs the result (success or error)
4. Waits for the configured interval (default: 30 minutes)
5. Repeats from step 2

### API Endpoint

The poster makes a POST request to:
```
https://top.gg/api/bots/{BOT_ID}/stats
```

With payload:
```json
{
  "server_count": 123
}
```

And headers:
```
Authorization: your_api_token
Content-Type: application/json
```

## Configuration Options

### Posting Interval

To change the posting interval, modify the `post_interval` parameter when calling `setup()`:

```python
# In client.py
if self.topgg_poster.setup(bot_id, Config.TOPGG_TOKEN, interval=3600):  # 1 hour
    self.topgg_poster.start()
```

**Note**: Top.gg recommends posting every 30 minutes (1800 seconds) or less frequently.

### Manual Control

You can manually control the poster:

```python
# Start posting
bot.topgg_poster.start()

# Stop posting
bot.topgg_poster.stop()

# Post stats immediately (one-time)
await bot.topgg_poster.post_stats()

# Get poster status
status = bot.topgg_poster.get_status()
```

## Monitoring

### Check Status

The poster status is included in the bot's statistics endpoint:

```python
stats = bot.get_stats()
topgg_status = stats.get("topgg", {})

print(topgg_status)
# Output:
# {
#     "configured": True,
#     "running": True,
#     "bot_id": "123456789012345678",
#     "interval": 1800,
#     "server_count": 42
# }
```

### Logs

The poster logs all activities:

- ✅ **Info**: Successful posts and configuration
- ⚠️ **Warning**: Failed posts (will retry)
- ❌ **Error**: Configuration errors or API errors
- 📊 **Debug**: Detailed posting information

Example logs:
```
✅ Top.gg poster configured (bot_id: 123456789012345678, interval: 1800s)
🚀 Top.gg poster task started
📊 Top.gg posting loop started (interval: 1800 seconds)
✅ Posted to top.gg: 42 servers (status: 200)
```

## Troubleshooting

### Poster Not Starting

**Symptoms**: No top.gg logs appear

**Solutions**:
1. Check that `BOT_ID` and `TOPGG_TOKEN` are set in your `.env` file
2. Verify the environment variables are loaded (check Config.TOPGG_TOKEN)
3. Look for warning logs like "Top.gg credentials not provided"

### API Errors

**Symptoms**: Logs show "Top.gg API error (status XXX)"

**Common Errors**:

- **401 Unauthorized**: Invalid API token
  - Solution: Verify your TOPGG_TOKEN is correct
  
- **403 Forbidden**: Bot not found on top.gg or wrong bot ID
  - Solution: Verify BOT_ID matches your bot's application ID
  - Ensure your bot is listed on top.gg

- **429 Too Many Requests**: Posting too frequently
  - Solution: Increase the posting interval (default 30 minutes should be fine)

- **500 Internal Server Error**: Top.gg API issues
  - Solution: This is a top.gg issue, the poster will retry automatically

### Network Errors

**Symptoms**: Logs show "Network error posting to top.gg" or "Timeout"

**Solutions**:
1. Check your internet connection
2. Verify you can reach https://top.gg from your server
3. Check for firewall rules blocking outbound HTTPS connections
4. The poster will automatically retry on next interval

### Poster Running But Not Updating

**Symptoms**: Poster starts but stats don't update on top.gg

**Solutions**:
1. Check the response status in logs (should be 200)
2. Verify your bot is claimed on top.gg
3. Check if you're using the correct API token for your bot
4. Wait up to 5-10 minutes for changes to appear on top.gg

## Code Structure

### Files Modified/Created

1. **`src/utils/topgg_poster.py`** (NEW)
   - Main TopGGPoster class
   - Background task logic
   - API communication

2. **`src/bot/client.py`** (MODIFIED)
   - Import TopGGPoster
   - Initialize poster in `__init__`
   - Start poster in `setup_hook` and `on_ready`
   - Stop poster in `close`
   - Include status in `get_stats`

3. **`config/settings.py`** (MODIFIED)
   - Added `BOT_ID` configuration variable

4. **`.env.example`** (MODIFIED)
   - Documented `BOT_ID` variable

### Class Structure

```python
class TopGGPoster:
    """Handles automatic posting of bot server count to top.gg"""
    
    def __init__(self, bot):
        """Initialize with bot instance"""
    
    def setup(self, bot_id: str, api_token: str, interval: int = 1800) -> bool:
        """Configure credentials and interval"""
    
    def start(self) -> bool:
        """Start the background posting task"""
    
    def stop(self):
        """Stop the background posting task"""
    
    async def post_stats(self) -> bool:
        """Post current server count (one-time)"""
    
    def get_status(self) -> dict:
        """Get current poster status"""
    
    async def _posting_loop(self):
        """Internal background task loop"""
```

## Testing

### Test the Integration

1. **Check Configuration**:
   ```python
   python -c "from config.settings import Config; print(f'BOT_ID: {Config.BOT_ID[:4]}..., TOPGG_TOKEN: {'✅' if Config.TOPGG_TOKEN else '❌'}')"
   ```

2. **Start the Bot**:
   - Watch for setup logs showing top.gg poster starting
   - Look for the first post attempt within 30 seconds

3. **Manual Test** (in bot console):
   ```python
   # Post immediately
   await bot.topgg_poster.post_stats()
   
   # Check status
   print(bot.topgg_poster.get_status())
   ```

4. **Verify on Top.gg**:
   - Go to your bot's page on top.gg
   - Check if the server count updated (may take 5-10 minutes)

## Security Considerations

1. **Never commit tokens**: Keep your `.env` file out of version control
2. **Token rotation**: Regenerate your top.gg token if exposed
3. **Rate limiting**: Respect top.gg's rate limits (30 minutes recommended)
4. **Error handling**: The poster gracefully handles all errors without crashing

## API Rate Limits

Top.gg recommendations:
- **Minimum interval**: No more than once every 5 minutes
- **Recommended interval**: Once every 30 minutes (default)
- **Maximum**: No specific limit, but respect their service

## Support

If you encounter issues:

1. Check the logs for specific error messages
2. Verify your environment variables are set correctly
3. Test your API token using the top.gg API documentation
4. Check the [top.gg API docs](https://docs.top.gg) for API changes

## Future Enhancements

Potential improvements for the future:

- [ ] Support for posting shard-specific stats
- [ ] Webhook support for vote notifications
- [ ] Retry backoff for failed posts
- [ ] Statistics dashboard for posting history
- [ ] Support for other bot lists (Discord Bot List, etc.)

## License

This feature is part of the Hear! Hear! bot project and follows the same license.

## Author

- **Author**: aldinn
- **Email**: kferdoush617@gmail.com
- **GitHub**: https://github.com/Taraldinn/hear-hear-bot
