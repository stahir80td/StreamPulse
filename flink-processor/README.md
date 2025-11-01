# Flink Processor

Real-time stream processing engine for StreamPulse. Consumes Avro-encoded events from Kafka, performs windowed aggregations, and writes results to PostgreSQL.

## Architecture

```
Kafka (Avro Events) → Flink Processor → PostgreSQL
                           ↓
                    Tumbling Windows (1 min)
                    ├─ Content Stats
                    ├─ Region Health
                    ├─ Device Stats
                    └─ Anomaly Detection
```

## Features

### 1. **Windowed Aggregations**
- **1-minute tumbling windows** for all metrics
- Exactly-once processing semantics
- Late event handling (within 5 minutes)

### 2. **Content Statistics**
- Downloads per content per minute
- Success/failure breakdown
- Aggregated by content_id

### 3. **Regional Health Monitoring**
- Performance metrics by region
- Success rate tracking
- Average speed and duration
- Automatic alerting for degraded regions

### 4. **Device Analytics**
- Performance by device type
- OS version tracking
- Speed comparisons across devices

### 5. **Anomaly Detection**
- High error rate alerts (>10%)
- Slow download alerts (<10 Mbps)
- Regional issues detection

## Setup

### Prerequisites
- Python 3.11+
- Access to Kafka cluster (Upstash)
- Access to PostgreSQL (Neon)

### Installation

```powershell
# Navigate to flink-processor directory
cd flink-processor

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Edit `.env` file:

```bash
# Kafka (Upstash)
KAFKA_BOOTSTRAP_SERVERS=your-endpoint.upstash.io:9092
KAFKA_USERNAME=your-username
KAFKA_PASSWORD=your-password

# PostgreSQL (Neon)
PG_HOST=your-db.neon.tech
PG_DATABASE=streampulse
PG_USER=your-username
PG_PASSWORD=your-password
```

## Running Locally

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Run processor
python src/processor.py
```

**Expected Output:**
```
✅ Configuration validated
   Kafka: your-endpoint.upstash.io:9092
   Topic: content-downloads
   Database: your-db.neon.tech/streampulse
   Parallelism: 1
✅ Loaded Avro schema from ../schemas/event.avsc
✅ Connected to Kafka consumer
🔄 Window flusher thread started
========================================================
🚀 StreamPulse Flink Processor
========================================================
📍 Topic: content-downloads
📊 Window Size: 60 seconds (tumbling)
🔐 Database: your-db.neon.tech/streampulse
========================================================

📊 Processed 50 events | Flushed 0 windows
📊 Processed 100 events | Flushed 0 windows
✅ Wrote 3 records to content_stats
✅ Wrote 5 records to region_health
📊 Processed 150 events | Flushed 1 windows
```

## Deployment

### Deploy to Railway

```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Set environment variables
railway variables set KAFKA_BOOTSTRAP_SERVERS=your-endpoint
railway variables set KAFKA_USERNAME=your-username
railway variables set KAFKA_PASSWORD=your-password
railway variables set PG_HOST=your-db-host
railway variables set PG_DATABASE=streampulse
railway variables set PG_USER=your-username
railway variables set PG_PASSWORD=your-password

# Deploy
railway up
```

## Processing Logic

### Content Stats Aggregation

```python
For each 1-minute window:
1. Group events by content_id
2. Count total downloads
3. Count successful vs failed
4. Write to content_stats table

Example:
Window: 19:15:00 - 19:16:00
- mov_avengers_2: 150 downloads (140 success, 10 failed)
- mov_taylor_swift: 90 downloads (85 success, 5 failed)
```

### Region Health Monitoring

```python
For each 1-minute window:
1. Group events by region
2. Calculate:
   - Success rate = successful / total
   - Average speed (Mbps)
   - Average duration (seconds)
3. Write to region_health table
4. Check thresholds:
   - If success_rate < 0.90 → Create WARNING alert
   - If success_rate < 0.80 → Create CRITICAL alert
   - If avg_speed < 10.0 → Create WARNING alert
```

### Windowing Strategy

```
Time: 19:15:00 ────────────── 19:16:00 ────────────── 19:17:00
      │                       │                       │
      └─── Window 1 ──────────┘                       │
                              └─── Window 2 ──────────┘

Tumbling Windows:
- No overlap
- Every event in exactly one window
- Flushed when window closes
```

## Metrics

Monitor these metrics in production:

- **Events Processed**: Total events consumed from Kafka
- **Windows Flushed**: Number of complete windows processed
- **Processing Lag**: Time between event timestamp and processing time
- **Alerts Generated**: Number of anomalies detected

## Troubleshooting

### Issue: "Failed to connect to Kafka"
```
Solution:
1. Check KAFKA_BOOTSTRAP_SERVERS is correct
2. Verify KAFKA_USERNAME and KAFKA_PASSWORD
3. Ensure firewall allows outbound connections
4. Test connection: telnet your-endpoint.upstash.io 9092
```

### Issue: "PostgreSQL connection failed"
```
Solution:
1. Verify PG_HOST, PG_DATABASE, PG_USER, PG_PASSWORD
2. Check if Neon database is active (not in sleep mode)
3. Ensure sslmode=require is set
4. Test connection: psql postgresql://user:pass@host/db
```

### Issue: "No events being processed"
```
Solution:
1. Check if event generator is running
2. Verify Kafka topic exists: content-downloads
3. Check consumer group offset: kafka-consumer-groups --describe
4. Ensure Avro schema matches producer schema
```

### Issue: "Events processed but no data in database"
```
Solution:
1. Check window flusher thread is running
2. Wait at least 60 seconds for first window to close
3. Check PostgreSQL logs for write errors
4. Verify tables exist: \dt in psql
```

## Performance

### Throughput
- **Single instance**: ~1,000 events/second
- **Bottleneck**: PostgreSQL writes
- **Optimization**: Batch writes every 60 seconds (window size)

### Latency
- **Event to database**: 60-65 seconds (window size + flush time)
- **Real-time query**: <100ms (PostgreSQL indexed queries)

### Resource Usage
- **Memory**: ~256 MB (small window state)
- **CPU**: <10% (mostly I/O wait)
- **Network**: ~500 KB/min (depends on event rate)

## Testing

### Unit Tests
```powershell
pytest tests/
```

### Integration Test
```powershell
# Terminal 1: Start processor
python src/processor.py

# Terminal 2: Send test events
cd ../event-generator
python src/generator.py

# Terminal 3: Query database
psql postgresql://your-connection-string
SELECT * FROM content_stats ORDER BY window_start DESC LIMIT 10;
```

## Production Checklist

- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure alerting (PagerDuty/Slack)
- [ ] Enable Flink checkpointing for fault tolerance
- [ ] Set up log aggregation (ELK stack)
- [ ] Configure auto-scaling based on Kafka lag
- [ ] Set up database connection pooling
- [ ] Enable SSL/TLS for all connections
- [ ] Document runbooks for common issues

## Future Enhancements

1. **ML Integration**
   - Real-time predictions for trending content
   - Anomaly detection with learned baselines

2. **Advanced Windowing**
   - Session windows for user behavior analysis
   - Sliding windows for trend detection

3. **State Management**
   - Store intermediate state in Redis
   - Enable faster recovery after crashes

4. **Multi-DC Support**
   - Process events from multiple Kafka clusters
   - Cross-region aggregations

## References

- [Apache Flink Documentation](https://flink.apache.org/docs/stable/)
- [Kafka Consumers Guide](https://kafka.apache.org/documentation/#consumerapi)
- [Avro Specification](https://avro.apache.org/docs/current/spec.html)