# Event Schemas

This directory contains Avro schema definitions for StreamPulse events.

## Why Avro?

**Avro** is a binary serialization format that offers:
- **60% size reduction** vs JSON (850 bytes → 320 bytes per event)
- **Schema evolution** - add fields without breaking consumers
- **Fast serialization/deserialization** - optimized for high throughput
- **Self-documenting** - schema is embedded in the data

At scale (10M events/day), Avro saves **5.3 GB/day** in network transfer and storage.

## Schema: ContentDownloadEvent

### Structure
```
ContentDownloadEvent
├── event_id (string) - UUID
├── timestamp (long) - Unix timestamp in milliseconds
├── user_id (string) - Anonymized user ID
├── content (record)
│   ├── content_id (string) - e.g., "mov_avengers_2"
│   ├── title (string) - e.g., "Avengers: Endgame 2"
│   ├── type (string) - movie, tv_show, music, app, book
│   ├── category (string) - action, comedy, drama, etc.
│   ├── size_mb (int) - Content size
│   └── price (float) - USD price
├── download (record)
│   ├── status (string) - success, failed, cancelled
│   ├── duration_seconds (int)
│   ├── speed_mbps (float)
│   ├── error_code (string, optional) - cdn_timeout, network_error, etc.
│   └── error_message (string, optional)
└── user_context (record)
    ├── region (string) - US-California, EU-London, etc.
    ├── city (string)
    ├── device (string) - iPhone, iPad, etc.
    ├── os_version (string)
    └── connection_type (string) - wifi, 5g, 4g
```

### Example Event (JSON representation)
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1698768000000,
  "user_id": "user_abc123",
  "content": {
    "content_id": "mov_avengers_2",
    "title": "Avengers: Endgame 2",
    "type": "movie",
    "category": "action",
    "size_mb": 4200,
    "price": 19.99
  },
  "download": {
    "status": "success",
    "duration_seconds": 120,
    "speed_mbps": 35.0,
    "error_code": null,
    "error_message": null
  },
  "user_context": {
    "region": "US-California",
    "city": "San Francisco",
    "device": "iPhone 15 Pro",
    "os_version": "iOS 18.1",
    "connection_type": "wifi"
  }
}
```

### Schema Evolution

Avro supports adding optional fields without breaking existing consumers:
```json
// Version 2: Add optional field
{
  "name": "content_rating",
  "type": ["null", "string"],
  "default": null,
  "doc": "Content rating: G, PG, PG-13, R"
}
```

Old consumers reading Version 2 events will ignore the new field. ✅

## Usage

### Python (Producer)
```python
import avro.schema
import avro.io
import io

# Load schema
schema = avro.schema.parse(open("schemas/event.avsc").read())

# Serialize event
def serialize(event_dict):
    writer = avro.io.DatumWriter(schema)
    bytes_writer = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)
    writer.write(event_dict, encoder)
    return bytes_writer.getvalue()
```

### Python (Consumer)
```python
# Deserialize event
def deserialize(event_bytes):
    bytes_reader = io.BytesIO(event_bytes)
    decoder = avro.io.BinaryDecoder(bytes_reader)
    reader = avro.io.DatumReader(schema)
    return reader.read(decoder)
```

## Testing Schema Changes
```bash
# Validate schema
python -c "import avro.schema; avro.schema.parse(open('schemas/event.avsc').read()); print('✅ Schema valid')"
```