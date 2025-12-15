"""Depth configuration table component."""

import streamlit as st
from typing import List, Dict


def render_depth_configuration_table(summary: List[Dict]):
    """
    Render depth configuration table showing depth levels and function counts.
    
    Args:
        summary: List of dictionaries containing depth and function_count
    
    Returns:
        Tuple of (selected_depth, max_functions_to_display)
    """
    st.divider()
    st.subheader("Configuration Table")
    
    # Prepare data for configuration table
    config_data = []
    for row in summary:
        config_data.append({
            "Depth": row["depth"],
            "Number of Functions": row["function_count"]
        })
    
    # Display configuration table
    st.dataframe(
        config_data,
        width="stretch",
        hide_index=True
    )
    
    # Create two columns for depth and function count selectors
    sel_col1, sel_col2 = st.columns(2)
    
    with sel_col1:
        # Extract available depth levels
        depths = [row["depth"] for row in summary]
        
        # Find current index or default to 0
        current_index = 0
        if st.session_state.selected_depth in depths:
            current_index = depths.index(st.session_state.selected_depth)
        
        # Depth selector dropdown
        selected_depth = st.selectbox(
            "Select Depth",
            depths,
            index=current_index,
            help="Choose depth level to view call relationships"
        )
        
        # Update session state
        st.session_state.selected_depth = selected_depth
    
    with sel_col2:
        # Get maximum functions available for selected depth
        max_funcs = next(
            (row["function_count"] for row in summary if row["depth"] == selected_depth),
            0
        )
        
        max_functions = st.session_state.max_functions
        
        if max_funcs > 0:
            # Number input for limiting displayed functions
            max_functions = st.number_input(
                "Number of Functions to Display",
                min_value=1,
                max_value=max_funcs,
                value=min(st.session_state.max_functions, max_funcs),
                step=1,
                help=f"Maximum {max_funcs} functions available at this depth"
            )
            
            # Update session state
            st.session_state.max_functions = max_functions
    
    return selected_depth, max_functions
