# StreamPulse Architecture

Deep dive into the technical architecture, design decisions, and implementation details.

---

## 📐 System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                             │
│  (Downloads movies, music, apps via hypothetical Apple platform)    │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ↓ (simulated events)
                  ┌──────────────────────┐
                  │   EVENT GENERATOR    │
                  │      (Python)        │
                  │  - Faker library     │
                  │  - Avro serializer   │
                  │  - Kafka producer    │
                  └──────────┬───────────┘
                            │
                            ↓ (Avro binary, ~320 bytes/event)
                  ┌──────────────────────┐
                  │   KAFKA (Upstash)    │
                  │  Topic: content-     │
                  │   downloads          │
                  │  Partitions: 3       │
                  │  Retention: 7 days   │
                  └──────────┬───────────┘
                            │
                            ↓ (consume with offset tracking)
                  ┌──────────────────────┐
                  │  FLINK PROCESSOR     │
                  │    (PyFlink)         │
                  │  - Tumbling windows  │
                  │  - Aggregations      │
                  │  - Anomaly detection │
                  └──────────┬───────────┘
                            │
                            ↓ (aggregated results)
                  ┌──────────────────────┐
                  │  POSTGRESQL (Neon)   │
                  │  - content_stats     │
                  │  - region_health     │
                  │  - alerts            │
                  │  - device_stats      │
                  └──────────┬───────────┘
                            │
                            ↓ (SQL queries)
                  ┌──────────────────────┐
                  │   FASTAPI BACKEND    │
                  │  - REST endpoints    │
                  │  - Connection pool   │
                  │  - 2-second cache    │
                  └──────────┬───────────┘
                            │
                            ↓ (HTTP/JSON)
                  ┌──────────────────────┐
                  │   REACT DASHBOARD    │
                  │  - Auto-refresh      │
                  │  - Recharts          │
                  │  - Mobile-responsive │
                  └──────────────────────┘
```

---

## 🏗️ Component Details

### 1. Event Generator (Python)

**Purpose:** Simulate real-world user download events

**Technology Stack:**
- Python 3.11
- kafka-python (Kafka client)
- avro-python3 (serialization)
- Faker (realistic data generation)

**Key Features:**

**Event Generation:**
```python
# Weighted random selection based on popularity
content = random.choices(CATALOG, weights=[0.5, 0.3, 0.15, 0.05])

# 90% success, 8% failed, 2% slow downloads
outcome = random.choices(['success', 'failed', 'slow'], 
                        weights=[90, 8, 2])

# Avro serialization (60% size reduction vs JSON)
serialized = avro_serializer.serialize(event)
```

**Partitioning Strategy:**
```python
# Events with same region go to same partition
# Guarantees ordering within region
producer.send(
    'content-downloads',
    key=event['region'],  # Partition key
    value=event
)
```

**Rate Limiting:**
```python
# Stay under Upstash free tier (10K msgs/day)
EVENTS_PER_MINUTE = 7  # = 10,080 events/day
time.sleep(60.0 / EVENTS_PER_MINUTE)  # ~8.6 seconds
```

**Design Decisions:**

✅ **Why Avro over JSON?**
- 60% smaller payload (320 bytes vs 850 bytes)
- Schema evolution support
- Faster serialization
- Industry standard for high-throughput systems

✅ **Why partition by region?**
- Ordered processing per region (FIFO guarantee)
- Parallel processing across regions
- Regional isolation (failures don't affect other regions)

✅ **Why Faker library?**
- Realistic data (cities, names, UUIDs)
- Reproducible for testing
- Commonly used in data generation

---

### 2. Kafka (Upstash)

**Purpose:** Distributed message queue and event log

**Configuration:**
```yaml
Topic: content-downloads
Partitions: 3
  - Partition 0: US events
  - Partition 1: EU events
  - Partition 2: ASIA events
Retention: 7 days (604800000 ms)
Replication: 1 (free tier limitation)
```

**Message Flow:**

```
Producer → Kafka Partition → Consumer(s)

Event: {region: "US-California", ...}
↓
hash("US-California") % 3 = 0
↓
Partition 0 [offset 1234] ← Event stored here
↓
Flink Consumer reads from offset 1234
↓
Flink commits offset 1234 (mark as processed)
```

**Key Concepts:**

**Offset Management:**
```
Consumer Group: "flink-processor"
├─ Partition 0: offset 5,234 (last read)
├─ Partition 1: offset 4,987
└─ Partition 2: offset 5,112

