# 🎭 Carl-bot Style Features Documentation

This document covers the Carl-bot inspired features in Hear! Hear! Bot, including reaction roles, logging, and moderation systems.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Reaction Roles System](#reaction-roles-system)
3. [Logging System](#logging-system)
4. [Auto-Moderation](#auto-moderation)
5. [Auto-Role System](#auto-role-system)
6. [Configuration Management](#configuration-management)
7. [Database Schema](#database-schema)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## 🎯 Overview

The Carl-bot style features provide comprehensive server management capabilities that are essential for running organized Discord communities, particularly debate tournaments and academic servers.

### Key Features
- **Advanced Reaction Roles** - Multiple modes for flexible role assignment
- **Comprehensive Logging** - Track all server activities
- **Auto-Moderation** - Automated rule enforcement
- **Auto-Role** - Automatic role assignment for new members
- **Configuration Management** - Persistent server settings

### Database Dependency
These features require MongoDB for persistent storage. Without a database connection:
- Reaction roles will not work
- Logging configurations will not persist
- Auto-moderation settings will reset on restart

## 🎭 Reaction Roles System

### Overview
The reaction role system allows users to assign/remove roles by reacting to messages with specific emojis. This is essential for tournament role assignment and server organization.

### Available Modes

#### 1. Normal Mode
**Behavior:** Standard reaction role functionality
- Users can add multiple roles by reacting
- Users can remove roles by unreacting
- No restrictions on role combinations

**Use Cases:**
- Optional server roles (notifications, interests)
- Non-exclusive role assignments
- General purpose role selection

**Example:**
```
/reactionrole title:"Optional Roles" description:"Choose your interests!" mode:normal
```

#### 2. Unique Mode ⭐ (Most Popular)
**Behavior:** Only one role per message allowed
- Reacting with a new emoji removes the previous role
- Users can only have one role from this message at a time
- Automatic role switching

**Use Cases:**
- Tournament role selection (Debater/Adjudicator/Spectator)
- Skill level selection (Beginner/Intermediate/Advanced)
- Team selection

**Example:**
```
/reactionrole title:"Tournament Roles" description:"Choose your role:" mode:unique
```

#### 3. Verify Mode
**Behavior:** Requires confirmation before role assignment
- Initial reaction prompts for confirmation
- Second reaction within time limit assigns role
- Prevents accidental role assignment

**Use Cases:**
- Important roles with privileges
- Roles that change server access significantly
- Administrative role assignment

**Example:**
```
/reactionrole title:"Moderator Application" description:"Confirm your application:" mode:verify
```

#### 4. Reversed Mode
**Behavior:** Reactions remove roles instead of adding them
- Users must already have the role
- Reacting removes the role from the user
- Useful for opt-out systems

**Use Cases:**
- Default roles that users can opt out of
- Ping roles that are assigned by default
- Punishment role removal systems

**Example:**
```
/reactionrole title:"Opt Out" description:"React to disable notifications:" mode:reversed
```

#### 5. Binding Mode ⚠️
**Behavior:** Roles cannot be removed once assigned
- Reacting assigns the role permanently
- Unreacting does not remove the role
- Use with extreme caution

**Use Cases:**
- Verification systems
- One-time access grants
- Permanent certification roles

**Example:**
```
/reactionrole title:"Server Verification" description:"React to verify (permanent):" mode:binding
```

#### 6. Temporary Mode
**Behavior:** Roles expire after a set time
- Roles are automatically removed after duration
- Useful for event-specific access
- Configurable expiration time

**Use Cases:**
- Event participant roles
- Temporary access permissions
- Time-limited privileges

**Example:**
```
/reactionrole title:"Event Access" description:"24-hour event access:" mode:temporary
```

### Setup Process

#### 1. Create Reaction Role Message
```
/reactionrole title:"Your Title" description:"Your description" mode:unique channel:#role-selection
```

#### 2. Add Role Options
```
/add-reaction-role message_id:123456789 emoji:🥊 role:@Debater description:Active debate participant
/add-reaction-role message_id:123456789 emoji:⚖️ role:@Adjudicator description:Debate judge
/add-reaction-role message_id:123456789 emoji:👀 role:@Spectator description:Tournament observer
```

#### 3. Test the System
- React with different emojis
- Verify role assignment/removal
- Test mode-specific behavior

### Advanced Features

#### Custom Emojis
```
/add-reaction-role message_id:123456789 emoji:<:custom_emoji:123456789> role:@Role
```

#### Role Limits
- Configure maximum users per role
- Automatic cutoff when limit reached
- First-come, first-served basis

#### Self-Destruct Messages
- Messages auto-delete after specified time
- Useful for temporary role assignments
- Prevents channel clutter

#### Cross-Server Support
- Reaction roles work across multiple servers
- Shared database for role configurations
- Consistent behavior across servers

### Message Formatting

The bot automatically formats reaction role messages with:
- **Embed title** with your specified title
- **Description** with role information
- **Footer** with mode information and instructions
- **Color coding** based on mode type
- **Emoji reactions** automatically added

Example output:
```
🎭 Tournament Role Selection

Choose your tournament role by reacting below:

🥊 **Debater** - Active debate participant
⚖️ **Adjudicator** - Debate judge and moderator
👀 **Spectator** - Tournament observer

Mode: Unique (one role only)
React to assign, unreact to remove
```

## 📊 Logging System

### Overview
The logging system provides comprehensive audit trails for all server activities. Essential for tournament management and server moderation.

### Logged Events

#### Message Events
- **Message Delete** - Who deleted what message when
- **Message Edit** - Original and edited content with timestamps
- **Bulk Delete** - Mass message deletion events
- **Message Pin/Unpin** - Message pinning activities

#### Member Events
- **Member Join** - New member arrivals with account age
- **Member Leave** - Member departures (leave vs kick vs ban)
- **Nickname Change** - Old and new nicknames
- **Avatar Change** - Profile picture updates
- **Member Update** - Status and activity changes

#### Role Events
- **Role Assignment** - Who gave what role to whom
- **Role Removal** - Role removal tracking
- **Role Creation** - New role creation
- **Role Deletion** - Role deletion events
- **Role Modification** - Permission and name changes

#### Channel Events
- **Channel Creation** - New channel creation
- **Channel Deletion** - Channel removal
- **Channel Modification** - Name, topic, permission changes
- **Channel Category Changes** - Channel organization updates

#### Voice Events
- **Voice Join** - Users joining voice channels
- **Voice Leave** - Users leaving voice channels
- **Voice Move** - Users moved between channels
- **Voice Mute/Unmute** - Voice moderation actions
- **Voice Deafen/Undeafen** - Voice privacy actions

#### Moderation Events
- **Kicks** - Member kick events with reason
- **Bans** - Ban events with duration and reason
- **Timeouts** - Temporary restrictions
- **Warning Issues** - Formal warnings given
- **Auto-Moderation** - Automated actions taken

### Setup Process

#### 1. Configure Logging Channel
```
/setup-logging log_channel:#mod-logs events:all
```

#### 2. Specify Events (Optional)
```
/setup-logging log_channel:#audit-log events:message_delete,member_join,role_assign
```

#### 3. Multiple Log Channels
```
/setup-logging log_channel:#message-logs events:message_delete,message_edit
/setup-logging log_channel:#member-logs events:member_join,member_leave
/setup-logging log_channel:#mod-logs events:kick,ban,timeout
```

### Log Format

#### Message Delete Example:
```
🗑️ **Message Deleted**

**Author:** @username#1234 (123456789)
**Channel:** #general
**Deleted by:** @moderator#5678
**Time:** 2025-09-21 15:30:25 UTC

**Content:**
```
This was the deleted message content
```

**Attachments:** image.png (uploaded)
```

#### Member Join Example:
```
📥 **Member Joined**

**User:** @newuser#9876 (987654321)
**Account Created:** 2025-09-15 (6 days ago)
**Join Time:** 2025-09-21 15:30:25 UTC
**Member Count:** 150

**Account Flags:** Verified Email
```

#### Role Assignment Example:
```
🎭 **Role Assigned**

**User:** @username#1234 (123456789)
**Role:** @Debater
**Assigned by:** @admin#5555
**Time:** 2025-09-21 15:30:25 UTC
**Method:** Reaction Role (Message: 987654321)
```

### Advanced Logging Features

#### Webhook Integration
- Custom webhook URLs for external logging
- Integration with external monitoring systems
- Discord webhook support for formatted logs

#### Log Filtering
- Filter by user, channel, or event type
- Exclude bot actions (optional)
- Time-based filtering

#### Log Retention
- Automatic log cleanup after specified time
- Archive old logs to external storage
- Database optimization for large servers

#### Log Analytics
- Event frequency tracking
- User activity patterns
- Moderation action statistics

## 🛡️ Auto-Moderation

### Overview
The auto-moderation system automatically enforces server rules and maintains order, especially useful during busy tournament periods.

### Detection Systems

#### Spam Detection
- **Message Rate Limiting** - Too many messages per minute
- **Duplicate Content** - Repeated message detection
- **Mass Mentions** - Excessive @mentions in messages
- **Link Spam** - Repeated link posting

**Configuration:**
```
/setup-moderation enabled:true spam_limit:5 duplicate_limit:3
```

#### Content Filtering
- **Profanity Filter** - Customizable word blacklist
- **Link Filtering** - Block suspicious or inappropriate links
- **Invite Filtering** - Block Discord server invites
- **All Caps Detection** - Excessive capitalization

**Configuration:**
```
/config setting:profanity_filter value:enabled
/config setting:link_filter value:strict
/config setting:caps_limit value:70
```

#### Raid Protection
- **Mass Join Detection** - Unusual member join patterns
- **Account Age Filtering** - Block very new accounts
- **Verification Requirements** - Enhanced verification during raids
- **Auto-Lockdown** - Temporary channel restrictions

**Configuration:**
```
/config setting:raid_protection value:enabled
/config setting:min_account_age value:7
/config setting:verification_level value:high
```

### Automated Actions

#### Warning System
- **First Offense** - Automatic warning message
- **Strike Accumulation** - Track user violations
- **Escalation Rules** - Increasing punishment severity
- **Warning Expiry** - Warnings expire after time

#### Temporary Restrictions
- **Message Timeout** - Prevent message sending
- **Voice Timeout** - Remove voice permissions
- **Channel Restrictions** - Block access to specific channels
- **Role Removal** - Temporarily remove roles

#### Escalation Actions
- **Automatic Kicks** - Remove from server temporarily
- **Temporary Bans** - Time-limited server bans
- **Permanent Bans** - Permanent removal
- **Staff Notifications** - Alert human moderators

### Moderation Logs

All auto-moderation actions are logged with:
- **User Information** - Who was affected
- **Action Taken** - What was done
- **Reason** - Why action was taken
- **Evidence** - Screenshots, message content
- **Moderator Override** - Manual review options

### Whitelist System

#### Channel Whitelist
- Exclude specific channels from auto-moderation
- Useful for testing or staff channels
- Event-specific temporary exemptions

#### Role Whitelist
- Exempt certain roles from auto-moderation
- Staff and trusted member exemptions
- Tournament-specific role protections

#### User Whitelist
- Individual user exemptions
- VIP or special guest protections
- Temporary exemption system

## 👥 Auto-Role System

### Overview
Automatically assign roles to new members when they join the server. Essential for establishing base permissions and channel access.

### Setup
```
/autorole role:@Member enabled:true
```

### Features

#### Single Role Assignment
- Assign one default role to all new members
- Immediate access to basic server features
- Foundation for permission structure

#### Multiple Role Assignment
- Assign multiple roles simultaneously
- Different roles for different join methods
- Conditional role assignment

#### Delayed Assignment
- Assign roles after a waiting period
- Verification-based role assignment
- Anti-raid protection

#### Welcome Integration
- Combine with welcome messages
- Role assignment announcements
- Custom welcome workflows

### Configuration Options

#### Basic Setup
```
/autorole role:@Newcomer enabled:true delay:0
```

#### Advanced Setup
```
/config setting:autorole_roles value:@Member,@Verified
/config setting:autorole_delay value:300
/config setting:autorole_channel value:#welcome
```

#### Conditional Rules
- Account age requirements
- Verification level requirements
- Invite source-based assignment
- Server boost-based bonus roles

## ⚙️ Configuration Management

### Overview
Persistent configuration storage for all Carl-bot features, ensuring settings survive bot restarts.

### Available Settings

#### General Settings
- **Prefix** - Command prefix (if using text commands)
- **Language** - Bot response language
- **Timezone** - Server timezone for logs
- **Welcome Channel** - Default welcome channel

#### Moderation Settings
- **Auto-Mod Enabled** - Enable/disable auto-moderation
- **Spam Limits** - Message rate limits
- **Filter Settings** - Content filtering configuration
- **Action Escalation** - Punishment progression rules

#### Logging Settings
- **Log Channels** - Different channels for different events
- **Event Filters** - Which events to log
- **Log Format** - Custom log message formatting
- **Retention Policy** - How long to keep logs

#### Role Settings
- **Auto-Role Configuration** - Default role assignment
- **Reaction Role Defaults** - Default settings for new reaction roles
- **Role Hierarchy** - Automatic role organization
- **Permission Templates** - Preset permission configurations

### Commands

#### View All Settings
```
/config
```

#### View Specific Setting
```
/config setting:auto_mod
```

#### Modify Setting
```
/config setting:spam_limit value:3
```

#### Reset to Defaults
```
/config setting:auto_mod value:default
```

### Setting Categories

#### Server Management
- Auto-role configurations
- Welcome message settings
- Channel organization rules
- Permission defaults

#### Content Moderation
- Auto-moderation sensitivity
- Filter word lists
- Link whitelist/blacklist
- Punishment escalation rules

#### Event Logging
- Log channel assignments
- Event type filtering
- Log message formatting
- Webhook integrations

#### User Experience
- Command cooldowns
- Response message styling
- Help message customization
- Feature enable/disable toggles

## 🗄️ Database Schema

### Collections Overview

The Carl-bot features use several MongoDB collections for data persistence:

#### `reaction_role_configs`
Stores reaction role message configurations:
```json
{
  "_id": ObjectId("..."),
  "guild_id": "123456789",
  "message_id": "987654321",
  "channel_id": "555666777",
  "mode": "unique",
  "self_destruct": null,
  "created_at": ISODate("2025-09-21T00:00:00Z"),
  "created_by": "user_id"
}
```

#### `reaction_roles`
Stores individual role-emoji mappings:
```json
{
  "_id": ObjectId("..."),
  "message_id": "987654321",
  "emoji": "🥊",
  "emoji_id": null,
  "role_id": "111222333",
  "description": "Active debate participant",
  "max_uses": null,
  "current_uses": 0
}
```

#### `logging_configs`
Stores server logging configurations:
```json
{
  "_id": ObjectId("..."),
  "guild_id": "123456789",
  "general_log_channel": "444555666",
  "moderation_log_channel": "777888999",
  "message_log_channel": "111222333",
  "member_log_channel": "444555666",
  "events": ["message_delete", "member_join", "role_assign"],
  "webhook_url": null,
  "enabled": true
}
```

#### `moderation_configs`
Stores auto-moderation settings:
```json
{
  "_id": ObjectId("..."),
  "guild_id": "123456789",
  "enabled": true,
  "spam_limit": 5,
  "duplicate_limit": 3,
  "caps_limit": 70,
  "link_filter": true,
  "invite_filter": true,
  "profanity_filter": ["word1", "word2"],
  "whitelist_channels": ["channel_id1"],
  "whitelist_roles": ["role_id1"],
  "escalation_rules": {
    "warnings": 3,
    "timeout_duration": 600,
    "ban_threshold": 5
  }
}
```

#### `guild_configs`
Stores general server configurations:
```json
{
  "_id": ObjectId("..."),
  "guild_id": "123456789",
  "prefix": "!",
  "language": "en",
  "timezone": "UTC",
  "welcome_channel": "channel_id",
  "autorole_enabled": true,
  "autorole_roles": ["role_id1", "role_id2"],
  "autorole_delay": 0,
  "settings": {
    "key": "value"
  }
}
```

#### `user_warnings`
Stores user warning history:
```json
{
  "_id": ObjectId("..."),
  "guild_id": "123456789",
  "user_id": "987654321",
  "warnings": [
    {
      "id": "warning_id",
      "reason": "Spam",
      "moderator": "mod_id",
      "timestamp": ISODate("2025-09-21T00:00:00Z"),
      "expired": false
    }
  ],
  "total_warnings": 1,
  "last_warning": ISODate("2025-09-21T00:00:00Z")
}
```

### Database Indexes

For optimal performance, create these indexes:

```javascript
// Reaction roles
db.reaction_role_configs.createIndex({ "guild_id": 1 })
db.reaction_role_configs.createIndex({ "message_id": 1 })
db.reaction_roles.createIndex({ "message_id": 1 })

// Logging
db.logging_configs.createIndex({ "guild_id": 1 })

// Moderation
db.moderation_configs.createIndex({ "guild_id": 1 })
db.user_warnings.createIndex({ "guild_id": 1, "user_id": 1 })

// General configs
db.guild_configs.createIndex({ "guild_id": 1 })
```

## 📝 Best Practices

### Reaction Roles

#### Planning
1. **Determine role purpose** before creating reaction roles
2. **Choose appropriate mode** for your use case
3. **Plan emoji selection** - use clear, recognizable emojis
4. **Consider role hierarchy** and permissions

#### Implementation
1. **Test with staff first** before announcing to users
2. **Use descriptive role names** and descriptions
3. **Monitor initial usage** for issues
4. **Provide clear instructions** to users

#### Maintenance
1. **Regular audits** of role assignments
2. **Clean up unused roles** periodically
3. **Update descriptions** as roles evolve
4. **Monitor for abuse** or misuse

### Logging

#### Channel Organization
1. **Separate log channels** by event type
2. **Use clear channel names** (e.g., #mod-logs, #message-logs)
3. **Set appropriate permissions** - staff only for most logs
4. **Consider channel position** in server layout

#### Log Management
1. **Regular log review** by staff
2. **Archive old logs** to prevent channel clutter
3. **Set up log rotation** for high-activity servers
4. **Monitor log storage** usage

#### Privacy Considerations
1. **Limit access** to sensitive logs
2. **Consider data retention** policies
3. **Respect user privacy** in logged content
4. **Follow applicable laws** and regulations

### Auto-Moderation

#### Gradual Implementation
1. **Start with logging only** to understand patterns
2. **Gradually increase** auto-mod sensitivity
3. **Monitor false positives** carefully
4. **Adjust settings** based on server culture

#### Whitelist Management
1. **Carefully consider** whitelist additions
2. **Regular review** of whitelisted users/roles
3. **Document exceptions** and reasons
4. **Monitor whitelisted activity**

#### Staff Training
1. **Train staff** on auto-mod systems
2. **Establish override procedures** for false positives
3. **Regular staff meetings** to discuss moderation
4. **Keep manual moderation** skills sharp

### Configuration Management

#### Backup Strategy
1. **Regular config backups** to external storage
2. **Document configuration** changes
3. **Test configuration** restore procedures
4. **Version control** for complex setups

#### Change Management
1. **Plan configuration changes** carefully
2. **Test changes** in development environment
3. **Communicate changes** to staff
4. **Monitor impact** after changes

## 🐛 Troubleshooting

### Common Issues

#### Reaction Roles Not Working

**Issue:** Users react but don't get roles
**Possible Causes:**
- Bot role is below target roles in hierarchy
- Database connection issues
- Missing permissions

**Solutions:**
1. Check bot role position in server settings
2. Verify database connectivity
3. Ensure bot has Manage Roles permission
4. Check reaction role configuration

#### Logging Not Working

**Issue:** Events not being logged
**Possible Causes:**
- Database connection problems
- Incorrect channel permissions
- Event filtering configuration

**Solutions:**
1. Verify database connection
2. Check log channel permissions
3. Review event filter settings
4. Test with simple events first

#### Auto-Moderation False Positives

**Issue:** Legitimate messages being flagged
**Possible Causes:**
- Overly sensitive settings
- Incorrect whitelist configuration
- Cultural/language differences

**Solutions:**
1. Adjust sensitivity settings
2. Add appropriate whitelist entries
3. Review and update filter lists
4. Consider cultural context

### Database Connection Issues

#### Connection Timeout
- Check network connectivity
- Verify MongoDB Atlas IP whitelist
- Test connection string independently

#### Authentication Failures
- Verify username/password in connection string
- Check database user permissions
- Ensure correct database specified

#### SSL Certificate Errors
- Update to latest MongoDB driver
- Use proper SSL configuration
- Check certificate validity

### Performance Issues

#### Slow Reaction Role Response
- Check database query performance
- Verify proper indexes exist
- Monitor bot memory usage

#### High Memory Usage
- Monitor database connection pooling
- Check for memory leaks in logging
- Consider log retention policies

#### Rate Limiting
- Monitor Discord API rate limits
- Implement proper request queuing
- Add delays between bulk operations

### Recovery Procedures

#### Lost Configuration
1. **Check database backups** for configuration recovery
2. **Manually recreate** critical configurations
3. **Document recovery process** for future reference
4. **Implement better backup strategy**

#### Database Corruption
1. **Stop bot immediately** to prevent further issues
2. **Restore from backup** if available
3. **Recreate database** if corruption is severe
4. **Investigate root cause** to prevent recurrence

#### Role Hierarchy Issues
1. **Document current role hierarchy**
2. **Carefully adjust** bot role position
3. **Test role assignment** after changes
4. **Update documentation** with new hierarchy

---

*For more information on setting up these features, see the [Setup Guide](SETUP.md) and [Commands Reference](COMMANDS.md).*