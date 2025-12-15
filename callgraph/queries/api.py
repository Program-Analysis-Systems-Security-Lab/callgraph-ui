"""
Query API for call graph analysis using LadyBugDB queries.

This module provides functions to query the LadyBugDB database
for call graph relationships, functions, and callsites.

All queries use standard database query language.
"""

from typing import Dict, List, Optional, Tuple

from callgraph.loader.db import DB
from callgraph.utils.log import get_logger

logger = get_logger(__name__)


def list_functions(db: DB) -> List[Dict[str, str]]:
    """
    List all functions in the database.
    
    Query: Select all functions from functions table
    
    Args:
        db: Database instance
        
    Returns:
        List of function dictionaries with id, name, file, signature
    """
    # Query to select all functions
    query = """
    SELECT id, name, file, signature
    FROM functions
    ORDER BY name
    """
    
    return db.execute(query)


def get_callees(db: DB, function: str) -> List[Dict[str, str]]:
    """
    Get all functions called by the given function (outgoing calls).
    
    Query: Join edges with functions to get callees
    
    Args:
        db: Database instance
        function: Function ID or name
        
    Returns:
        List of callee function dictionaries
    """
    # Query to find all functions called by the given function
    query = """
    SELECT DISTINCT f.id, f.name, f.file, f.signature
    FROM edges e
    JOIN functions f ON e.callee_function_id = f.id
    JOIN functions caller ON e.caller_function_id = caller.id
    WHERE caller.id = :function OR caller.name = :function
    ORDER BY f.name
    """
    
    return db.execute(query, {"function": function})


def get_callers(db: DB, function: str) -> List[Dict[str, str]]:
    """
    Get all functions that call the given function (incoming calls).
    
    Query: Join edges with functions to get callers
    
    Args:
        db: Database instance
        function: Function ID or name
        
    Returns:
        List of caller function dictionaries
    """
    # Query to find all functions that call the given function
    query = """
    SELECT DISTINCT f.id, f.name, f.file, f.signature
    FROM edges e
    JOIN functions f ON e.caller_function_id = f.id
    JOIN functions callee ON e.callee_function_id = callee.id
    WHERE callee.id = :function OR callee.name = :function
    ORDER BY f.name
    """
    
    return db.execute(query, {"function": function})


def depth_summary(db: DB, root: str = "main") -> List[Dict[str, int]]:
    """
    Get summary of call graph grouped by depth level.
    
    Query: Aggregates edges by depth
    
    Args:
        db: Database instance
        root: Root function for depth computation (not currently used in query)
        
    Returns:
        List of dictionaries with depth, function_count, edge_count
    """
    # Query to summarize calls by depth
    # Groups by depth and counts unique callers and total edges
    query = """
    SELECT 
        depth,
        COUNT(DISTINCT caller_function_id) as function_count,
        COUNT(*) as edge_count
    FROM edges
    WHERE depth IS NOT NULL
    GROUP BY depth
    ORDER BY depth
    """
    
    return db.execute(query)


def edges_at_depth(db: DB, root: str = "main", depth: int = 0) -> List[Tuple[str, str]]:
    """Get all edges at a specific depth level.
    
    Args:
        db: Database instance
        root: Root function for depth computation
        depth: Depth level to query
        
    Returns:
        List of (caller_name, callee_name) tuples
    """
    query = """
    SELECT caller.name as caller_name, callee.name as callee_name
    FROM edges e
    JOIN functions caller ON e.caller_function_id = caller.id
    JOIN functions callee ON e.callee_function_id = callee.id
    WHERE e.depth = :depth
    ORDER BY caller.name, callee.name
    """
    
    results = db.execute(query, {"depth": depth})
    return [(row["caller_name"], row["callee_name"]) for row in results]


def function_detail(db: DB, function: str) -> Optional[Dict]:
    """Get detailed information about a function.
    
    Args:
        db: Database instance
        function: Function ID or name
        
    Returns:
        Dictionary with function info, callers, callees, and callsites
    """
    # Get function info
    query = """
    SELECT id, name, file, signature
    FROM functions
    WHERE id = :function OR name = :function
    """
    
    results = db.execute(query, {"function": function})
    
    if not results:
        return None
    
    func_info = results[0]
    
    # Get callers
    callers = get_callers(db, function)
    
    # Get callees
    callees = get_callees(db, function)
    
    # Get callsites where this function is the caller
    callsite_query = """
    SELECT cs.id, caller.name as caller_name, callee.name as callee_name,
           cs.file, cs.line
    FROM callsites cs
    JOIN functions caller ON cs.caller_function_id = caller.id
    JOIN functions callee ON cs.callee_function_id = callee.id
    WHERE caller.id = :function OR caller.name = :function
    ORDER BY cs.file, cs.line
    """
    
    callsites = db.execute(callsite_query, {"function": function})
    
    return {
        "function": func_info,
        "callers": callers,
        "callees": callees,
        "callsites": callsites,
    }


def get_all_depths(db: DB) -> List[int]:
    """Get all available depth levels in the database.
    
    Args:
        db: Database instance
        
    Returns:
        Sorted list of depth values
    """
    query = """
    SELECT DISTINCT depth
    FROM edges
    WHERE depth IS NOT NULL
    ORDER BY depth
    """
    
    results = db.execute(query)
    return [row["depth"] for row in results]
