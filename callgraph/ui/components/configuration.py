"""Configuration component for database and root function settings."""

import streamlit as st
from callgraph.config import settings


def render_configuration():
    """
    Render configuration UI component.
    
    Displays input fields for:
    - Database path
    - Root function name
    
    Automatically reloads app when configuration changes.
    """
    st.divider()
    
    # Create two columns for configuration inputs
    config_col1, config_col2 = st.columns(2)
    
    with config_col1:
        # Database path input
        db_path = st.text_input(
            "Database Path",
            value=st.session_state.db_path,
            help="Path to KuzuDB database directory"
        )
        
        # If database path changed, update and reload
        if db_path != st.session_state.db_path:
            st.session_state.db_path = db_path
            st.rerun()
    
    with config_col2:
        # Root function input
        root_function = st.text_input(
            "Root Function",
            value=st.session_state.root_function,
            help="Starting function for call graph traversal"
        )
        
        # If root function changed, update and reload
        if root_function != st.session_state.root_function:
            st.session_state.root_function = root_function
            st.rerun()
