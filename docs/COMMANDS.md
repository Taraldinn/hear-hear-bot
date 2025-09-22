# 📚 Complete Commands Reference

This document provides a comprehensive reference for all commands available in the Hear! Hear! Bot.

## 🏆 Tournament Commands

### `/create_tournament`
**Description:** Creates a complete tournament setup with venues, roles, and channels.

**Parameters:**
- `tournament_type` (required): Choose between "AP" (Asian Parliamentary) or "BP" (British Parliamentary)
- `venues` (required): Number of venues to create (1-20)
- `setup_roles` (optional): Whether to create tournament roles (default: true)
- `setup_role_assignment` (optional): Whether to setup role assignment channel (default: true)

**Usage Examples:**
```
/create_tournament tournament_type:BP venues:5 setup_roles:true setup_role_assignment:true
/create_tournament tournament_type:AP venues:3 setup_roles:false
/create_tournament tournament_type:BP venues:8
```

**What it creates:**

#### For BP (British Parliamentary):
- **Roles:** Debater (🥊), Adjudicator (⚖️), Spectator (👀)
- **Categories:** Welcome, Info Desk, Feedback & Check-in, Grand Auditorium, Venue 1-N
- **Per Venue:**
  - Text channel: `venue-N-debate`
  - Voice channels: `Venue-N-Debate`, `Venue-N-OG-Prep`, `Venue-N-OO-Prep`, `Venue-N-CG-Prep`, `Venue-N-CO-Prep`
  - Adjudicator channel: `venue-N-result-discussion`

#### For AP (Asian Parliamentary):
- **Roles:** Debater (🥊), Adjudicator (⚖️), Spectator (👀)
- **Categories:** Welcome, Info Desk, Feedback & Check-in, Grand Auditorium, Venue 1-N
- **Per Venue:**
  - Text channel: `venue-N-debate`
  - Voice channels: `Venue-N-Debate`, `Venue-N-Gov-Prep`, `Venue-N-Opp-Prep`
  - Adjudicator channel: `venue-N-result-discussion`

**Permissions Set:**
- **Debater role:** Access to prep rooms (capacity limited), general channels
- **Adjudicator role:** Access to all channels including result discussions
- **Spectator role:** Read-only access to general channels

---

## ⏰ Timer Commands

### `/timer`
**Description:** Creates an interactive debate timer with button controls.

**Parameters:**
- `duration` (required): Timer duration in MM:SS format (e.g., "07:00" for 7 minutes)
- `title` (optional): Custom title for the timer
- `public` (optional): Whether the timer should be visible to everyone (default: false)

**Usage Examples:**
```
/timer duration:07:00 title:Government Speech public:true
/timer duration:05:00 title:Prep Time
/timer duration:03:00 public:false
```

**Timer Controls:**
- ▶️ **Start/Resume** - Start or resume the timer
- ⏸️ **Pause** - Pause the timer (can be resumed)
- ⏹️ **Stop** - Stop and reset the timer
- 🔄 **Reset** - Reset timer to original duration

**Features:**
- Each user can have their own timer
- Timers persist across bot restarts
- Visual feedback with color changes
- Audio notifications (if enabled)

### `/timer-stop`
**Description:** Stops your currently active timer.

**Parameters:** None

**Usage:**
```
/timer-stop
```

### `/timer-pause`
**Description:** Pauses or resumes your currently active timer.

**Parameters:** None

**Usage:**
```
/timer-pause
```

### `/currenttime`
**Description:** Get the current Unix timestamp.

**Parameters:** None

**Usage:**
```
/currenttime
```

---

## 🎲 Debate Utility Commands

### `/randommotion`
**Description:** Get a random debate motion from the database.

**Parameters:**
- `language` (required): Choose the language for the motion (English, Bangla)
- `category` (optional): Specific motion category (if available)

**Usage Examples:**
```
/randommotion language:English
/randommotion language:Bangla
```

**Motion Database:**
- **English:** Over 500 curated motions from various tournaments
- **Bangla:** Collection of motions in Bengali language
- **Categories:** Policy, Philosophy, International Relations, etc.

### `/coinflip`
**Description:** Flip a fair coin for random decisions.

**Parameters:** None

**Usage:**
```
/coinflip
```

**Output:** Either "Heads" or "Tails" with a coin emoji

### `/toss`
**Description:** Generic coin toss for side determination.

**Parameters:** None

**Usage:**
```
/toss
```

**Output:** Government or Opposition side assignment

### `/ap-toss`
**Description:** Specialized coin toss for Asian Parliamentary format.

