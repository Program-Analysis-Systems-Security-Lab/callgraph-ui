"""Call graph validation logic.
Describes validation rules:

No duplicate function IDs.
No duplicate callsite IDs.
Every edge’s caller and callee refer to existing functions.
Every callsite’s caller/callee refer to valid functions.
This matches the real validator logic we’ll see later."""

from pathlib import Path
from typing import Dict, Set

from callgraph.model.callgraph import CallGraph
from callgraph.utils.files import read_json
from callgraph.utils.log import get_logger

logger = get_logger(__name__)


class ValidationError(ValueError):
    """Custom exception for validation errors."""
    pass


def validate_callgraph(graph: CallGraph) -> None:
    """Validate a CallGraph object for consistency.
    
    Checks:
    - All function IDs are unique
    - All referenced function IDs exist
    - No empty or duplicate callsite IDs
    - Callsite references valid functions
    - Edge references valid functions
    
    Args:
        graph: CallGraph to validate
        
    Raises:
        ValidationError: If validation fails
    """
    # Check for functions
    if not graph.functions:
        raise ValidationError("Call graph must contain at least one function")
    
    # Build function ID set and check for duplicates
    function_ids: Set[str] = set()
    duplicate_functions = []
    
    for func in graph.functions:
        if func.id in function_ids:
            duplicate_functions.append(func.id)
        function_ids.add(func.id)
    
    if duplicate_functions:
        raise ValidationError(
            f"Duplicate function IDs found: {', '.join(duplicate_functions)}"
        )
    
    # Check callsites
    callsite_ids: Set[str] = set()
    duplicate_callsites = []
    invalid_callsite_refs = []
    
    for cs in graph.callsites:
        if cs.id in callsite_ids:
            duplicate_callsites.append(cs.id)
        callsite_ids.add(cs.id)
        
        # Check that caller and callee exist
        if cs.caller not in function_ids:
            invalid_callsite_refs.append(
                f"Callsite {cs.id}: caller '{cs.caller}' not found"
            )
        if cs.callee not in function_ids:
            invalid_callsite_refs.append(
                f"Callsite {cs.id}: callee '{cs.callee}' not found"
            )
    
    if duplicate_callsites:
        raise ValidationError(
            f"Duplicate callsite IDs found: {', '.join(duplicate_callsites)}"
        )
    
    if invalid_callsite_refs:
        raise ValidationError(
            f"Invalid function references in callsites:\n" +
            "\n".join(invalid_callsite_refs)
        )
    
    # Check edges
    invalid_edge_refs = []
    
    for i, edge in enumerate(graph.edges):
        if edge.caller not in function_ids:
            invalid_edge_refs.append(
                f"Edge {i}: caller '{edge.caller}' not found"
            )
        if edge.callee not in function_ids:
            invalid_edge_refs.append(
                f"Edge {i}: callee '{edge.callee}' not found"
            )
        if edge.callsite_id and edge.callsite_id not in callsite_ids:
            invalid_edge_refs.append(
                f"Edge {i}: callsite '{edge.callsite_id}' not found"
            )
    
    if invalid_edge_refs:
        raise ValidationError(
            f"Invalid references in edges:\n" + "\n".join(invalid_edge_refs)
        )
    
    logger.info(
        f"Validation passed: {len(graph.functions)} functions, "
        f"{len(graph.callsites)} callsites, {len(graph.edges)} edges"
    )


def validate_json_file(file_path: str | Path) -> CallGraph:
    """Load and validate a call graph JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Validated CallGraph object
        
    Raises:
        ValidationError: If validation fails
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid
    """
    try:
        data = read_json(file_path)
        graph = CallGraph.from_dict(data)
        validate_callgraph(graph)
        return graph
    except Exception as e:
        if isinstance(e, (ValidationError, FileNotFoundError, ValueError)):
            raise
        raise ValidationError(f"Validation failed: {e}")
