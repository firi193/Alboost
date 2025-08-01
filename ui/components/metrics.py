import streamlit as st

def render_metric_card(title: str, value: str, delta: str = None, delta_color: str = "normal"):
    """
    Render a metric card with title, value, and optional delta.
    
    Args:
        title: Metric title
        value: Metric value
        delta: Optional delta value (e.g., "+5.2%")
        delta_color: Delta color ("normal", "inverse", "off")
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def render_kpi_row(metrics: dict):
    """
    Render a row of KPI cards.
    
    Args:
        metrics: Dictionary of {title: value} pairs
    """
    cols = st.columns(len(metrics))
    for idx, (title, value) in enumerate(metrics.items()):
        with cols[idx]:
            render_metric_card(title, value)

def render_section_header(title: str, icon: str = "📊"):
    """
    Render a consistent section header.
    
    Args:
        title: Section title
        icon: Emoji icon
    """
    st.markdown(f"### {icon} {title}")
    st.markdown("---") 