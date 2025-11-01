"""
Database connection and utilities
"""

import psycopg2
from psycopg2 import pool
from typing import Optional, List, Dict, Any

from .config import Config

config = Config()

# Create connection pool
db_pool: Optional[psycopg2.pool.SimpleConnectionPool] = None


def init_db_pool():
    """Initialize database connection pool"""
    global db_pool
    
    if db_pool is None:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=config.PG_HOST,
            port=config.PG_PORT,
            database=config.PG_DATABASE,
            user=config.PG_USER,
            password=config.PG_PASSWORD,
            sslmode=config.PG_SSLMODE
        )
    
    return db_pool


def get_db_connection():
    """Get connection from pool"""
    if db_pool is None:
        init_db_pool()
    
    return db_pool.getconn()


def release_db_connection(conn):
    """Release connection back to pool"""
    if db_pool:
        db_pool.putconn(conn)


def execute_query(query: str, params: tuple = None, fetch_one: bool = False) -> List[Dict[str, Any]]:
    """
    Execute a SELECT query and return results as list of dicts
    
    Args:
        query: SQL query string
        params: Query parameters (optional)
        fetch_one: If True, return single dict instead of list
    
    Returns:
        List of dictionaries with column names as keys (or single dict if fetch_one=True)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Fetch rows
        if fetch_one:
            row = cursor.fetchone()
            result = dict(zip(columns, row)) if row else None
        else:
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
        
        cursor.close()
        return result
        
    except Exception as e:
        print(f"Query execution error: {e}")
        raise
    
    finally:
        if conn:
            release_db_connection(conn)


def check_database_health() -> bool:
    """Check if database is accessible"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        release_db_connection(conn)
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False


def close_db_pool():
    """Close all connections in pool"""
    global db_pool
    if db_pool:
        db_pool.closeall()
        db_pool = None