import streamlit as st

def render_metric_card(title: str, value: str, delta: str = None, delta_color: str = "normal"):
    """
    Render a metric card with optional delta.
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def render_kpi_row(metrics_dict: dict):
    """
    Render a row of KPI cards.
    """
    cols = st.columns(len(metrics_dict))
    for idx, (title, value) in enumerate(metrics_dict.items()):
        with cols[idx]:
            render_metric_card(title, value) 