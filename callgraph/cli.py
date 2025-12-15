"""Command-line interface for callgraph-cli."""

import sys
from pathlib import Path

import click

from callgraph.config import settings
from callgraph.loader.db import DB
from callgraph.loader.writer import Writer
from callgraph.queries import api as queries
from callgraph.validate.validator import validate_json_file
from callgraph.utils.log import get_logger

logger = get_logger(__name__)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """callgraph-cli: A tool for managing and analyzing call graphs."""
    pass


@cli.command()
@click.option(
    "--db-path",
    type=click.Path(),
    default=None,
    help=f"Database path (default: {settings.DEFAULT_DB_PATH})"
)
def init_db(db_path: str | None):
    """Initialize a new call graph database."""
    try:
        with DB(db_path) as db:
            db.init_schema()
        
        path = Path(db_path) if db_path else settings.DEFAULT_DB_PATH
        click.echo(f"✓ Database initialized at {path}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("json_file", type=click.Path(exists=True))
def validate_json(json_file: str):
    """Validate a call graph JSON file."""
    try:
        graph = validate_json_file(json_file)
        click.echo(f"✓ JSON is valid")
        click.echo(f"  Functions: {len(graph.functions)}")
        click.echo(f"  Callsites: {len(graph.callsites)}")
        click.echo(f"  Edges: {len(graph.edges)}")
    except Exception as e:
        click.echo(f"✗ Validation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("json_file", type=click.Path(exists=True))
@click.option(
    "--db-path",
    type=click.Path(),
    default=None,
    help=f"Database path (default: {settings.DEFAULT_DB_PATH})"
)
@click.option(
    "--root",
    default=settings.DEFAULT_ROOT_FUNCTION,
    help="Root function for depth computation"
)
def load_json(json_file: str, db_path: str | None, root: str):
    """Load a call graph JSON file into the database."""
    try:
        # Validate first
        click.echo("Validating JSON...")
        graph = validate_json_file(json_file)
        
        # Load into database
        click.echo("Loading into database...")
        with DB(db_path) as db:
            # Ensure schema exists
            db.init_schema()
            
            # Load graph
            writer = Writer(db)
            writer.load_callgraph(graph, root_function=root)
        
        click.echo(f"✓ Successfully loaded call graph")
        click.echo(f"  Functions: {len(graph.functions)}")
        click.echo(f"  Callsites: {len(graph.callsites)}")
        click.echo(f"  Edges: {len(graph.edges)}")
        click.echo(f"  Root: {root}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def query():
    """Query the call graph database."""
    pass

@query.command()
@click.option(
    "--db-path",
    type=click.Path(),
    default=None,
    help=f"Database path (default: {settings.DEFAULT_DB_PATH})"
)
def functions(db_path: str | None):
    """List all functions in the database."""
    try:
        with DB(db_path) as db:
            funcs = queries.list_functions(db)
        
        if not funcs:
            click.echo("No functions found")
            return
        
        click.echo(f"Found {len(funcs)} functions:\n")
        for func in funcs:
            file_info = f" ({func['file']})" if func['file'] else ""
            click.echo(f"  {func['name']}{file_info}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@query.command()
@click.option("--function", required=True, help="Function name or ID")
@click.option(
    "--db-path",
    type=click.Path(),
    default=None,
    help=f"Database path (default: {settings.DEFAULT_DB_PATH})"
)
def callees(function: str, db_path: str | None):
    """List all functions called by the given function."""
    try:
        with DB(db_path) as db:
            callees_list = queries.get_callees(db, function)
        
        if not callees_list:
            click.echo(f"No callees found for function '{function}'")
            return
        
        click.echo(f"Callees of '{function}':\n")
        for callee in callees_list:
            file_info = f" ({callee['file']})" if callee['file'] else ""
            click.echo(f"  → {callee['name']}{file_info}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@query.command()
@click.option("--function", required=True, help="Function name or ID")
@click.option(
    "--db-path",
    type=click.Path(),
    default=None,
    help=f"Database path (default: {settings.DEFAULT_DB_PATH})"
)
def callers(function: str, db_path: str | None):
    """List all functions that call the given function."""
    try:
        with DB(db_path) as db:
            callers_list = queries.get_callers(db, function)
        
        if not callers_list:
            click.echo(f"No callers found for function '{function}'")
            return
        
        click.echo(f"Callers of '{function}':\n")
        for caller in callers_list:
            file_info = f" ({caller['file']})" if caller['file'] else ""
            click.echo(f"  ← {caller['name']}{file_info}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@query.command()
@click.option(
    "--root",
    default=settings.DEFAULT_ROOT_FUNCTION,
    help="Root function for depth computation"
)
@click.option(
    "--db-path",
    type=click.Path(),
    default=None,
    help=f"Database path (default: {settings.DEFAULT_DB_PATH})"
)
def depth_summary(root: str, db_path: str | None):
    """Show call graph depth summary."""
    try:
        with DB(db_path) as db:
            summary = queries.depth_summary(db, root)
        
        if not summary:
            click.echo(f"No depth information found for root '{root}'")
            return
        
        click.echo(f"Depth summary from root '{root}':\n")
        click.echo(f"{'Depth':<8} {'Functions':<12} {'Edges':<8}")
        click.echo("-" * 30)
        for row in summary:
            click.echo(
                f"{row['depth']:<8} {row['function_count']:<12} {row['edge_count']:<8}"
            )
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@query.command()
@click.option(
    "--root",
    default=settings.DEFAULT_ROOT_FUNCTION,
    help="Root function for depth computation"
)
@click.option("--depth", required=True, type=int, help="Depth level to query")
@click.option(
    "--db-path",
    type=click.Path(),
    default=None,
    help=f"Database path (default: {settings.DEFAULT_DB_PATH})"
)
def edges_at_depth(root: str, depth: int, db_path: str | None):
    """Show edges at a specific depth level."""
    try:
        with DB(db_path) as db:
            edges = queries.edges_at_depth(db, root, depth)
        
        if not edges:
            click.echo(f"No edges found at depth {depth} from root '{root}'")
            return
        
        click.echo(f"Edges at depth {depth} from root '{root}':\n")
        for caller, callee in edges:
            click.echo(f"  {caller} → {callee}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@query.command()
@click.option("--function", required=True, help="Function name or ID")
@click.option(
    "--db-path",
    type=click.Path(),
    default=None,
    help=f"Database path (default: {settings.DEFAULT_DB_PATH})"
)
def detail(function: str, db_path: str | None):
    """Show detailed information about a function."""
    try:
        with DB(db_path) as db:
            info = queries.function_detail(db, function)
        
        if not info:
            click.echo(f"Function '{function}' not found")
            return
        
        func = info["function"]
        click.echo(f"Function: {func['name']}")
        if func['file']:
            click.echo(f"File: {func['file']}")
        if func['signature']:
            click.echo(f"Signature: {func['signature']}")
        click.echo()
        
        click.echo(f"Callers ({len(info['callers'])}):")
        for caller in info['callers']:
            click.echo(f"  ← {caller['name']}")
        click.echo()
        
        click.echo(f"Callees ({len(info['callees'])}):")
        for callee in info['callees']:
            click.echo(f"  → {callee['name']}")
        click.echo()
        
        if info['callsites']:
            click.echo(f"Callsites ({len(info['callsites'])}):")
            for cs in info['callsites']:
                loc = f"{cs['file']}:{cs['line']}" if cs['file'] and cs['line'] else "unknown"
                click.echo(f"  {cs['caller_name']} → {cs['callee_name']} ({loc})")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
