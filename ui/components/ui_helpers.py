import streamlit as st

def render_section_header(title: str, icon: str = ""):
    """Render a clean section header."""
    st.markdown(f"### {icon} {title}")
    st.markdown("---")

def render_status_message(message: str, message_type: str = "info"):
    """Render consistent status messages."""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "💡"
    }
    
    colors = {
        "success": "#d4edda",
        "error": "#f8d7da",
        "warning": "#fff3cd",
        "info": "#d1ecf1"
    }
    
    icon = icons.get(message_type, "💡")
    color = colors.get(message_type, "#d1ecf1")
    
    st.markdown(f"""
    <div style="background-color: {color}; 
                border-radius: 8px; 
                padding: 12px 16px; 
                margin: 12px 0; 
                border-left: 4px solid #3D5AFE;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 16px;">{icon}</span>
            <span style="font-weight: 500;">{message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_onboarding_card():
    """Render the onboarding trigger card."""
    st.markdown("""
    <div style="background: white; 
                border-radius: 12px; 
                padding: 3rem 2rem; 
                text-align: center; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                border: 1px solid #E9ECEF; 
                margin-bottom: 16px;">
        <h2 style="margin-bottom: 1rem; color: #1A1A40;">🚀 Welcome to Alboost - AI Campaign Assistant</h2>
        <p style="color: #6C757D; margin-bottom: 2rem;">
            Complete onboarding to unlock AI-powered campaign insights and strategy generation.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(title: str, value: str, delta: str = None, icon: str = ""):
    """Render a professional metric card."""
    st.markdown(f"""
    <div style="background: white; 
                border-radius: 12px; 
                padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                border: 1px solid #E9ECEF; 
                margin-bottom: 16px;">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 20px; margin-right: 8px;">{icon}</span>
            <span style="font-size: 14px; color: #6C757D; font-weight: 500;">{title}</span>
        </div>
        <div style="font-size: 28px; font-weight: 700; color: #1A1A40;">{value}</div>
        {f'<div style="color: #28a745; font-size: 14px; font-weight: 500; margin-top: 4px;">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def render_kpi_row(metrics_dict: dict):
    """Render a row of KPI cards."""
    cols = st.columns(len(metrics_dict))
    icons = ["📊", "📈", "", "🎯", "", ""]
    
    for idx, (title, value) in enumerate(metrics_dict.items()):
        with cols[idx]:
            icon = icons[idx % len(icons)]
            render_metric_card(title, value, icon=icon)

def add_spacing():
    """Add consistent spacing."""
    st.write("")
    st.write("")

def render_clean_button(text: str, key: str = None, use_container_width: bool = False):
    """Render a clean, consistent button."""
    return st.button(
        text, 
        key=key, 
        use_container_width=use_container_width,
        help="Click to proceed"
    )

def render_clean_selectbox(label: str, options: list, key: str = None):
    """Render a clean selectbox."""
    return st.selectbox(
        label,
        options=options,
        key=key,
        help=f"Select {label.lower()}"
    ) 