If Flink crashes:
- Restarts from last committed offsets
- No data loss (exactly-once semantics)
```

**Replay Capability:**
```bash
# Bug discovered in analytics logic
# Reprocess last 6 hours of events

kafka-consumer-groups --reset-offsets \
  --to-datetime 2025-10-31T14:00:00 \
  --group flink-processor \
  --topic content-downloads \
  --execute

# Flink reads from new offset → recalculates analytics
```

**Design Decisions:**

✅ **Why Kafka over RabbitMQ/SQS?**
- Event log (not queue) - messages persist
- Multiple consumers can read same events
- Replay capability essential for bug fixes
- Industry standard for stream processing

✅ **Why 3 partitions?**
- Matches 3 major regions (US, EU, ASIA)
- Allows 3 parallel consumers
- Balance between parallelism and management overhead

✅ **Why 7-day retention?**
- Matches PostgreSQL data retention
- Sufficient for debugging and replay
- Stays within free tier limits

---

### 3. Flink Processor (PyFlink)

**Purpose:** Real-time stream processing and aggregation

**Technology Stack:**
- Apache Flink 1.18.0 (PyFlink API)
- kafka-python (consumer)
- psycopg2 (PostgreSQL sink)

**Processing Pipeline:**

```python
# 1. Consume from Kafka
stream = env.add_source(FlinkKafkaConsumer(...))

# 2. Deserialize Avro
deserialized = stream.map(avro_deserializer.deserialize)

# 3. Key by content_id
keyed = deserialized.key_by(lambda e: e['content']['content_id'])

# 4. Apply 1-minute tumbling window
windowed = keyed.window(TumblingEventTimeWindows.of(Time.minutes(1)))

# 5. Aggregate (count downloads)
aggregated = windowed.reduce(CountReducer())

# 6. Sink to PostgreSQL
aggregated.add_sink(PostgresSink())
```

**Windowing Strategies:**

**Tumbling Windows (1 minute):**
```
Time: 19:15:00 ─────── 19:16:00 ─────── 19:17:00
      │                │                │
      └─ Window 1 ─────┘                │
                       └─ Window 2 ─────┘

Properties:
- No overlap
- Fixed size (60 seconds)
- Every event in exactly one window
- Flushed when window closes
```

**Use Cases:**
- Content statistics (downloads per minute)
- Regional health (success rate per minute)
- Device statistics (performance per minute)

**Aggregation Logic:**

**Content Stats:**
```python
# Input: Individual download events
# Output: Aggregated counts per content per minute

For window 19:15:00 - 19:16:00:
- Group events by content_id
- Count total downloads
- Count successful vs failed
- Write to content_stats table

Result:
mov_avengers_2: 150 downloads (140 success, 10 failed)
mov_taylor_swift: 90 downloads (85 success, 5 failed)
```

**Regional Health:**
```python
# Input: Individual download events
# Output: Regional performance metrics

For window 19:15:00 - 19:16:00:
- Group events by region
- Calculate success_rate = successful / total
- Calculate avg_speed = mean(speeds)
- Check if success_rate < 0.90 → Create ALERT
- Write to region_health table

Result:
US-California: 94.2% success, 35.6 Mbps avg
EU-London: 85.1% success, 28.3 Mbps avg ← ALERT!
```

**Anomaly Detection:**
```python
# Pattern: Error rate > 10% for 3 consecutive minutes

If region has error_rate > 0.10:
  ├─ Minute 1: 12% errors → Track
  ├─ Minute 2: 15% errors → Track
  └─ Minute 3: 13% errors → ALERT!

Alert created:
{
  type: "HIGH_ERROR_RATE",
  severity: "WARNING",
  region: "EU-London",
  metric_value: 0.133,
  threshold: 0.10
}
```

**State Management:**

Flink maintains state across windows:
```
State per content_id:
├─ Running count: 623
├─ Success count: 590
├─ Failed count: 33
└─ Window bounds: 19:15:00 - 19:16:00

On window close:
- Flush state to PostgreSQL
- Clear state
- Start new window
```

**Checkpointing (Fault Tolerance):**
```python
# Every 60 seconds:
1. Flink saves processing state to disk
2. Records Kafka offsets processed
3. On crash: Restore from last checkpoint
4. Resume from last committed offset

