PROMPTS = {
    "strategy": """
    Given a project type of "{project_type}" and the goal "{goal}", generate a concise strategy.
    Mention 2 key ideas and a suggested content format (e.g., blog, video, tweet).
    """,

    "writing": """
    Write a {format} for a campaign targeting {audience} with the following goals: {goal}.
    Keep it on-brand and engaging.
    """,

    "research": """
    Search the web or internal DB for recent trends about "{topic}". Return 3 insights in bullet points.
    """,

    "feedback_analysis": """
    Based on the feedback: "{feedback}", suggest a strategy tweak or rewrite recommendation.
    """
}
