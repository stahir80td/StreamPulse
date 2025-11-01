"""
Pydantic Models for API Request/Response Validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Response Models

class RealtimeStatsResponse(BaseModel):
    """Real-time statistics (last 5 minutes)"""
    total_downloads: int = Field(..., description="Total downloads in window")
    unique_content: int = Field(..., description="Number of unique content items")
    avg_success_rate: float = Field(..., description="Average success rate (0.0-1.0)")
    avg_download_time: Optional[float] = Field(None, description="Average download time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_downloads": 1247,
                "unique_content": 4,
                "avg_success_rate": 0.925,
                "avg_download_time": 125.3
            }
        }


class ContentTrendingItem(BaseModel):
    """Trending content item"""
    content_id: str
    title: str
    total_downloads: int
    successful_downloads: int
    failed_downloads: int
    success_rate: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_id": "mov_avengers_2",
                "title": "Avengers: Endgame 2",
                "total_downloads": 623,
                "successful_downloads": 590,
                "failed_downloads": 33,
                "success_rate": 0.947
            }
        }


class RegionHealthItem(BaseModel):
    """Regional health metrics"""
    region: str
    downloads: int
    success_rate: float
    avg_speed: float
    health_status: str = Field(..., description="healthy, degraded, or critical")
    
    class Config:
        json_schema_extra = {
            "example": {
                "region": "US-California",
                "downloads": 342,
                "success_rate": 0.942,
                "avg_speed": 35.6,
                "health_status": "healthy"
            }
        }


class AlertItem(BaseModel):
    """Alert item"""
    id: int
    alert_type: str
    severity: str = Field(..., description="CRITICAL, WARNING, or INFO")
    message: str
    region: Optional[str]
    metric_name: Optional[str]
    metric_value: Optional[float]
    threshold_value: Optional[float]
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "alert_type": "HIGH_ERROR_RATE",
                "severity": "WARNING",
                "message": "Download error rate above threshold in EU-London",
                "region": "EU-London",
                "metric_name": "error_rate",
                "metric_value": 0.125,
                "threshold_value": 0.10,
                "created_at": "2025-10-31T19:15:32Z"
            }
        }


class TimeSeriesPoint(BaseModel):
    """Time series data point"""
    window_start: datetime
    total_downloads: int
    success_rate: Optional[float]
    
    class Config:
        json_schema_extra = {
            "example": {
                "window_start": "2025-10-31T19:15:00Z",
                "total_downloads": 1247,
                "success_rate": 0.925
            }
        }


class DeviceStatsItem(BaseModel):
    """Device statistics"""
    device: str
    total_downloads: int
    success_rate: float
    avg_speed: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "device": "iPhone 15 Pro",
                "total_downloads": 456,
                "success_rate": 0.947,
                "avg_speed": 38.2
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="healthy or unhealthy")
    database: bool = Field(..., description="Database connection status")
    timestamp: datetime
    version: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": True,
                "timestamp": "2025-10-31T19:15:32Z",
                "version": "1.0.0"
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Database connection failed",
                "detail": "Connection timeout after 30 seconds",
                "timestamp": "2025-10-31T19:15:32Z"
            }
        }


# Response wrapper models

class TrendingResponse(BaseModel):
    """Trending content response"""
    data: List[ContentTrendingItem]
    count: int
    window_minutes: int = Field(default=5, description="Time window in minutes")


class RegionsResponse(BaseModel):
    """Regional health response"""
    data: List[RegionHealthItem]
    count: int
    window_minutes: int = Field(default=5, description="Time window in minutes")


class AlertsResponse(BaseModel):
    """Alerts response"""
    data: List[AlertItem]
    count: int
    unacknowledged_count: int


class TimeSeriesResponse(BaseModel):
    """Time series response"""
    data: List[TimeSeriesPoint]
    count: int
    start_time: datetime
    end_time: datetime


class DeviceStatsResponse(BaseModel):
    """Device statistics response"""
    data: List[DeviceStatsItem]
    count: int
    window_minutes: int = Field(default=5, description="Time window in minutes")