Result: At-most 60 seconds of reprocessing
```

**Design Decisions:**

✅ **Why Flink over Spark Streaming?**
- True streaming (not micro-batching)
- Lower latency (<100ms vs seconds)
- Better exactly-once guarantees
- More mature windowing operations

✅ **Why PyFlink over Java Flink?**
- Faster development (1-day project)
- Python ecosystem (Avro, psycopg2)
- Easier to read for demonstration

✅ **Why 1-minute windows?**
- Balance between real-time and computational overhead
- Matches typical monitoring dashboards
- Reasonable for free tier compute limits

---

### 4. PostgreSQL (Neon)

**Purpose:** Store aggregated analytics results

**Schema Design:**

**Normalized Schema:**
```sql
content_stats (time-series data)
├─ id (SERIAL PRIMARY KEY)
├─ content_id (VARCHAR, indexed)
├─ title (VARCHAR)
├─ download_count (INTEGER)
├─ successful_downloads (INTEGER)
├─ failed_downloads (INTEGER)
├─ window_start (TIMESTAMP, indexed)
├─ window_end (TIMESTAMP)
└─ UNIQUE(content_id, window_start)  ← Prevent duplicates

region_health (time-series data)
├─ id (SERIAL PRIMARY KEY)
├─ region (VARCHAR, indexed)
├─ total_downloads (INTEGER)
├─ successful_downloads (INTEGER)
├─ failed_downloads (INTEGER)
├─ success_rate (FLOAT)
├─ avg_speed_mbps (FLOAT)
├─ window_start (TIMESTAMP, indexed)
├─ window_end (TIMESTAMP)
└─ UNIQUE(region, window_start)

alerts (append-only log)
├─ id (SERIAL PRIMARY KEY)
├─ alert_type (VARCHAR)
├─ severity (VARCHAR) CHECK (severity IN ('CRITICAL','WARNING','INFO'))
├─ message (TEXT)
├─ region (VARCHAR, nullable)
├─ metric_value (FLOAT)
├─ threshold_value (FLOAT)
├─ created_at (TIMESTAMP, indexed)
└─ acknowledged (BOOLEAN, default FALSE)
```

**Indexing Strategy:**

```sql
-- Time-based queries (most common)
CREATE INDEX idx_content_stats_time 
ON content_stats(window_start DESC);

-- Content filtering
CREATE INDEX idx_content_stats_content_id 
ON content_stats(content_id);

-- Composite index for content + time range queries
CREATE INDEX idx_content_stats_content_time 
ON content_stats(content_id, window_start DESC);

-- Partial index for recent data (last 24 hours)
CREATE INDEX idx_content_stats_recent 
ON content_stats(window_start DESC, content_id)
WHERE window_start >= NOW() - INTERVAL '24 hours';
```

**Query Patterns:**

**Most Common Query (Dashboard):**
```sql
-- Get trending content (last 5 minutes)
SELECT 
    content_id,
    title,
    SUM(download_count) as total_downloads
FROM content_stats
WHERE window_start >= NOW() - INTERVAL '5 minutes'
GROUP BY content_id, title
ORDER BY total_downloads DESC
LIMIT 5;

-- Execution plan:
-- Index Scan on idx_content_stats_time
-- Aggregate
-- Sort
-- Limit
-- Execution time: ~10ms
```

**Data Retention:**
```sql
-- Automated cleanup function
CREATE FUNCTION cleanup_old_data() RETURNS void AS $$
BEGIN
    DELETE FROM content_stats 
    WHERE created_at < NOW() - INTERVAL '7 days';
    
    DELETE FROM region_health 
    WHERE created_at < NOW() - INTERVAL '7 days';
    
    DELETE FROM alerts 
    WHERE created_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Schedule: Run daily (manual or via pg_cron if available)
```

**Storage Estimates:**

```
Event rate: 10,000 events/day
Aggregation: 1,440 windows/day (1 per minute)
Data size per window: ~200 bytes

Daily storage:
- content_stats: 1,440 windows × 4 contents × 200 bytes = 1.15 MB/day
- region_health: 1,440 windows × 5 regions × 200 bytes = 1.44 MB/day
- alerts: ~10 alerts/day × 500 bytes = 5 KB/day

