-- StreamPulse Database Schema
-- PostgreSQL 14+ compatible
-- Neon serverless PostgreSQL optimized

-- ============================================================================
-- Table: content_stats
-- Purpose: Stores aggregated download counts per content per minute
-- Updated by: Flink processor (windowed aggregations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS content_stats (
    id SERIAL PRIMARY KEY,
    content_id VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    download_count INTEGER NOT NULL DEFAULT 0,
    successful_downloads INTEGER NOT NULL DEFAULT 0,
    failed_downloads INTEGER NOT NULL DEFAULT 0,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_content_window UNIQUE (content_id, window_start)
);

-- Indexes for fast queries
CREATE INDEX idx_content_stats_time ON content_stats(window_start DESC);
CREATE INDEX idx_content_stats_content_id ON content_stats(content_id);
CREATE INDEX idx_content_stats_created ON content_stats(created_at DESC);

-- Comments
COMMENT ON TABLE content_stats IS 'Aggregated content download statistics per 1-minute window';
COMMENT ON COLUMN content_stats.content_id IS 'Unique content identifier (e.g., mov_avengers_2)';
COMMENT ON COLUMN content_stats.window_start IS 'Start of 1-minute tumbling window';

-- ============================================================================
-- Table: region_health
-- Purpose: Regional performance metrics and health status
-- Updated by: Flink processor (regional aggregations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS region_health (
    id SERIAL PRIMARY KEY,
    region VARCHAR(50) NOT NULL,
    total_downloads INTEGER NOT NULL DEFAULT 0,
    successful_downloads INTEGER NOT NULL DEFAULT 0,
    failed_downloads INTEGER NOT NULL DEFAULT 0,
    success_rate FLOAT NOT NULL DEFAULT 0.0,
    avg_speed_mbps FLOAT NOT NULL DEFAULT 0.0,
    avg_duration_seconds FLOAT NOT NULL DEFAULT 0.0,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_region_window UNIQUE (region, window_start)
);

-- Indexes for fast queries
CREATE INDEX idx_region_health_time ON region_health(window_start DESC);
CREATE INDEX idx_region_health_region ON region_health(region);
CREATE INDEX idx_region_health_success_rate ON region_health(success_rate);

-- Comments
COMMENT ON TABLE region_health IS 'Regional performance and health metrics per 1-minute window';
COMMENT ON COLUMN region_health.success_rate IS 'Percentage of successful downloads (0.0-1.0)';
COMMENT ON COLUMN region_health.avg_speed_mbps IS 'Average download speed in megabits per second';

-- ============================================================================
-- Table: alerts
-- Purpose: System alerts and anomalies detected by Flink
-- Updated by: Flink processor (anomaly detection)
-- ============================================================================

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('CRITICAL', 'WARNING', 'INFO')),
    message TEXT NOT NULL,
    region VARCHAR(50),
    content_id VARCHAR(100),
    metric_name VARCHAR(50),
    metric_value FLOAT,
    threshold_value FLOAT,
    window_start TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100)
);

