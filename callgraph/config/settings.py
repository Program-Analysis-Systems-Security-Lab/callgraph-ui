"""Global configuration settings for callgraph-cli."""

import os
from pathlib import Path

# KuzuDB database path (embedded database)
DEFAULT_DB_PATH = Path(os.getenv("CALLGRAPH_DB_PATH", str(Path.home() / ".callgraph" / "kuzu_db")))

# Debug mode
DEBUG = os.getenv("CALLGRAPH_DEBUG", "false").lower() == "true"

# Default root function for call graph traversal
DEFAULT_ROOT_FUNCTION = "main"

# Logging configuration
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

