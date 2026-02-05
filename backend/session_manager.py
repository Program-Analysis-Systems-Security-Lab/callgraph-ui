import os
import shutil
import uuid
import tempfile
import streamlit as st
from backend.loader_kuzu import build_database

class SessionManager:
    @staticmethod
    def get_session_id():
        """Generates a unique ID for the user's browser tab."""
        if "session_id" not in st.session_state:
            st.session_state["session_id"] = str(uuid.uuid4())
        return st.session_state["session_id"]

    @staticmethod
    def setup_user_db(uploaded_file):
        """Creates a private, temporary database for the uploaded file."""
        session_id = SessionManager.get_session_id()
        
        
        temp_dir = tempfile.gettempdir()
        db_path = os.path.join(temp_dir, f"kuzu_session_{session_id}")
        
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_json:
            tmp_json.write(uploaded_file.getbuffer())
            json_path = tmp_json.name
            
        
        if os.path.exists(db_path):
            shutil.rmtree(db_path, ignore_errors=True)
            
        
        build_database(json_path, db_path)
        
        
        os.remove(json_path)
        
        return db_path