**Parameters:** None

**Usage:**
```
/ap-toss
```

**Output:**
- **Government** or **Opposition** side
- Includes format-specific information

### `/bp-toss`
**Description:** Specialized coin toss for British Parliamentary format.

**Parameters:** None

**Usage:**
```
/bp-toss
```

**Output:**
- **Opening Government (OG)**
- **Opening Opposition (OO)**
- **Closing Government (CG)**
- **Closing Opposition (CO)**

### `/diceroll`
**Description:** Roll a dice with customizable number of sides.

**Parameters:**
- `sides` (optional): Number of sides on the dice (default: 6, max: 100)

**Usage Examples:**
```
/diceroll
/diceroll sides:20
/diceroll sides:4
```

**Output:** Random number between 1 and the specified number of sides

---

## 🎭 Carl-bot Style Commands

### `/reactionrole`
**Description:** Create a reaction role message for role assignment.

**Parameters:**
- `title` (required): Title for the reaction role embed
- `description` (required): Description explaining the role assignment
- `mode` (optional): Role assignment mode (default: normal)
- `channel` (optional): Channel to send the message (default: current channel)

**Available Modes:**
- **normal**: Standard behavior, users can add/remove roles freely
- **unique**: Users can only have one role from this message
- **verify**: Users must confirm their role selection
- **reversed**: Reactions remove roles instead of adding them
- **binding**: Roles cannot be removed once assigned
- **temporary**: Roles expire after a set time

**Usage Examples:**
```
/reactionrole title:"Tournament Roles" description:"React to get your role!" mode:unique
/reactionrole title:"Optional Roles" description:"Choose your interests" mode:normal
/reactionrole title:"Verification" description:"React to verify" mode:binding
```

### `/add-reaction-role`
**Description:** Add a role option to an existing reaction role message.

**Parameters:**
- `message_id` (required): Discord message ID of the reaction role message
- `emoji` (required): Emoji to react with (can be custom emoji)
- `role` (required): Role to assign when reacted
- `description` (optional): Description of what this role does

**Usage Examples:**
```
/add-reaction-role message_id:123456789012345678 emoji:🥊 role:@Debater description:Active debate participant
/add-reaction-role message_id:123456789012345678 emoji:⚖️ role:@Adjudicator description:Debate judge
/add-reaction-role message_id:123456789012345678 emoji:👀 role:@Spectator description:Tournament observer
```

**Finding Message ID:**
1. Enable Developer Mode in Discord settings
2. Right-click on the reaction role message
3. Select "Copy ID"

### `/remove-reaction-role`
**Description:** Remove a role option from a reaction role message.

**Parameters:**
- `message_id` (required): Discord message ID of the reaction role message
- `emoji` (required): Emoji to remove from the message

**Usage:**
```
/remove-reaction-role message_id:123456789012345678 emoji:🥊
```

---

## 🛠️ Admin Commands

### `/autorole`
**Description:** Set up automatic role assignment for new members.

**Parameters:**
- `role` (required): Role to automatically assign to new members
- `enabled` (optional): Whether to enable or disable autorole (default: true)

**Usage Examples:**
```
/autorole role:@Member enabled:true
/autorole role:@Newcomer
/autorole enabled:false  # Disable autorole
```

### `/setup-logging`
**Description:** Configure comprehensive server logging.

**Parameters:**
- `log_channel` (required): Channel where logs will be sent
- `events` (optional): Specific events to log (default: all)

**Usage Examples:**
```
/setup-logging log_channel:#mod-logs
/setup-logging log_channel:#audit-log events:message_delete,member_join
```

**Logged Events:**
- Member join/leave events
- Message edits and deletions
- Role assignments and removals
- Channel creation, deletion, and modifications
- Voice channel activities
- Moderation actions (kicks, bans, timeouts)

### `/setup-moderation`
**Description:** Set up automated moderation features.

**Parameters:**
- `enabled` (required): Whether to enable auto-moderation
- `spam_limit` (optional): Messages per minute before triggering spam detection
- `auto_timeout` (optional): Whether to automatically timeout offenders

**Usage Examples:**
```
/setup-moderation enabled:true spam_limit:5 auto_timeout:true
/setup-moderation enabled:false
```

### `/config`
**Description:** View and manage server configuration.

**Parameters:**
- `setting` (optional): Specific setting to view or modify
- `value` (optional): New value for the setting

**Usage Examples:**
```
/config  # View all settings
/config setting:prefix value:!
/config setting:welcome_channel value:#general
```

### `/unmute`
**Description:** Unmute a member in voice channels.

