"""
StreamPulse Flink Processor
Real-time stream processing for content analytics
"""

import json
from datetime import datetime, timedelta
from kafka import KafkaConsumer
import avro.schema
import avro.io
import io
from collections import defaultdict
import time
import threading

from config import config
from sinks import (
    content_stats_sink,
    region_health_sink,
    alert_sink,
    device_stats_sink,
    event_log_sink
)


class AvroDeserializer:
    """Deserialize Avro binary events"""
    
    def __init__(self, schema_path):
        with open(schema_path, 'r') as f:
            self.schema = avro.schema.parse(f.read())
        print(f"✅ Loaded Avro schema from {schema_path}")
    
    def deserialize(self, value):
        """Deserialize Avro binary to dict"""
        bytes_reader = io.BytesIO(value)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(self.schema)
        return reader.read(decoder)


class TumblingWindow:
    """
    1-minute tumbling window aggregator
    Processes events and flushes complete windows to database
    """
    
    def __init__(self, window_size_seconds=60):
        self.window_size = window_size_seconds
        self.windows = defaultdict(lambda: {
            'events': [],
            'start_time': None,
            'end_time': None
        })
    
    def add_event(self, event):
        """Add event to appropriate window"""
        event_time = datetime.fromtimestamp(event['timestamp'] / 1000)
        
        # Calculate window start (round down to nearest minute)
        window_start = event_time.replace(second=0, microsecond=0)
        window_end = window_start + timedelta(seconds=self.window_size)
        
        window_key = window_start.strftime('%Y-%m-%d %H:%M:%S')
        
        window = self.windows[window_key]
        window['events'].append(event)
        window['start_time'] = window_start
        window['end_time'] = window_end
        
        return window_key
    
    def get_complete_windows(self, current_time):
        """Get windows that have ended and should be flushed"""
        complete = []
        
        for window_key, window in list(self.windows.items()):
            if window['end_time'] and window['end_time'] < current_time:
                complete.append((window_key, window))
        
        return complete
    
    def remove_window(self, window_key):
        """Remove window after flushing"""
        if window_key in self.windows:
            del self.windows[window_key]


