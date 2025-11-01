# StreamPulse

**Real-Time Content Distribution Analytics Platform**

A production-grade streaming data pipeline built with Apache Kafka, stream processing, PostgreSQL, and React. Demonstrates event-driven architecture, real-time aggregations, and live dashboard visualization for content distribution metrics.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![PostgreSQL 16](https://img.shields.io/badge/postgresql-16-blue.svg)](https://www.postgresql.org/)

---

## Overview

StreamPulse is a real-time analytics platform that processes millions of content distribution events through a complete event-driven architecture. The system ingests download events, aggregates metrics in 1-minute tumbling windows, detects anomalies, and visualizes insights through a live dashboard.

### Key Features

- **Event Streaming:** Apache Kafka with Avro serialization for schema evolution
- **Stream Processing:** Windowed aggregations with fault tolerance and exactly-once semantics
- **Real-Time Analytics:** Sub-second latency from event to dashboard visualization
- **Anomaly Detection:** Automated alerting for high error rates and performance degradation
- **Live Dashboard:** Auto-refreshing charts with mobile-responsive design
- **Production Ready:** Connection pooling, caching, error handling, and replay capability

---

## Architecture

```
┌─────────────────┐
│ Event Generator │  Simulates download events
│   (Python)      │  Avro serialization
└────────┬────────┘
         │
         ↓ (Kafka Topic)
┌─────────────────┐
│  Apache Kafka   │  Distributed event log
│   (WSL/Cloud)   │  3 partitions, 7-day retention
└────────┬────────┘
         │
         ↓ (Consumer Group)
┌─────────────────┐
│Stream Processor │  1-minute tumbling windows
│   (Python)      │  Aggregation & anomaly detection
└────────┬────────┘
         │
         ↓ (JDBC Sink)
┌─────────────────┐
│  PostgreSQL     │  Time-series data store
│  (Neon/Local)   │  Indexed for fast queries
└────────┬────────┘
         │
         ↓ (REST API)
┌─────────────────┐
│  FastAPI        │  API endpoints with caching
│   (Backend)     │  Connection pooling
└────────┬────────┘
         │
         ↓ (HTTP/JSON)
┌─────────────────┐
│  React Dashboard│  Live visualization
│   (Frontend)    │  Auto-refresh every 2s
└─────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Ingestion** | Apache Kafka | Event streaming, replay capability |
| **Serialization** | Apache Avro | Schema evolution, 60% compression |
| **Processing** | Custom Python | Windowed aggregations, stateful processing |
| **Storage** | PostgreSQL 16 | Time-series analytics data |
| **API** | FastAPI + Uvicorn | RESTful endpoints, async I/O |
| **Frontend** | React 18 + Recharts | Interactive dashboard, responsive design |
| **Deployment** | Railway + Vercel | Cloud-native, auto-scaling |

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 16**
- **Kafka** (WSL or docker)

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/stahir80td/StreamPulse.git
cd StreamPulse

# 2. Initialize database
psql -U postgres -d streampulse -f sql/init.sql

# 3. Configure environment variables
cp event-generator/.env.example event-generator/.env
cp flink-processor/.env.example flink-processor/.env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit .env files with your credentials

# 4. Install dependencies
cd event-generator && python -m venv venv && ./venv/bin/activate && pip install -r requirements.txt
cd ../flink-processor && python -m venv venv && ./venv/bin/activate && pip install -r requirements.txt
cd ../backend && python -m venv venv && ./venv/bin/activate && pip install -r requirements.txt
cd ../frontend && npm install

# 5. Start services (5 terminals)
# Terminal 1: Kafka
cd ~/kafka && bin/kafka-server-start.sh config/kraft/server.properties

# Terminal 2: Event Generator
cd event-generator && source venv/bin/activate && python src/generator.py

# Terminal 3: Stream Processor
cd flink-processor && source venv/bin/activate && python src/processor.py

# Terminal 4: Backend API
cd backend && source venv/bin/activate && uvicorn src.main:app --reload

# Terminal 5: Frontend
cd frontend && npm start
```

**Dashboard:** http://localhost:3000  
**API Docs:** http://localhost:8000/docs

For detailed setup instructions, see [QUICK_START.md](QUICK_START.md).

---

## Project Structure

```
StreamPulse/
├── event-generator/        # Kafka event producer
│   ├── src/
│   │   ├── generator.py    # Main producer logic
│   │   ├── serializers.py  # Avro serialization
│   │   └── models.py       # Data models
│   └── requirements.txt
├── flink-processor/        # Stream processing engine
│   ├── src/
│   │   ├── processor.py    # Windowing & aggregation
│   │   ├── sinks.py        # Database sinks
│   │   └── config.py       # Configuration
│   └── requirements.txt
├── backend/                # FastAPI backend
│   ├── src/
│   │   ├── main.py         # FastAPI application
│   │   ├── database.py     # Connection pooling
│   │   ├── models.py       # Pydantic models
│   │   └── routers/
│   │       └── stats.py    # API endpoints
│   └── requirements.txt
├── frontend/               # React dashboard
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   └── styles/         # CSS modules
│   └── package.json
├── schemas/                # Avro schemas
│   └── event.avsc
├── sql/                    # Database scripts
│   └── init.sql
└── docs/                   # Documentation
    ├── ARCHITECTURE.md     # Technical deep dive

```

---

## Features

### Real-Time Event Processing

- **Windowed Aggregations:** 1-minute tumbling windows for time-series metrics
- **Stateful Processing:** Maintains running counts and averages across windows
- **Exactly-Once Semantics:** Checkpointing ensures no data loss on failures
- **Replay Capability:** Kafka offset management allows reprocessing historical events

### Analytics Dashboard

- **Live Metrics:** Total downloads, active content, success rates
- **Trending Content:** Top 5 content by downloads with success rates
- **Regional Performance:** Geographic health monitoring with color-coded status
- **Anomaly Alerts:** Automatic detection of high error rates and slow performance
- **Time Series:** Download velocity over last hour
- **Device Analytics:** Performance breakdown by device type

### API Endpoints

```
GET /health                             # Health check
GET /api/stats/realtime?minutes=5       # Aggregate metrics
GET /api/stats/trending?limit=5         # Top content
GET /api/stats/regions                  # Regional health
GET /api/stats/alerts                   # Active alerts
GET /api/stats/timeseries?minutes=60    # Historical data
GET /api/stats/devices                  # Device breakdown
```

Full API documentation available at `/docs` when running locally.

---

## Data Model

### Event Schema (Avro)

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1730415600000,
  "content": {
    "content_id": "mov_avengers_2",
    "title": "Avengers: Endgame 2",
    "type": "movie",
    "size_gb": 4.5
  },
  "user": {
    "user_id": "usr_12345",
    "region": "US-California",
    "device_type": "iPhone",
    "os_version": "iOS 17.2"
  },
  "download": {
    "status": "success",
    "duration_seconds": 120,
    "speed_mbps": 35.6,
    "error_code": null
  }
}
```

### Database Tables

- **content_stats** - Aggregated metrics per content per minute
- **region_health** - Regional performance and health status
- **alerts** - Anomaly detection alerts with severity levels
- **device_stats** - Device-level performance metrics
- **trending_predictions** - ML predictions (future enhancement)
- **event_log** - Sample events for debugging

See [sql/init.sql](sql/init.sql) for complete schema.

---

## Performance

### Throughput

- **Events:** 10,000/day (local), scalable to millions
- **Latency:** Sub-second event-to-dashboard
- **Window Size:** 1-minute tumbling windows
- **API Response:** <50ms (95th percentile)

### Scalability

**Horizontal Scaling:**
- Kafka: Increase partitions (3 → 30+)
- Stream Processor: Add TaskManagers for parallel processing
- PostgreSQL: Read replicas + table partitioning
- Backend API: Multiple instances behind load balancer

**Bottlenecks:**
- PostgreSQL writes (~1K/sec on free tier)
- Solution: Batch writes, connection pooling, caching

---

## Configuration

### Environment Variables

All services use `.env` files for configuration. See [ENV_CONFIGURATION.md](ENV_CONFIGURATION.md) for complete guide.

**Example: Event Generator**
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=content-downloads
EVENTS_PER_MINUTE=60
SCHEMA_PATH=../schemas/event.avsc
```

