"""Database writer for loading call graphs: takes a CallGraph model and inserts rows into DB tables."""
from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from callgraph.loader.db import DB
from callgraph.model.callgraph import CallGraph, Function, CallSite, Edge
from callgraph.utils.log import get_logger

logger = get_logger(__name__)


class Writer:
    """Writer for inserting call graph data into the database."""
    
    def __init__(self, db: DB):
        """Initialize writer with database connection.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def load_callgraph(self, graph: CallGraph, root_function: str = "main") -> None:
        """Load a complete call graph into the database.
        
        Performs idempotent upserts and computes BFS depths from root.
        
        Args:
            graph: CallGraph to load
            root_function: Root function for depth computation
        """
        try:
            # Insert functions
            self._insert_functions(graph.functions)
            
            # Insert callsites
            self._insert_callsites(graph.callsites)
            
            # Insert edges
            self._insert_edges(graph.edges)
            
            # Compute and update depths
            self._compute_depths(root_function)
            
            self.db.commit()
            logger.info(f"Successfully loaded call graph with {len(graph.functions)} functions")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to load call graph: {e}")
            raise
    
    def _insert_functions(self, functions: List[Function]) -> None:
        """Insert or update functions (idempotent upsert).
        
        Args:
            functions: List of Function objects
        """
        query = """
            INSERT INTO functions (id, name, file, signature)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                file = excluded.file,
                signature = excluded.signature
        """
        
        params = [
            (f.id, f.name, f.file, f.signature)
            for f in functions
        ]
        
        self.db.executemany(query, params)
        logger.debug(f"Inserted/updated {len(functions)} functions")
    
    def _insert_callsites(self, callsites: List[CallSite]) -> None:
        """Insert or update callsites (idempotent upsert).
        
        Args:
            callsites: List of CallSite objects
        """
        if not callsites:
            return
        
        query = """
            INSERT INTO callsites (id, caller_function_id, callee_function_id, file, line)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                caller_function_id = excluded.caller_function_id,
                callee_function_id = excluded.callee_function_id,
                file = excluded.file,
                line = excluded.line
        """
        
        params = [
            (cs.id, cs.caller, cs.callee, cs.file, cs.line)
            for cs in callsites
        ]
        
        self.db.executemany(query, params)
        logger.debug(f"Inserted/updated {len(callsites)} callsites")
    
    def _insert_edges(self, edges: List[Edge]) -> None:
        """Insert edges (idempotent - skip duplicates).
        
        Args:
            edges: List of Edge objects
        """
        if not edges:
            return
        
        query = """
            INSERT OR IGNORE INTO edges (caller_function_id, callee_function_id, callsite_id)
            VALUES (?, ?, ?)
        """
        
        params = [
            (e.caller, e.callee, e.callsite_id)
            for e in edges
        ]
        
        self.db.executemany(query, params)
        logger.debug(f"Inserted {len(edges)} edges")
    
    def _compute_depths(self, root_function: str) -> None:
        """Compute BFS depths from root function and update edges.
        
        Args:
            root_function: Root function ID or name for BFS traversal
        """
        # First, resolve root function ID (may be name or ID)
        cursor = self.db.execute(
            "SELECT id FROM functions WHERE id = ? OR name = ?",
            (root_function, root_function)
        )
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"Root function '{root_function}' not found, skipping depth computation")
            return
        
        root_id = row["id"]
        
        # Build adjacency list from edges
        cursor = self.db.execute(
            "SELECT caller_function_id, callee_function_id FROM edges"
        )
        
        adjacency: Dict[str, List[str]] = {}
        for row in cursor:
            caller = row["caller_function_id"]
            callee = row["callee_function_id"]
            
            if caller not in adjacency:
                adjacency[caller] = []
            adjacency[caller].append(callee)
        
        # BFS to compute depths
        depths: Dict[str, int] = {root_id: 0}
        queue = deque([root_id])
        
        while queue:
            current = queue.popleft()
            current_depth = depths[current]
            
            if current in adjacency:
                for neighbor in adjacency[current]:
                    if neighbor not in depths:
                        depths[neighbor] = current_depth + 1
                        queue.append(neighbor)
        
        # Update edge depths
        update_query = """
            UPDATE edges
            SET depth = ?
            WHERE caller_function_id = ? AND callee_function_id = ?
        """
        
        updates = []
        for caller, callees in adjacency.items():
            if caller in depths:
                for callee in callees:
                    if callee in depths:
                        # Edge depth is the depth of the caller
                        updates.append((depths[caller], caller, callee))
        
        if updates:
            self.db.executemany(update_query, updates)
            logger.debug(f"Updated depths for {len(updates)} edges")
