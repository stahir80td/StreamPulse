# StreamPulse Environment Configuration Guide

Complete guide for configuring all `.env` files for local development.

---

## 📋 **Overview**

StreamPulse requires 4 `.env` files:

1. **event-generator/.env** - Kafka producer configuration
2. **flink-processor/.env** - Stream processor configuration (Kafka + PostgreSQL)
3. **backend/.env** - FastAPI backend configuration (PostgreSQL + CORS)
4. **frontend/.env** - React frontend configuration (API URL)

---

## 🔧 **Configuration Files**

### **1. event-generator/.env**

**Location:** `StreamPulse/event-generator/.env`

```bash
# ============================================================================
# Kafka Configuration (Local WSL)
# ============================================================================

# Kafka broker address (localhost for local WSL Kafka)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Topic name (must match topic created in Kafka)
KAFKA_TOPIC=content-downloads

# Kafka authentication (leave empty for local PLAINTEXT)
KAFKA_USERNAME=
KAFKA_PASSWORD=

# Security protocol (PLAINTEXT for local, SASL_SSL for Upstash cloud)
KAFKA_SECURITY_PROTOCOL=PLAINTEXT

# SASL mechanism (only used if SECURITY_PROTOCOL=SASL_SSL)
KAFKA_SASL_MECHANISM=PLAIN

# ============================================================================
# Event Generation Settings
# ============================================================================

# Number of events to produce per minute
# Current: 60 events/min = 86,400 events/day
# Max recommended for Upstash free tier: 7 events/min = ~10,000/day
EVENTS_PER_MINUTE=60

# ============================================================================
# Schema Configuration
# ============================================================================

# Path to Avro schema file (relative to event-generator directory)
SCHEMA_PATH=../schemas/event.avsc
```

**Key Points:**
- ✅ `localhost:9092` works when Kafka runs in WSL
- ✅ Leave username/password empty for local setup
- ✅ `EVENTS_PER_MINUTE` can be adjusted (1-1000)
- ⚠️ For cloud Kafka (Upstash), change `SECURITY_PROTOCOL=SASL_SSL` and add credentials

---

### **2. flink-processor/.env**

**Location:** `StreamPulse/flink-processor/.env`

```bash
# ============================================================================
# Kafka Configuration (Local WSL)
# ============================================================================

# Kafka broker address
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Topic name to consume from
KAFKA_TOPIC=content-downloads

# Consumer group ID (for offset management)
KAFKA_GROUP_ID=flink-processor

# Kafka authentication (leave empty for local PLAINTEXT)
KAFKA_USERNAME=
KAFKA_PASSWORD=

# Security protocol
KAFKA_SECURITY_PROTOCOL=PLAINTEXT

# SASL mechanism (only used if SECURITY_PROTOCOL=SASL_SSL)
KAFKA_SASL_MECHANISM=PLAIN

# ============================================================================
# PostgreSQL Configuration (Local Windows)
# ============================================================================

# PostgreSQL connection settings
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=streampulse
PG_USER=postgres

# ⚠️ CHANGE THIS to match your PostgreSQL password!
PG_PASSWORD=password

# SSL mode (disable for local, require for cloud)
PG_SSLMODE=disable

# ============================================================================
# Flink Configuration
# ============================================================================

# Number of parallel tasks (1 for single machine)
FLINK_PARALLELISM=1

# Checkpoint interval in milliseconds (60 seconds)
FLINK_CHECKPOINT_INTERVAL=60000

# ============================================================================
# Schema Configuration
# ============================================================================

# Path to Avro schema file (relative to flink-processor directory)
SCHEMA_PATH=../schemas/event.avsc
```

**Key Points:**
- ⚠️ **MUST CHANGE:** `PG_PASSWORD` to match your PostgreSQL installation
- ✅ `KAFKA_GROUP_ID` enables offset tracking and replay capability
- ✅ `FLINK_CHECKPOINT_INTERVAL` controls fault tolerance (default 60s)
- ⚠️ For cloud PostgreSQL (Neon), change `PG_SSLMODE=require`

---

### **3. backend/.env**

**Location:** `StreamPulse/backend/.env`