-- Indexes for fast queries
CREATE INDEX idx_alerts_time ON alerts(created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_acknowledged ON alerts(acknowledged);
CREATE INDEX idx_alerts_region ON alerts(region);

-- Comments
COMMENT ON TABLE alerts IS 'System alerts for anomalies and performance issues';
COMMENT ON COLUMN alerts.alert_type IS 'Alert type: HIGH_ERROR_RATE, SLOW_DOWNLOADS, CDN_FAILURE, etc.';
COMMENT ON COLUMN alerts.severity IS 'Alert severity: CRITICAL, WARNING, INFO';

-- ============================================================================
-- Table: trending_predictions
-- Purpose: ML predictions for trending content
-- Updated by: Flink processor (ML integration - future enhancement)
-- ============================================================================

CREATE TABLE IF NOT EXISTS trending_predictions (
    id SERIAL PRIMARY KEY,
    content_id VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    predicted_rank INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    predicted_downloads INTEGER NOT NULL,
    prediction_window VARCHAR(20) NOT NULL, -- '1_hour', '6_hours', '24_hours'
    window_start TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    actual_rank INTEGER,
    actual_downloads INTEGER,
    accuracy_score FLOAT
);

-- Indexes for fast queries
CREATE INDEX idx_trending_predictions_time ON trending_predictions(window_start DESC);
CREATE INDEX idx_trending_predictions_content ON trending_predictions(content_id);
CREATE INDEX idx_trending_predictions_rank ON trending_predictions(predicted_rank);

-- Comments
COMMENT ON TABLE trending_predictions IS 'ML predictions for trending content (future enhancement)';
COMMENT ON COLUMN trending_predictions.confidence IS 'Prediction confidence score (0.0-1.0)';

-- ============================================================================
-- Table: device_stats
-- Purpose: Device-level analytics (iOS, iPad, Apple TV, etc.)
-- Updated by: Flink processor (device aggregations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS device_stats (
    id SERIAL PRIMARY KEY,
    device VARCHAR(100) NOT NULL,
    os_version VARCHAR(50) NOT NULL,
    total_downloads INTEGER NOT NULL DEFAULT 0,
    successful_downloads INTEGER NOT NULL DEFAULT 0,
    failed_downloads INTEGER NOT NULL DEFAULT 0,
    avg_speed_mbps FLOAT NOT NULL DEFAULT 0.0,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_device_window UNIQUE (device, os_version, window_start)
);

-- Indexes for fast queries
CREATE INDEX idx_device_stats_time ON device_stats(window_start DESC);
CREATE INDEX idx_device_stats_device ON device_stats(device);

-- Comments
COMMENT ON TABLE device_stats IS 'Device-level performance statistics';

-- ============================================================================
-- Table: event_log (Optional - for debugging)
-- Purpose: Sample of raw events for debugging (circular buffer - last 1000)
-- ============================================================================

CREATE TABLE IF NOT EXISTS event_log (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    content_id VARCHAR(100),
    region VARCHAR(50),
    device VARCHAR(100),
    status VARCHAR(20),
    error_code VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for time-based queries
CREATE INDEX idx_event_log_time ON event_log(created_at DESC);

-- Circular buffer: Keep only last 1000 events
-- (This can be automated with a trigger or periodic cleanup)

-- Comments
COMMENT ON TABLE event_log IS 'Sample event log for debugging (last 1000 events)';

-- ============================================================================
-- Data Retention Policies
-- ============================================================================

-- Function to clean old data (7-day retention for stats, 30-day for alerts)
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Clean content_stats older than 7 days
    DELETE FROM content_stats WHERE created_at < NOW() - INTERVAL '7 days';
    
    -- Clean region_health older than 7 days
    DELETE FROM region_health WHERE created_at < NOW() - INTERVAL '7 days';
    
    -- Clean device_stats older than 7 days
    DELETE FROM device_stats WHERE created_at < NOW() - INTERVAL '7 days';
    
    -- Clean alerts older than 30 days
    DELETE FROM alerts WHERE created_at < NOW() - INTERVAL '30 days';
    
    -- Clean trending_predictions older than 7 days
    DELETE FROM trending_predictions WHERE created_at < NOW() - INTERVAL '7 days';
    
    -- Keep only last 1000 events in event_log
    DELETE FROM event_log WHERE id NOT IN (
        SELECT id FROM event_log ORDER BY created_at DESC LIMIT 1000
    );
    
    RAISE NOTICE 'Old data cleanup completed';
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (run manually or via cron/pg_cron if available)
-- SELECT cleanup_old_data();

-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================

-- Insert sample content stats
INSERT INTO content_stats (content_id, title, download_count, successful_downloads, failed_downloads, window_start, window_end)
VALUES 
    ('mov_avengers_2', 'Avengers: Endgame 2', 150, 140, 10, NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '4 minutes'),
    ('mov_taylor_swift', 'Taylor Swift: Eras Tour', 90, 85, 5, NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '4 minutes'),
    ('mov_batman', 'The Batman Returns', 45, 43, 2, NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '4 minutes')
ON CONFLICT (content_id, window_start) DO NOTHING;

-- Insert sample region health
INSERT INTO region_health (region, total_downloads, successful_downloads, failed_downloads, success_rate, avg_speed_mbps, avg_duration_seconds, window_start, window_end)
VALUES 
    ('US-California', 120, 110, 10, 0.917, 35.5, 118.0, NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '4 minutes'),
    ('EU-London', 80, 70, 10, 0.875, 28.3, 145.0, NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '4 minutes'),
    ('ASIA-Tokyo', 65, 60, 5, 0.923, 32.1, 125.0, NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '4 minutes')
ON CONFLICT (region, window_start) DO NOTHING;

-- Insert sample alert
INSERT INTO alerts (alert_type, severity, message, region, metric_name, metric_value, threshold_value, window_start)
VALUES 
    ('HIGH_ERROR_RATE', 'WARNING', 'Download error rate above threshold in EU-London', 'EU-London', 'error_rate', 0.125, 0.10, NOW() - INTERVAL '5 minutes')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Views for common queries
-- ============================================================================

-- View: Latest content stats (last 5 minutes)
CREATE OR REPLACE VIEW v_latest_content_stats AS
SELECT 
    content_id,
    title,
    SUM(download_count) as total_downloads,
    SUM(successful_downloads) as successful_downloads,
    SUM(failed_downloads) as failed_downloads,
    ROUND(AVG(CAST(successful_downloads AS FLOAT) / NULLIF(download_count, 0)), 3) as avg_success_rate
FROM content_stats
WHERE window_start >= NOW() - INTERVAL '5 minutes'
GROUP BY content_id, title
ORDER BY total_downloads DESC;

-- View: Latest region health (last 5 minutes)
CREATE OR REPLACE VIEW v_latest_region_health AS
SELECT 
    region,
    SUM(total_downloads) as total_downloads,
    ROUND(AVG(success_rate), 3) as avg_success_rate,
    ROUND(AVG(avg_speed_mbps), 1) as avg_speed_mbps,
    CASE 
        WHEN AVG(success_rate) >= 0.95 THEN 'healthy'
        WHEN AVG(success_rate) >= 0.90 THEN 'degraded'
        ELSE 'critical'
    END as health_status
FROM region_health
WHERE window_start >= NOW() - INTERVAL '5 minutes'
GROUP BY region
ORDER BY total_downloads DESC;

-- View: Active alerts (unacknowledged)
CREATE OR REPLACE VIEW v_active_alerts AS
SELECT 
    id,
    alert_type,
    severity,
    message,
    region,
    metric_name,
    metric_value,
    threshold_value,
    created_at
FROM alerts
WHERE acknowledged = FALSE
ORDER BY 
    CASE severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'WARNING' THEN 2
        WHEN 'INFO' THEN 3
    END,
    created_at DESC;

-- ============================================================================
-- Permissions (adjust based on your user setup)
-- ============================================================================

-- Grant permissions to application user (replace 'streampulse_user' with your user)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO streampulse_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO streampulse_user;

-- ============================================================================
-- Database Ready!
-- ============================================================================

SELECT 'StreamPulse database initialized successfully!' AS status;