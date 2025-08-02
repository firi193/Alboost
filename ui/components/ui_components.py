import streamlit as st
from datetime import date, timedelta

def render_metric_card(title: str, value: str, delta: str = None, icon: str = "📊"):
    """
    Render a professional metric card.
    """
    st.markdown(f"""
    <div class="metric-container">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
            <span class="metric-label">{title}</span>
        </div>
        <div class="metric-value">{value}</div>
        {f'<div style="color: #28a745; font-size: 0.875rem; font-weight: 500;">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def render_kpi_row(metrics_dict: dict):
    """
    Render a row of KPI cards.
    """
    cols = st.columns(len(metrics_dict))
    icons = ["📊", "📈", "👥", "🎯", "💰", "��"]
    
    for idx, (title, value) in enumerate(metrics_dict.items()):
        with cols[idx]:
            icon = icons[idx % len(icons)]
            render_metric_card(title, value, icon=icon)

def render_time_range_selector():
    """
    Render a professional time range selector.
    """
    st.markdown("### �� Time Range")
    
    today = date.today()
    max_past_date = today - timedelta(days=90)
    
    range_options = {
        "Past Day": (today - timedelta(days=1), today),
        "This Week": (today - timedelta(days=today.weekday()), today),
        "Last 7 Days": (today - timedelta(days=7), today),
        "Last 30 Days": (today - timedelta(days=30), today),
        "Last 60 Days": (today - timedelta(days=60), today),
        "Last 90 Days": (today - timedelta(days=90), today),
        "Custom Range": None
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_range = st.selectbox(
            "Select Time Range",
            options=list(range_options.keys()),
            key="time_range_selector"
        )
    
    if selected_range == "Custom Range":
        with col2:
            start_date, end_date = st.date_input(
                "Custom Range",
                value=(today - timedelta(days=7), today),
                min_value=max_past_date,
                max_value=today,
                key="custom_date_range"
            )
    else:
        start_date, end_date = range_options[selected_range]
        with col2:
            st.markdown(f"**{start_date}** to **{end_date}**")
    
    return start_date, end_date

def render_platform_selector():
    """
    Render a professional platform selector.
    """
    st.markdown("### 🎯 Platform")
    
    platform_options = {
        "All Platforms": "all",
        "GA4": "ga4", 
        "Instagram/Meta": "meta",
        "Twitter/X": "twitter"
    }
    
    selected_platform = st.selectbox(
        "Select Platform",
        options=list(platform_options.keys()),
        key="platform_selector"
    )
    
    return platform_options[selected_platform]

def render_filters_section():
    """
    Render the filters section in the main area.
    """
    st.markdown("""
    <div class="custom-card">
        <h3 style="margin-top: 0;">🔧 Filters</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        platform = render_platform_selector()
    
    with col2:
        start_date, end_date = render_time_range_selector()
    
    return platform, start_date, end_date

def render_onboarding_card():
    """
    Render the onboarding trigger card.
    """
    st.markdown("""
    <div class="custom-card" style="text-align: center; padding: 3rem 2rem;">
        <h2 style="margin-bottom: 1rem;">🚀 Welcome to Alboost - AI Campaign Assistant</h2>
        <p style="color: var(--text-secondary); margin-bottom: 2rem;">
            Complete onboarding to unlock AI-powered campaign insights and strategy generation.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_success_message(message: str, icon: str = "✅"):
    """
    Render a professional success message.
    """
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #d4edda, #c3e6cb); 
                border: 1px solid #c3e6cb; 
                border-radius: var(--border-radius); 
                padding: 1rem; 
                margin: 1rem 0;">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 1.25rem; margin-right: 0.5rem;">{icon}</span>
            <span style="color: #155724; font-weight: 500;">{message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_error_message(message: str, icon: str = "❌"):
    """
    Render a professional error message.
    """
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f8d7da, #f5c6cb); 
                border: 1px solid #f5c6cb; 
                border-radius: var(--border-radius); 
                padding: 1rem; 
                margin: 1rem 0;">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 1.25rem; margin-right: 0.5rem;">{icon}</span>
            <span style="color: #721c24; font-weight: 500;">{message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_info_message(message: str, icon: str = "💡"):
    """
    Render a professional info message.
    """
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #d1ecf1, #bee5eb); 
                border: 1px solid #bee5eb; 
                border-radius: var(--border-radius); 
                padding: 1rem; 
                margin: 1rem 0;">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 1.25rem; margin-right: 0.5rem;">{icon}</span>
            <span style="color: #0c5460; font-weight: 500;">{message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True) 
