"""
Database Connection Pool and Utilities
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import config


class DatabasePool:
    """PostgreSQL connection pool"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabasePool, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **config.get_connection_params()
            )
            print("✅ Database connection pool initialized")
        except Exception as e:
            print(f"❌ Failed to initialize database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Get database connection from pool (context manager)
        
        Usage:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """
        Get database cursor (context manager)
        
        Usage:
            with db_pool.get_cursor() as cursor:
                cursor.execute("SELECT * FROM table")
                results = cursor.fetchall()
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def close_all(self):
        """Close all connections in pool"""
        if self._pool:
            self._pool.closeall()
            print("🔒 Database connection pool closed")


# Singleton instance
db_pool = DatabasePool()


# Helper functions for common queries

def execute_query(query: str, params: tuple = None, fetch_one: bool = False):
    """
    Execute query and return results
    
    Args:
        query: SQL query string
        params: Query parameters tuple
        fetch_one: If True, return single result; if False, return all results
    
    Returns:
        Query results as list of dicts or single dict
    """
    with db_pool.get_cursor() as cursor:
        cursor.execute(query, params)
        
        if fetch_one:
            return cursor.fetchone()
        else:
            return cursor.fetchall()


def execute_insert(query: str, params: tuple = None, returning: bool = False):
    """
    Execute INSERT query
    
    Args:
        query: SQL INSERT query string
        params: Query parameters tuple
        returning: If True, return inserted row
    
    Returns:
        Inserted row if returning=True, else None
    """
    with db_pool.get_cursor() as cursor:
        cursor.execute(query, params)
        
        if returning:
            return cursor.fetchone()
        
        return None


def execute_update(query: str, params: tuple = None):
    """
    Execute UPDATE query
    
    Args:
        query: SQL UPDATE query string
        params: Query parameters tuple
    
    Returns:
        Number of rows affected
    """
    with db_pool.get_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.rowcount


def execute_delete(query: str, params: tuple = None):
    """
    Execute DELETE query
    
    Args:
        query: SQL DELETE query string
        params: Query parameters tuple
    
    Returns:
        Number of rows deleted
    """
    with db_pool.get_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.rowcount


def check_database_health():
    """
    Check database connection health
    
    Returns:
        True if healthy, False otherwise
    """
    try:
        with db_pool.get_cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False