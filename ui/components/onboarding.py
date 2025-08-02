import streamlit as st

def render_onboarding_modal():
    """
    Render onboarding modal when triggered.
    """
    if st.session_state.get("show_onboarding", False):
        st.markdown("## 👋 Welcome to Alboost - Your AI Campaign Assistant!")
        st.info("Let's set up your account to get started.")
        
        # Onboarding form
        with st.form("onboarding_form"):
            st.markdown("### 🏢 Business Information")
            brand_name = st.text_input("Brand Name")
            industry = st.selectbox("Industry", ["Skincare", "Fashion", "Tech", "Food", "Other"])
            
            st.markdown("### 🎯 Campaign Goals")
            campaign_objective = st.selectbox("Primary Objective", ["Awareness", "Engagement", "Conversion", "Retention"])
            channels = st.multiselect("Channels", ["Instagram", "TikTok", "Twitter", "Facebook", "Email", "Web"])
            
            st.markdown("### �� Target Audience")
            age_range = st.text_input("Age Range (e.g., 18-30)")
            location = st.text_input("Primary Location")
            
            submitted = st.form_submit_button("✨ Complete Setup")
            
            if submitted:
                # Save onboarding data
                st.session_state["onboarding_data"] = {
                    "brand_name": brand_name,
                    "industry": industry,
                    "campaign_objective": campaign_objective,
                    "channels": channels,
                    "age_range": age_range,
                    "location": location
                }
                st.session_state["show_onboarding"] = False
                st.success("✅ Setup completed! You can now use the app.")
                st.rerun()
        
        # Cancel button
        if st.button("❌ Cancel Setup"):
            st.session_state["show_onboarding"] = False
            st.rerun() 
