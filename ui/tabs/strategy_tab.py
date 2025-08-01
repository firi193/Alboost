import streamlit as st
import sys
import os
import json
from ui.components.ui_helpers import render_section_header, render_status_message, render_clean_button

def render_strategy_tab(filtered_posts, selected_platform, start_date, end_date):
    """Render the Campaign Strategy tab."""
    # render_section_header("Campaign Strategy", "")
    
    if len(filtered_posts) == 0:
        render_status_message(
            f"No posts found for {selected_platform} in the selected date range ({start_date} to {end_date}).",
            "warning"
        )
    else:
        if "research_results" in st.session_state:
            research_result = st.session_state["research_results"]
            
            if research_result.get("success"):
                if "campaign_plan" in research_result:
                    render_status_message("Campaign strategy ready!", "success")
                    
                    # Parse campaign plan - it might be a string or dict
                    campaign_plan = research_result.get("campaign_plan", {})
                    
                    # Debug: Show raw data
                    # with st.expander("Debug: Raw Campaign Plan Data", expanded=False):
                    #     st.json(campaign_plan)
                    
                    # If it's a string, try to parse it as JSON
                    if isinstance(campaign_plan, str):
                        try:
                            campaign_plan = json.loads(campaign_plan)
                        except json.JSONDecodeError:
                            # If it's not JSON, treat it as plain text
                            campaign_plan = {"summary": campaign_plan}
                    
                    # Display strategy in organized sections
                    with st.expander("Campaign Strategy", expanded=True):
                        # Top Priority Section
                        with st.expander("Top Priority", expanded=True):
                            top_priority = campaign_plan.get("top_priority", "")
                            if top_priority:
                                st.markdown("**Primary Focus Area:**")
                                st.write(top_priority)
                            else:
                                st.info("No top priority identified.")
                        
                        # Recommendations Section
                        with st.expander("Strategic Recommendations", expanded=True):
                            recommendations = campaign_plan.get("recommendations", [])
                            if recommendations:
                                st.markdown("**Key Strategic Recommendations:**")
                                for i, rec in enumerate(recommendations, 1):
                                    st.markdown(f"**{i}. {rec.get('focus', 'Focus Area')}**")
                                    st.markdown(f"*Insight:* {rec.get('insight', 'No insight provided')}")
                                    
                                    # Handle tactics - could be list or string
                                    tactics = rec.get('tactics', [])
                                    if tactics:
                                        st.markdown("*Tactics:*")
                                        if isinstance(tactics, list):
                                            for tactic in tactics:
                                                # Clean up the tactic text (remove quotes and brackets if present)
                                                clean_tactic = str(tactic).strip("'\"[]")
                                                st.markdown(f"  • {clean_tactic}")
                                        else:
                                            # If it's a string, split by commas or display as is
                                            if ',' in str(tactics):
                                                for tactic in str(tactics).split(','):
                                                    clean_tactic = tactic.strip("'\"[] ")
                                                    st.markdown(f"  • {clean_tactic}")
                                            else:
                                                st.markdown(f"  • {tactics}")
                                    else:
                                        st.markdown("*Tactics:* No tactics provided")
                                    
                                    st.markdown(f"*Expected Impact:* {rec.get('expected_impact', 'No impact assessment')}")
                                    st.markdown("---")
                            else:
                                st.info("No strategic recommendations available.")
                        
                        # Content Themes Section
                        with st.expander("Content Themes", expanded=True):
                            content_themes = campaign_plan.get("content_themes", [])
                            if content_themes:
                                st.markdown("**Recommended Content Themes:**")
                                if isinstance(content_themes, list):
                                    for theme in content_themes:
                                        st.markdown(f"• {theme}")
                                else:
                                    st.write(content_themes)
                            else:
                                st.info("No content themes identified.")
                        
                        # Captions Section
                        with st.expander("Caption Strategy", expanded=True):
                            captions = campaign_plan.get("captions", [])
                            if captions:
                                st.markdown("**Caption Recommendations:**")
                                if isinstance(captions, list):
                                    for caption in captions:
                                        st.markdown(f"• {caption}")
                                else:
                                    st.write(captions)
                            else:
                                st.info("No caption strategy available.")
                        
                        # Hashtags Section
                        with st.expander("Suggested Hashtags", expanded=True):
                            hashtags = campaign_plan.get("hashtags", [])
                            if hashtags:
                                st.markdown("**Recommended Hashtags:**")
                                if isinstance(hashtags, list):
                                    for hashtag in hashtags:
                                        st.markdown(f"• {hashtag}")
                                else:
                                    st.write(hashtags)
                            else:
                                st.info("No hashtag strategy available.")
                        
                        # Tone & Style Section
                        with st.expander("Tone & Style", expanded=True):
                            tone_style = campaign_plan.get("tone_style_summary", "")
                            if tone_style:
                                st.markdown("**Recommended Tone & Style:**")
                                st.write(tone_style)
                            else:
                                st.info("No tone and style guidance available.")
                        
                        # Collaborations Section
                        with st.expander("Collaboration Opportunities", expanded=True):
                            collaborations = campaign_plan.get("optional_collaborations", [])
                            if collaborations:
                                st.markdown("**Potential Collaboration Opportunities:**")
                                if isinstance(collaborations, list):
                                    for collab in collaborations:
                                        st.markdown(f"• {collab}")
                                else:
                                    st.write(collaborations)
                            else:
                                st.info("No collaboration opportunities identified.")
                        
                        # Timeline Section
                        with st.expander("Implementation Timeline", expanded=True):
                            timeline = campaign_plan.get("timeline", "")
                            if timeline:
                                st.markdown("**Recommended Timeline:**")
                                if isinstance(timeline, dict):
                                    for period, action in timeline.items():
                                        st.markdown(f"**{period.replace('_', ' ').title()}:** {action}")
                                else:
                                    st.write(timeline)
                            else:
                                st.info("No timeline available.")
                
                else:
                    render_status_message("Generating campaign strategy from existing insights...", "info")
                    with st.spinner("Creating campaign strategy..."):
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
                                type="plan"
                            )
                            
                            if research_result.get("success"):
                                render_status_message("Campaign strategy generated!", "success")
                                
                                # Parse and display the new campaign plan
                                campaign_plan = research_result.get("campaign_plan", {})
                                
                                # Debug: Show raw data
                                with st.expander("Debug: Raw Campaign Plan Data", expanded=False):
                                    st.json(campaign_plan)
                                
                                # If it's a string, try to parse it as JSON
                                if isinstance(campaign_plan, str):
                                    try:
                                        campaign_plan = json.loads(campaign_plan)
                                    except json.JSONDecodeError:
                                        campaign_plan = {"summary": campaign_plan}
                                
                                # Display strategy in organized sections
                                with st.expander("Campaign Strategy", expanded=True):
                                    # Top Priority Section
                                    with st.expander("Top Priority", expanded=True):
                                        top_priority = campaign_plan.get("top_priority", "")
                                        if top_priority:
                                            st.markdown("**Primary Focus Area:**")
                                            st.write(top_priority)
                                        else:
                                            st.info("No top priority identified.")
                                    
                                    # Recommendations Section
                                    with st.expander("Strategic Recommendations", expanded=True):
                                        recommendations = campaign_plan.get("recommendations", [])
                                        if recommendations:
                                            st.markdown("**Key Strategic Recommendations:**")
                                            for i, rec in enumerate(recommendations, 1):
                                                st.markdown(f"**{i}. {rec.get('focus', 'Focus Area')}**")
                                                st.markdown(f"*Insight:* {rec.get('insight', 'No insight provided')}")
                                                
                                                # Handle tactics - could be list or string
                                                tactics = rec.get('tactics', [])
                                                if tactics:
                                                    st.markdown("*Tactics:*")
                                                    if isinstance(tactics, list):
                                                        for tactic in tactics:
                                                            # Clean up the tactic text (remove quotes and brackets if present)
                                                            clean_tactic = str(tactic).strip("'\"[]")
                                                            st.markdown(f"  • {clean_tactic}")
                                                    else:
                                                        # If it's a string, split by commas or display as is
                                                        if ',' in str(tactics):
                                                            for tactic in str(tactics).split(','):
                                                                clean_tactic = tactic.strip("'\"[] ")
                                                                st.markdown(f"  • {clean_tactic}")
                                                        else:
                                                            st.markdown(f"  • {tactics}")
                                                else:
                                                    st.markdown("*Tactics:* No tactics provided")
                                                
                                                st.markdown(f"*Expected Impact:* {rec.get('expected_impact', 'No impact assessment')}")
                                                st.markdown("---")
                                        else:
                                            st.info("No strategic recommendations available.")
                                    
                                    # Content Themes Section
                                    with st.expander("Content Themes", expanded=True):
                                        content_themes = campaign_plan.get("content_themes", [])
                                        if content_themes:
                                            st.markdown("**Recommended Content Themes:**")
                                            if isinstance(content_themes, list):
                                                for theme in content_themes:
                                                    st.markdown(f"• {theme}")
                                            else:
                                                st.write(content_themes)
                                        else:
                                            st.info("No content themes identified.")
                                    
                                    # Captions Section
                                    with st.expander("Caption Strategy", expanded=True):
                                        captions = campaign_plan.get("captions", [])
                                        if captions:
                                            st.markdown("**Caption Recommendations:**")
                                            if isinstance(captions, list):
                                                for caption in captions:
                                                    st.markdown(f"• {caption}")
                                            else:
                                                st.write(captions)
                                        else:
                                            st.info("No caption strategy available.")
                                    
                                    # Hashtags Section
                                    with st.expander("Suggested Hashtags", expanded=True):
                                        hashtags = campaign_plan.get("hashtags", [])
                                        if hashtags:
                                            st.markdown("**Recommended Hashtags:**")
                                            if isinstance(hashtags, list):
                                                for hashtag in hashtags:
                                                    st.markdown(f"• {hashtag}")
                                            else:
                                                st.write(hashtags)
                                        else:
                                            st.info("No hashtag strategy available.")
                                    
                                    # Tone & Style Section
                                    with st.expander("Tone & Style", expanded=True):
                                        tone_style = campaign_plan.get("tone_style_summary", "")
                                        if tone_style:
                                            st.markdown("**Recommended Tone & Style:**")
                                            st.write(tone_style)
                                        else:
                                            st.info("No tone and style guidance available.")
                                    
                                    # Collaborations Section
                                    with st.expander("Collaboration Opportunities", expanded=True):
                                        collaborations = campaign_plan.get("optional_collaborations", [])
                                        if collaborations:
                                            st.markdown("**Potential Collaboration Opportunities:**")
                                            if isinstance(collaborations, list):
                                                for collab in collaborations:
                                                    st.markdown(f"• {collab}")
                                            else:
                                                st.write(collaborations)
                                        else:
                                            st.info("No collaboration opportunities identified.")
                                    
                                    # Timeline Section
                                    with st.expander("Implementation Timeline", expanded=True):
                                        timeline = campaign_plan.get("timeline", "")
                                        if timeline:
                                            st.markdown("**Recommended Timeline:**")
                                            if isinstance(timeline, dict):
                                                for period, action in timeline.items():
                                                    st.markdown(f"**{period.replace('_', ' ').title()}:** {action}")
                                            else:
                                                st.write(timeline)
                                        else:
                                            st.info("No timeline available.")
                                
                                st.session_state["research_results"]["campaign_plan"] = research_result.get("campaign_plan", "")
                            else:
                                render_status_message(
                                    f"Strategy generation failed: {research_result.get('error', 'Unknown error')}", 
                                    "error"
                                )
                            
                        except Exception as e:
                            render_status_message(f"Error generating strategy: {str(e)}", "error")
            else:
                render_status_message("No valid research data available", "error")
        else:
            render_status_message(
                "Complete the research in the Campaign Insights tab first to generate your strategy.", 
                "info"
            ) 