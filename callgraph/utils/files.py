"""File I/O utilities."""

import json
from pathlib import Path
from typing import Any, Dict

from callgraph.utils.log import get_logger

logger = get_logger(__name__)


def read_json(file_path: str | Path) -> Dict[str, Any]:
    """Read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data as a dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file contains invalid JSON
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Successfully loaded JSON from {path}")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")


def write_json(data: Dict[str, Any], file_path: str | Path) -> None:
    """Write data to a JSON file.
    
    Args:
        data: Data to write
        file_path: Path to the output file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Successfully wrote JSON to {path}")
