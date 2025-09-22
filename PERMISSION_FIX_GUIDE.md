# 🔧 Tournament Permission Fix Guide

## 🚨 **Current Problem**
Your bot is getting **"403 Forbidden (error code: 50013): Missing Permissions"** when trying to create tournament channels and roles.

## ✅ **Quick Fix Steps**

### **Step 1: Check Bot Permissions**

1. **Go to your Discord server**
2. **Server Settings** → **Roles**
3. **Find "Hear! Hear! Bot" role** (or whatever your bot's role is named)
4. **Enable these permissions:**
   - ✅ **Administrator** (RECOMMENDED - gives all permissions)
   
   **OR** enable these specific permissions:
   - ✅ **Manage Channels**
   - ✅ **Manage Roles** 
   - ✅ **Manage Permissions**
   - ✅ **Send Messages**
   - ✅ **Add Reactions**
   - ✅ **Read Message History**

### **Step 2: Fix Role Hierarchy**

1. **Server Settings** → **Roles**
2. **Drag the bot's role to the TOP** of the role list
3. The bot role must be **above** any roles it needs to create or manage

### **Step 3: Test the Command**

Now try the tournament setup command:
```
/create_tournament tournament_type:AP venues:2
```

## 🔍 **How the New System Works**

The improved tournament setup now includes:

### **1. Permission Pre-Check**
- ✅ Checks permissions **before** starting setup
- ✅ Shows **exactly what's missing** if permissions are insufficient
- ✅ Provides **step-by-step fix instructions**

### **2. Better Error Handling**
- ✅ **Permission errors** - Shows how to fix role hierarchy issues
- ✅ **Rate limit errors** - Suggests waiting and using fewer venues
- ✅ **API errors** - Provides troubleshooting steps

### **3. Improved Progress Tracking**
- ✅ **Step-by-step progress** updates during setup
- ✅ **Clear success/failure** messages
- ✅ **Detailed error explanations**

## 🎯 **What You Should See Now**

### **If Permissions are Missing:**
```
❌ Missing Required Permissions

🚫 Missing Permissions
• Manage Channels
• Manage Roles

🔧 How to Fix This
Option 1: Give Administrator Permission (Recommended)
1. Go to Server Settings → Roles
2. Find my role (Hear! Hear! Bot)
3. Enable Administrator permission

Option 2: Give Specific Permissions
1. Go to Server Settings → Roles
2. Find my role and enable the missing permissions above
3. Make sure my role is above other roles in the hierarchy
```

### **If Permissions are Correct:**
```
🏆 Creating Tournament Setup
Setting up AP tournament with 2 venues...

📝 Step 1/5: Creating tournament roles...
📁 Step 2/5: Creating general channels...
🏟️ Step 3/5: Creating 2 venues...
🔒 Step 4/5: Configuring permissions...
🎭 Step 5/5: Setting up role assignment...

✅ Tournament Setup Complete!
Successfully created AP tournament with 2 venues
```

## 🆘 **If You Still Get Errors**

### **Permission Error During Setup:**
```
❌ Permission Error During Setup
I lost permissions while creating the tournament.

🔧 How to Fix This:
1. Move my role to the TOP of the role hierarchy
2. Give me Administrator permission (recommended)
3. Use /tournament_cleanup confirmation:DELETE to remove partial setup
4. Try the tournament setup command again
```

**Solution:** 
1. Use `/tournament_cleanup confirmation:DELETE`
2. Fix bot role position (move to top)
3. Try again with fewer venues

### **Rate Limit Error:**
```
❌ Discord API Error
🚦 Rate Limited
Discord is rate limiting the bot due to too many requests.
Solution: Wait a few minutes and try again with fewer venues.
```

**Solution:** 
1. Wait 5-10 minutes
2. Try with fewer venues (start with 1-2)
3. Gradually increase venue count

## 🎯 **Testing the Fixed System**

### **Test 1: Permission Check**
```
/create_tournament tournament_type:AP venues:1
```
- Should either show permission error OR start creating

### **Test 2: Small Tournament**
```
/create_tournament tournament_type:AP venues:2 setup_roles:true
```
- Should create 2 venues successfully

### **Test 3: Larger Tournament**
```
/create_tournament tournament_type:BP venues:5 setup_roles:true setup_role_assignment:true
```
- Should create full tournament with role assignment

### **Test 4: Cleanup**
```
/tournament_cleanup confirmation:DELETE
```
- Should remove all tournament infrastructure

## 🏆 **What Gets Created**

### **Roles Created:**
- 🥊 **Debater** (Blue) - Can access prep rooms and debates
- ⚖️ **Adjudicator** (Gold) - Can access all areas + result discussions  
- 👀 **Spectator** (Grey) - Read-only access

### **Channel Categories:**
- 📋 **Welcome** - Instructions, role assignment
- 🏢 **Info Desk** - Bot commands, schedules, tech support
- 📝 **Feedback & Check-in** - Tournament administration  
- 🏛️ **Grand Auditorium** - Announcements, clarifications
- 🏟️ **Tournament Venues** - Individual venue channels

### **Per Venue (AP Format):**
- 💬 `venue-N-debate` (text)
- 🔊 `Venue-N-Debate` (voice)
- 🔒 `Venue-N-Gov-Prep` (3 person limit)
- 🔒 `Venue-N-Opp-Prep` (3 person limit)
- ⚖️ `Venue-N-Result-Discussion` (adjudicator only)

### **Per Venue (BP Format):**
- 💬 `venue-N-debate` (text)
- 🔊 `Venue-N-Debate` (voice)
- 🔒 `Venue-N-OG-Prep` (2 person limit)
- 🔒 `Venue-N-OO-Prep` (2 person limit)
- 🔒 `Venue-N-CG-Prep` (2 person limit)
- 🔒 `Venue-N-CO-Prep` (2 person limit)
- ⚖️ `Venue-N-Result-Discussion` (adjudicator only)

## 🎭 **Role Assignment System**

Users can react in the `#role-assignment` channel:
- 🥊 - Get **Debater** role
- ⚖️ - Get **Adjudicator** role  
- 👀 - Get **Spectator** role

The system automatically removes old roles when users react with new ones.

## 📞 **Need More Help?**

If you're still having issues:

1. **Check bot role hierarchy** - Must be at the top
2. **Try with 1 venue first** - Test with minimal setup
3. **Use Administrator permission** - Simplest solution
4. **Check Discord status** - Sometimes Discord has API issues
5. **Wait between attempts** - Give Discord's rate limits time to reset

The new system should give you **much better error messages** that tell you exactly what's wrong and how to fix it! 🚀