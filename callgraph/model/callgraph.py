"""Data models for call graph representation.
Describes Pydantic models: Function, CallSite, Edge, and the root CallGraph.
Emphasises: enforcing types and making the JSON IR predictable and validated before DB insertion."""


from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class Function(BaseModel):
    """Represents a function in the call graph."""
    
    id: str = Field(..., description="Unique function identifier")
    name: str = Field(..., description="Function name")
    file: Optional[str] = Field(None, description="Source file path")
    signature: Optional[str] = Field(None, description="Function signature")
    
    @field_validator("id", "name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class CallSite(BaseModel):
    """Represents a call site where one function calls another."""
    
    id: str = Field(..., description="Unique callsite identifier")
    caller: str = Field(..., description="Caller function ID")
    callee: str = Field(..., description="Callee function ID")
    file: Optional[str] = Field(None, description="Source file path")
    line: Optional[int] = Field(None, description="Line number")
    
    @field_validator("id", "caller", "callee")
    @classmethod
    def not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    @field_validator("line")
    @classmethod
    def valid_line(cls, v: Optional[int]) -> Optional[int]:
        """Validate line number is positive if present."""
        if v is not None and v < 1:
            raise ValueError("Line number must be positive")
        return v


class Edge(BaseModel):
    """Represents an edge in the call graph."""
    
    caller: str = Field(..., description="Caller function ID")
    callee: str = Field(..., description="Callee function ID")
    callsite_id: Optional[str] = Field(None, description="Associated callsite ID")
    
    @field_validator("caller", "callee")
    @classmethod
    def not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class CallGraph(BaseModel):
    """Complete call graph representation."""
    
    functions: List[Function] = Field(default_factory=list, description="List of functions")
    callsites: List[CallSite] = Field(default_factory=list, description="List of callsites")
    edges: List[Edge] = Field(default_factory=list, description="List of edges")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CallGraph":
        """Create CallGraph from dictionary with flexible key names.
        
        Supports various JSON formats by mapping common key names.
        
        Args:
            data: Dictionary containing call graph data
            
        Returns:
            CallGraph instance
        """
        # Normalize keys to handle different JSON formats
        functions_data = data.get("functions", [])
        callsites_data = data.get("callsites", data.get("callSites", []))
        edges_data = data.get("edges", [])
        
        # Parse functions
        functions = [Function(**f) for f in functions_data]
        
        # Parse callsites (support alternative key names)
        callsites = []
        for cs in callsites_data:
            normalized = {
                "id": cs.get("id"),
                "caller": cs.get("caller", cs.get("caller_id")),
                "callee": cs.get("callee", cs.get("callee_id")),
                "file": cs.get("file"),
                "line": cs.get("line"),
            }
            callsites.append(CallSite(**normalized))
        
        # Parse edges or derive from callsites if not present
        if edges_data:
            edges = []
            for e in edges_data:
                normalized = {
                    "caller": e.get("caller", e.get("caller_id")),
                    "callee": e.get("callee", e.get("callee_id")),
                    "callsite_id": e.get("callsite_id"),
                }
                edges.append(Edge(**normalized))
        else:
            # Derive edges from callsites
            edges = [
                Edge(caller=cs.caller, callee=cs.callee, callsite_id=cs.id)
                for cs in callsites
            ]
        
        return cls(functions=functions, callsites=callsites, edges=edges)
