# 🏆 Tournament System Documentation

This document provides comprehensive information about the tournament management system in Hear! Hear! Bot.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Tournament Formats](#tournament-formats)
3. [Setup Process](#setup-process)
4. [Channel Structure](#channel-structure)
5. [Role System](#role-system)
6. [Permissions & Access Control](#permissions--access-control)
7. [Role Assignment System](#role-assignment-system)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## 🎯 Overview

The tournament system in Hear! Hear! Bot is designed to automate the complete setup of debate tournaments on Discord. With a single command, you can create:

- **Tournament-specific roles** with proper permissions
- **Organized channel structure** with categories and voice channels
- **Venue-specific channels** with capacity controls
- **Role assignment system** with reaction-based selection
- **Proper permission structure** for different participant types

### Supported Formats
- **Asian Parliamentary (AP)** - 2 teams per venue
- **British Parliamentary (BP)** - 4 teams per venue

### Key Features
- **Scalable:** Support for 1-20 venues
- **Automated:** Complete setup with one command
- **Flexible:** Optional role and assignment setup
- **Secure:** Proper permission controls
- **Organized:** Logical channel categorization

## 🏛️ Tournament Formats

### Asian Parliamentary (AP)

#### Structure
- **2 teams per venue:** Government vs Opposition
- **2 prep rooms per venue:** Gov-Prep, Opp-Prep
- **Capacity:** 3 members per prep room
- **Total participants per venue:** Up to 6 debaters + adjudicators

#### Typical Use Cases
- School debate competitions
- Regional tournaments
- Training sessions
- Smaller-scale events

#### Advantages
- Simpler structure for beginners
- Easier to manage with fewer participants
- Clear Government vs Opposition dynamic
- More speaking time per participant

### British Parliamentary (BP)

#### Structure
- **4 teams per venue:** Opening Government (OG), Opening Opposition (OO), Closing Government (CG), Closing Opposition (CO)
- **4 prep rooms per venue:** OG-Prep, OO-Prep, CG-Prep, CO-Prep
- **Capacity:** 2 members per prep room
- **Total participants per venue:** Up to 8 debaters + adjudicators

#### Typical Use Cases
- University tournaments
- International competitions
- World Championships format
- Large-scale events

#### Advantages
- More complex strategic dynamics
- Higher participant density
- Standard for major competitions
- More diverse argumentation

## 🚀 Setup Process

### Basic Command
```
/create_tournament tournament_type:BP venues:5 setup_roles:true setup_role_assignment:true
```

### Setup Parameters

#### `tournament_type` (Required)
- **AP**: Asian Parliamentary format
- **BP**: British Parliamentary format

#### `venues` (Required)
- **Range:** 1-20 venues
- **Recommendation:** Start with fewer venues for testing

#### `setup_roles` (Optional, default: true)
- **true**: Creates Debater, Adjudicator, and Spectator roles
- **false**: Skip role creation (use existing roles)

#### `setup_role_assignment` (Optional, default: true)
- **true**: Creates role assignment channel with reactions
- **false**: Manual role assignment required

### Setup Process Flow

1. **Validation**
   - Check user permissions (Manage Channels)
   - Validate parameter ranges
   - Check for existing tournament setup

2. **Role Creation** (if enabled)
   - Create Debater role (🥊, blue color)
   - Create Adjudicator role (⚖️, gold color)
   - Create Spectator role (👀, light grey color)

3. **Category Creation**
   - Welcome
   - Info Desk
   - Feedback & Check-in
   - Grand Auditorium
   - Venue categories (1 per venue)

4. **Channel Creation**
   - General channels in each category
   - Venue-specific channels with proper permissions
   - Voice channels with capacity limits

5. **Permission Setup**
   - Role-based channel access
   - Capacity controls for voice channels
   - Special permissions for adjudicators

6. **Role Assignment** (if enabled)
   - Create role-assignment channel
   - Add reaction role message
   - Configure emoji reactions

## 🏗️ Channel Structure

### Category: Welcome
**Purpose:** Initial information and role assignment

#### Channels Created:
- **📄 welcome** - General welcome message and tournament info
- **📋 instructions-for-teams** - Detailed team instructions
- **📋 instructions-for-adjudicators** - Adjudicator-specific guidelines
- **⚖️ equity-policy** - Tournament equity and conduct policies
- **🚨 report-problems** - Channel for reporting issues
- **🎭 role-assignment** - Reaction-based role selection

**Permissions:**
- **Everyone:** Read messages
- **Debater/Adjudicator/Spectator:** Send messages in appropriate channels

### Category: Info Desk
**Purpose:** Technical support and scheduling information

#### Channels Created:
- **🤖 bot-commands** - Bot command usage and testing
- **📅 schedules** - Tournament schedule and timing
- **🛠️ tech-support** - Technical assistance

**Permissions:**
- **Everyone:** Read and send messages
- **Adjudicator:** Additional moderation permissions

### Category: Feedback & Check-in
**Purpose:** Tournament administration and feedback

#### Channels Created:
- **📝 feedback-submission** - Participant feedback collection
- **✅ check-in** - Team check-in and attendance
- **✅ check-out** - End-of-round check-out

**Permissions:**
- **Debater/Adjudicator:** Full access
- **Spectator:** Read-only access

### Category: Grand Auditorium
**Purpose:** Main tournament communications and announcements

#### Channels Created:
- **📢 announcements** - Official tournament announcements
- **❓ motion-clarifications** - Motion and rule clarifications
- **📊 draws-and-motion-release** - Round draws and motion releases
- **⚖️ equity-announcements** - Equity-related announcements
- **🎵 music-control** - Background music control
- **🔗 important-links** - Important tournament links
- **💬 auditorium-text** - General text chat
- **🔊 Grand-Auditorium** - Main voice channel for announcements

**Permissions:**
- **Adjudicator:** Send messages, manage voice
- **Debater/Spectator:** Limited send permissions in some channels
- **Everyone:** Connect to voice channel

### Per-Venue Categories
**Purpose:** Individual venue management

#### British Parliamentary (BP) Venues:
Each venue creates:
- **💬 venue-N-debate** - Text discussion for the venue
- **🔊 Venue-N-Debate** - Main debate voice channel
- **🔒 Venue-N-OG-Prep** - Opening Government prep room (2 person limit)
- **🔒 Venue-N-OO-Prep** - Opening Opposition prep room (2 person limit)
- **🔒 Venue-N-CG-Prep** - Closing Government prep room (2 person limit)
- **🔒 Venue-N-CO-Prep** - Closing Opposition prep room (2 person limit)
- **⚖️ venue-N-result-discussion** - Adjudicator-only result discussion

#### Asian Parliamentary (AP) Venues:
Each venue creates:
- **💬 venue-N-debate** - Text discussion for the venue
- **🔊 Venue-N-Debate** - Main debate voice channel
- **🔒 Venue-N-Gov-Prep** - Government prep room (3 person limit)
- **🔒 Venue-N-Opp-Prep** - Opposition prep room (3 person limit)
- **⚖️ venue-N-result-discussion** - Adjudicator-only result discussion

**Permissions:**
- **Debater:** Access to prep rooms, main debate channel
- **Adjudicator:** Access to all channels including result discussion
- **Spectator:** Read-only access to main debate channel

## 👥 Role System

### 🥊 Debater Role
**Color:** Blue (`#3498db`)
**Icon:** 🥊 (Boxing Glove)

#### Permissions:
- **Text Channels:**
  - Read/send in general channels
  - Read/send in venue debate channels
  - Cannot access result discussion channels
- **Voice Channels:**
  - Connect to prep rooms (subject to capacity)
  - Connect to main debate channels
  - Cannot access adjudicator-only channels

#### Access Level:
- **Welcome category:** Full access except role-assignment (reaction only)
- **Info Desk category:** Full access
- **Feedback category:** Full access
- **Grand Auditorium:** Limited send permissions in some channels
- **Venue categories:** Access to prep rooms and main debate channels

### ⚖️ Adjudicator Role
**Color:** Gold (`#f1c40f`)
**Icon:** ⚖️ (Balance Scale)

#### Permissions:
- **Text Channels:**
  - Read/send in all channels
  - Access to result discussion channels
  - Moderation permissions in most channels
- **Voice Channels:**
  - Connect to all voice channels
  - Mute/deafen participants
  - Move members between channels

#### Special Permissions:
- **Manage Messages:** In venue and general channels
- **Mute Members:** In voice channels
- **Deafen Members:** In voice channels
- **Move Members:** Between voice channels

#### Access Level:
- **All categories:** Full access
- **Venue-specific:** Access to result discussion channels
- **Moderation:** Enhanced permissions for tournament management

### 👀 Spectator Role
**Color:** Light Grey (`#95a5a6`)
**Icon:** 👀 (Eyes)

#### Permissions:
- **Text Channels:**
  - Read messages in most channels
  - Limited send permissions
  - Cannot access prep areas or result discussions
- **Voice Channels:**
  - Cannot connect to most voice channels
  - Read-only access to main announcements

#### Access Level:
- **Welcome category:** Read-only access
- **Info Desk category:** Read-only access
- **Feedback category:** Read-only access
- **Grand Auditorium:** Listen to announcements, limited text
- **Venue categories:** Read-only access to main debate channels

## 🔐 Permissions & Access Control

### Channel Permission Structure

#### Public Channels (Everyone can access)
- **welcome**
- **bot-commands**
- **schedules**
- **tech-support**

#### Role-Restricted Channels

**Debater + Adjudicator Only:**
- **instructions-for-teams**
- **feedback-submission**
- **check-in**
- **check-out**
- **venue-N-debate** (text)

**Adjudicator Only:**
- **venue-N-result-discussion**
- **equity-announcements** (send messages)

**Voice Channel Restrictions:**
- **Prep rooms:** Role-based access with capacity limits
- **Main debate channels:** Debater and Adjudicator access
- **Grand Auditorium:** Everyone can listen, limited speaking

### Capacity Controls

#### British Parliamentary (BP):
- **Prep rooms:** 2 person limit each
- **Main debate:** 10 person limit (4 teams + adjudicators)

#### Asian Parliamentary (AP):
- **Prep rooms:** 3 person limit each
- **Main debate:** 8 person limit (2 teams + adjudicators)

#### Grand Channels:
- **Grand Auditorium:** 50 person limit for large announcements

### Override Permissions

#### Server Administrators:
- Full access to all channels regardless of tournament roles
- Can modify tournament setup
- Can manage roles and permissions

#### Bot Role:
- Must be above tournament roles in hierarchy
- Requires Manage Channels, Manage Roles permissions
- Needs Send Messages and Connect permissions

## 🎭 Role Assignment System

### Reaction Role Setup

When `setup_role_assignment:true`, the bot creates a reaction role system in the **🎭 role-assignment** channel.

#### Message Content:
```
🏆 **Tournament Role Assignment**

React with the appropriate emoji to get your tournament role:

🥊 - **Debater**: Active debate participant
⚖️ - **Adjudicator**: Debate judge and moderator  
👀 - **Spectator**: Tournament observer

You can only have one tournament role at a time. Reacting will automatically remove your previous tournament role.
```

#### Reaction Configuration:
- **Mode:** Unique (one role per person)
- **🥊 Emoji:** Assigns Debater role
- **⚖️ Emoji:** Assigns Adjudicator role
- **👀 Emoji:** Assigns Spectator role

### Role Assignment Process

1. **User reacts** with desired emoji
2. **Bot removes** any existing tournament role
3. **Bot assigns** new tournament role
4. **Channels become visible** based on new role
5. **User gains access** to appropriate voice channels

### Manual Role Assignment

If `setup_role_assignment:false`, administrators must manually assign roles using:
- Discord's role management interface
- Bot commands (if available)
- Other role assignment bots

### Role Switching

Users can switch roles by:
1. **Reacting** with a different emoji (automatic removal of old role)
2. **Manual assignment** by administrators
3. **Removing current role** and reacting again

## 📝 Best Practices

### Pre-Tournament Setup

#### Planning Phase:
1. **Determine tournament format** (AP vs BP)
2. **Calculate venue requirements** based on participant count
3. **Plan staff roles** (who will be adjudicators)
4. **Prepare welcome materials** and instructions

#### Technical Setup:
1. **Test with small venue count** first (1-2 venues)
2. **Verify bot permissions** before main setup
3. **Prepare backup plans** for technical issues
4. **Train staff** on Discord interface

### During Tournament

#### Role Management:
1. **Monitor role assignment** in role-assignment channel
2. **Assist participants** with role selection
3. **Handle role conflicts** promptly
4. **Maintain adjudicator coverage** across venues

#### Channel Management:
1. **Guide participants** to correct venues
2. **Monitor capacity limits** in prep rooms
3. **Facilitate tech support** requests
4. **Manage announcements** effectively

### Post-Tournament

#### Cleanup:
1. **Archive important discussions** before cleanup
2. **Export feedback** and logs if needed
3. **Consider keeping structure** for future events
4. **Document lessons learned** for improvement

## 🐛 Troubleshooting

### Common Issues

#### "Bot lacks permissions"
**Cause:** Bot role is below tournament roles or lacks required permissions
**Solution:** 
1. Move bot role above tournament roles in server settings
2. Ensure bot has Manage Channels and Manage Roles permissions

#### "Channels not visible to users"
**Cause:** Users don't have the correct tournament role
**Solution:**
1. Check role assignment in role-assignment channel
2. Manually assign roles if reaction system fails
3. Verify role permissions in channel settings

#### "Voice channel capacity reached"
**Cause:** Too many users trying to join prep rooms
**Solution:**
1. Check prep room capacity limits (2 for BP, 3 for AP)
2. Guide overflow participants to correct teams
3. Consider creating additional prep rooms if needed

#### "Role assignment reactions not working"
**Cause:** Database connection issues or reaction role setup problems
**Solution:**
1. Check bot logs for database errors
2. Try manual role assignment temporarily
3. Recreate role assignment message if needed

### Permission Debugging

#### Check Bot Role Position:
1. Go to Server Settings → Roles
2. Ensure bot role is above Debater, Adjudicator, Spectator roles
3. Bot needs permission to manage roles below it

#### Verify Required Permissions:
- **Manage Channels:** Required for channel creation
- **Manage Roles:** Required for role creation and assignment
- **Send Messages:** Required for role assignment messages
- **Add Reactions:** Required for reaction role setup
- **Manage Messages:** Required for reaction role management

#### Test Permission Inheritance:
1. Check category permissions
2. Verify channel-specific overrides
3. Test with different roles

### Database Issues

#### MongoDB Connection:
- Verify connection string in environment variables
- Check database server status
- Test connection independently

#### Reaction Role Storage:
- Check reaction_roles collection in database
- Verify message IDs are correctly stored
- Test reaction role functionality

### Recovery Procedures

#### Partial Setup Failure:
1. **Document** what was created successfully
2. **Complete setup manually** for missing components
3. **Update permissions** as needed
4. **Test functionality** before proceeding

#### Complete Setup Failure:
1. **Clean up** any partially created channels/roles
2. **Check and fix** permission issues
3. **Retry setup** with fewer venues for testing
4. **Contact support** if issues persist

---

*For additional help, refer to the [Commands Reference](COMMANDS.md) or contact support.*