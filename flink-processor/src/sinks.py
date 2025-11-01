"""
PostgreSQL Sink Functions
Write aggregated results from Flink to PostgreSQL
"""

import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from config import config


class PostgresSink:
    """Base PostgreSQL sink with connection management"""
    
    def __init__(self):
        self.connection_string = config.get_pg_connection_string()
    
    def get_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(self.connection_string)
    
    def write_batch(self, records, table_name, columns):
        """
        Write batch of records to PostgreSQL
        
        Args:
            records: List of tuples with data
            table_name: Target table name
            columns: List of column names
        """
        if not records:
            return
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Build INSERT query with ON CONFLICT DO UPDATE
            placeholders = ','.join(['%s'] * len(columns))
            columns_str = ','.join(columns)
            
            # Create conflict resolution (update all columns except id)
            update_columns = [col for col in columns if col not in ('id', 'created_at')]
            updates = ','.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
            updates += ", updated_at = NOW()"
            
            query = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES %s
                ON CONFLICT ON CONSTRAINT unique_{table_name.replace('_stats', '').replace('_health', '')}_window
                DO UPDATE SET {updates}
            """
            
            execute_values(cursor, query, records)
            conn.commit()
            cursor.close()
            
            print(f"✅ Wrote {len(records)} records to {table_name}")
            
        except Exception as e:
            print(f"❌ Error writing to {table_name}: {e}")
            conn.rollback()
        finally:
            conn.close()


class ContentStatsSink(PostgresSink):
    """Sink for content_stats table"""
    
    def write(self, content_id, title, download_count, successful, failed, window_start, window_end):
        """Write content statistics"""
        record = (
            content_id,
            title,
            download_count,
            successful,
            failed,
            window_start,
            window_end
        )
        
        columns = [
            'content_id', 'title', 'download_count',
            'successful_downloads', 'failed_downloads',
            'window_start', 'window_end'
        ]
        
        self.write_batch([record], 'content_stats', columns)


class RegionHealthSink(PostgresSink):
    """Sink for region_health table"""
    
    def write(self, region, total, successful, failed, success_rate, 
              avg_speed, avg_duration, window_start, window_end):
        """Write region health metrics"""
        record = (
            region,
            total,
            successful,
            failed,
            success_rate,
            avg_speed,
            avg_duration,
            window_start,
            window_end
        )
        
        columns = [
            'region', 'total_downloads', 'successful_downloads',
            'failed_downloads', 'success_rate', 'avg_speed_mbps',
            'avg_duration_seconds', 'window_start', 'window_end'
        ]
        
        self.write_batch([record], 'region_health', columns)


class AlertSink(PostgresSink):
    """Sink for alerts table"""
    
    def write(self, alert_type, severity, message, region=None, 
              content_id=None, metric_name=None, metric_value=None, 
              threshold_value=None, window_start=None):
        """Write alert"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                INSERT INTO alerts (
                    alert_type, severity, message, region, content_id,
                    metric_name, metric_value, threshold_value, window_start
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                alert_type, severity, message, region, content_id,
                metric_name, metric_value, threshold_value, window_start
            ))
            
            conn.commit()
            cursor.close()
            
            print(f"🚨 Alert: {severity} - {message}")
            
        except Exception as e:
            print(f"❌ Error writing alert: {e}")
            conn.rollback()
        finally:
            conn.close()


class DeviceStatsSink(PostgresSink):
    """Sink for device_stats table"""
    
    def write(self, device, os_version, total, successful, failed, 
              avg_speed, window_start, window_end):
        """Write device statistics"""
        record = (
            device,
            os_version,
            total,
            successful,
            failed,
            avg_speed,
            window_start,
            window_end
        )
        
        columns = [
            'device', 'os_version', 'total_downloads',
            'successful_downloads', 'failed_downloads',
            'avg_speed_mbps', 'window_start', 'window_end'
        ]
        
        self.write_batch([record], 'device_stats', columns)


class EventLogSink(PostgresSink):
    """Sink for event_log table (sampling for debugging)"""
    
    def write_sample(self, event_id, event_timestamp, content_id, 
                     region, device, status, error_code=None):
        """Write sampled event to log"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                INSERT INTO event_log (
                    event_id, event_timestamp, content_id, region,
                    device, status, error_code
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                event_id, event_timestamp, content_id, region,
                device, status, error_code
            ))
            
            conn.commit()
            cursor.close()
            
        except Exception as e:
            print(f"❌ Error writing event log: {e}")
            conn.rollback()
        finally:
            conn.close()


# Singleton instances
content_stats_sink = ContentStatsSink()
region_health_sink = RegionHealthSink()
alert_sink = AlertSink()
device_stats_sink = DeviceStatsSink()
event_log_sink = EventLogSink()