"""
LadyBugDB: Custom database for call graph storage.
This module provides a simple interface to interact with the callgraph database.
"""

class Database:
    """Database class for LadyBugDB."""
    
    def __init__(self, path: str):
        """Initialize database.
        
        Args:
            path: Path to database file
        """
        self.path = path
        self._conn = None
    
    def get_connection(self):
        """Get database connection.
        
        Returns:
            Connection object
        """
        if self._conn is None:
            self._conn = Connection(self)
        return self._conn


class Connection:
    """Connection class for LadyBugDB."""
    
    def __init__(self, database: Database):
        """Initialize connection.
        
        Args:
            database: Database instance
        """
        self.database = database
        self._setup_connection()
    
    def _setup_connection(self):
        """Setup internal connection."""
        # Import here to avoid circular dependency
        import sqlite3
        self._internal_conn = sqlite3.connect(self.database.path)
        self._internal_conn.row_factory = sqlite3.Row
    
    def execute(self, query: str, parameters: dict = None):
        """Execute a query.
        
        Args:
            query: SQL query string
            parameters: Query parameters
            
        Returns:
            Cursor with results
        """
        cursor = self._internal_conn.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        return cursor
    
    def commit(self):
        """Commit transaction."""
        self._internal_conn.commit()
    
    def rollback(self):
        """Rollback transaction."""
        self._internal_conn.rollback()
    
    def close(self):
        """Close connection."""
        if self._internal_conn:
            self._internal_conn.close()
            self._internal_conn = None