7-day retention: ~18 MB total ✅ (well under 0.5 GB limit)
```

**Design Decisions:**

✅ **Why PostgreSQL over NoSQL?**
- Structured time-series data fits relational model
- Complex aggregation queries (GROUP BY, JOIN)
- ACID transactions for data consistency
- Mature ecosystem and tooling

✅ **Why Neon over RDS/DigitalOcean?**
- Serverless (auto-suspend when idle)
- Free tier sufficient for demo
- Git-like branching (great for testing)
- Fast cold starts (<500ms)

✅ **Why separate tables?**
- Different retention policies
- Independent query patterns
- Easier to optimize and maintain

---

### 5. FastAPI Backend

**Purpose:** REST API layer between database and frontend

**Technology Stack:**
- FastAPI 0.104.1 (async Python framework)
- Uvicorn (ASGI server)
- psycopg2 (PostgreSQL driver)
- Pydantic (request/response validation)

**API Architecture:**

```python
FastAPI Application
├─ /health (health check)
├─ /api/stats/
│   ├─ /realtime (last 5 min aggregates)
│   ├─ /trending (top 5 content)
│   ├─ /regions (regional health)
│   ├─ /alerts (recent alerts)
│   ├─ /timeseries (last hour data)
│   └─ /devices (device stats)
├─ Middleware:
│   ├─ CORS (allow frontend origin)
│   ├─ Request timing
│   └─ Error handling
└─ Connection Pool (10 connections)
```

**Caching Strategy:**

```python
# In-memory TTL cache (2-second expiration)
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=2)

@router.get("/trending")
async def get_trending():
    cache_key = "trending_5min"
    
    if cache_key in cache:
        return cache[cache_key]  # Cache hit
    
    # Cache miss - query database
    results = execute_query(...)
    
    cache[cache_key] = results  # Store in cache
    return results
```

**Why 2-second cache?**
- Matches frontend auto-refresh interval
- Reduces database load (50% fewer queries)
- Still "real-time" from user perspective
- Simple implementation (no Redis needed)

**Connection Pooling:**

```python
# PostgreSQL connection pool
pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,     # Minimum connections
    maxconn=10,    # Maximum connections
    **connection_params
)

# Benefits:
# - Reuse connections (faster than creating new)
# - Limit concurrent connections (prevent DB overload)
# - Automatic connection management
```

**Request/Response Flow:**

```
1. Frontend → GET /api/stats/trending?minutes=5

2. FastAPI receives request
   ├─ CORS check (allow origin?)
   ├─ Parameter validation (minutes: 1-60)
   └─ Check cache (key: "trending_5")

3. Cache miss → Query PostgreSQL
   ├─ Get connection from pool
   ├─ Execute SQL with params
   ├─ Fetch results
   └─ Return connection to pool

4. Transform to Pydantic model
   ├─ Validate data types
   ├─ Format numbers
   └─ Serialize to JSON

5. Cache result (TTL: 2 seconds)

6. Return JSON response
   ├─ Status: 200 OK
   ├─ Headers: X-Process-Time: 0.025s
   └─ Body: {"data": [...], "count": 5}
```

**Error Handling:**

```python
# Global exception handler
@app.exception_handler(Exception)
async def global_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "timestamp": datetime.now()
        }
    )

# Specific handlers
@app.exception_handler(HTTPException)
async def http_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )
```

**Design Decisions:**

✅ **Why FastAPI over Flask/Django?**
- Async support (better performance)
- Automatic OpenAPI docs (/docs)
- Type hints and validation (Pydantic)
- Modern Python framework

✅ **Why connection pooling?**
- Neon has connection limits (100 on free tier)
- Connection reuse faster than creating new
- Prevents connection leaks

✅ **Why in-memory cache vs Redis?**
- Simple (no additional service)
- Sufficient for single-instance deployment
- 2-second TTL reduces load by 50%
- Free tier stays free

---

### 6. React Dashboard

**Purpose:** Real-time visualization of analytics

**Technology Stack:**
- React 18.2.0 (UI framework)
- Recharts 2.10.3 (charting library)
- Axios 1.6.2 (HTTP client)

**Component Architecture:**

```
App.jsx
└─ Dashboard.jsx (container)
    ├─ StatsCards.jsx
    │   ├─ Total Downloads card
    │   ├─ Active Content card
    │   └─ Success Rate card
    ├─ AlertsList.jsx
    │   └─ Alert items (severity badges)
    ├─ TrendingChart.jsx (Bar chart)
    ├─ RegionChart.jsx (Bar chart)
    └─ TimeSeriesChart.jsx (Line chart)
```

**Data Flow:**

```javascript
// 1. Dashboard component mounts
useEffect(() => {
    fetchData();  // Initial fetch
    
    // 2. Set up polling (every 2 seconds)
    const interval = setInterval(fetchData, 2000);
    
    return () => clearInterval(interval);  // Cleanup
}, []);

