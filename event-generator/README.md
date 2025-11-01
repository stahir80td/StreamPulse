# Event Generator

Produces realistic content download events to Kafka using Avro serialization.

## Setup
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Kafka credentials
```

## Run Locally
```powershell
python src/generator.py
```

## Deploy to Railway
```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Set environment variables
railway variables set KAFKA_BOOTSTRAP_SERVERS=your-endpoint
railway variables set KAFKA_USERNAME=your-username
railway variables set KAFKA_PASSWORD=your-password

# Deploy
railway up
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker endpoint | localhost:9092 |
| `KAFKA_USERNAME` | SASL username (Upstash) | - |
| `KAFKA_PASSWORD` | SASL password (Upstash) | - |
| `KAFKA_TOPIC` | Target topic | content-downloads |
| `EVENTS_PER_MINUTE` | Event generation rate | 7 (=10K/day) |

## Event Distribution

- 50% Avengers: Endgame 2
- 30% Taylor Swift: Eras Tour
- 15% The Batman Returns
- 5% Barbie 2

**Outcomes:**
- 90% successful downloads
- 8% failed downloads
- 2% slow downloads