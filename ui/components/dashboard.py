# dashboard.py

import streamlit as st
import pandas as pd
from datetime import datetime
from workflows.core.utils.performance_analyzer import analyze_performance
from workflows.core.utils.kpi_normalizer import normalize_post
from ui.components.ui_helpers import render_metric_card, render_kpi_row

def render_social_media_dashboard(filtered_posts):
    """
    Render comprehensive social media dashboard using real KPI data.
    """
    if not filtered_posts:
        st.markdown("""
        <div style="background: white; 
                    border-radius: 12px; 
                    padding: 40px; 
                    text-align: center; 
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                    border: 1px solid #E9ECEF;">
            <h3 style="margin: 0; color: #6C757D;">No data available</h3>
            <p style="color: #6C757D; margin-top: 8px;">No posts found in the selected date range.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Normalize all posts first
    normalized_posts = []
    for post in filtered_posts:
        platform = post.get("platform", "unknown")
        try:
            normalized_post = normalize_post(post, platform)
            normalized_posts.append(normalized_post)
        except Exception as e:
            continue
    
    # Get performance analysis
    performance_data = analyze_performance(normalized_posts)
    
    # Row 1: KPI Cards
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Total Posts", str(performance_data["total_posts"]), icon="📝")
    with col2:
        render_metric_card("Avg Engagement", f"{performance_data['avg_engagement_rate']:.2f}%", icon="📈")
    with col3:
        total_reach = sum(p.get("reach", 0) for p in normalized_posts)
        render_metric_card("Total Reach", f"{total_reach:,}", icon="👥")
    with col4:
        render_metric_card("Avg Conversion", f"{performance_data['avg_conversion_rate']:.2f}%", icon="🎯")
    
    st.markdown("---")
    
    # Row 2: Charts
    st.markdown("###  Performance Trends")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Engagement Rate Over Time**")
        df = pd.DataFrame(normalized_posts)
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            engagement_trend = df.groupby('date')['engagement_rate'].mean()
            st.line_chart(engagement_trend)
    
    with col2:
        st.markdown("**Reach vs Impressions**")
        if not df.empty:
            reach_impressions = df.groupby('date').agg({
                'reach': 'sum',
                'impressions': 'sum'
            })
            st.line_chart(reach_impressions)
    
    st.markdown("---")
    
    # Row 3: Platform Comparison
    st.markdown("### 🎯 Platform Performance")
    platform_data = performance_data.get("platform_summary", {})
    if platform_data:
        platform_df = pd.DataFrame(platform_data).T
        st.bar_chart(platform_df['avg_engagement'])
    
    st.markdown("---")
    
    # Row 4: Top Posts
    st.markdown("### 🔥 Top Performing Posts")
    if normalized_posts:
        top_posts = sorted(normalized_posts, 
                          key=lambda x: x.get('engagement_rate', 0), 
                          reverse=True)[:10]
        
        top_posts_df = pd.DataFrame(top_posts)
        if not top_posts_df.empty:
            display_cols = ['platform', 'date', 'text', 'engagement_rate', 'reach', 'impressions']
            available_cols = [col for col in display_cols if col in top_posts_df.columns]
            
            st.dataframe(
                top_posts_df[available_cols].head(10),
                use_container_width=True
            )

# Keep the old function for backward compatibility
def render_dashboard():
    st.markdown("""
    <div style="background: white; 
                border-radius: 12px; 
                padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                border: 1px solid #E9ECEF; 
                margin-bottom: 16px;">
        <h3 style="margin: 0; color: #1A1A40;">Campaign KPIs (Legacy)</h3>
        <p style="color: #6C757D; margin: 8px 0 0 0;">This is the old dashboard with mock data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    import random
    metrics = {
        "CTR (%)": round(random.uniform(3, 7), 2),
        "Conversion Rate (%)": round(random.uniform(1, 4), 2),
        "Reach": random.randint(5000, 10000),
        "Engagement": random.randint(200, 800),
    }

    render_kpi_row(metrics)