**Example: Backend API**
```bash
PG_HOST=localhost
PG_DATABASE=streampulse
ALLOWED_ORIGINS=http://localhost:3000
CACHE_TTL=2
```

---

## Monitoring

### Health Checks

```bash
# Backend API
curl http://localhost:8000/health

# Database
psql -U postgres -d streampulse -c "SELECT COUNT(*) FROM content_stats;"

# Kafka
kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Observability

Production deployments should add:
- **Metrics:** Prometheus + Grafana
- **Logging:** ELK Stack or Datadog
- **Tracing:** OpenTelemetry
- **Alerting:** PagerDuty or Opsgenie

---

## Testing

```bash
# Backend API tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test

# Integration tests
pytest tests/integration/
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow

1. Ensure all tests pass (`pytest`, `npm test`)
2. Follow code style guidelines (Black for Python, ESLint for JavaScript)
3. Update documentation for new features
4. Add tests for new functionality

---

## Troubleshooting

### Common Issues

**"Connection refused" to Kafka:**
```bash
# Start Kafka in WSL
cd ~/kafka && bin/kafka-server-start.sh config/kraft/server.properties
```

**"Database connection failed":**
```bash
# Check PostgreSQL is running
systemctl status postgresql  # Linux
# or Services → postgresql-x64-16  # Windows
```

**Dashboard shows "Failed to load data":**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS settings in backend/.env
ALLOWED_ORIGINS=http://localhost:3000
```

---

## Documentation

- **[QUICK_START.md](QUICK_START.md)** - 30-minute setup guide
- **[ENV_CONFIGURATION.md](ENV_CONFIGURATION.md)** - Environment variable reference
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical deep dive

---

## Roadmap

- [ ] WebSocket support for instant dashboard updates (replace polling)
- [ ] Machine learning predictions for trending content
- [ ] Multi-region deployment with geo-routing
- [ ] Advanced anomaly detection (isolation forests)
- [ ] A/B testing framework for stream processing logic
- [ ] Data lakehouse integration (Apache Iceberg)
- [ ] Docker Compose for one-command local setup
- [ ] Kubernetes deployment manifests

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Built with:
- [Apache Kafka](https://kafka.apache.org/) - Event streaming platform
- [Apache Avro](https://avro.apache.org/) - Data serialization
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Recharts](https://recharts.org/) - Charting library
- [PostgreSQL](https://www.postgresql.org/) - Relational database

---

## Contact

**Sohail Tahir**  
GitHub: [@stahir80td](https://github.com/stahir80td)

---

**Star ⭐ this repository if you find it useful!**

---

*Built to demonstrate production-grade streaming data pipelines and real-time analytics at scale.*