```bash
# ============================================================================
# PostgreSQL Configuration (Local Windows)
# ============================================================================

# PostgreSQL connection settings
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=streampulse
PG_USER=postgres

# ⚠️ CHANGE THIS to match your PostgreSQL password!
PG_PASSWORD=password

# SSL mode (disable for local, require for cloud)
PG_SSLMODE=disable

# ============================================================================
# API Configuration
# ============================================================================

# API metadata
API_TITLE=StreamPulse API
API_VERSION=1.0.0
API_PREFIX=/api

# ============================================================================
# CORS Configuration
# ============================================================================

# Allowed origins (comma-separated for multiple origins)
# For local development
ALLOWED_ORIGINS=http://localhost:3000

# For production deployment (example)
# ALLOWED_ORIGINS=https://streampulse.vercel.app,http://localhost:3000

# ============================================================================
# Cache Configuration
# ============================================================================

# Cache TTL in seconds (default: 2 seconds)
# Reduces database load by caching API responses
CACHE_TTL=2
```

**Key Points:**
- ⚠️ **MUST CHANGE:** `PG_PASSWORD` to match your PostgreSQL installation
- ⚠️ **MUST UPDATE:** `ALLOWED_ORIGINS` when deploying frontend to production
- ✅ `CACHE_TTL=2` matches frontend refresh interval (optimal)
- ⚠️ For multiple origins, use: `ALLOWED_ORIGINS=http://localhost:3000,https://prod.com`

---

### **4. frontend/.env**

**Location:** `StreamPulse/frontend/.env`

```bash
# ============================================================================
# Backend API Configuration
# ============================================================================

# Backend API URL
# For local development
REACT_APP_API_URL=http://localhost:8000

# For production deployment (example)
# REACT_APP_API_URL=https://streampulse-api.up.railway.app

# ============================================================================
# Dashboard Configuration
# ============================================================================

# Auto-refresh interval in milliseconds (default: 2000ms = 2 seconds)
REACT_APP_REFRESH_INTERVAL=2000
```

