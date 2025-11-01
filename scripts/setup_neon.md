# Neon PostgreSQL Setup Guide

Complete guide to setting up free serverless PostgreSQL database on Neon for StreamPulse.

---

## 📋 Prerequisites

- Email address for account creation
- No credit card required for free tier! ✅

---

## 🚀 Step-by-Step Setup

### Step 1: Create Neon Account

1. Go to [https://neon.tech](https://neon.tech)
2. Click **"Sign Up"** or **"Get Started"**
3. Sign up with:
   - Email + Password, OR
   - GitHub OAuth (recommended), OR
   - Google OAuth
4. Email verification (if using email signup)

---

### Step 2: Create Project

1. After logging in, click **"Create Project"** or **"New Project"**

2. **Configure Project:**
   ```
   Project Name: streampulse
   PostgreSQL Version: 16 (latest)
   Region: Choose closest to you
           - US East (N. Virginia)
           - US West (Oregon)
           - Europe (Frankfurt)
           - Asia Pacific (Singapore)
   ```

3. Click **"Create Project"**

4. Wait 10-30 seconds for database creation

---

### Step 3: Get Connection Details

After project creation, you'll see connection details:

**Connection String:**
```
postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

**Parse the details:**
```
Host: ep-xxx-xxx.region.aws.neon.tech
Port: 5432
Database: neondb (default)
Username: username (shown in dashboard)
Password: password (auto-generated)
SSL Mode: require
```

**Save these credentials - you'll need them later!**

---

### Step 4: Initialize Database Schema

**Option A: Using Neon SQL Editor (Easiest)**

1. In your project dashboard, click **"SQL Editor"**

2. Copy contents of `sql/init.sql` from StreamPulse repo

3. Paste into SQL Editor

4. Click **"Run"** or press `Ctrl+Enter`

5. Wait for execution (should take 5-10 seconds)

6. Verify tables created:
   ```sql
   \dt
   ```
   You should see:
   - content_stats
   - region_health
   - alerts
   - trending_predictions
   - device_stats
   - event_log

**Option B: Using psql CLI**

```powershell
# Install psql (if not installed)
# Windows: Download from https://www.postgresql.org/download/windows/

# Connect to Neon database
psql "postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require"

# Run init script
\i sql/init.sql

# Verify tables
\dt

# Exit
\q
```

**Option C: Using DBeaver / pgAdmin**

1. Download [DBeaver](https://dbeaver.io/) or [pgAdmin](https://www.pgadmin.org/)

2. Create new PostgreSQL connection with Neon credentials

3. Open SQL editor

4. Execute `sql/init.sql`

---

### Step 5: Test Database Connection

**Quick Test Query:**

In Neon SQL Editor or psql:

```sql
-- Insert test data
INSERT INTO content_stats (content_id, title, download_count, successful_downloads, failed_downloads, window_start, window_end)
VALUES ('test_content', 'Test Movie', 100, 95, 5, NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '4 minutes');

-- Query test data
SELECT * FROM content_stats ORDER BY created_at DESC LIMIT 5;

-- Clean up test data (optional)
DELETE FROM content_stats WHERE content_id = 'test_content';
```

If query succeeds, database is ready! ✅

---

### Step 6: Configure StreamPulse

**For Flink Processor:**

Create `.env` file in `flink-processor/`:
```bash
PG_HOST=ep-xxx-xxx.region.aws.neon.tech
PG_PORT=5432
PG_DATABASE=neondb
PG_USER=your-username
PG_PASSWORD=your-password
PG_SSLMODE=require
```

**For Backend API:**

Create `.env` file in `backend/`:
```bash
PG_HOST=ep-xxx-xxx.region.aws.neon.tech
PG_PORT=5432
PG_DATABASE=neondb
PG_USER=your-username
PG_PASSWORD=your-password
PG_SSLMODE=require
```

---

## 📊 Free Tier Limits

```
✅ Storage: 0.5 GB
✅ Compute: 191.9 hours/month (always active for project)
✅ Projects: 1 project
✅ Branches: 10 branches (Git-like workflow)
✅ Auto-suspend: After 5 minutes inactivity
✅ Auto-resume: On first query (300ms cold start)
```

**How StreamPulse Stays Under Limits:**

- Database size: ~50 MB (7 days retention, 10K events/day)
- Compute: API queries are lightweight (<10ms each)
- Auto-suspend saves compute hours when idle
- Total usage: ~5-10 hours/month active compute ✅

---

## 🔍 Monitoring Your Database

### Neon Dashboard Metrics

1. Go to project dashboard

2. Click **"Monitoring"** tab

3. View metrics:
   - **Active Time**: Compute hours used
   - **Storage Used**: Current database size
   - **Connection Count**: Active connections
   - **Query Performance**: Slow query log

### Query Statistics

```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('neondb')) AS size;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check row counts
SELECT 
    'content_stats' AS table_name,
    COUNT(*) AS row_count
