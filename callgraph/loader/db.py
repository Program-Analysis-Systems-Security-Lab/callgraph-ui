"""Database connection and management: wraps LadyBugDB connection"""
import ladybugdb
from pathlib import Path
from typing import Any, List, Optional, Dict

from callgraph.config import settings
from callgraph.schema.ddl import DB_SCHEMA
from callgraph.utils.log import get_logger

logger = get_logger(__name__)


class DB:
    """Database connection manager for call graph storage.
    
    Provides connection management and schema initialization.
    Uses LadyBugDB as the backend database.
    """
    
    def __init__(self, db_path: Optional[str | Path] = None):
        """Initialize LadyBugDB database connection.
        
        Args:
            db_path: Path to LadyBugDB database file
        """
        self.db_path = Path(db_path) if db_path else settings.DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            self.db = ladybugdb.Database(str(self.db_path))
            self.conn = self.db.get_connection()
            logger.info(f"Connected to LadyBugDB at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to LadyBugDB: {e}")
            raise
    
    def init_schema(self) -> None:
        """Initialize database schema by creating tables."""
        for statement in DB_SCHEMA:
            try:
                self.conn.execute(statement)
                logger.debug(f"Executed: {statement}")
            except Exception as e:
                logger.warning(f"Schema statement might already exist: {e}")
        self.conn.commit()
        logger.info("Database schema initialized")
    
    def execute(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """Execute a query.
        
        Args:
            query: Query string
            parameters: Query parameters as dictionary
            
        Returns:
            List of result records as dictionaries
        """
        parameters = parameters or {}
        
        try:
            cursor = self.conn.execute(query, parameters)
            
            # Convert result to list of dictionaries
            records = []
            for row in cursor.fetchall():
                record = dict(row)
                records.append(record)
            
            return records
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    def execute_write(self, query: str, parameters: Optional[Dict] = None) -> None:
        """Execute a write query.
        
        Args:
            query: Query string
            parameters: Query parameters as dictionary
        """
        parameters = parameters or {}
        self.conn.execute(query, parameters)
        self.conn.commit()
    
    def executemany(self, query: str, params_list: List[Dict]) -> None:
        """Execute a query with multiple parameter sets.
        
        Args:
            query: Query string
            params_list: List of parameter dictionaries
        """
        for params in params_list:
            self.conn.execute(query, params)
        self.conn.commit()
    
    def commit(self) -> None:
        """Commit current transaction."""
        self.conn.commit()
    
    def rollback(self) -> None:
        """Rollback current transaction."""
        self.conn.rollback()
    
    def close(self) -> None:
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()
            logger.info("LadyBugDB connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