class StreamProcessor:
    """Main stream processor"""
    
    def __init__(self):
        # Validate configuration
        config.validate()
        
        # Initialize deserializer
        self.deserializer = AvroDeserializer(config.SCHEMA_PATH)
        
        # Initialize Kafka consumer
        kafka_props = config.get_kafka_properties()
        
        self.consumer = KafkaConsumer(
            config.KAFKA_TOPIC,
            bootstrap_servers=[config.KAFKA_BOOTSTRAP_SERVERS],
            group_id=kafka_props['group.id'],
            auto_offset_reset=kafka_props['auto.offset.reset'],
            enable_auto_commit=False,  # Manual commit for exactly-once
            value_deserializer=self.deserializer.deserialize,
            security_protocol=kafka_props.get('security.protocol'),
            sasl_mechanism=kafka_props.get('sasl.mechanism'),
            sasl_plain_username=kafka_props.get('sasl.username'),
            sasl_plain_password=kafka_props.get('sasl.password'),
        )
        
        print("✅ Connected to Kafka consumer")
        
        # Initialize windows
        self.content_window = TumblingWindow(60)
        self.region_window = TumblingWindow(60)
        self.device_window = TumblingWindow(60)
        
        # Metrics
        self.events_processed = 0
        self.windows_flushed = 0
        
        # Start window flusher thread
        self.running = True
        self.flusher_thread = threading.Thread(target=self.window_flusher, daemon=True)
        self.flusher_thread.start()
    
    def process_event(self, event):
        """Process a single event"""
        try:
            # Add to windows
            self.content_window.add_event(event)
            self.region_window.add_event(event)
            self.device_window.add_event(event)
            
            # Sample 1% of events to event_log for debugging
            if self.events_processed % 100 == 0:
                event_log_sink.write_sample(
                    event_id=event['event_id'],
                    event_timestamp=datetime.fromtimestamp(event['timestamp'] / 1000),
                    content_id=event['content']['content_id'],
                    region=event['user_context']['region'],
                    device=event['user_context']['device'],
                    status=event['download']['status'],
                    error_code=event['download'].get('error_code')
                )
            
            self.events_processed += 1
            
            # Log progress
            if self.events_processed % 50 == 0:
                print(f"📊 Processed {self.events_processed} events | "
                      f"Flushed {self.windows_flushed} windows")
        
        except Exception as e:
            print(f"❌ Error processing event: {e}")
    
    def flush_content_window(self, window_key, window):
        """Flush content statistics window"""
        events = window['events']
        
        # Group by content_id
        content_stats = defaultdict(lambda: {
            'title': '',
            'total': 0,
            'successful': 0,
            'failed': 0
        })
        
        for event in events:
            content_id = event['content']['content_id']
            stats = content_stats[content_id]
            
            stats['title'] = event['content']['title']
            stats['total'] += 1
            
            if event['download']['status'] == 'success':
                stats['successful'] += 1
            else:
                stats['failed'] += 1
        
        # Write to database
        for content_id, stats in content_stats.items():
            content_stats_sink.write(
                content_id=content_id,
                title=stats['title'],
                download_count=stats['total'],
                successful=stats['successful'],
                failed=stats['failed'],
                window_start=window['start_time'],
                window_end=window['end_time']
            )
    
    def flush_region_window(self, window_key, window):
        """Flush region health window"""
        events = window['events']
        
        # Group by region
        region_stats = defaultdict(lambda: {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'speeds': [],
            'durations': []
        })
        
        for event in events:
            region = event['user_context']['region']
            stats = region_stats[region]
            
            stats['total'] += 1
            
            if event['download']['status'] == 'success':
                stats['successful'] += 1
            else:
                stats['failed'] += 1
            
            stats['speeds'].append(event['download']['speed_mbps'])
            stats['durations'].append(event['download']['duration_seconds'])
        
        # Write to database and check for alerts
        for region, stats in region_stats.items():
            success_rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            avg_speed = sum(stats['speeds']) / len(stats['speeds']) if stats['speeds'] else 0
            avg_duration = sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0
            
            region_health_sink.write(
                region=region,
                total=stats['total'],
                successful=stats['successful'],
                failed=stats['failed'],
                success_rate=success_rate,
                avg_speed=avg_speed,
                avg_duration=avg_duration,
                window_start=window['start_time'],
                window_end=window['end_time']
            )
            
            # Check for alerts
            if success_rate < 0.90:  # Less than 90% success rate
                severity = 'CRITICAL' if success_rate < 0.80 else 'WARNING'
                alert_sink.write(
                    alert_type='HIGH_ERROR_RATE',
                    severity=severity,
                    message=f"Download success rate in {region} is {success_rate*100:.1f}% (threshold: 90%)",
                    region=region,
                    metric_name='success_rate',
                    metric_value=success_rate,
                    threshold_value=0.90,
                    window_start=window['start_time']
                )
            
            if avg_speed < 10.0:  # Less than 10 Mbps average
                alert_sink.write(
                    alert_type='SLOW_DOWNLOADS',
                    severity='WARNING',
                    message=f"Average download speed in {region} is {avg_speed:.1f} Mbps (threshold: 10 Mbps)",
                    region=region,
                    metric_name='avg_speed_mbps',
                    metric_value=avg_speed,
                    threshold_value=10.0,
                    window_start=window['start_time']
                )
    
    def flush_device_window(self, window_key, window):
        """Flush device statistics window"""
        events = window['events']
        
        # Group by device and os_version
        device_stats = defaultdict(lambda: {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'speeds': []
        })
        
        for event in events:
            device = event['user_context']['device']
            os_version = event['user_context'].get('os_version', 'Unknown')
            key = (device, os_version)
            stats = device_stats[key]
            
            stats['total'] += 1
            
            if event['download']['status'] == 'success':
                stats['successful'] += 1
            else:
                stats['failed'] += 1
            
            stats['speeds'].append(event['download']['speed_mbps'])
        
        # Write to database
        for (device, os_version), stats in device_stats.items():
            avg_speed = sum(stats['speeds']) / len(stats['speeds']) if stats['speeds'] else 0
            
            device_stats_sink.write(
                device=device,
                os_version=os_version,
                total=stats['total'],
                successful=stats['successful'],
                failed=stats['failed'],
                avg_speed=avg_speed,
                window_start=window['start_time'],
                window_end=window['end_time']
            )
    
    def window_flusher(self):
        """Background thread to flush complete windows"""
        print("🔄 Window flusher thread started")
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Flush content windows
                for window_key, window in self.content_window.get_complete_windows(current_time):
                    self.flush_content_window(window_key, window)
                    self.content_window.remove_window(window_key)
                    self.windows_flushed += 1
                
                # Flush region windows
                for window_key, window in self.region_window.get_complete_windows(current_time):
                    self.flush_region_window(window_key, window)
                    self.region_window.remove_window(window_key)
                
                # Flush device windows
                for window_key, window in self.device_window.get_complete_windows(current_time):
                    self.flush_device_window(window_key, window)
                    self.device_window.remove_window(window_key)
                
                # Sleep for 5 seconds
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Error in window flusher: {e}")
    
    def run(self):
        """Main processing loop"""
        print("\n" + "="*60)
        print("🚀 StreamPulse Flink Processor")
        print("="*60)
        print(f"📍 Topic: {config.KAFKA_TOPIC}")
        print(f"📊 Window Size: 60 seconds (tumbling)")
        print(f"🔐 Database: {config.PG_HOST}/{config.PG_DATABASE}")
        print("="*60 + "\n")
        
        try:
            for message in self.consumer:
                event = message.value
                self.process_event(event)
                
                # Commit offset every 100 messages
                if self.events_processed % 100 == 0:
                    self.consumer.commit()
        
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Stopped. Total events processed: {self.events_processed}")
            print(f"   Windows flushed: {self.windows_flushed}")
            self.running = False
            self.consumer.close()
        
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            self.running = False
            self.consumer.close()
            raise


if __name__ == "__main__":
    processor = StreamProcessor()
    processor.run()