**Key Points:**
- ✅ `localhost:8000` works for local development
- ⚠️ **MUST UPDATE:** `REACT_APP_API_URL` when deploying backend to cloud
- ✅ `REFRESH_INTERVAL` can be adjusted (1000-10000ms recommended)
- ⚠️ Changes require `npm start` restart (React doesn't hot-reload .env)

---

## 🔄 **Environment-Specific Configurations**

### **Local Development (Current Setup)**

**Kafka:** WSL localhost  
**PostgreSQL:** Windows localhost  
**Backend:** Windows localhost:8000  
**Frontend:** Windows localhost:3000

```bash
# event-generator/.env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT

# flink-processor/.env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT
PG_HOST=localhost
PG_SSLMODE=disable

# backend/.env
PG_HOST=localhost
PG_SSLMODE=disable
ALLOWED_ORIGINS=http://localhost:3000

# frontend/.env
REACT_APP_API_URL=http://localhost:8000
```

---

### **Cloud Deployment (Example)**

**Kafka:** Upstash  
**PostgreSQL:** Neon  
**Backend:** Railway  
**Frontend:** Vercel

```bash
# event-generator/.env (Railway)
KAFKA_BOOTSTRAP_SERVERS=your-cluster.upstash.io:9092
KAFKA_USERNAME=your-username
KAFKA_PASSWORD=your-password
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=SCRAM-SHA-256

# flink-processor/.env (Railway)
KAFKA_BOOTSTRAP_SERVERS=your-cluster.upstash.io:9092
KAFKA_USERNAME=your-username
KAFKA_PASSWORD=your-password
KAFKA_SECURITY_PROTOCOL=SASL_SSL
PG_HOST=ep-xxx.neon.tech
PG_SSLMODE=require

# backend/.env (Railway)
PG_HOST=ep-xxx.neon.tech
PG_SSLMODE=require
ALLOWED_ORIGINS=https://streampulse.vercel.app

# frontend/.env (Vercel)
REACT_APP_API_URL=https://streampulse-api.up.railway.app
```

---

## 🔐 **Security Best Practices**

### **1. Never Commit .env Files**

✅ All `.env` files are in `.gitignore`  
❌ Never commit credentials to Git  
✅ Share `.env.example` files (templates without secrets)

---

### **2. Use Strong Passwords**

```bash
# ❌ BAD (default passwords)
PG_PASSWORD=password
KAFKA_PASSWORD=admin123

# ✅ GOOD (strong passwords)
PG_PASSWORD=X7k#mR9$pL2@vN5q
KAFKA_PASSWORD=A8j$nB4&wP6*tQ9s
```

---

### **3. Rotate Credentials Regularly**

**For production:**
- Rotate PostgreSQL password every 90 days
- Rotate Kafka credentials every 90 days
- Update all services with new credentials simultaneously

---

### **4. Environment-Specific Files**

```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production

# Load appropriate file based on environment
```

---

## 🐛 **Troubleshooting**

### **Issue: "FATAL: password authentication failed"**

**Cause:** Wrong PostgreSQL password in `.env`

**Solution:**
```bash
# Check your PostgreSQL password
psql -U postgres
# Enter password manually

# If successful, update .env files:
PG_PASSWORD=your_correct_password
```

---

### **Issue: "Connection refused" to Kafka**

**Cause:** Kafka not running or wrong address

**Solution:**
```bash
# Check if Kafka is running in WSL
wsl
ps aux | grep kafka

# Verify Kafka is accessible
nc -zv localhost 9092

# If not accessible, ensure KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

---

### **Issue: Frontend shows "Failed to load data"**

**Cause:** CORS error or wrong backend URL

**Solution:**
1. Check browser console (F12) for CORS errors
2. Verify backend is running: http://localhost:8000/health
3. Check `ALLOWED_ORIGINS` in backend/.env includes frontend URL
4. Check `REACT_APP_API_URL` in frontend/.env points to backend

---

### **Issue: Changes to .env not taking effect**

**Cause:** Service needs restart

**Solution:**
```powershell
# Python services (event-generator, flink-processor, backend)
# Stop with Ctrl+C, then restart:
python src/generator.py

# React frontend (requires full restart)
# Stop with Ctrl+C, then:
npm start
```

---

## 📝 **Verification Checklist**

Before running StreamPulse, verify all `.env` files:

### **event-generator/.env**
- [ ] `KAFKA_BOOTSTRAP_SERVERS` points to Kafka
- [ ] `KAFKA_TOPIC=content-downloads`
- [ ] `KAFKA_SECURITY_PROTOCOL` matches Kafka setup
- [ ] `SCHEMA_PATH` points to valid Avro file

### **flink-processor/.env**
- [ ] Kafka settings match event-generator
- [ ] `PG_HOST`, `PG_PORT`, `PG_DATABASE` correct
- [ ] `PG_USER` and `PG_PASSWORD` correct
- [ ] `PG_SSLMODE` matches PostgreSQL setup
- [ ] `SCHEMA_PATH` points to valid Avro file

### **backend/.env**
- [ ] PostgreSQL settings match flink-processor
- [ ] `ALLOWED_ORIGINS` includes frontend URL
- [ ] `CACHE_TTL` set to 2 seconds

### **frontend/.env**
- [ ] `REACT_APP_API_URL` points to backend
- [ ] `REACT_APP_REFRESH_INTERVAL` set (2000ms default)

---

## 🎯 **Quick Reference**

| Service | Config File | Key Settings |
|---------|------------|--------------|
| **Event Generator** | `event-generator/.env` | Kafka address, topic, events/min |
| **Flink Processor** | `flink-processor/.env` | Kafka + PostgreSQL credentials |
| **Backend API** | `backend/.env` | PostgreSQL credentials, CORS |
| **Frontend** | `frontend/.env` | Backend URL, refresh interval |

---

## 🔗 **Related Documentation**

- [README.md](../README.md) - Complete setup guide
- [ARCHITECTURE.md](../docs/ARCHITECTURE.md) - Technical architecture

---

## 📧 **Need Help?**

If configuration issues persist:

1. Check PostgreSQL is running: `psql -U postgres`
2. Check Kafka is running: `ps aux | grep kafka` (in WSL)
3. Verify network connectivity: `nc -zv localhost 9092`
4. Review service logs for specific error messages

---

**All `.env` files configured correctly = StreamPulse ready to run! 🚀**