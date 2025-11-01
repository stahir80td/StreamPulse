# StreamPulse Deployment Guide

Complete step-by-step guide to deploy StreamPulse on 100% free tier infrastructure.

---

## 🎯 Deployment Overview

```
┌─────────────────┐
│  1. Upstash     │  Kafka (Message Queue)
│     Kafka       │  Free: 10K msgs/day
└─────────────────┘
         ↓
┌─────────────────┐
│  2. Railway     │  Event Generator, Flink, Backend API
│     (3 services)│  Free: $5 credit/month
└─────────────────┘
         ↓
┌─────────────────┐
│  3. Neon        │  PostgreSQL Database
│     PostgreSQL  │  Free: 0.5GB storage
└─────────────────┘
         ↓
┌─────────────────┐
│  4. Vercel      │  React Dashboard
│     Frontend    │  Free: Unlimited deployments
└─────────────────┘
```

**Total Monthly Cost: $0** ✅

---

## 📋 Prerequisites

### Required Accounts
- [ ] GitHub account (for authentication)
- [ ] Upstash account ([upstash.com](https://upstash.com))
- [ ] Neon account ([neon.tech](https://neon.tech))
- [ ] Railway account ([railway.app](https://railway.app))
- [ ] Vercel account ([vercel.com](https://vercel.com))

### Required Software
- [ ] Git (for version control)
- [ ] Node.js 18+ ([nodejs.org](https://nodejs.org))
- [ ] Python 3.11+ ([python.org](https://python.org))
- [ ] PowerShell 7+ (Windows built-in)

### Optional Software
- [ ] VS Code (recommended IDE)
- [ ] Docker Desktop (for local testing)
- [ ] PostgreSQL client (psql, DBeaver, pgAdmin)

---

## 🚀 Deployment Steps

### Step 1: Clone Repository

```powershell
# Clone from GitHub
git clone https://github.com/stahir80td/StreamPulse.git
cd StreamPulse

# Verify structure
dir
# You should see: event-generator/, flink-processor/, backend/, frontend/, etc.
```

---

### Step 2: Set Up Upstash Kafka

**Detailed guide:** See `scripts/setup_upstash.md`

**Quick steps:**
1. Create Upstash account
2. Create Kafka cluster (free tier)
3. Create topic: `content-downloads` (3 partitions)
4. Copy connection credentials

**What you'll need:**
- Bootstrap servers URL
- Username
- Password

⏱️ **Time: 5 minutes**

---

### Step 3: Set Up Neon PostgreSQL

**Detailed guide:** See `scripts/setup_neon.md`

**Quick steps:**
1. Create Neon account
2. Create project: `streampulse`
3. Run database initialization script (`sql/init.sql`)
4. Copy connection credentials

**What you'll need:**
- Host URL
- Database name
- Username
- Password

⏱️ **Time: 5 minutes**

---

### Step 4: Deploy Backend Services to Railway

**Automated script:** `scripts/deploy_railway.ps1`

```powershell
# Run deployment script
.\scripts\deploy_railway.ps1
```

**Manual steps:**

**4a. Install Railway CLI**
```powershell
npm install -g @railway/cli
```

**4b. Login to Railway**
```powershell
railway login
```

**4c. Create Project**
```powershell
railway init
# Name: streampulse
```

**4d. Deploy Event Generator**
```powershell
cd event-generator
railway up
```

Set environment variables in Railway dashboard:
```
KAFKA_BOOTSTRAP_SERVERS=xxx.upstash.io:9092
KAFKA_USERNAME=your-username
KAFKA_PASSWORD=your-password
KAFKA_TOPIC=content-downloads
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
EVENTS_PER_MINUTE=7
```

**4e. Deploy Flink Processor**
```powershell
cd ../flink-processor
railway up
```

Set environment variables:
```
# Kafka
KAFKA_BOOTSTRAP_SERVERS=xxx.upstash.io:9092
KAFKA_USERNAME=your-username
KAFKA_PASSWORD=your-password
KAFKA_TOPIC=content-downloads
KAFKA_GROUP_ID=flink-processor

# PostgreSQL
PG_HOST=ep-xxx.neon.tech
PG_DATABASE=neondb
PG_USER=your-username
PG_PASSWORD=your-password
PG_SSLMODE=require
```

**4f. Deploy Backend API**
```powershell
cd ../backend
railway up
```

Set environment variables:
```
# PostgreSQL
PG_HOST=ep-xxx.neon.tech
PG_DATABASE=neondb
PG_USER=your-username
PG_PASSWORD=your-password
PG_SSLMODE=require

# API
API_TITLE=StreamPulse API
API_VERSION=1.0.0
ALLOWED_ORIGINS=http://localhost:3000
```

**Get Backend API URL:**
```powershell
railway status
# Copy the URL (e.g., https://streampulse-api.up.railway.app)
```

⏱️ **Time: 15-20 minutes**

---

### Step 5: Deploy Frontend to Vercel

**Automated script:** `scripts/deploy_vercel.ps1`

```powershell
# Run deployment script
.\scripts\deploy_vercel.ps1
```

**Manual steps:**

**5a. Install Vercel CLI**
```powershell
npm install -g vercel
```

**5b. Navigate to Frontend**
```powershell
cd frontend
```

**5c. Install Dependencies**
```powershell
npm install
```

**5d. Deploy**
```powershell
vercel --prod
```

Follow prompts:
- Set up and deploy? **Y**
- Which scope? **Your account**
- Link to existing project? **N**
- Project name? **streampulse**
- Directory? **./  (current directory)**
- Override settings? **N**

**5e. Set Environment Variable**
```powershell
vercel env add REACT_APP_API_URL production
# Enter value: https://your-backend.up.railway.app
```

**5f. Redeploy with Environment Variable**
```powershell
vercel --prod
```

**Get Frontend URL:**
```
Visit: https://vercel.com/dashboard
Your URL will be: https://streampulse.vercel.app (or similar)
```

⏱️ **Time: 10 minutes**

---

### Step 6: Update CORS Settings

**Important:** Allow frontend to call backend API.

1. Go to Railway dashboard
2. Select **Backend API** service
3. Go to **Variables** tab
4. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```
5. Save (Railway auto-redeploys)

⏱️ **Time: 2 minutes**

---

### Step 7: Verify Deployment

**Check each service:**

**✅ Upstash Kafka**
```
Go to: https://console.upstash.com
Check: Messages being produced (should see counter incrementing)
```

**✅ Railway Event Generator**
```
Go to: https://railway.app/dashboard
Select: event-generator service
Check logs: Should see "✅ Sent X events"
```

**✅ Railway Flink Processor**
```
Select: flink-processor service
Check logs: Should see "✅ Wrote X records to content_stats"
```

**✅ Neon PostgreSQL**
```
Go to: https://console.neon.tech
SQL Editor: SELECT COUNT(*) FROM content_stats;
Should return: > 0 rows
```

**✅ Railway Backend API**
```
Open browser: https://your-backend.up.railway.app/health
Should return: {"status": "healthy", "database": true, ...}
```

**✅ Vercel Frontend**
```
Open browser: https://your-frontend.vercel.app
Should see: StreamPulse dashboard with live data
```

⏱️ **Time: 5 minutes**

---

## 🎉 Total Deployment Time

- **Upstash setup:** 5 minutes
- **Neon setup:** 5 minutes
- **Railway deployment:** 20 minutes
- **Vercel deployment:** 10 minutes
- **CORS update:** 2 minutes
- **Verification:** 5 minutes

**Total: ~45-50 minutes** ⏱️

---

## 🐛 Troubleshooting

### Issue: Event Generator Not Producing Events

**Symptoms:**
- Upstash console shows 0 messages
- Railway logs show connection errors

**Solutions:**
1. Check Kafka credentials in Railway environment variables
2. Verify `KAFKA_BOOTSTRAP_SERVERS` includes `:9092` port
3. Ensure `KAFKA_SECURITY_PROTOCOL=SASL_SSL`
4. Check Railway logs for specific error messages

---

### Issue: Flink Processor Not Writing to Database

**Symptoms:**
- PostgreSQL tables empty
- Railway logs show database connection errors

**Solutions:**
1. Verify PostgreSQL credentials in environment variables
2. Check `PG_SSLMODE=require` is set
3. Test connection: `psql "postgresql://user:pass@host/db?sslmode=require"`
4. Ensure database schema is initialized (`sql/init.sql`)
5. Check if Neon database is suspended (wake it with a query)

---

### Issue: Backend API Returns 500 Errors

**Symptoms:**
- Frontend shows "Failed to load data"
- `/health` endpoint returns error

**Solutions:**
1. Check Railway logs for backend service
2. Verify PostgreSQL connection (same as Flink troubleshooting)
3. Ensure all required environment variables are set
4. Try redeploying: `railway up --detach`

---

### Issue: Frontend Shows CORS Error

**Symptoms:**
- Browser console: "CORS policy blocked"
- API calls fail with CORS error

**Solutions:**
1. Verify `ALLOWED_ORIGINS` in Backend API includes frontend URL
2. Ensure URL includes `https://` (not `http://`)
3. No trailing slash in URL
4. Redeploy backend after changing CORS settings
5. Hard refresh frontend (Ctrl+Shift+R)

---

### Issue: Frontend Shows No Data

**Symptoms:**
- Dashboard loads but all widgets empty
- "No data available" messages

**Solutions:**
1. Check if backend API is running (visit `/health`)
2. Verify `REACT_APP_API_URL` is set in Vercel
3. Open browser DevTools → Network tab
4. Check if API calls return 200 status
5. Wait 60 seconds (Flink needs at least 1 complete window)

---

### Issue: Railway Service Crashes on Startup

**Symptoms:**
- Service shows "Crashed" status
- Logs show immediate exit

**Solutions:**
1. Check for missing environment variables
2. Verify `Dockerfile` is present in service directory
3. Check `railway.json` configuration
4. Try manual deploy: `railway up --detach`
5. Check Railway build logs for errors

---

## 📊 Monitoring & Maintenance

### Daily Checks

**Upstash Dashboard:**
- Messages produced today (should be ~7,000-9,000)
- Storage used (should be < 5 MB)
- No errors reported

**Railway Dashboard:**
- All 3 services showing "Active" status
- No recurring errors in logs
- Compute hours used (should be ~5-10 hours total)

**Neon Dashboard:**
- Database size (should be < 100 MB)
- Active compute time (should be minimal due to auto-suspend)
- No slow queries reported

**Vercel Dashboard:**
- Deployment status: "Ready"
- No build failures
- Analytics: Page views, load times

### Weekly Maintenance

**Database Cleanup:**
```sql
-- Run in Neon SQL Editor
SELECT cleanup_old_data();

-- Verify size
SELECT pg_size_pretty(pg_database_size('neondb'));
```

**Log Review:**
```powershell
# Check Railway logs
railway logs -s event-generator
railway logs -s flink-processor
railway logs -s backend

# Check for recurring errors
```

**Performance Check:**
```
Visit frontend dashboard
- Check all charts loading
- Verify data is recent (<2 minutes old)
- Test responsiveness on mobile
```

### Monthly Tasks

- [ ] Review Upstash usage (stay under 10K msgs/day)
- [ ] Review Railway compute hours (stay under 450 hrs/month)
- [ ] Review Neon storage (stay under 0.5 GB)
- [ ] Check for security updates (npm, pip)
- [ ] Backup database (Neon has automatic backups)
- [ ] Review and acknowledge old alerts

---

## 🔄 Redeployment Guide

### Update Code and Redeploy

**1. Update Repository:**
```powershell
git pull origin main
```

**2. Redeploy Railway Services:**
```powershell
# Event Generator
cd event-generator
railway up --detach

# Flink Processor
cd ../flink-processor
railway up --detach

# Backend API
cd ../backend
railway up --detach
```

**3. Redeploy Vercel Frontend:**
```powershell
cd frontend
vercel --prod
```

**4. Verify Changes:**
- Check Railway logs
- Test frontend functionality
- Monitor for errors

---

## 🔐 Security Checklist

- [ ] All `.env` files in `.gitignore`
- [ ] No hardcoded credentials in source code
- [ ] Kafka credentials rotated every 90 days
- [ ] PostgreSQL credentials rotated every 90 days
- [ ] CORS configured correctly (no wildcards)
- [ ] HTTPS enforced on all services
- [ ] Environment variables set in dashboards (not in code)

---

## 📈 Scaling Guide

### When to Scale

**Upstash Kafka:**
- Approaching 10K messages/day
- Need longer retention (>7 days)
- Need dedicated throughput

→ **Upgrade to Upstash Pro:** $10/month (100K msgs/day)

**Railway:**
- Services crashing due to memory limits
- Exceeding 450 compute hours/month
- Need more than 3 services

→ **Add credit or upgrade plan:** $5/month per additional 100 hours

**Neon PostgreSQL:**
- Database size approaching 0.5 GB
- Cold starts causing issues
- Need faster queries

→ **Upgrade to Neon Pro:** $19/month (10 GB, always-on)

**Vercel:**
- High traffic (>100GB bandwidth/month on free tier)
- Need custom domain
- Need team features

→ **Upgrade to Pro:** $20/month (1 TB bandwidth)

---

## 📚 Additional Resources

- [Upstash Documentation](https://docs.upstash.com)
- [Neon Documentation](https://neon.tech/docs)
- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)

---

## 🎯 Deployment Checklist

Use this checklist to track your deployment:

- [ ] Repository cloned
- [ ] Upstash Kafka cluster created
- [ ] Kafka topic created (3 partitions)
- [ ] Neon PostgreSQL project created
- [ ] Database schema initialized
- [ ] Railway account created
- [ ] Event Generator deployed to Railway
- [ ] Event Generator environment variables set
- [ ] Flink Processor deployed to Railway
- [ ] Flink Processor environment variables set
- [ ] Backend API deployed to Railway
- [ ] Backend API environment variables set
- [ ] Backend API URL copied
- [ ] Vercel account created
- [ ] Frontend deployed to Vercel
- [ ] Frontend environment variable set (REACT_APP_API_URL)
- [ ] CORS updated in Backend API
- [ ] All services verified working
- [ ] Dashboard accessible and showing data

---

