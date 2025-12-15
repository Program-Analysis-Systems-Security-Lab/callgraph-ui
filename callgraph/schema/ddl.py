"""Database schema definition using LadyBugDB."""

# LadyBugDB schema for call graph storage
# Database tables: functions, callsites, and edges

DB_SCHEMA = [
    # Create functions table
    """
    CREATE TABLE IF NOT EXISTS functions (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        file TEXT,
        signature TEXT
    )
    """,
    
    # Create callsites table
    """
    CREATE TABLE IF NOT EXISTS callsites (
        id TEXT PRIMARY KEY,
        caller_function_id TEXT NOT NULL,
        callee_function_id TEXT NOT NULL,
        file TEXT,
        line INTEGER,
        FOREIGN KEY (caller_function_id) REFERENCES functions(id),
        FOREIGN KEY (callee_function_id) REFERENCES functions(id)
    )
    """,
    
    # Create edges table
    """
    CREATE TABLE IF NOT EXISTS edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caller_function_id TEXT NOT NULL,
        callee_function_id TEXT NOT NULL,
        callsite_id TEXT,
        depth INTEGER NOT NULL,
        FOREIGN KEY (caller_function_id) REFERENCES functions(id),
        FOREIGN KEY (callee_function_id) REFERENCES functions(id),
        FOREIGN KEY (callsite_id) REFERENCES callsites(id)
    )
    """,
    
    # Create indexes for faster queries
    """
    CREATE INDEX IF NOT EXISTS idx_edges_caller ON edges(caller_function_id)
    """,
    
    """
    CREATE INDEX IF NOT EXISTS idx_edges_callee ON edges(callee_function_id)
    """,
    
    """
    CREATE INDEX IF NOT EXISTS idx_edges_depth ON edges(depth)
    """,
]
