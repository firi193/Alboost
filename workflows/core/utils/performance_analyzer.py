from typing import List, Dict
from collections import defaultdict
import numpy as np

def analyze_performance(posts: List[Dict]) -> Dict:
    # Handle empty posts list
    if not posts:
        return {
            "total_posts": 0,
            "avg_engagement_rate": 0.0,
            "avg_conversion_rate": 0.0,
            "top_post": None,
            "platform_summary": {},
            "message": "No posts found in the selected date range"
        }
    
    return {
        "total_posts": len(posts),
        "avg_engagement_rate": round(np.mean([
            p["engagement_rate"] for p in posts if p.get("engagement_rate") is not None
        ]), 4),
        "avg_conversion_rate": round(np.mean([
            p["conversion_rate"] for p in posts if p.get("conversion_rate") is not None
        ]), 4),
        "top_post": max(posts, key=lambda x: x.get("engagements", 0)),
        "platform_summary": platform_breakdown(posts),
    }

def platform_breakdown(posts: List[Dict]) -> Dict:
    if not posts:
        return {}
        
    by_platform = defaultdict(list)
    for post in posts:
        platform = post.get("platform", "unknown")
        by_platform[platform].append(post)

    summary = {}
    for platform, entries in by_platform.items():
        summary[platform] = {
            "total_posts": len(entries),
            "avg_engagement": round(np.mean([
                p["engagement_rate"] for p in entries if p.get("engagement_rate") is not None
            ]), 4),
        }
    return summary