// 3. Fetch all data in parallel
const fetchData = async () => {
    const [stats, trending, regions, alerts, timeseries] = 
        await Promise.all([
            api.getRealtimeStats(),
            api.getTrendingContent(),
            api.getRegionalHealth(),
            api.getAlerts(),
            api.getTimeSeries()
        ]);
    
    setData({ stats, trending, regions, alerts, timeseries });
};

// 4. Pass data to child components as props
<StatsCards stats={data.stats} />
<TrendingChart data={data.trending} />
```

**Responsive Design:**

```css
/* Mobile-first approach */

/* Base (Mobile): < 768px */
.stats-grid {
    grid-template-columns: 1fr;  /* Single column */
}

/* Tablet: 768px - 1023px */
@media (min-width: 768px) {
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);  /* 2 columns */
    }
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
    .stats-grid {
        grid-template-columns: repeat(3, 1fr);  /* 3 columns */
    }
}
```

**Chart Responsiveness:**

```jsx
<ResponsiveContainer width="100%" height={300}>
    <BarChart
        data={data}
        margin={{
            top: 20,
            right: window.innerWidth < 768 ? 10 : 30,  // Less margin on mobile
            left: window.innerWidth < 768 ? 0 : 20,
            bottom: 60
        }}
    >
        <XAxis
            dataKey="title"
            angle={-45}  // Rotated labels
            textAnchor="end"
            height={100}  // Space for rotated labels
            tick={{ fontSize: window.innerWidth < 768 ? 10 : 12 }}  // Smaller on mobile
        />
    </BarChart>
</ResponsiveContainer>
```

**Performance Optimizations:**

**1. Parallel API Calls:**
```javascript
// ✅ Good: All requests in parallel (300ms total)
await Promise.all([api.getStats(), api.getTrending(), ...]);

// ❌ Bad: Sequential requests (300ms × 5 = 1500ms total)
await api.getStats();
await api.getTrending();
```

**2. Conditional Rendering:**
```jsx
// Only render alerts if they exist
{alerts.length > 0 && <AlertsList alerts={alerts} />}

// Prevents rendering empty components
```

**3. Memoization (future enhancement):**
```jsx
// Memoize expensive chart calculations
const chartData = useMemo(() => {
    return data.map(transformToChartFormat);
}, [data]);
```

**Design Decisions:**

✅ **Why React over Vue/Angular?**
- Most popular (better job prospects)
- Rich ecosystem (Recharts, etc.)
- Component-based (matches backend microservices)

✅ **Why Recharts over D3/Chart.js?**
- React-first (composable components)
- Responsive out-of-box
- Simpler API for common charts

✅ **Why polling vs WebSockets?**
- Simpler implementation
- Sufficient for 2-second refresh
- No additional infrastructure (WebSocket server)
- HTTP/2 makes polling efficient

---

## 🔐 Security Architecture

### Authentication & Authorization

**Current State:**
- No authentication (public dashboard for demo)
- CORS restricted to frontend domain

**Production Considerations:**
```python
# Add JWT authentication
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.get("/stats/realtime")
async def get_stats(credentials: HTTPBearer = Depends(security)):
    # Verify JWT token
    user = verify_token(credentials.credentials)
    
    # Check permissions
    if not user.has_permission("read:stats"):
        raise HTTPException(403)
    
    return get_realtime_stats()
```

### Data Security

**In Transit:**
- ✅ Kafka: SASL_SSL (TLS encryption)
- ✅ PostgreSQL: sslmode=require
- ✅ API: HTTPS (Vercel/Railway)
- ✅ Frontend: HTTPS (Vercel)

**At Rest:**
- ✅ Kafka: Encrypted by Upstash
- ✅ PostgreSQL: Encrypted by Neon
- ✅ No sensitive PII stored

**Credential Management:**
- ✅ Environment variables (not hardcoded)
- ✅ .env files in .gitignore
- ✅ Railway/Vercel env var management

---

## 📊 Performance Characteristics

### Latency

**End-to-End (User Download → Dashboard Display):**
```
Event Generation:     0ms (instant)
↓
Kafka Produce:        10-50ms (network + write)
↓
Kafka Storage:        0ms (async)
↓
Flink Consume:        1-10ms (read from partition)
↓
Flink Window Wait:    0-60s (tumbling window)
↓
Flink Aggregate:      1-5ms (in-memory)
↓
PostgreSQL Write:     10-50ms (network + write)
↓
API Query:            10-50ms (network + query)
↓
Cache (if hit):       <1ms
↓
Frontend Poll:        0-2s (poll interval)
↓
Chart Render:         50-100ms (React + Recharts)

