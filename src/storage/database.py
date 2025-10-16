"""Database manager for RMN system."""

import logging
from typing import Optional, Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(
        self,
        database_url: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        echo: bool = False
    ):
        """
        Initialize database manager.
        
        Args:
            database_url: SQLAlchemy database URL
            pool_size: Connection pool size
            max_overflow: Max overflow connections
            echo: Echo SQL statements
        """
        self.database_url = database_url
        
        # Create engine with connection pooling
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # Verify connections before using
            echo=echo
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Set up event listeners
        self._setup_event_listeners()
        
        logger.info(f"Database manager initialized: {database_url}")
    
    def _setup_event_listeners(self):
        """Set up database event listeners."""
        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            """Enable foreign keys for SQLite."""
            if "sqlite" in self.database_url:
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
    
    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("Database tables dropped")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup.
        
        Yields:
            Database session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_factory(self):
        """Get session factory for dependency injection."""
        return self.SessionLocal
    
    def health_check(self) -> bool:
        """
        Check database health.
        
        Returns:
            True if database is healthy
        """
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def close(self):
        """Close database connections."""
        self.engine.dispose()
        logger.info("Database connections closed")


# Global database instance
_db_manager: Optional[DatabaseManager] = None


def init_db(database_url: str, **kwargs) -> DatabaseManager:
    """
    Initialize global database manager.
    
    Args:
        database_url: SQLAlchemy database URL
        **kwargs: Additional arguments for DatabaseManager
    
    Returns:
        Database manager instance
    """
    global _db_manager
    _db_manager = DatabaseManager(database_url, **kwargs)
    _db_manager.create_tables()
    return _db_manager


def get_db() -> DatabaseManager:
    """
    Get global database manager.
    
    Returns:
        Database manager instance
    
    Raises:
        RuntimeError: If database not initialized
    """
    if _db_manager is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db_manager


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session.
    
    Yields:
        Database session
    """
    db = get_db()
    with db.get_session() as session:
        yield session