FROM content_stats
UNION ALL
SELECT 'region_health', COUNT(*) FROM region_health
UNION ALL
SELECT 'alerts', COUNT(*) FROM alerts;
```

---

## 🛠️ Troubleshooting

### Issue: "Connection timeout"
```
Solution:
1. Verify host URL is correct (includes "ep-" prefix)
2. Ensure sslmode=require is set
3. Check firewall allows outbound connections to port 5432
4. Try from different network
5. Check Neon status: https://neon.tech/status
```

### Issue: "Password authentication failed"
```
Solution:
1. Copy password exactly from Neon dashboard
2. Check for trailing spaces
3. Try regenerating password:
   - Settings → Reset Password
4. Update .env files with new password
```

### Issue: "Database does not exist"
```
Solution:
1. Default database is "neondb" (not "streampulse")
2. To create custom database:
   CREATE DATABASE streampulse;
3. Update PG_DATABASE in .env files
```

### Issue: "SSL connection required"
```
Solution:
1. Always use sslmode=require
2. Neon requires SSL for all connections
3. Verify connection string includes ?sslmode=require
```

### Issue: "Too many connections"
```
Solution:
1. Neon free tier: 100 concurrent connections
2. Close idle connections in code
3. Use connection pooling (already configured in backend)
4. Check for connection leaks in Flink processor
```

### Issue: "Database suspended"
```
Solution:
1. Neon auto-suspends after 5 minutes inactivity
2. First query after suspend takes 300-500ms (cold start)
3. Normal behavior for free tier
4. Paid tier: Always-on compute
```

---

## 🔐 Security Best Practices

1. **Never commit credentials:**
   ```bash
   # .env files are in .gitignore
   # Never push to GitHub
   ```

2. **Rotate passwords regularly:**
   - Neon dashboard → Settings → Reset Password
   - Update all services

3. **Use read-only users (optional):**
   ```sql
   -- Create read-only user for analytics
   CREATE USER analytics_readonly WITH PASSWORD 'secure_password';
   GRANT CONNECT ON DATABASE neondb TO analytics_readonly;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_readonly;
   ```

4. **Enable query logging:**
   - Neon dashboard → Settings → Query Logging
   - Helps debug issues

---

## 🗄️ Database Maintenance

### Data Retention Cleanup

Run weekly to keep database under 0.5 GB:

```sql
-- Manual cleanup (or automate via pg_cron)
SELECT cleanup_old_data();

-- Or delete manually
DELETE FROM content_stats WHERE created_at < NOW() - INTERVAL '7 days';
DELETE FROM region_health WHERE created_at < NOW() - INTERVAL '7 days';
DELETE FROM alerts WHERE created_at < NOW() - INTERVAL '30 days';
```

### Vacuum and Analyze

```sql
-- Reclaim space and update statistics
VACUUM ANALYZE;

-- Check last vacuum time
SELECT 
    schemaname,
    tablename,
    last_vacuum,
    last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

### Backup (Built-in)

Neon automatically backs up your database:
- **Point-in-time recovery**: Restore to any point in last 7 days
- **Branch from backup**: Create test branch from production
- **No manual backups needed** on free tier ✅

---

## 📈 Scaling Beyond Free Tier

When you need more than 0.5 GB storage:

### Neon Pro ($19/month)
```
- 10 GB storage
- Always-on compute (no cold starts)
- Unlimited projects
- Point-in-time recovery (30 days)
- Priority support
```

### Neon Scale (Custom pricing)
```
- Custom storage limits
- Dedicated compute
- SLA guarantees
- Advanced monitoring
```

---

## 🎯 Verification Checklist

Before moving to next step:

- [ ] Neon project created
- [ ] Database connection tested
- [ ] Schema initialized (all tables created)
- [ ] Sample query successful
- [ ] Connection credentials saved
- [ ] `.env` files configured in flink-processor and backend
- [ ] SSL mode set to "require"

---

## 🌿 Neon Branching (Bonus Feature)

Neon's unique Git-like branching for databases:

```bash
# Create development branch
# Neon Dashboard → Branches → Create Branch
# Branch name: development
# Branch from: main

# Now you have 2 independent databases:
# - main (production)
# - development (for testing)

# Test schema changes on development branch
# If successful, apply to main branch
# If failed, delete development branch
```

Perfect for testing Flink processor changes without affecting production! 🎉

---

## 📚 Additional Resources

- [Neon Documentation](https://neon.tech/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Neon Status Page](https://neon.tech/status)
- [Neon Discord Community](https://discord.gg/neon)

---

## 🎉 Next Steps

After completing Neon setup:

1. ✅ Upstash Kafka setup complete
2. ✅ Neon PostgreSQL setup complete
3. ⏭️ Deploy services to Railway → See `deploy_railway.ps1`
4. ⏭️ Deploy frontend to Vercel → See `deploy_vercel.ps1`

---

**Neon PostgreSQL is ready for StreamPulse! 🚀**