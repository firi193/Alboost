import streamlit as st
from datetime import date, timedelta

def render_global_filters():
    """
    Render global filters in the sidebar.
    Returns the selected platform and date range.
    """
    st.sidebar.markdown("## 🔧 Global Filters")
    
    # Platform selector
    platform = st.sidebar.selectbox(
        "�� Social Platform",
        ["All Platforms", "GA4", "Twitter/X", "Facebook/Meta"],
        key="global_platform"
    )
    
    # Time range selector
    today = date.today()
    time_options = {
        "Past Day": (today - timedelta(days=1), today),
        "This Week": (today - timedelta(days=today.weekday()), today),
        "Last 7 Days": (today - timedelta(days=7), today),
        "Last 30 Days": (today - timedelta(days=30), today),
        "Last 60 Days": (today - timedelta(days=60), today),
        "Last 90 Days": (today - timedelta(days=90), today),
    }
    
    selected_range = st.sidebar.selectbox(
        "📅 Time Range",
        list(time_options.keys()),
        key="global_time_range"
    )
    
    start_date, end_date = time_options[selected_range]
    
    # Show selected range
    st.sidebar.info(f"📊 Analyzing: {start_date} to {end_date}")
    
    # Setup/Onboarding trigger
    st.sidebar.markdown("---")
    if st.sidebar.button("�� Reconnect Accounts", key="reconnect_accounts"):
        st.session_state["show_onboarding"] = True
        st.rerun()
    
    return platform, start_date, end_date

def filter_data_by_platform(data: list, platform: str) -> list:
    """
    Filter data by selected platform.
    
    Args:
        data: List of data dictionaries
        platform: Selected platform ("All Platforms", "GA4", etc.)
    
    Returns:
        Filtered data list
    """
    if platform == "All Platforms":
        return data
    
    platform_mapping = {
        "GA4": "ga4",
        "Twitter/X": "twitter", 
        "Facebook/Meta": "meta"
    }
    
    target_platform = platform_mapping.get(platform, platform.lower())
    return [item for item in data if item.get("platform") == target_platform] 