**Parameters:**
- `member` (required): Member to unmute

**Usage:**
```
/unmute member:@username
```

### `/undeafen`
**Description:** Undeafen a member in voice channels.

**Parameters:**
- `member` (required): Member to undeafen

**Usage:**
```
/undeafen member:@username
```

---

## 📊 Information Commands

### `/ping`
**Description:** Check bot latency and response time.

**Parameters:** None

**Usage:**
```
/ping
```

**Output:**
- Bot latency to Discord API
- Database connection status
- Websocket heartbeat
- Command processing time

### `/help`
**Description:** Display comprehensive help information.

**Parameters:**
- `command` (optional): Get help for a specific command
- `category` (optional): Get help for a command category

**Usage Examples:**
```
/help
/help command:timer
/help category:tournament
```

**Categories Available:**
- **tournament**: Tournament setup and management
- **timer**: Timer and timing utilities
- **debate**: Debate-specific utilities
- **reaction**: Reaction role system
- **admin**: Administrative commands
- **info**: Information and help commands

### `/about`
**Description:** Show detailed bot information and statistics.

**Parameters:** None

**Usage:**
```
/about
```

**Information Displayed:**
- Bot version and uptime
- Server count and user count
- Command usage statistics
- Feature overview
- Support and documentation links

---

## 🔧 Utility Commands

### `/server-info`
**Description:** Display information about the current server.

**Parameters:** None

**Usage:**
```
/server-info
```

**Information Displayed:**
- Server name, ID, and creation date
- Owner information
- Member count and online status
- Channel and role counts
- Server features and boosts

### `/user-info`
**Description:** Display information about a user.

**Parameters:**
- `user` (optional): User to get information about (default: yourself)

**Usage Examples:**
```
/user-info
/user-info user:@username
```

**Information Displayed:**
- User ID and account creation date
- Server join date
- Roles and permissions
- Activity status

---

## 🎯 Command Permissions

### Permission Levels

#### **Everyone**
- `/ping`, `/help`, `/about`
- `/timer`, `/timer-stop`, `/timer-pause`
- `/randommotion`, `/coinflip`, `/diceroll`
- `/toss`, `/ap-toss`, `/bp-toss`
- `/currenttime`
- `/server-info`, `/user-info`

#### **Manage Roles Permission**
- `/reactionrole`, `/add-reaction-role`, `/remove-reaction-role`
- `/autorole`

#### **Manage Channels Permission**
- `/create_tournament`
- `/setup-logging`

#### **Administrator Permission**
- `/setup-moderation`
- `/config`
- All admin commands

#### **Voice Channel Permissions**
- `/unmute`, `/undeafen` (requires appropriate voice permissions)

---

## 🚨 Error Handling

### Common Error Messages

#### "Missing Permissions"
**Cause:** Bot lacks required permissions for the command
**Solution:** Ensure bot has appropriate permissions in server settings

#### "Invalid Duration Format"
**Cause:** Timer duration not in MM:SS format
**Solution:** Use format like "07:00" for 7 minutes

#### "Message Not Found"
**Cause:** Invalid message ID for reaction role commands
**Solution:** Ensure message exists and ID is correct

#### "Role Not Found"
**Cause:** Specified role doesn't exist or bot cannot access it
**Solution:** Check role name/mention and bot's role hierarchy

#### "Database Connection Error"
**Cause:** Cannot connect to MongoDB database
**Solution:** Check database configuration and connection string

### Command Cooldowns

Most commands have cooldowns to prevent spam:
- **Tournament commands:** 30 seconds
- **Timer commands:** 5 seconds
- **Utility commands:** 3 seconds
- **Admin commands:** 10 seconds

---

## 💡 Tips and Best Practices

### Tournament Setup
1. **Plan your tournament structure** before running `/create_tournament`
2. **Test permissions** with a small number of venues first
3. **Inform participants** about role assignment process
4. **Use descriptive venue names** if customizing

### Timer Usage
1. **Set appropriate durations** for different speech types
2. **Use public timers** for shared activities like prep time
3. **Test timer controls** before important events
4. **Remember each user** can have their own timer

### Reaction Roles
1. **Choose appropriate modes** for your use case
2. **Use clear descriptions** for each role option
3. **Test thoroughly** before announcing to users
4. **Keep role hierarchies** in mind

### Server Management
1. **Set up logging** before other features for audit trails
2. **Configure moderation** gradually to avoid false positives
3. **Regular backups** of important configurations
4. **Monitor command usage** through logs

---

*For more detailed information, see the main [README.md](README.md) file.*