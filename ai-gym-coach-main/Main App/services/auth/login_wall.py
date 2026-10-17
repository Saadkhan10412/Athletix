import streamlit as st
from services.persistence.exercise_repository import get_or_create_user


def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True
    
    # Auto-login via query parameter passed from ATHLETIX main app
    query_username = None
    try:
        if hasattr(st, "query_params") and "username" in st.query_params:
            val = st.query_params["username"]
            query_username = val[0] if isinstance(val, list) else val
    except Exception:
        query_username = None

    if query_username:
        user = get_or_create_user(query_username)
        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]
        return True
    
    st.title("🏋️‍♂️ AI Real-time GYM Trainer")
    st.markdown("### Welcome! Please enter a username to start.")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Name (unique)", placeholder="unique name e.g. princekhunt")
        submit_button = st.form_submit_button("Start Session", use_container_width=True)

    if submit_button:
        if not username:
            st.error("Name cannot be empty.")
            return False
        
        user = get_or_create_user(username)
    
        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]

        st.rerun()

    return False