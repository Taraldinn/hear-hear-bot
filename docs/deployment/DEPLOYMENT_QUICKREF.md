# 🚀 Quick Deployment Reference Card

## ⚡ 5-Minute Quick Start

### 1. Environment Setup (2 min)
```bash
# Copy production template
cp .env.production .env

# Edit with your credentials
nano .env

# Set these 3 REQUIRED variables:
DISCORD_BOT_TOKEN=your_token_here
BOT_ID=your_bot_id_here
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### 2. Verify Configuration (1 min)
```bash
python check_config.py
```

### 3. Deploy (2 min)

**Heroku:**
```bash
heroku create && git push heroku main
```

**Railway:**
```bash
# Connect repo in Railway dashboard
# Set env vars → Auto-deploys
```

**VPS:**
```bash
pip install -r requirements.txt
python main.py
```

---

## 📋 Essential Commands

```bash
# Test configuration
python check_config.py

# Run bot locally
python main.py

# Check logs
tail -f logs/bot.log

# Test database
python -c "from src.database.connection import DatabaseManager; print('DB OK')"

# Update dependencies
pip install -r requirements.txt --upgrade
```

---

## 🔐 Required Environment Variables

```bash
# Minimum to run
DISCORD_BOT_TOKEN=MTxxxxxx.xxxxxx.xxxxxx
BOT_ID=1234567890123456789
DATABASE_URL=postgresql://user:pass@host:5432/db

# Recommended
TOPGG_TOKEN=your_topgg_token
LOG_LEVEL=INFO
```

---

## 🌐 Quick Platform Deploy

| Platform | Time | Command |
|----------|------|---------|
| **Heroku** | 5 min | `heroku create && git push heroku main` |
| **Railway** | 3 min | Connect repo → Set vars → Deploy |
| **Render** | 5 min | New Service → Connect repo → Set vars |
| **VPS** | 10 min | Clone → Install → Configure → Run |

---

## 🔍 Health Check URLs

```bash
# After deployment, test these:
http://your-bot-url/health        # Should return 200
http://your-bot-url/              # Homepage
http://your-bot-url/invite        # Bot invite page
http://your-bot-url/api/stats     # JSON stats
```

---

## 🚨 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Bot offline | Check `DISCORD_BOT_TOKEN` |
| DB connection fail | Verify `DATABASE_URL` with `sslmode=require` |
| Commands not showing | Wait 1h or rejoin server |
| Port in use | Change `WEB_SERVER_PORT` |
| Logs not showing | Check `LOG_LEVEL=INFO` |

---

## 📊 Monitoring Quick Setup

**UptimeRobot:**
1. Add monitor → HTTP
2. URL: `https://your-bot.com/health`
3. Interval: 5 minutes

**Logs:**
```bash
# Real-time logs
heroku logs --tail          # Heroku
railway logs               # Railway
sudo journalctl -u bot -f  # VPS
```

---

## 🔄 Update & Rollback

**Update:**
```bash
git pull && pip install -r requirements.txt --upgrade
# Then restart bot
```

**Rollback:**
```bash
git log --oneline          # Find commit
git checkout <commit>      # Rollback
# Then restart bot
```

---

## 📝 Pre-Launch Checklist

- [ ] Environment configured (`.env`)
- [ ] Database created and accessible
- [ ] Bot invited to test server
- [ ] Commands tested (`/help`, `/ping`)
- [ ] Web server accessible
- [ ] Monitoring configured
- [ ] Logs working
- [ ] Backup plan ready

---

## 🎯 Success Indicators

✅ Bot shows "Online" in Discord  
✅ `/help` responds within 1 second  
✅ Web page loads at your URL  
✅ Health check returns 200  
✅ No errors in logs  
✅ Database queries execute  

---

## 📞 Emergency Contacts

**Platform Support:**
- Heroku: support.heroku.com
- Railway: help.railway.app
- Render: render.com/docs

**Discord:**
- API Status: status.discord.com
- Developer Portal: discord.com/developers

---

## 📚 Full Documentation

For detailed guides, see:
- **DEPLOYMENT_GUIDE.md** (12K) - Complete deployment guide
- **DEPLOYMENT_CHECKLIST.md** (9.3K) - Step-by-step checklist
- **.env.production** (12K) - Full environment template

---

## ⏱️ Deployment Time Estimates

| Platform | Setup Time | Experience Level |
|----------|-----------|------------------|
| Railway | 10 min | Beginner-friendly |
| Heroku | 15 min | Beginner-friendly |
| Render | 15 min | Beginner-friendly |
| VPS | 30 min | Intermediate |
| Docker | 20 min | Intermediate |

---

## 🎉 You're Ready!

Everything you need is prepared:
- ✅ Production environment template
- ✅ Deployment guide
- ✅ Checklist
- ✅ This quick reference

**Next step:** Copy `.env.production` to `.env` and start deploying!

---

**Last Updated:** October 2, 2025  
**Version:** 2.1.0  
**Status:** Ready for Production 🚀
