# Top.gg Integration - Implementation Summary

## Overview
Added automatic server count posting to top.gg for the Hear! Hear! Discord bot.

## Files Created

### 1. `src/utils/topgg_poster.py` (NEW)
**Purpose**: Core implementation of top.gg integration

**Key Components**:
- `TopGGPoster` class for managing automatic stats posting
- Background task that posts every 30 minutes (configurable)
- Comprehensive error handling and logging
- Manual posting capability
- Status monitoring

**Key Methods**:
```python
- setup(bot_id, api_token, interval): Configure credentials
- start(): Start background posting task
- stop(): Stop background posting task
- post_stats(): Manually post stats once
- get_status(): Get current status information
- _posting_loop(): Internal background task
```

### 2. `TOPGG_INTEGRATION.md` (NEW)
**Purpose**: Comprehensive documentation

**Contents**:
- Setup instructions
- Configuration guide
- How it works explanation
- Troubleshooting guide
- API documentation
- Code structure reference
- Testing procedures
- Security considerations

## Files Modified

### 3. `src/bot/client.py`
**Changes**:
- Added import: `from src.utils.topgg_poster import TopGGPoster`
- Added import: `import os` (for BOT_ID environment variable)
- Initialized `self.topgg_poster = TopGGPoster(self)` in `__init__`
- Added top.gg setup and start in `setup_hook()`:
  ```python
  bot_id = str(self.user.id) if self.user else os.getenv("BOT_ID", "")
  if self.topgg_poster.setup(bot_id, Config.TOPGG_TOKEN):
      self.topgg_poster.start()
  ```
- Added fallback start in `on_ready()` (ensures it starts even if user not ready in setup_hook)
- Added `self.topgg_poster.stop()` in `close()` method for graceful shutdown
- Modified `get_stats()` to include top.gg status:
  ```python
  if self.topgg_poster:
      stats["topgg"] = self.topgg_poster.get_status()
  ```

### 4. `config/settings.py`
**Changes**:
- Added `BOT_ID: str = os.getenv("BOT_ID", "")` configuration variable
- This allows users to set bot ID via environment variable for top.gg integration

### 5. `.env.example`
**Changes**:
- Added documentation for `BOT_ID` environment variable:
  ```bash
  # Your Discord Bot ID (get from Discord Developer Portal - for top.gg integration)
  BOT_ID=your_bot_id_here
  ```

### 6. `src/commands/admin.py`
**Changes**:
- Added `/topgg` slash command with two actions:
  - **status**: Shows current top.gg integration status
  - **post**: Manually posts stats to top.gg immediately
- Administrator-only command with ephemeral responses
- Rich embed responses with status information
- Error handling for unconfigured integration

## Features Implemented

### ✅ Automatic Posting
- Posts server count every 30 minutes by default
- Configurable interval
- Starts automatically when bot connects
- Runs in background without blocking

### ✅ Error Handling
- Network errors: Logs and retries on next interval
- API errors: Logs specific error codes and messages
- Timeout handling: 10-second timeout with retry
- Configuration errors: Gracefully skips if not configured

### ✅ Logging
- Info logs: Successful posts, configuration
- Warning logs: Failed posts, missing configuration
- Error logs: API errors, network issues
- Debug logs: Detailed posting information

### ✅ Manual Control
- Admin command `/topgg status` to check status
- Admin command `/topgg post` to post immediately
- Status information in bot stats endpoint
- Start/stop methods available

### ✅ Status Monitoring
- Configuration status (configured/not configured)
- Running status (running/stopped)
- Bot ID (masked for security)
- Posting interval
- Current server count
- Included in bot's `get_stats()` output

### ✅ Security
- API token never logged or exposed
- Bot ID masked in status display
- Environment variable-based configuration
- Graceful degradation if not configured

### ✅ Production Ready
- Async/await for non-blocking operation
- Proper task management and cleanup
- Graceful shutdown handling
- No external dependencies beyond aiohttp (already in requirements)

## Configuration

### Required Environment Variables
```bash
BOT_ID=your_bot_id_here           # Discord application ID
TOPGG_TOKEN=your_topgg_token_here # Top.gg API token
```

