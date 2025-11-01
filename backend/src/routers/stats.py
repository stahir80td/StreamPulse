"""
Statistics API Router
Endpoints for real-time content analytics
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import List
from cachetools import TTLCache
import time

from ..database import execute_query
from ..models import (
    RealtimeStatsResponse,
    TrendingResponse,
    ContentTrendingItem,
    RegionsResponse,
    RegionHealthItem,
    AlertsResponse,
    AlertItem,
    TimeSeriesResponse,
    TimeSeriesPoint,
    DeviceStatsResponse,
    DeviceStatsItem
)
from ..config import config

router = APIRouter(prefix="/stats", tags=["Statistics"])

# Simple in-memory cache (TTL: 2 seconds)
cache = TTLCache(maxsize=100, ttl=config.CACHE_TTL)


@router.get("/realtime", response_model=RealtimeStatsResponse)
async def get_realtime_stats(
    minutes: int = Query(default=5, ge=1, le=60, description="Time window in minutes")
):
    """
    Get real-time statistics for the last N minutes
    
    Returns:
        - Total downloads
        - Unique content count
        - Average success rate
        - Average download time
    """
    cache_key = f"realtime_{minutes}"
    
    # Check cache
    if cache_key in cache:
        return cache[cache_key]
    
    try:
        time_threshold = datetime.now() - timedelta(minutes=minutes)
        
        query = """
            SELECT 
                COALESCE(SUM(download_count), 0) as total_downloads,
                COUNT(DISTINCT content_id) as unique_content,
                COALESCE(AVG(CAST(successful_downloads AS FLOAT) / NULLIF(download_count, 0)), 0) as avg_success_rate
            FROM content_stats
            WHERE window_start >= %s
        """
        
        result = execute_query(query, (time_threshold,), fetch_one=True)
        
        if not result:
            raise HTTPException(status_code=404, detail="No data found")
        
        response = RealtimeStatsResponse(
            total_downloads=int(result['total_downloads']),
            unique_content=int(result['unique_content']),
            avg_success_rate=round(float(result['avg_success_rate']), 3),
            avg_download_time=None  # TODO: Add from region_health table
        )
        
        # Cache result
        cache[cache_key] = response
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/trending", response_model=TrendingResponse)
async def get_trending_content(
    minutes: int = Query(default=5, ge=1, le=60, description="Time window in minutes"),
    limit: int = Query(default=5, ge=1, le=20, description="Number of results")
):
    """
    Get top trending content by downloads
    
    Returns list of top N content items sorted by download count
    """
    cache_key = f"trending_{minutes}_{limit}"
    
    # Check cache
    if cache_key in cache:
        return cache[cache_key]
    
    try:
        time_threshold = datetime.now() - timedelta(minutes=minutes)
        
        query = """
            SELECT 
                content_id,
                title,
                SUM(download_count) as total_downloads,
                SUM(successful_downloads) as successful_downloads,
                SUM(failed_downloads) as failed_downloads,
                AVG(CAST(successful_downloads AS FLOAT) / NULLIF(download_count, 0)) as success_rate
            FROM content_stats
            WHERE window_start >= %s
            GROUP BY content_id, title
            ORDER BY total_downloads DESC
            LIMIT %s
        """
        
        results = execute_query(query, (time_threshold, limit))
        
        items = [
            ContentTrendingItem(
                content_id=row['content_id'],
                title=row['title'],
                total_downloads=int(row['total_downloads']),
                successful_downloads=int(row['successful_downloads']),
                failed_downloads=int(row['failed_downloads']),
                success_rate=round(float(row['success_rate']), 3)
            )
            for row in results
        ]
        
        response = TrendingResponse(
            data=items,
            count=len(items),
            window_minutes=minutes
        )
        
        # Cache result
        cache[cache_key] = response
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/regions", response_model=RegionsResponse)
async def get_regional_health(
    minutes: int = Query(default=5, ge=1, le=60, description="Time window in minutes")
):
    """
    Get regional performance metrics
    
    Returns health metrics for each region including:
    - Total downloads
    - Success rate
    - Average speed
    - Health status
    """
    cache_key = f"regions_{minutes}"
    
    # Check cache
    if cache_key in cache:
        return cache[cache_key]
    
    try:
        time_threshold = datetime.now() - timedelta(minutes=minutes)
        
        query = """
            SELECT 
                region,
                SUM(total_downloads) as downloads,
                AVG(success_rate) as success_rate,
                AVG(avg_speed_mbps) as avg_speed,
                CASE 
                    WHEN AVG(success_rate) >= 0.95 THEN 'healthy'
                    WHEN AVG(success_rate) >= 0.90 THEN 'degraded'
                    ELSE 'critical'
                END as health_status
            FROM region_health
            WHERE window_start >= %s
            GROUP BY region
            ORDER BY downloads DESC
        """
        
        results = execute_query(query, (time_threshold,))
        
        items = [
            RegionHealthItem(
                region=row['region'],
                downloads=int(row['downloads']),
                success_rate=round(float(row['success_rate']), 3),
                avg_speed=round(float(row['avg_speed']), 1),
                health_status=row['health_status']
            )
            for row in results
        ]
        
        response = RegionsResponse(
            data=items,
            count=len(items),
            window_minutes=minutes
        )
        
        # Cache result
        cache[cache_key] = response
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(
    limit: int = Query(default=10, ge=1, le=50, description="Number of alerts"),
    severity: str = Query(default=None, description="Filter by severity (CRITICAL, WARNING, INFO)"),
    acknowledged: bool = Query(default=False, description="Include acknowledged alerts")
):
    """
    Get recent alerts
    
    Returns list of alerts with optional filtering by severity and acknowledgment status
    """
    try:
        query = """
            SELECT 
                id, alert_type, severity, message, region,
                metric_name, metric_value, threshold_value, created_at
            FROM alerts
            WHERE acknowledged = %s
        """
        
        params = [acknowledged]
        
        if severity:
            query += " AND severity = %s"
            params.append(severity.upper())
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        results = execute_query(query, tuple(params))
        
        items = [
            AlertItem(
                id=row['id'],
                alert_type=row['alert_type'],
                severity=row['severity'],
                message=row['message'],
                region=row['region'],
                metric_name=row['metric_name'],
                metric_value=float(row['metric_value']) if row['metric_value'] else None,
                threshold_value=float(row['threshold_value']) if row['threshold_value'] else None,
                created_at=row['created_at']
            )
            for row in results
        ]
        
        # Count unacknowledged alerts
        count_query = "SELECT COUNT(*) as count FROM alerts WHERE acknowledged = FALSE"
        count_result = execute_query(count_query, fetch_one=True)
        unack_count = int(count_result['count']) if count_result else 0
        
        response = AlertsResponse(
            data=items,
            count=len(items),
            unacknowledged_count=unack_count
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/timeseries", response_model=TimeSeriesResponse)
async def get_timeseries(
    minutes: int = Query(default=60, ge=5, le=1440, description="Time window in minutes")
):
    """
    Get time series data for downloads over time
    
    Returns downloads aggregated by 1-minute windows for the specified time range
    """
    cache_key = f"timeseries_{minutes}"
    
    # Check cache
    if cache_key in cache:
        return cache[cache_key]
    
    try:
        time_threshold = datetime.now() - timedelta(minutes=minutes)
        
        query = """
            SELECT 
                window_start,
                SUM(download_count) as total_downloads,
                AVG(CAST(successful_downloads AS FLOAT) / NULLIF(download_count, 0)) as success_rate
            FROM content_stats
            WHERE window_start >= %s
            GROUP BY window_start
            ORDER BY window_start ASC
        """
        
        results = execute_query(query, (time_threshold,))
        
        items = [
            TimeSeriesPoint(
                window_start=row['window_start'],
                total_downloads=int(row['total_downloads']),
                success_rate=round(float(row['success_rate']), 3) if row['success_rate'] else None
            )
            for row in results
        ]
        
        response = TimeSeriesResponse(
            data=items,
            count=len(items),
            start_time=time_threshold,
            end_time=datetime.now()
        )
        
        # Cache result
        cache[cache_key] = response
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/devices", response_model=DeviceStatsResponse)
async def get_device_stats(
    minutes: int = Query(default=5, ge=1, le=60, description="Time window in minutes"),
    limit: int = Query(default=10, ge=1, le=20, description="Number of results")
):
    """
    Get device performance statistics
    
    Returns performance metrics grouped by device type
    """
    cache_key = f"devices_{minutes}_{limit}"
    
    # Check cache
    if cache_key in cache:
        return cache[cache_key]
    
    try:
        time_threshold = datetime.now() - timedelta(minutes=minutes)
        
        query = """
            SELECT 
                device,
                SUM(total_downloads) as total_downloads,
                AVG(CAST(successful_downloads AS FLOAT) / NULLIF(total_downloads, 0)) as success_rate,
                AVG(avg_speed_mbps) as avg_speed
            FROM device_stats
            WHERE window_start >= %s
            GROUP BY device
            ORDER BY total_downloads DESC
            LIMIT %s
        """
        
        results = execute_query(query, (time_threshold, limit))
        
        items = [
            DeviceStatsItem(
                device=row['device'],
                total_downloads=int(row['total_downloads']),
                success_rate=round(float(row['success_rate']), 3) if row['success_rate'] else 0.0,
                avg_speed=round(float(row['avg_speed']), 1) if row['avg_speed'] else 0.0
            )
            for row in results
        ]
        
        response = DeviceStatsResponse(
            data=items,
            count=len(items),
            window_minutes=minutes
        )
        
        # Cache result
        cache[cache_key] = response
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")