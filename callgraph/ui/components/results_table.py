"""Results table component for displaying caller-callee relationships."""

import streamlit as st
from typing import List, Tuple
from callgraph.queries import api as queries
from callgraph.loader.db import DB


def render_results_table(db: DB, root_function: str, selected_depth: int, max_functions: int):
    """
    Render results table showing caller-callee relationships at selected depth.
    
    Args:
        db: Database connection instance
        root_function: Root function name for traversal
        selected_depth: Selected depth level
        max_functions: Maximum number of functions to display
    """
    st.divider()
    st.subheader("Results Table")
    
    # Query edges at the selected depth level
    edges = queries.edges_at_depth(db, root_function, selected_depth)
    
    if edges:
        # Limit results to max_functions
        display_edges = edges[:max_functions]
        
        # Show count information
        st.write(
            f"Showing {len(display_edges)} of {len(edges)} edges at depth {selected_depth}"
        )
        
        # Prepare data for results table
        results_data = []
        for caller, callee in display_edges:
            results_data.append({
                "Src's Caller": caller,
                "Src's Callee": callee
            })
        
        # Display results table
        st.dataframe(
            results_data,
            width="stretch",
            hide_index=True,
            height=400
        )
    else:
        # No edges found at this depth
        st.info(f"No edges found at depth {selected_depth}")
