from typing import Dict, List
from .agent_base import AgentBase
from .utils.qloo_utils import (
    generate_campaign_insights, 
    gpt_extract_audience_signals, 
    generate_campaign_plan, 
    get_insights,
    run_full_campaign_generator
)
import requests
import json
import re
from dotenv import load_dotenv
import os
import sys

# Add the server/db path to import database functions
try:
    # Try multiple import paths
    try:
        from workflows.server.db.onboarding_db import get_onboarding_data
    except ImportError:
        # Try relative import
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'server', 'db')
        sys.path.append(db_path)
        from onboarding_db import get_onboarding_data
except ImportError:
    print("Warning: Could not import onboarding_db module")
    get_onboarding_data = None

class ResearcherAgent(AgentBase):
    def __init__(self, name: str, initial_state: dict, context: dict = None):
        super().__init__(name, initial_state, context)
        self.research_methods = {
            'web_search': True,
            'social_media_trends': True,
            'competitor_analysis': True
        }

    def get_onboarding_profile(self, onboarding_id: str = None) -> Dict:
        """
        Fetch onboarding data from database and format it for research.
        
        Args:
            onboarding_id (str): Specific onboarding ID to fetch. If None, gets the latest.
            
        Returns:
            Dict: Formatted onboarding data for research
        """
        if not get_onboarding_data:
            return {
                "audience_profile": "No onboarding data available",
                "product_description": "No product information available",
                "campaign_goal": "No campaign goal specified"
            }
        
        try:
            # Get onboarding data from database
            if onboarding_id:
                data = get_onboarding_data(onboarding_id)
                if not data:
                    return {"error": f"No onboarding data found for ID: {onboarding_id}"}
            else:
                # Get the latest onboarding data
                all_data = get_onboarding_data()
                if not all_data:
                    return {"error": "No onboarding data found in database"}
                data = all_data[0]  # Get the most recent
            
            # Format the data for research
            audience_profile = f"""
            Age Range: {data.age_range or 'Not specified'}
            Location: {data.location or 'Not specified'}
            Gender: {data.gender or 'Not specified'}
            Values: {data.values or 'Not specified'}
            Interests: {data.interests or 'Not specified'}
            Behavior: {data.behavior or 'Not specified'}
            """
                        
            product_description = f"""
            Brand: {data.brand_name or 'Not specified'}
            Industry: {data.industry or 'Not specified'}
            Product/Service: {data.product or 'Not specified'}
            Brand Voice: {data.voice or 'Not specified'}
            Visual Aesthetic: {data.aesthetic or 'Not specified'}
            """
                        
            campaign_goal = f"""
            Objective: {data.campaign_objective or 'Not specified'}
            Campaign Type: {data.campaign_type or 'Not specified'}
            Urgency: {data.urgency or 'Not specified'}
            Channels: {', '.join(data.channels) if data.channels else 'Not specified'}
            """
            
            return {
                "audience_profile": audience_profile,
                "product_description": product_description,
                "campaign_goal": campaign_goal,
                "onboarding_id": data.id,
                "raw_data": data
            }
            
        except Exception as e:
            self.log_event("onboarding_fetch_error", {"error": str(e)})
            return {"error": f"Failed to fetch onboarding data: {str(e)}"}

    def conduct_research(self, topic: str) -> Dict:
        """
        Conduct research on a given topic using RAG (Retrieval-Augmented Generation).
        
        Args:
            topic (str): Topic to research
            
        Returns:
            Dict: Research findings including summary and key points
        """
        load_dotenv()

        collection_name = os.getenv("VULTR_COLLECTION_NAME", "alboostcollect")
        vultr_api_key = os.getenv("VULTR_API_KEY")

        vultr_llm_model = "llama-3.3-70b-instruct-fp8"  # or use another supported Vultr model

        headers = {
            "Authorization": f"Bearer {vultr_api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a marketing research assistant. "
                    "Your job is to analyze campaign topics using relevant context and deliver concise insights."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Research the topic: '{topic}'.\n"
                    "Use context from the collection to:\n"
                    "- Write a 3–5 sentence summary of the topic\n"
                    "- Extract 3 key insights\n\n"
                    "Respond ONLY in JSON format with keys: 'summary' and 'key_points'."
                )
            }
        ]

        payload = {
            "collection": collection_name,
            "model": vultr_llm_model,
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        try:
            response = requests.post(
                "https://api.vultrinference.com/v1/chat/completions/RAG",
                headers=headers,
                data=json.dumps(payload),
                timeout=200
            )

            if response.status_code == 200 or 201:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Extract JSON portion from the LLM output
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    parsed = json.loads(json_str)
                else:
                    raise ValueError("No JSON object found in LLM response.")
                
                # seed_signals = gpt_extract_audience_signals(parsed.get("summary", ""))
                

                summary = parsed.get("summary", "")
                key_points = parsed.get("key_points", [])

            else:
                self.log_event("rag_failure", {
                    "status": response.status_code,
                    "error": response.text
                })
                summary = "RAG request failed."
                key_points = ["No insights generated due to error."]

        except Exception as e:
            self.log_event("rag_exception", {"error": str(e)})
            print(f"[{self.name}] RAG Exception: {e}")
            summary = "Failed to generate research due to system error."
            key_points = ["Internal error occurred."]

        return {
            'topic': topic,
            'summary': summary,
            'key_points': key_points,
            'trends': {},
            'competitors': [],
            'sources': []
        }

    def conduct_comprehensive_research(self, onboarding_id: str = None, type: str = "insights") -> Dict:
        """
        Conduct comprehensive research using onboarding data and Qloo insights.
        
        Args:
            onboarding_id (str): Specific onboarding ID to use. If None, uses the latest.
            type (str): Type of output - "insights" or "plan"
            
        Returns:
            Dict: Comprehensive research findings including Qloo insights and/or campaign plan
        """
        try:
            # Step 1: Get onboarding profile
            print("onboarding_id:\n\n", onboarding_id)
            onboarding_data = self.get_onboarding_profile(onboarding_id)
            if "error" in onboarding_data:
                return {"error": onboarding_data["error"]}
            
            audience_profile = onboarding_data["audience_profile"]
            product_description = onboarding_data["product_description"]
            campaign_goal = onboarding_data["campaign_goal"]
            
            # Step 2: Extract audience signals from the profile
            combined_text = f"{audience_profile}\n{product_description}\n{campaign_goal}"
            seed_signals = gpt_extract_audience_signals(combined_text)
            
            # Step 3: Get Qloo insights
            try:
                qloo_api_key = os.getenv("QLOO_API_KEY")
                if not qloo_api_key:
                    raise Exception("QLOO_API_KEY not found in environment variables")
                
                qloo_result = get_insights(seed_signals, {
                    "x-api-key": qloo_api_key,
                    "Content-Type": "application/json"
                })
                
                # Unpack the tuple returned by get_insights
                selected_tags, selected_entities, trending_data, demographics_data = qloo_result
                
                # Create the qloo_data dictionary expected by generate_campaign_insights
                qloo_data = {
                    "selected_tags": selected_tags,
                    "selected_entities": selected_entities,
                    "trending_data": trending_data,
                    "demographics_data": demographics_data
                }
                
                onboarding_id = onboarding_data.get("onboarding_id")
                
                # Step 4: Generate campaign insights (always needed)
                campaign_insights = generate_campaign_insights(
                    audience_profile, 
                    product_description, 
                    qloo_data, 
                    seed_signals
                )
                
                # Step 5: Generate response based on type
                if type == "plan":
                    # Generate campaign plan from insights
                    campaign_plan = generate_campaign_plan(
                        audience_profile, 
                        product_description, 
                        campaign_insights
                    )
                    
                    return {
                        "success": True,
                        "onboarding_id": onboarding_id,
                        "audience_profile": audience_profile,
                        "product_description": product_description,
                        "campaign_goal": campaign_goal,
                        "seed_signals": seed_signals,
                        "campaign_insights": campaign_insights,  # Include insights too
                        "campaign_plan": campaign_plan,
                        "research_summary": f"Comprehensive research and campaign plan completed using onboarding data and Qloo insights"
                    }
                else:
                    # Default: return insights only
                    return {
                        "success": True,
                        "onboarding_id": onboarding_id,
                        "audience_profile": audience_profile,
                        "product_description": product_description,
                        "campaign_goal": campaign_goal,
                        "seed_signals": seed_signals,
                        "campaign_insights": campaign_insights,
                        "research_summary": f"Comprehensive research completed using onboarding data and Qloo insights"
                    }
                
            except Exception as qloo_error:
                self.log_event("qloo_research_error", {"error": str(qloo_error)})
                return {
                    "success": False,
                    "error": f"Qloo research failed: {str(qloo_error)}",
                    "onboarding_data": onboarding_data,
                    "partial_research": True
                }
                
        except Exception as e:
            self.log_event("comprehensive_research_error", {"error": str(e)})
            return {"error": f"Comprehensive research failed: {str(e)}"}


    def generate_strategic_analysis_and_plan(
        self,
        onboarding_id: str = None,
        performance_data: List[Dict] = None,
        type: str = "insights"
        ) -> Dict:
        """
        Generate strategic campaign analysis or plan:
        - "insights" → Analyze past performance + cultural insights
        - "plan" → Generate recommendations based on insights
        """
        from .utils.strategic_analyzer import (
            get_performance_summary,
            generate_strategic_recommendations,
            generate_campaign_insights,
        )

        # Step 1: Get Qloo insights (audience + culture)
        qloo_result = self.conduct_comprehensive_research(onboarding_id, type=type)

        # Step 2: Analyze performance
        performance_summary = get_performance_summary(performance_data or [])

        # Branch based on type
        if type == "insights":
            campaign_insights = generate_campaign_insights(
                performance_summary=performance_summary,
                qloo_insights=qloo_result.get("campaign_insights", "")
            )

            return {
                "success": True,
                "performance_analysis": performance_summary,
                "campaign_insights": campaign_insights
            }

        elif type == "plan":
            # Step 2a: Always generate insights first before strategy
            campaign_insights = generate_campaign_insights(
                performance_summary=performance_summary,
                qloo_insights=qloo_result.get("campaign_insights", "")
            )

            campaign_plan = generate_strategic_recommendations(
                campaign_insights=campaign_insights,
                audience_profile=qloo_result.get("audience_profile", ""),
                product_description=qloo_result.get("product_description", "")
            )

            return {
                "success": True,
                "performance_analysis": performance_summary,
                "campaign_plan": campaign_plan
            }

        else:
            return {
                "success": False,
                "error": f"Unknown type: {type}. Use 'insights' or 'plan'."
            }



    def receive_message(self, sender: str, message: dict) -> None:
        if message.get('type') != 'task':
            return

        task = message['content']
        task_type = task.get('type')

        if task_type == 'goal':
            topic = task.get('content', '')
            findings = self.conduct_research(topic)

            # Send to strategist agent
            self.send_message('strategist', {
                'type': 'task',
                'content': {
                    'type': 'strategy_request',
                    'goal': topic,
                    'research_data': findings
                }
            })

            self.log_event('research_completed')
        elif task_type == 'comprehensive_research':
            # New task type for comprehensive research using onboarding data
            onboarding_id = task.get('onboarding_id')
            findings = self.conduct_comprehensive_research(onboarding_id)

            # Send comprehensive research to strategist agent
            self.send_message('strategist', {
                'type': 'task',
                'content': {
                    'type': 'comprehensive_strategy_request',
                    'research_data': findings,
                    'onboarding_id': onboarding_id
                }
            })

            self.log_event('comprehensive_research_completed', {
                'onboarding_id': onboarding_id,
                'success': findings.get('success', False)
            })
        elif task_type == 'research_request':
            result = self.act(task)
            self.log_event('research_request', {'status': result['status']})
        else:
            self.log_event('invalid_task_type', {'type': task_type})
