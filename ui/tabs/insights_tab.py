import streamlit as st
import sys
import os
import json
from ui.components.ui_helpers import render_section_header, render_status_message, render_clean_button

def render_insights_tab(filtered_posts, selected_platform, start_date, end_date):
    """Render the Campaign Insights tab."""
    # render_section_header("Campaign Insights", "")
    
    if len(filtered_posts) == 0:
        render_status_message(
            f"No posts found for {selected_platform} in the selected date range ({start_date} to {end_date}).",
            "warning"
        )
    else:
        render_status_message(f"Analyzing {len(filtered_posts)} posts from {selected_platform}", "success")
        
        if "onboarding_id" in st.session_state:
            # Remove the column constraint - use full width
            if render_clean_button("Generate Comprehensive Insights", "generate_insights", use_container_width=True):
                with st.spinner("Conducting comprehensive research with Qloo insights..."):
                    try:
                        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
                        from workflows.core.researcher_agent import ResearcherAgent
                        
                        researcher = ResearcherAgent(
                            name="streamlit_researcher",
                            initial_state={},
                            context={}
                        )
                        
                        research_result = researcher.generate_strategic_analysis_and_plan(
                            onboarding_id=st.session_state["onboarding_id"],
                            performance_data=filtered_posts,
                            type="insights"
                        )
                        
                        if research_result.get("success"):
                            render_status_message("Comprehensive research completed!", "success")
                            
                            # Parse campaign insights - it might be a string or dict
                            campaign_insights = research_result.get("campaign_insights", {})
                            
                            # If it's a string, try to parse it as JSON
                            if isinstance(campaign_insights, str):
                                try:
                                    campaign_insights = json.loads(campaign_insights)
                                except json.JSONDecodeError:
                                    # If it's not JSON, treat it as plain text
                                    campaign_insights = {"summary": campaign_insights}
                            
                            # Display insights in organized sections
                            with st.expander("Campaign Insights", expanded=True):
                                # Key Insights Section
                                with st.expander("Key Insights", expanded=True):
                                    key_insights = campaign_insights.get("key_insights", [])
                                    if key_insights:
                                        st.markdown("**Key findings from your campaign analysis:**")
                                        for insight in key_insights:
                                            st.markdown(f"• {insight}")
                                    else:
                                        st.info("No key insights available.")
                                
                                # Audience Trends Section
                                with st.expander("Audience Trends", expanded=True):
                                    audience_trends = campaign_insights.get("audience_trends", [])
                                    if audience_trends:
                                        st.markdown("**Trends in your audience behavior:**")
                                        for trend in audience_trends:
                                            st.markdown(f"• {trend}")
                                    else:
                                        st.info("No audience trends available.")
                                
                                # Performance Drivers Section
                                with st.expander("Performance Drivers", expanded=True):
                                    performance_drivers = campaign_insights.get("performance_drivers", [])
                                    if performance_drivers:
                                        st.markdown("**Factors driving your campaign success:**")
                                        for driver in performance_drivers:
                                            st.markdown(f"• {driver}")
                                    else:
                                        st.info("No performance drivers identified.")
                                
                                # Blind Spots Section
                                with st.expander("Blind Spots", expanded=True):
                                    blindspots = campaign_insights.get("blindspots", [])
                                    if blindspots:
                                        st.markdown("**Areas that need attention:**")
                                        for spot in blindspots:
                                            st.markdown(f"• {spot}")
                                    else:
                                        st.info("No blind spots identified.")
                                
                                # Summary Section
                                with st.expander("Summary", expanded=True):
                                    summary = campaign_insights.get("summary", "")
                                    if summary:
                                        st.markdown("**Campaign Overview:**")
                                        st.write(summary)
                                    else:
                                        st.info("No summary available.")
                            
                            with st.expander("Performance Analysis"):
                                st.text(research_result.get("performance_analysis", ""))
                            
                            st.session_state["research_results"] = research_result
                            
                        else:
                            render_status_message(
                                f"Research failed: {research_result.get('error', 'Unknown error')}", 
                                "error"
                            )
                            
                    except Exception as e:
                        render_status_message(f"Error during research: {str(e)}", "error")
                        render_status_message(
                            "Make sure all environment variables are set (QLOO_API_KEY, etc.)", 
                            "info"
                        )
        else:
            render_status_message("Complete onboarding to generate insights.", "info")