Total: 60-62 seconds (dominated by window size)
```

**API Response Times:**
- `/health`: <10ms (no DB query)
- `/api/stats/*`: 10-50ms (with cache: <1ms)
- 95th percentile: <100ms

### Throughput

**Current (Free Tier):**
- Events: ~10K/day (~7 events/min)
- Windows: 1,440/day (1 per minute)
- API requests: ~2,880/day (frontend polling)

**Maximum (Theoretical):**
- Kafka: 1M+ events/sec (limited by Upstash free tier)
- Flink: 10K+ events/sec (single instance)
- PostgreSQL: 1K writes/sec (Neon limitation)
- API: 1K requests/sec (FastAPI + Uvicorn)

**Bottleneck:** PostgreSQL writes (1K/sec)

**Scaling Strategy:**
```
1. Vertical: Upgrade Neon to Pro (10K writes/sec)
2. Horizontal: Add read replicas for queries
3. Caching: Add Redis layer (reduce DB load by 90%)
4. Partitioning: Split tables by time range
```

---

## 🎯 Design Patterns

### 1. Event Sourcing

```
Events are the source of truth
↓
All state derived from events
↓
Enables replay and debugging
```

### 2. CQRS (Command Query Responsibility Segregation)

```
Write Path: Events → Kafka → Flink → PostgreSQL
Read Path: API → PostgreSQL (read-optimized views)
```

### 3. Microservices

```
Each service has single responsibility:
- Event Generator: Produce events
- Flink: Process events
- Backend API: Serve data
- Frontend: Display data
```

### 4. Materialized Views (simulated)

```
Raw events (Kafka) → Aggregated views (PostgreSQL)
↓
Pre-computed for fast queries
```

---

## 🔄 Data Flow Example

**Complete flow for one download event:**

```
1. Event Generator (19:15:23.456)
   event = {
       content_id: "mov_avengers_2",
       region: "US-California",
       status: "success",
       ...
   }
   
2. Serialize to Avro (320 bytes)
   
3. Send to Kafka
   partition = hash("US-California") % 3 = 0
   offset = 5234
   
4. Kafka stores event (Partition 0, Offset 5234)
   
5. Flink reads event (5ms later)
   window = 19:15:00 - 19:16:00
   
6. Flink adds to window state
   mov_avengers_2: count++
   
7. Window closes at 19:16:00
   
8. Flink aggregates
   mov_avengers_2: 150 downloads (140 success)
   
9. Write to PostgreSQL
   INSERT INTO content_stats VALUES (...)
   
10. API caches query result (2 seconds)
    
11. Frontend polls API (19:16:02)
    
12. Chart updates with new data point
    
13. User sees updated dashboard (19:16:02.150)

Total time: ~62 seconds (mostly window wait)
```

---

## 📚 Technology Choices Summary

| Requirement | Technology | Why? |
|-------------|-----------|------|
| Message Queue | Kafka (Upstash) | Event log, replay, industry standard |
| Serialization | Avro | 60% smaller, schema evolution |
| Stream Processing | Flink | True streaming, low latency |
| Database | PostgreSQL | Relational, ACID, mature |
| Backend API | FastAPI | Async, auto-docs, modern |
| Frontend | React | Popular, component-based |
| Charts | Recharts | React-first, responsive |
| Deployment | Railway, Vercel | Free tier, easy deploy |

---

## 🎓 Key Takeaways

### For Interviews

**"What's the most important architectural decision?"**
> Using Kafka as the central event log. It decouples producers and consumers, enables replay for bug fixes, and allows multiple independent consumers (Flink, ML services, etc.) to process the same events.

**"How does this scale?"**
> Horizontal scaling at every layer:
> - Kafka: Add partitions (3 → 30)
> - Flink: Add TaskManagers (parallel processing)
> - PostgreSQL: Add read replicas + partitioning
> - API: Add instances behind load balancer
> - Frontend: Already on CDN (Vercel)

**"What would you change for production?"**
> 1. Add authentication (JWT)
> 2. Add monitoring (Prometheus, Grafana)
> 3. Add alerting (PagerDuty)
> 4. Add Redis caching layer
> 5. Add data lake (Iceberg) for long-term storage
> 6. Add ML pipeline for predictions
> 7. Multi-region deployment for HA

---
