"""Search bar component for function search."""

import streamlit as st
from callgraph.queries import api as queries
from callgraph.loader.db import DB


def render_search_bar(db: DB):
    """
    Render enhanced search bar UI component.
    
    Args:
        db: Database connection instance
        
    Returns:
        search_term: The search query string
    """
    # Create columns for search bar layout
    search_col, btn_col = st.columns([5, 1])
    
    with search_col:
        # Search input field
        search_term = st.text_input(
            "Search Functions",
            placeholder="Type: main, foo, bar, baz, qux...",
            label_visibility="visible",
            help="🔍 Search by function name | Press Enter or click 🔍 to search",
            key="search_input"
        )
    
    with btn_col:
        # Add spacing to align buttons with inputs
        st.write("")
        st.write("")
        
        # Search and Clear buttons
        btn1, btn2 = st.columns(2)
        with btn1:
            search_clicked = st.button("🔍", help="Search", width="stretch")
        with btn2:
            clear_clicked = st.button("✕", help="Clear", width="stretch")
    
    # Handle search button click
    if search_clicked:
        if search_term and search_term.strip():
            st.session_state.trigger_search = True
            st.session_state.last_search_term = search_term
        else:
            st.warning("⚠️ Please enter a function name to search")
    
    # Handle clear button click
    if clear_clicked:
        st.session_state.trigger_search = False
        st.session_state.last_search_term = ""
        st.rerun()
    
    return search_term


def render_search_results(search_term: str, db: DB):
    """
    Render enhanced search results with function details.
    
    Args:
        search_term: The search query string
        db: Database connection instance
    """
    # Check if search was triggered
    if not st.session_state.get('trigger_search', False):
        return
    
    # Use the stored search term from session state
    actual_search_term = st.session_state.get('last_search_term', search_term)
    
    if not actual_search_term:
        st.session_state.trigger_search = False
        return
    
    st.divider()
    
    # Search results header
    st.markdown(f"### 🔍 Search Results for: `{actual_search_term}`")
    
    # Show available functions as hint
    with st.expander("💡 Available Functions in Database", expanded=False):
        try:
            all_funcs = queries.list_functions(db)
            func_names = sorted([f['name'] for f in all_funcs])
            st.info(f"**Functions you can search:** {', '.join([f'`{name}`' for name in func_names])}")
        except:
            pass
    
    try:
        # Get all functions from database
        functions = queries.list_functions(db)
        
        # Filter functions by search term (case-insensitive)
        filtered_functions = [
            func for func in functions
            if actual_search_term.lower() in func['name'].lower()
        ]
        
        if filtered_functions:
            st.success(f"✓ Found {len(filtered_functions)} matching function(s)")
            
            # Build call relationship table for all matching functions
            table_data = []
            for func in filtered_functions[:50]:  # Limit to 50 results
                try:
                    callers = queries.get_callers(db, func['name'])
                    callees = queries.get_callees(db, func['name'])
                    
                    # Add rows for each caller -> function relationship
                    if callers:
                        for caller in callers:
                            caller_file = caller.get('file', 'N/A')
                            func_file = func['file'] if func['file'] else 'N/A'
                            table_data.append({
                                "Caller": f"{caller['name']} ({caller_file})",
                                "Callee": f"{func['name']} ({func_file})"
                            })
                    
                    # Add rows for function -> callee relationship
                    if callees:
                        for callee in callees:
                            func_file = func['file'] if func['file'] else 'N/A'
                            callee_file = callee.get('file', 'N/A')
                            table_data.append({
                                "Caller": f"{func['name']} ({func_file})",
                                "Callee": f"{callee['name']} ({callee_file})"
                            })
                    
                    # If no relationships, show the function itself
                    if not callers and not callees:
                        func_file = func['file'] if func['file'] else 'N/A'
                        table_data.append({
                            "Caller": "-",
                            "Callee": f"{func['name']} ({func_file})"
                        })
                except:
                    pass
            
            # Display table
            if table_data:
                st.markdown("### Call Relationships Table")
                st.dataframe(table_data, width="stretch", hide_index=True)
                st.caption(f"Showing {len(table_data)} call relationships")
            else:
                st.info("No call relationships found")
            
            # Show message if results were truncated
            if len(filtered_functions) > 50:
                st.info(f"ℹ️ Showing first 50 of {len(filtered_functions)} results")
        
        else:
            st.warning(f"⚠️ No functions found matching `{actual_search_term}`")
            
            # Show suggestions
            all_funcs = queries.list_functions(db)
            func_names = sorted([f['name'] for f in all_funcs])
            
            st.markdown("**💡 Suggestions:**")
            st.markdown(f"- Available functions: {', '.join([f'`{name}`' for name in func_names])}")
            st.markdown(f"- Try partial match: `{actual_search_term[0]}`, `{actual_search_term[:2] if len(actual_search_term) > 1 else actual_search_term}`")
            st.markdown("- Search is case-insensitive")
    
    except Exception as e:
        st.error(f"❌ Error searching functions: {str(e)}")
    
    # Reset search trigger after displaying results
    st.session_state.trigger_search = False
