import streamlit as st
from datetime import date, timedelta

def render_global_filters():
    """
    Render clean global filters in the sidebar with onboarding at the top.
    """
    # Navigation section at the top
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #3D5AFE, #5C6BC0); 
                border-radius: 12px; 
                padding: 16px; 
                margin-bottom: 24px; 
                color: white;">
        <h4 style="margin: 0; color: white;">Navigation</h4>
        <p style="margin: 8px 0 0 0; font-size: 12px; opacity: 0.9;">
            Manage your campaigns
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Onboarding", key="go_onboarding", use_container_width=True):
        st.switch_page("ui/streamlit_app.py")
    
    if st.sidebar.button("Reconnect Accounts", key="reconnect_accounts", use_container_width=True):
        if "onboarding_id" in st.session_state:
            del st.session_state["onboarding_id"]
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Platform selector
    st.sidebar.markdown("**Platform**")
    platform_options = {
        "All Platforms": "all",
        "GA4": "ga4", 
        "Instagram/Meta": "meta",
        "Twitter/X": "twitter"
    }
    
    selected_platform = st.sidebar.selectbox(
        "Select Platform",
        options=list(platform_options.keys()),
        key="global_platform"
    )
    
    st.session_state["selected_platform"] = platform_options[selected_platform]
    
    st.sidebar.markdown("")
    
    # Time range selector
    st.sidebar.markdown("**Time Range**")
    
    today = date.today()
    max_past_date = today - timedelta(days=90)
    
    range_options = {
        "Past Day": (today - timedelta(days=1), today),
        "This Week": (today - timedelta(days=today.weekday()), today),
        "Last 7 Days": (today - timedelta(days=7), today),
        "Last 30 Days": (today - timedelta(days=30), today),
        "Last 60 Days": (today - timedelta(days=60), today),
        "Last 90 Days": (today - timedelta(days=90), today),
        "Custom": None
    }
    
    selected_range = st.sidebar.selectbox(
        "Select Range",
        options=list(range_options.keys()),
        key="global_time_range"
    )
    
    if selected_range == "Custom":
        start_date, end_date = st.sidebar.date_input(
            "Custom Range",
            value=(today - timedelta(days=7), today),
            min_value=max_past_date,
            max_value=today,
            key="global_custom_range"
        )
    else:
        start_date, end_date = range_options[selected_range]
    
    st.session_state["start_date"] = start_date
    st.session_state["end_date"] = end_date
    
    return platform_options[selected_platform], start_date, end_date 