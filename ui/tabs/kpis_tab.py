import streamlit as st
from ui.components.ui_helpers import render_section_header, render_status_message

def render_kpis_tab(filtered_posts, selected_platform, start_date, end_date):
    """Render the Campaign KPIs tab."""
    render_section_header("Performance Dashboard", "")
    
    if len(filtered_posts) > 0:
        from ui.components.dashboard import render_social_media_dashboard
        render_social_media_dashboard(filtered_posts)
    else:
        render_status_message(
            f"No posts found for {selected_platform} in the selected date range ({start_date} to {end_date}).",
            "warning"
        )
        
        # Fallback to mock data
        render_status_message("Showing mock data instead:", "info")
        from ui.components.dashboard import render_dashboard
        render_dashboard()