### Optional Configuration
- Posting interval (default: 1800 seconds / 30 minutes)
- Can be changed by modifying the `interval` parameter in `setup()`

## Usage

### For Bot Owners

1. **Setup**:
   ```bash
   # Add to .env file
   BOT_ID=123456789012345678
   TOPGG_TOKEN=your_topgg_api_token
   ```

2. **Start Bot**:
   - Bot automatically starts posting to top.gg
   - Check logs for confirmation

3. **Monitor**:
   - Use `/topgg status` command in Discord
   - Check bot logs for posting activity
   - View stats endpoint for status

4. **Manual Post**:
   - Use `/topgg post` command to post immediately
   - Useful for testing or immediate updates

### For Developers

1. **Access TopGGPoster**:
   ```python
   # In any cog or bot code
   poster = bot.topgg_poster
   ```

2. **Post Manually**:
   ```python
   # Post stats once
   success = await bot.topgg_poster.post_stats()
   ```

3. **Check Status**:
   ```python
   # Get status dict
   status = bot.topgg_poster.get_status()
   print(status["running"])  # True/False
   ```

4. **Control Posting**:
   ```python
   # Start posting
   bot.topgg_poster.start()
   
   # Stop posting
   bot.topgg_poster.stop()
   ```

## Testing Checklist

- [x] Code compiles without errors
- [x] No pylint errors
- [x] Proper error handling
- [x] Comprehensive logging
- [x] Documentation complete
- [x] Admin commands added
- [x] Environment variables documented
- [x] Graceful degradation (works without configuration)
- [x] Proper shutdown handling
- [x] Status monitoring available

## API Specification

### Top.gg Endpoint
```
POST https://top.gg/api/bots/{BOT_ID}/stats
```

### Headers
```
Authorization: {API_TOKEN}
Content-Type: application/json
```

### Payload
```json
{
  "server_count": 123
}
```

### Response
- **200 OK**: Stats posted successfully
- **401 Unauthorized**: Invalid API token
- **403 Forbidden**: Bot not found or wrong bot ID
- **429 Too Many Requests**: Rate limited
- **500 Internal Server Error**: Top.gg API issue

## Integration Points

### Bot Lifecycle
1. **Bot.__init__()**: Create TopGGPoster instance
2. **Bot.setup_hook()**: Configure and start poster
3. **Bot.on_ready()**: Fallback start (if not started in setup_hook)
4. **Bot.close()**: Stop poster gracefully

### Background Task
- Runs in `asyncio` event loop
- Non-blocking
- Automatic retry on failure
- Cancellable via `stop()` method

### Statistics
- Integrated into `Bot.get_stats()` method
- Available via web server stats endpoint
- Included in `/topgg status` command

## Dependencies

### Existing (No New Dependencies)
- `aiohttp`: Already in requirements.txt
- `asyncio`: Python standard library
- `logging`: Python standard library
- `typing`: Python standard library

## Error Scenarios Handled

1. **Missing Configuration**: Skips posting, logs warning
2. **Invalid Credentials**: Logs error, continues bot operation
3. **Network Error**: Logs error, retries on next interval
4. **API Error**: Logs specific error, retries on next interval
5. **Timeout**: Logs timeout, retries on next interval
6. **Bot Shutdown**: Gracefully cancels task

## Performance Impact

- **Memory**: Minimal (~1-2 KB for poster instance)
- **CPU**: Negligible (posts every 30 minutes)
- **Network**: ~1 KB per post every 30 minutes
- **Blocking**: None (fully async)

## Future Enhancements

Possible improvements for future versions:
- Shard-specific stats posting
- Webhook support for vote notifications
- Exponential backoff for retries
- Statistics dashboard for posting history
- Support for other bot lists

## Author

- **Name**: aldinn
- **Email**: kferdoush617@gmail.com
- **GitHub**: https://github.com/Taraldinn/hear-hear-bot

## Version

- **Implementation Date**: 2025-10-01
- **Bot Version**: 2.1.0
- **Python Version**: 3.8+
- **Discord.py Version**: 2.4.0+

---

**Status**: ✅ Ready for Production
