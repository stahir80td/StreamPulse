-- Migration: 001_add_indexes.sql
-- Purpose: Add additional indexes for performance optimization
-- Date: 2025-10-31
-- Description: Composite indexes and partial indexes for common query patterns

-- ============================================================================
-- Composite Indexes for Content Stats
-- ============================================================================

-- Index for queries filtering by content and time range
CREATE INDEX IF NOT EXISTS idx_content_stats_content_time 
ON content_stats(content_id, window_start DESC);

-- Index for queries filtering by time and ordering by download count
CREATE INDEX IF NOT EXISTS idx_content_stats_time_count 
ON content_stats(window_start DESC, download_count DESC);

-- Partial index for recent data (last 24 hours) - frequently queried
CREATE INDEX IF NOT EXISTS idx_content_stats_recent 
ON content_stats(window_start DESC, content_id)
WHERE window_start >= NOW() - INTERVAL '24 hours';

-- ============================================================================
-- Composite Indexes for Region Health
-- ============================================================================

-- Index for queries filtering by region and time range
CREATE INDEX IF NOT EXISTS idx_region_health_region_time 
ON region_health(region, window_start DESC);

-- Partial index for unhealthy regions (success_rate < 0.90)
CREATE INDEX IF NOT EXISTS idx_region_health_unhealthy 
ON region_health(region, window_start DESC, success_rate)
WHERE success_rate < 0.90;

-- ============================================================================
-- Composite Indexes for Alerts
-- ============================================================================

-- Index for active alerts by severity
CREATE INDEX IF NOT EXISTS idx_alerts_active_severity 
ON alerts(acknowledged, severity, created_at DESC)
WHERE acknowledged = FALSE;

-- Index for alerts by region and time
CREATE INDEX IF NOT EXISTS idx_alerts_region_time 
ON alerts(region, created_at DESC)
WHERE region IS NOT NULL;

-- ============================================================================
-- Indexes for Trending Predictions
-- ============================================================================

-- Index for latest predictions by content
CREATE INDEX IF NOT EXISTS idx_trending_predictions_content_time 
ON trending_predictions(content_id, window_start DESC);

-- Index for predictions by rank
CREATE INDEX IF NOT EXISTS idx_trending_predictions_recent_rank 
ON trending_predictions(window_start DESC, predicted_rank)
WHERE window_start >= NOW() - INTERVAL '1 hour';

-- ============================================================================
-- Indexes for Device Stats
-- ============================================================================

-- Index for device performance queries
CREATE INDEX IF NOT EXISTS idx_device_stats_device_time 
ON device_stats(device, window_start DESC);

-- ============================================================================
-- Statistics Update
-- ============================================================================

-- Analyze tables to update query planner statistics
ANALYZE content_stats;
ANALYZE region_health;
ANALYZE alerts;
ANALYZE trending_predictions;
ANALYZE device_stats;

-- ============================================================================
-- Verify Indexes
-- ============================================================================

-- Query to list all indexes on content_stats table
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'content_stats'
ORDER BY indexname;

-- Migration completed
SELECT 'Migration 001_add_indexes completed successfully!' AS status;