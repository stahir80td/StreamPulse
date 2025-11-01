# StreamPulse Quick Start Guide

**Get StreamPulse running on Windows in under 30 minutes!**

---

## ⚡ **Prerequisites Checklist**

Before starting, ensure you have:

- [ ] **Windows 10/11** with WSL2 installed
- [ ] **Python 3.11+** installed
- [ ] **Node.js 18+** installed
- [ ] **PostgreSQL 16** installed
- [ ] **Git** installed

---

## 🚀 **Setup Steps (5 Phases)**

### **Phase 1: Install Kafka on WSL (5 min)**

```bash
# Open WSL terminal
wsl

# Install Java & download Kafka
sudo apt update && sudo apt install -y default-jre
cd ~
wget https://downloads.apache.org/kafka/3.8.1/kafka_2.13-3.8.1.tgz
tar -xzf kafka_2.13-3.8.1.tgz
cd kafka_2.13-3.8.1

# Start Kafka (KRaft mode)
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties
bin/kafka-server-start.sh config/kraft/server.properties

# In NEW WSL terminal - create topic
cd ~/kafka_2.13-3.8.1
bin/kafka-topics.sh --create --topic content-downloads --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

---

### **Phase 2: Initialize PostgreSQL (3 min)**

```powershell
# In PowerShell
psql -U postgres

# In psql prompt
CREATE DATABASE streampulse;
\c streampulse
\q

# Run init script
cd C:\path\to\StreamPulse
psql -U postgres -d streampulse -f sql/init.sql
```

---

### **Phase 3: Configure .env Files (5 min)**

Create 4 `.env` files from templates:

```powershell
copy event-generator\.env.example event-generator\.env
copy flink-processor\.env.example flink-processor\.env
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
```

**⚠️ Edit these files:**
- `flink-processor/.env` - Change `PG_PASSWORD` to your PostgreSQL password
- `backend/.env` - Change `PG_PASSWORD` to your PostgreSQL password

All other defaults work for local setup!

---

### **Phase 4: Install Dependencies (10 min)**

```powershell
# Event Generator
cd event-generator
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..

# Flink Processor
cd flink-processor
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..

# Backend API
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..

# Frontend
cd frontend
npm install
cd ..
```

---

### **Phase 5: Run All Services (2 min)**

Open 5 terminals and run:

**Terminal 1 (WSL) - Kafka:**
```bash
wsl
cd ~/kafka_2.13-3.8.1
bin/kafka-server-start.sh config/kraft/server.properties
```

**Terminal 2 (PowerShell) - Event Generator:**
```powershell
cd C:\path\to\StreamPulse\event-generator
.\venv\Scripts\activate
python src/generator.py
```

**Terminal 3 (PowerShell) - Flink Processor:**
```powershell
cd C:\path\to\StreamPulse\flink-processor
.\venv\Scripts\activate
python src/processor.py
```

**Terminal 4 (PowerShell) - Backend API:**
```powershell
cd C:\path\to\StreamPulse\backend
.\venv\Scripts\activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 5 (PowerShell) - Frontend:**
```powershell
cd C:\path\to\StreamPulse\frontend
npm start
```

---

## ✅ **Verify Everything Works**

1. **Frontend:** http://localhost:3000 (should show live dashboard)
2. **Backend:** http://localhost:8000/health (should return JSON)
3. **Database:** Run `psql -U postgres -d streampulse` and check `SELECT COUNT(*) FROM content_stats;` returns > 0

---

## 📋 **All Commands in One Script**

Save this as `run_streampulse.ps1`:

```powershell
# StreamPulse Startup Script
# Run after Phase 1-4 complete

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "Starting StreamPulse Services..." -ForegroundColor Cyan

# Start Event Generator
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\event-generator'; .\venv\Scripts\activate; python src/generator.py"

# Wait 2 seconds
Start-Sleep -Seconds 2

# Start Flink Processor
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\flink-processor'; .\venv\Scripts\activate; python src/processor.py"

# Wait 2 seconds
Start-Sleep -Seconds 2

# Start Backend API
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\backend'; .\venv\Scripts\activate; uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"

# Wait 2 seconds
Start-Sleep -Seconds 2

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; npm start"

Write-Host "`nAll services started!" -ForegroundColor Green
Write-Host "Dashboard will open at http://localhost:3000" -ForegroundColor Yellow
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
```

**Usage:**
```powershell
.\run_streampulse.ps1
```

This opens 4 PowerShell windows automatically! (You still need to start Kafka manually in WSL)

---

## 🐛 **Common Issues & Fixes**

| Issue | Solution |
|-------|----------|
| **"Connection refused" Kafka** | Start Kafka in WSL: `cd ~/kafka_2.13-3.8.1 && bin/kafka-server-start.sh config/kraft/server.properties` |
| **"Password authentication failed"** | Update `PG_PASSWORD` in `.env` files |
| **"ModuleNotFoundError"** | Activate venv: `.\venv\Scripts\activate` then `pip install -r requirements.txt` |
| **Frontend "Failed to load"** | Wait 60 seconds for first Flink window to close and write data |
| **No data in dashboard** | Check Flink terminal - should see "✅ Wrote X records" |

---

## 📊 **What You'll See**

**Terminal 1 (Kafka):**
```
[KafkaRaftServer nodeId=1] Kafka Server started
```

**Terminal 2 (Event Generator):**
```
✅ Sent 10 events
✅ Sent 20 events
✅ Sent 30 events
```

**Terminal 3 (Flink Processor):**
```
📊 Processed 50 events | Flushed 1 windows
✅ Wrote 4 records to content_stats
✅ Wrote 5 records to region_health
```

**Terminal 4 (Backend):**
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: 127.0.0.1:56630 - "GET /api/stats/realtime" 200 OK
```

**Terminal 5 (Frontend):**
```
Compiled successfully!
Local: http://localhost:3000
```

**Browser (localhost:3000):**
- ✅ Stats cards showing numbers
- ✅ Charts updating every 2 seconds
- ✅ Live data flowing

---

## 📚 **Full Documentation**

- **[README.md](README.md)** - Complete setup guide
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical deep dive

---

## 🆘 **Need Help?**

If something doesn't work:

1. Check [README.md](README.md) troubleshooting section
2. Verify all 5 services are running
3. Check `.env` files have correct settings
4. Ensure PostgreSQL password is correct
5. Wait 60 seconds after starting for data to appear

**Most common issue:** Forgetting to change `PG_PASSWORD` in `.env` files!

---
