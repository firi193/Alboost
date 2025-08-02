# streamlit_app.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import requests
import json
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import pandas as pd
import docx
from google_auth_oauthlib.flow import Flow
try:
    from ga4_utils import get_user_properties
    GOOGLE_ANALYTICS_AVAILABLE = True
except ImportError:
    GOOGLE_ANALYTICS_AVAILABLE = False
    def get_user_properties(credentials):
        return []
import plotly.express as px
from urllib.parse import urlencode

# Import our components
from ui.components.ui_helpers import render_status_message, render_onboarding_card
from ui.components.global_filters import render_global_filters
from ui.components.data_loader import load_json_with_platform, get_filtered_data

# Import database functions
try:
    try:
        from workflows.server.db.onboarding_db import save_onboarding_data
    except ImportError:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'workflows', 'server', 'db'))
        from onboarding_db import save_onboarding_data
except ImportError as e:
    print(f"Database import error: {e}")
    def save_onboarding_data(**kwargs):
        return {
            "success": False, 
            "error": "Database module not available",
            "message": "Database module not available"
        }

# Load environment variables
load_dotenv()
api_key = os.getenv("VULTR_API_KEY")
collection_name = os.getenv("VULTR_COLLECTION_NAME")
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

def extract_text_from_file(file):
    if file.type == "application/pdf":
        pdf = PdfReader(file)
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif file.type in ["text/plain"]:
        content = file.read().decode("utf-8")
        return content
    elif file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return "Unsupported file type."

# Page config
st.set_page_config(
    page_title="AI Campaign Assistant", 
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
# st.title("AI Campaign Assistant")
# st.markdown("Plan, generate, and deploy marketing content with AI agents.")

# Check if user has completed onboarding
if "onboarding_id" in st.session_state:
    # User has completed onboarding, redirect to dashboard
    st.success("Welcome back! You're all set up.")
    
    # Add navigation to dashboard
    if st.button("Go to Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")
    
    # Show a preview of what's available
    st.markdown("### What's Available:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Campaign Insights**")
        st.markdown("Generate AI-powered insights from your data")
    
    with col2:
        st.markdown("**Campaign Strategy**")
        st.markdown("Create strategic campaign plans")
    
    with col3:
        st.markdown("**Performance KPIs**")
        st.markdown("Analyze your campaign performance")
    
    st.markdown("---")
    st.markdown("Click 'Go to Dashboard' to access all features.")

else:
    # Show onboarding
    render_onboarding_card()
    
    with st.expander("Complete Onboarding", expanded=True):
        with st.form("onboarding_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Business & Brand")
                brand_name = st.text_input("Brand Name")
                industry = st.selectbox("Industry", ["Skincare", "Fashion", "Tech", "Food", "Other"])
                product = st.text_input("Core Product/Service")
                voice = st.text_area("Brand Voice")
                aesthetic = st.text_area("Visual Aesthetic")
            
            with col2:
                st.markdown("### Campaign & Audience")
                campaign_objective = st.selectbox("Objective", ["Awareness", "Engagement", "Conversion", "Retention"])
                campaign_type = st.selectbox("Campaign Type", ["New product launch", "Seasonal promo", "Rebrand", "Other"])
                urgency = st.selectbox("Timeline", ["High", "Medium", "Low"])
                channels = st.multiselect("Channels", ["Instagram", "TikTok", "SEO", "Email", "Web", "Influencers"])
                
                st.markdown("### Audience Profile")
                age_range = st.text_input("Age Range")
                location = st.text_input("Location")
                values = st.text_area("Values")
                interests = st.text_area("Interests")
            
            submitted = st.form_submit_button("Complete Onboarding", use_container_width=True)
            
            if submitted:
                onboarding_data = {
                    "brand_name": brand_name, "industry": industry, "product": product,
                    "voice": voice, "aesthetic": aesthetic, "campaign_objective": campaign_objective,
                    "campaign_type": campaign_type, "urgency": urgency, "channels": list(channels),
                    "age_range": age_range, "location": location, "values": values, "interests": interests
                }
                
                with st.spinner("Saving your onboarding information..."):
                    result = save_onboarding_data(**onboarding_data)
                    
                    if result.get("success"):
                        render_status_message("Onboarding completed successfully!", "success")
                        if "id" in result:
                            st.session_state["onboarding_id"] = result["id"]
                        
                        # Show success message
                        st.success("Setup complete! You can now access the dashboard.")
                        # Set a flag to show navigation button outside form
                        st.session_state["show_dashboard_nav"] = True
                    else:
                        render_status_message(result.get('message', 'Unknown error occurred'), "error")

# Add navigation button outside the form context
if st.session_state.get("show_dashboard_nav", False):
    st.markdown("---")
    if st.button("Go to Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")
    # Clear the flag after showing the button
    st.session_state["show_dashboard_nav"] = False
