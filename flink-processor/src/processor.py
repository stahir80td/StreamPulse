"""
StreamPulse Stream Processor (Simplified)
Replaces PyFlink with lightweight Python processing
Does the same windowing, aggregation, and anomaly detection
"""

import os
import sys
import time
import json
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any
from kafka import KafkaConsumer
import psycopg2
from psycopg2.extras import execute_batch
import avro.io
import avro.schema
from io import BytesIO

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config


class Window:
    """Represents a 1-minute tumbling window"""
    
    def __init__(self, window_start: datetime):
        self.window_start = window_start
        self.window_end = window_start + timedelta(minutes=1)
        self.events: List[Dict] = []
        self.is_closed = False
    
    def add_event(self, event: Dict):
        """Add event to window"""
        self.events.append(event)
    
    def should_close(self, current_time: datetime) -> bool:
        """Check if window should be closed"""
        return current_time >= self.window_end and not self.is_closed
    
    def close(self):
        """Mark window as closed"""
        self.is_closed = True


class StreamProcessor:
    """Simplified stream processor with windowing"""
    
    def __init__(self):
        self.config = Config()
        self.consumer = None
        self.db_conn = None
        self.avro_schema = None
        
        # Windowing state
        self.windows: Dict[datetime, Window] = {}
        self.window_lock = threading.Lock()
        
        # Statistics
        self.total_events = 0
        self.total_windows_flushed = 0
        
    def setup(self):
        """Initialize connections and schema"""
        print("🔧 Setting up Stream Processor...")
        
        # Load Avro schema
        with open(self.config.SCHEMA_PATH, 'r') as f:
            self.avro_schema = avro.schema.parse(f.read())
        print(f"✅ Loaded Avro schema from {self.config.SCHEMA_PATH}")
        
        # Connect to Kafka
        self.consumer = KafkaConsumer(
            self.config.KAFKA_TOPIC,
            bootstrap_servers=self.config.KAFKA_BOOTSTRAP_SERVERS,
            group_id=self.config.KAFKA_GROUP_ID,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=self.deserialize_avro,
            security_protocol=self.config.KAFKA_SECURITY_PROTOCOL,
            sasl_mechanism=self.config.KAFKA_SASL_MECHANISM if self.config.KAFKA_USERNAME else None,
            sasl_plain_username=self.config.KAFKA_USERNAME if self.config.KAFKA_USERNAME else None,
            sasl_plain_password=self.config.KAFKA_PASSWORD if self.config.KAFKA_PASSWORD else None,
        )
        print(f"✅ Connected to Kafka: {self.config.KAFKA_BOOTSTRAP_SERVERS}")
        
        # Connect to PostgreSQL
        self.db_conn = psycopg2.connect(
            host=self.config.PG_HOST,
            port=self.config.PG_PORT,
            database=self.config.PG_DATABASE,
            user=self.config.PG_USER,
            password=self.config.PG_PASSWORD,
            sslmode=self.config.PG_SSLMODE
        )
        self.db_conn.autocommit = False
        print(f"✅ Connected to PostgreSQL: {self.config.PG_HOST}:{self.config.PG_PORT}/{self.config.PG_DATABASE}")
        
    def deserialize_avro(self, data: bytes) -> Dict:
        """Deserialize Avro binary to dict"""
        if data is None:
            return None
        
        bytes_reader = BytesIO(data)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(self.avro_schema)
        return reader.read(decoder)
    
    def get_window_start(self, timestamp: datetime) -> datetime:
        """Get window start time for a given timestamp (1-minute tumbling)"""
        return timestamp.replace(second=0, microsecond=0)
    
    def process_event(self, event: Dict):
        """Process single event and add to appropriate window"""
        # Parse timestamp - handle both Unix timestamp and ISO string
        timestamp = event['timestamp']
        
        if isinstance(timestamp, int):
            # Unix timestamp in milliseconds
            event_time = datetime.utcfromtimestamp(timestamp / 1000)
        elif isinstance(timestamp, str):
            # ISO string format
            event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            # Fallback to current time
            event_time = datetime.utcnow()
        
        window_start = self.get_window_start(event_time)
        
        # Add to window
        with self.window_lock:
            if window_start not in self.windows:
                self.windows[window_start] = Window(window_start)
            
            self.windows[window_start].add_event(event)
        
        self.total_events += 1
    
    def close_windows(self):
        """Close windows that are past their end time"""
        current_time = datetime.utcnow()
        windows_to_close = []
        
        with self.window_lock:
            for window_start, window in self.windows.items():
                if window.should_close(current_time):
                    windows_to_close.append(window_start)
        
        # Process closed windows
        for window_start in windows_to_close:
            with self.window_lock:
                window = self.windows.pop(window_start)
            
            if window.events:
                self.aggregate_window(window)
                self.total_windows_flushed += 1
    
    def aggregate_window(self, window: Window):
        """Aggregate events in a window and write to database"""
        events = window.events
        
        # Content stats aggregation
        content_stats = defaultdict(lambda: {
            'download_count': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_size_gb': 0,
            'title': None
        })
        
        for event in events:
            content_id = event['content']['content_id']
            stats = content_stats[content_id]
            
            stats['download_count'] += 1
            stats['title'] = event['content']['title']
            stats['total_size_gb'] += event['content']['size_gb']
            
            if event['download']['status'] == 'success':
                stats['successful_downloads'] += 1
            else:
                stats['failed_downloads'] += 1
        
        # Region health aggregation
        region_health = defaultdict(lambda: {
            'total_downloads': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_speed': 0,
            'speed_count': 0
        })
        
        for event in events:
            region = event['user']['region']
            health = region_health[region]
            
            health['total_downloads'] += 1
            
            if event['download']['status'] == 'success':
                health['successful_downloads'] += 1
                if event['download']['speed_mbps']:
                    health['total_speed'] += event['download']['speed_mbps']
                    health['speed_count'] += 1
            else:
                health['failed_downloads'] += 1
        
        # Device stats aggregation
        device_stats = defaultdict(lambda: {
            'download_count': 0,
            'successful_downloads': 0,
            'avg_speed': 0,
            'total_speed': 0,
            'speed_count': 0
        })
        
        for event in events:
            device = event['user']['device_type']
            stats = device_stats[device]
            
            stats['download_count'] += 1
            
            if event['download']['status'] == 'success':
                stats['successful_downloads'] += 1
                if event['download']['speed_mbps']:
                    stats['total_speed'] += event['download']['speed_mbps']
                    stats['speed_count'] += 1
        
        # Write to database
        try:
            cursor = self.db_conn.cursor()
            
            # Insert content stats
            content_rows = []
            for content_id, stats in content_stats.items():
                content_rows.append((
                    content_id,
                    stats['title'],
                    stats['download_count'],
                    stats['successful_downloads'],
                    stats['failed_downloads'],
                    round(stats['total_size_gb'], 2),
                    window.window_start,
                    window.window_end
                ))
            
            if content_rows:
                execute_batch(cursor, """
                    INSERT INTO content_stats 
                    (content_id, title, download_count, successful_downloads, 
                     failed_downloads, total_size_gb, window_start, window_end)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (content_id, window_start) DO NOTHING
                """, content_rows)
                print(f"✅ Wrote {len(content_rows)} records to content_stats")
            
            # Insert region health
            region_rows = []
            alerts = []
            
            for region, health in region_health.items():
                success_rate = health['successful_downloads'] / health['total_downloads'] if health['total_downloads'] > 0 else 0
                avg_speed = health['total_speed'] / health['speed_count'] if health['speed_count'] > 0 else 0
                
                region_rows.append((
                    region,
                    health['total_downloads'],
                    health['successful_downloads'],
                    health['failed_downloads'],
                    round(success_rate, 4),
                    round(avg_speed, 2),
                    window.window_start,
                    window.window_end
                ))
                
                # Check for anomalies (success rate < 90%)
                if success_rate < 0.90:
                    alerts.append((
                        'HIGH_ERROR_RATE',
                        'WARNING' if success_rate >= 0.85 else 'CRITICAL',
                        f"High error rate detected in {region}: {(1-success_rate)*100:.1f}% failures",
                        region,
                        'error_rate',
                        1 - success_rate,
                        0.10
                    ))
            
            if region_rows:
                execute_batch(cursor, """
                    INSERT INTO region_health 
                    (region, total_downloads, successful_downloads, failed_downloads,
                     success_rate, avg_speed_mbps, window_start, window_end)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (region, window_start) DO NOTHING
                """, region_rows)
                print(f"✅ Wrote {len(region_rows)} records to region_health")
            
            # Insert alerts
            if alerts:
                execute_batch(cursor, """
                    INSERT INTO alerts 
                    (alert_type, severity, message, region, metric_name, metric_value, threshold_value)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, alerts)
                print(f"⚠️  Created {len(alerts)} alerts")
            
            # Insert device stats
            device_rows = []
            for device, stats in device_stats.items():
                avg_speed = stats['total_speed'] / stats['speed_count'] if stats['speed_count'] > 0 else 0
                
                device_rows.append((
                    device,
                    stats['download_count'],
                    stats['successful_downloads'],
                    round(avg_speed, 2),
                    window.window_start,
                    window.window_end
                ))
            
            if device_rows:
                execute_batch(cursor, """
                    INSERT INTO device_stats 
                    (device_type, download_count, successful_downloads, avg_speed_mbps,
                     window_start, window_end)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (device_type, window_start) DO NOTHING
                """, device_rows)
                print(f"✅ Wrote {len(device_rows)} records to device_stats")
            
            # Commit transaction
            self.db_conn.commit()
            cursor.close()
            
        except Exception as e:
            print(f"❌ Error writing to database: {e}")
            self.db_conn.rollback()
    
    def window_flusher(self):
        """Background thread to close windows periodically"""
        print("🔄 Window flusher thread started")
        while True:
            time.sleep(5)  # Check every 5 seconds
            self.close_windows()
    
    def run(self):
        """Main processing loop"""
        print("="*60)
        print("🚀 StreamPulse Stream Processor")
        print("="*60)
        print(f"📥 Consuming from topic: {self.config.KAFKA_TOPIC}")
        print(f"🪟 Window size: 1 minute (tumbling)")
        print(f"💾 Writing to: {self.config.PG_HOST}/{self.config.PG_DATABASE}")
        print("="*60)
        
        # Start window flusher thread
        flusher_thread = threading.Thread(target=self.window_flusher, daemon=True)
        flusher_thread.start()
        
        # Main consumption loop
        try:
            for message in self.consumer:
                event = message.value
                
                if event:
                    self.process_event(event)
                    
                    # Print progress every 50 events
                    if self.total_events % 50 == 0:
                        print(f"📊 Processed {self.total_events} events | Flushed {self.total_windows_flushed} windows")
        
        except KeyboardInterrupt:
            print("\n⚠️  Shutting down gracefully...")
        
        finally:
            # Close final windows
            self.close_windows()
            
            # Cleanup
            if self.consumer:
                self.consumer.close()
            if self.db_conn:
                self.db_conn.close()
            
            print(f"✅ Total events processed: {self.total_events}")
            print(f"✅ Total windows flushed: {self.total_windows_flushed}")
            print("👋 Processor stopped")


def main():
    """Entry point"""
    processor = StreamProcessor()
    processor.setup()
    processor.run()


if __name__ == "__main__":
    main()