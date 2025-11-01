"""
StreamPulse Backend API
FastAPI application for serving real-time content analytics
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import time

from .config import config
from .database import db_pool, check_database_health
from .models import HealthResponse, ErrorResponse
from .routers import stats

# Validate configuration on startup
config.validate()

# Initialize FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="""
    **StreamPulse Real-Time Content Analytics API**
    
    Real-time analytics for digital content distribution. 
    Powers insights for content performance, regional health, and infrastructure monitoring.
    
    ## Features
    
    * **Real-time Statistics**: Aggregate metrics updated every 2 seconds
    * **Trending Content**: Top-K content by downloads with windowed queries
    * **Regional Health**: Performance monitoring across geographic regions
    * **Alerts**: Anomaly detection and alerting for infrastructure issues
    * **Time Series**: Historical trends for downloads and performance
    * **Device Analytics**: Performance breakdown by device type
    
    ## Architecture
    
    ```
    Event Generator → Kafka → Flink Processor → PostgreSQL → FastAPI (You are here!) → React Dashboard
    ```
    
    Built with ❤️ for Apple Services Engineering portfolio demonstration
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header to all requests"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            timestamp=datetime.now()
        ).dict()
    )

# Include routers
app.include_router(stats.router, prefix=config.API_PREFIX)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    API Root - Welcome message and quick links
    """
    return {
        "message": "Welcome to StreamPulse API",
        "version": config.API_VERSION,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "health": "/health",
            "realtime_stats": f"{config.API_PREFIX}/stats/realtime",
            "trending": f"{config.API_PREFIX}/stats/trending",
            "regions": f"{config.API_PREFIX}/stats/regions",
            "alerts": f"{config.API_PREFIX}/stats/alerts",
            "timeseries": f"{config.API_PREFIX}/stats/timeseries",
            "devices": f"{config.API_PREFIX}/stats/devices"
        },
        "tech_stack": {
            "framework": "FastAPI",
            "database": "PostgreSQL (Neon)",
            "cache": "In-Memory TTL Cache",
            "deployment": "Railway"
        },
        "github": "https://github.com/stahir80td/StreamPulse"
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns:
        - API status
        - Database connection status
        - Current timestamp
        - API version
    """
    db_healthy = check_database_health()
    
    status = "healthy" if db_healthy else "unhealthy"
    
    return HealthResponse(
        status=status,
        database=db_healthy,
        timestamp=datetime.now(),
        version=config.API_VERSION
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("\n" + "="*60)
    print("🚀 StreamPulse API Starting...")
    print("="*60)
    print(f"   Version: {config.API_VERSION}")
    print(f"   Database: {config.PG_HOST}/{config.PG_DATABASE}")
    print(f"   CORS Origins: {config.ALLOWED_ORIGINS}")
    print("="*60 + "\n")
    
    # Test database connection
    if check_database_health():
        print("✅ Database connection healthy")
    else:
        print("⚠️  Database connection failed - API may not function properly")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("\n🛑 StreamPulse API Shutting down...")
    db_pool.close_all()
    print("✅ Cleanup complete\n")

# Additional utility endpoints

@app.get("/ping", tags=["Health"])
async def ping():
    """Simple ping endpoint for uptime monitoring"""
    return {"ping": "pong", "timestamp": datetime.now()}

@app.get("/version", tags=["Info"])
async def version():
    """Get API version information"""
    return {
        "version": config.API_VERSION,
        "api_title": config.API_TITLE,
        "python_version": "3.11",
        "fastapi_version": "0.104.1"
    }

# Metrics endpoint (for monitoring systems like Prometheus)
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Basic metrics endpoint
    
    In production, integrate with Prometheus or similar
    """
    return {
        "uptime": "N/A",  # TODO: Track actual uptime
        "requests_total": "N/A",  # TODO: Track request count
        "database_pool_size": 10,
        "cache_size": "N/A"  # TODO: Track cache stats
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )