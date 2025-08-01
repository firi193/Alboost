import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import our components
from ui.components.ui_helpers import render_status_message
from ui.components.global_filters import render_global_filters
from ui.components.data_loader import load_json_with_platform, get_filtered_data

# Import tab modules
from ui.tabs.insights_tab import render_insights_tab
from ui.tabs.strategy_tab import render_strategy_tab
from ui.tabs.kpis_tab import render_kpis_tab
from ui.tabs.uploader_tab import render_uploader_tab

# Page config
st.set_page_config(
    page_title="Dashboard - AI Campaign Assistant", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 16px;
    font-weight: 500;
    color: #3D5AFE;
    border-bottom: 2px solid transparent;
}
.stTabs [data-baseweb="tab"]:hover {
    border-bottom: 2px solid #BBDEFB;
}
.stTabs [aria-selected="true"] {
    border-bottom: 2px solid #3D5AFE;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Main title
st.title("Alboost AI Campaign Assistant")
st.markdown("Manage your campaigns and analyze performance.")

# Check if user has completed onboarding
if "onboarding_id" not in st.session_state:
    st.warning("Please complete onboarding first.")
    st.stop()

# Global filters in sidebar
selected_platform, start_date, end_date = render_global_filters()

# Load all data once
@st.cache_data
def load_all_data():
    """Load all platform data and cache it."""
    try:
        ga4_data = load_json_with_platform("ui/mock_ga4_data.json", "ga4")
        meta_data = load_json_with_platform("ui/mock_meta_data.json", "meta")
        twitter_data = load_json_with_platform("ui/mock_twitter_data.json", "twitter")
        return ga4_data + meta_data + twitter_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return []

all_posts = load_all_data()

# Filter data based on global filters
filtered_posts = get_filtered_data(all_posts, selected_platform, start_date, end_date)

# Main tabs
tab1_insights, tab1_strategy, tab2, tab3 = st.tabs([
    "Campaign Insights", "Campaign Strategy", "Campaign KPIs", "File Uploader"
])

# Tab 1: Campaign Insights
with tab1_insights:
    render_insights_tab(filtered_posts, selected_platform, start_date, end_date)

# Tab 2: Campaign Strategy
with tab1_strategy:
    render_strategy_tab(filtered_posts, selected_platform, start_date, end_date)

# Tab 3: Campaign KPIs
with tab2:
    render_kpis_tab(filtered_posts, selected_platform, start_date, end_date)

# Tab 4: File Uploader
with tab3:
    render_uploader_tab() 