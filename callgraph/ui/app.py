"""
Main Streamlit UI application for Call Graph Explorer.

This application uses KuzuDB (embedded graph database) to store and query
call graph relationships. The UI is modularized into separate components
for better maintainability.
"""

import streamlit as st
from pathlib import Path

from callgraph.config import settings
from callgraph.loader.db import DB
from callgraph.queries import api as queries
from callgraph.ui.components import (
    render_search_bar,
    render_search_results,
    render_depth_configuration_table,
    render_results_table
)

# Configure page settings
st.set_page_config(
    page_title="Call Graph Explorer",
    layout="wide"
)


def initialize_session_state():
    """Initialize session state variables with default values."""
    if "db_path" not in st.session_state:
        # Use test database file by default (LadyBugDB database file)
        st.session_state.db_path = str(Path("test_callgraph.db").absolute())
    
    if "selected_depth" not in st.session_state:
        st.session_state.selected_depth = 0
    
    if "max_functions" not in st.session_state:
        st.session_state.max_functions = 10
    
    if "root_function" not in st.session_state:
        st.session_state.root_function = settings.DEFAULT_ROOT_FUNCTION


def render_sidebar_configuration():
    """Render configuration in sidebar."""
    with st.sidebar:
        st.header("Configuration")
        
        # Database path input
        db_path = st.text_input(
            "Database Path",
            value=st.session_state.db_path,
            help="Path to LadyBugDB database file (e.g., test_callgraph.db)"
        )
        
        if db_path != st.session_state.db_path:
            st.session_state.db_path = db_path
            st.rerun()
        
        st.divider()
        
        # Root function input
        root_function = st.text_input(
            "Root Function",
            value=st.session_state.root_function,
            help="Starting function for call graph traversal"
        )
        
        if root_function != st.session_state.root_function:
            st.session_state.root_function = root_function
            st.rerun()
        
        st.divider()
        
        # Show connection status
        try:
            db_file = Path(st.session_state.db_path)
            if db_file.exists():
                st.success("✓ Database file found")
            else:
                st.warning("⚠ Database file not found")
                st.info("Please create database or check path")
        except:
            pass


def load_db() -> DB:
    """
    Load KuzuDB database connection and initialize schema if needed.
    
    Returns:
        DB: Database connection instance
    """
    db = DB(st.session_state.db_path)
    # Initialize schema if tables don't exist
    try:
        db.init_schema()
    except Exception as e:
        pass  # Schema might already exist
    return db


def main():
    """Main application entry point."""
    
    # Initialize session state
    initialize_session_state()
    
    # Display title
    st.title("Call Graph Explorer")
    
    # Render sidebar configuration
    render_sidebar_configuration()
    
    try:
        # Load database connection first
        db = load_db()
        
        # Get depth summary from database
        summary = queries.depth_summary(db, st.session_state.root_function)
        
        # Check if data exists
        if not summary:
            st.warning("No call graph data found in database")
            st.info("""
            **To get started:**
            1. Make sure you have a valid KuzuDB database file
            2. Check the database path in the sidebar
            3. The database should contain Function nodes and CALLS relationships
            
            **Database Path:** `{}`
            """.format(st.session_state.db_path))
            db.close()
            return
        
        # Render search bar component at the top
        search_term = render_search_bar(db)
        
        # Render search results if search was performed
        render_search_results(search_term, db)
        
        st.divider()
        
        # Render depth configuration table
        selected_depth, max_functions = render_depth_configuration_table(summary)
        
        # Render results table with caller-callee relationships
        render_results_table(
            db, 
            st.session_state.root_function, 
            selected_depth, 
            max_functions
        )
        
        # Close database connection
        db.close()
        
    except Exception as e:
        # Display error message if something goes wrong
        st.error(f"Database Error: {e}")
        st.info("""
        **Troubleshooting:**
        - Check if database path is correct in sidebar
        - Make sure database file exists
        - Verify database contains data
        """)


# Run the application
if __name__ == "__main__":
    main()
