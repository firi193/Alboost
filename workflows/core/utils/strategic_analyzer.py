from typing import Dict, List
from .performance_analyzer import analyze_performance
from .kpi_normalizer import normalize_post
import json
import requests
import os
import openai
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY_")

def call_openai_llm(prompt: str, model: str = "gpt-4", temperature: float = 0.7) -> str:
    """
    Call OpenAI LLM and extract JSON response.
    
    Args:
        prompt: The prompt to send
        model: Model to use (default: gpt-4)
        temperature: Creativity level (default: 0.7)
    
    Returns:
        str: Extracted JSON response
    """
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON portion from the LLM output
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            json_str = match.group(0)
            # Validate JSON
            json.loads(json_str)  # This will raise an error if invalid
            return json_str
        else:
            raise ValueError("No JSON object found in LLM response.")
            
    except Exception as e:
        print(f"OpenAI LLM call failed: {e}")
        return json.dumps({"error": f"LLM call failed: {str(e)}"})

def call_vultr_llm(prompt: str, model: str = "llama-3.3-70b-instruct-fp8", temperature: float = 0.7) -> str:
    """
    Call Vultr LLM and extract JSON response.
    
    Args:
        prompt: The prompt to send
        model: Model to use (default: llama-3.3-70b-instruct-fp8)
        temperature: Creativity level (default: 0.7)
    
    Returns:
        str: Extracted JSON response
    """
    try:
        vultr_api_key = os.getenv("VULTR_API_KEY")
        if not vultr_api_key:
            raise ValueError("VULTR_API_KEY not found in environment variables")

        headers = {
            "Authorization": f"Bearer {vultr_api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {
                "role": "system",
                "content": "You are a marketing strategist and analyst. Always respond with valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": temperature,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        response = requests.post(
            "https://api.vultrinference.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=200
        )

        if response.status_code in [200, 201]:
            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Extract JSON portion from the LLM output
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                json_str = match.group(0)
                # Validate JSON
                json.loads(json_str)  # This will raise an error if invalid
                return json_str
            else:
                raise ValueError("No JSON object found in LLM response.")
        else:
            raise Exception(f"Vultr API request failed with status {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Vultr LLM call failed: {e}")
        return json.dumps({"error": f"LLM call failed: {str(e)}"})

def get_performance_summary(posts: List[Dict], weeks: int = 6) -> Dict:
    """
    Get performance summary for the last N weeks.
    
    Args:
        posts: List of post data from various platforms
        weeks: Number of weeks to analyze (default 6)
    
    Returns:
        Dict: Performance summary with key metrics
    """
    # Filter posts from last N weeks
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    
    recent_posts = []
    for post in posts:
        # Normalize the post data first
        platform = post.get("platform", "unknown")
        print(f"\n\n\n\n\nPlatform: {platform}")
        normalized_post = normalize_post(post, platform)
        
        # Check if post is within date range
        post_date = normalized_post.get("date")
        if post_date:
            try:
                post_datetime = datetime.strptime(post_date, "%Y-%m-%d")
                if post_datetime >= cutoff_date:
                    recent_posts.append(normalized_post)
            except ValueError:
                # Skip posts with invalid dates
                continue
    
    # Use existing performance analyzer
    return analyze_performance(recent_posts)

def generate_campaign_insights(performance_summary: Dict, qloo_insights: str, use_vultr: bool = False) -> Dict:
    prompt = f"""
You're an expert campaign analyst combining data science and cultural intelligence.

Past weeks of campaign performance data:
{json.dumps(performance_summary, indent=2)}

Audience and cultural insights from Qloo:
{qloo_insights}

Analyze and synthesize these inputs. For each insight:
- Quantify impact (e.g., engagement %, conversion uplift)
- Cite specific examples of posts, audience segments, or content themes
- Link Qloo cultural insights directly to performance outcomes
- Identify emerging trends and missed growth opportunities
- Suggest clear, actionable recommendations for future campaigns

Return ONLY a valid JSON object with these keys:
- "key_insights": array of 3-5 precise insight statements with data references
- "audience_trends": array of 2-3 audience behaviors or preferences to prioritize
- "performance_drivers": array of 2-3 top contributors to engagement or reach
- "blindspots": array of 2-3 missed opportunities or underleveraged assets
- "recommendations": array of 2-3 tactical next steps to improve campaign impact
- "summary": brief 2-3 sentence overview highlighting key takeaways
"""

    try:
        if use_vultr:
            json_response = call_vultr_llm(prompt, temperature=0.6)
        else:
            json_response = call_openai_llm(prompt, temperature=0.6)
        
        result = json.loads(json_response)
        
        # Basic validation and fallback
        for key in ["key_insights", "audience_trends", "performance_drivers", "blindspots", "recommendations", "summary"]:
            if key not in result:
                result[key] = [] if key != "summary" else ""
        
        return result
        
    except Exception as e:
        print(f"Failed to generate campaign insights: {e}")
        return {
            "key_insights": ["Analysis failed - please check data quality"],
            "audience_trends": [],
            "performance_drivers": [],
            "blindspots": [],
            "recommendations": [],
            "summary": f"Error generating insights: {str(e)}"
        }





import json
from typing import Dict

def generate_strategic_recommendations(
    campaign_insights: Dict,
    qloo_campaign_plan: str = "",
    audience_profile: str = "",
    product_description: str = "",
    platform_trends: str = "",
    onboarding_info: str = "",
    use_vultr: bool = False
) -> Dict:
    """
    Generate strategic recommendations based on campaign insights.
    
    Args:
        campaign_insights: Output from generate_campaign_insights()
        qloo_campaign_plan: Qloo-generated campaign plan text
        audience_profile: Optional audience profile for context
        product_description: Optional product description for context
        platform_trends: Optional platform-specific trends
        onboarding_info: Optional onboarding/brand info
        use_vultr: Whether to use Vultr instead of OpenAI (default: False)
    
    Returns:
        Dict: Strategic recommendations and marketing assets
    """
    prompt = f"""
You're a marketing strategist. Create actionable recommendations and marketing assets based on the analysis below.

Campaign Analysis:
{json.dumps(campaign_insights, indent=2)}

{f"Qloo Campaign Plan: {qloo_campaign_plan}" if qloo_campaign_plan else ""}
{f"Audience Profile: {audience_profile}" if audience_profile else ""}
{f"Product Description: {product_description}" if product_description else ""}
{f"Platform Trends: {platform_trends}" if platform_trends else ""}
{f"Onboarding Info: {onboarding_info}" if onboarding_info else ""}

Leverage cultural insights from Qloo and platform trends to tailor campaign content and KPIs.

Generate the following:

1. 3 actionable strategic recommendations, each with:
    - Strategic focus area
    - Supporting insight
    - 3-5 specific tactics
    - Expected impact on key metrics

2. Top priority action to take immediately

3. 3-5 content themes to emphasize in the next campaign

4. Captions: 3-5 example social media captions that fit the brand and audience

5. Hashtags: 5-7 relevant hashtags aligned with campaign themes and trends

6. Tone and style summary: Brief description of the ideal tone and style for messaging

7. Optional collaborations: 2-3 collaboration ideas with influencers or brands relevant to audience culture

8. 30/60/90 day implementation timeline with milestones

Return ONLY a valid JSON object with these keys:
- "recommendations": array of 3 recommendation objects, each with:
  - "focus"
  - "insight"
  - "tactics"
  - "expected_impact"
- "top_priority"
- "content_themes"
- "captions"
- "hashtags"
- "tone_style_summary"
- "optional_collaborations"
- "timeline"
"""

    try:
        if use_vultr:
            json_response = call_vultr_llm(prompt, temperature=0.7)
        else:
            json_response = call_openai_llm(prompt, temperature=0.7)
        
        result = json.loads(json_response)

        # Ensure keys exist with defaults
        keys_defaults = {
            "recommendations": [],
            "top_priority": "",
            "content_themes": [],
            "captions": [],
            "hashtags": [],
            "tone_style_summary": "",
            "optional_collaborations": [],
            "timeline": {}
        }
        for key, default in keys_defaults.items():
            if key not in result:
                result[key] = default
        
        return result
        
    except Exception as e:
        print(f"Failed to generate strategic recommendations: {e}")
        return {
            "recommendations": [
                {
                    "focus": "Data Analysis",
                    "insight": "Unable to generate recommendations due to error",
                    "tactics": ["Review data quality", "Check system logs"],
                    "expected_impact": "Resolve technical issues"
                }
            ],
            "top_priority": "Fix data processing pipeline",
            "content_themes": [],
            "captions": [],
            "hashtags": [],
            "tone_style_summary": "",
            "optional_collaborations": [],
            "timeline": {},
            "error": str(e)
        }

