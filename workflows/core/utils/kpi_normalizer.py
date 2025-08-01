from typing import Dict, List, Union

def normalize_twitter_kpi(post: Dict) -> Dict:
    impressions = post.get("impressions", 0)
    engagements = post.get("engagements", 0)

    return {
        "platform": "twitter",
        "date": post.get("date"),
        "post_id": post.get("post_id", None),
        "text": post.get("text", ""),
        "campaign_name": infer_campaign_name(post.get("text", "")),

        "impressions": impressions,
        "reach": impressions,  # Twitter does not separate reach
        "engagements": engagements,
        "engagement_rate": round(engagements / impressions, 4) if impressions else 0.0,
        "likes": post.get("likes", 0),
        "comments": post.get("replies", 0),
        "shares": post.get("retweets", 0),
        "saves": None,
        "conversions": None,
        "conversion_rate": None,
    }

def normalize_instagram_kpi(post: Dict) -> Dict:
    reach = post.get("reach", 0)
    engagements = post.get("engagements", 0)

    return {
        "platform": "instagram",
        "date": post.get("created_at", "").split("T")[0],
        "post_id": post.get("post_id", None),
        "text": post.get("caption", ""),
        "campaign_name": infer_campaign_name(post.get("caption", "")),

        "impressions": post.get("impressions", 0),
        "reach": reach,
        "engagements": engagements,
        "engagement_rate": round(engagements / reach, 4) if reach else 0.0,
        "likes": post.get("likes", 0),
        "comments": post.get("comments", 0),
        "shares": post.get("shares", 0),
        "saves": post.get("saves", 0),
        "conversions": None,
        "conversion_rate": None,
    }

def normalize_ga4_kpi(event: Dict) -> Dict:
    sessions = event.get("sessions", 0)
    conversions = event.get("conversions", 0)

    return {
        "platform": "ga4",
        "date": event.get("date"),
        "post_id": None,
        "text": "",
        "campaign_name": event.get("utm_campaign", "unknown"),

        "impressions": sessions,  # you might treat sessions as impressions
        "reach": event.get("users", 0),
        "engagements": event.get("engaged_sessions", 0),
        "engagement_rate": round(event.get("engagement_rate", 0.0), 4),
        "likes": None,
        "comments": None,
        "shares": None,
        "saves": None,
        "conversions": conversions,
        "conversion_rate": round(conversions / sessions, 4) if sessions else 0.0,
    }

# Optional helper function
def infer_campaign_name(text: str) -> str:
    if not text:
        return "general"
    if "launch" in text.lower():
        return "product_launch"
    if "tips" in text.lower():
        return "educational"
    if "sale" in text.lower():
        return "promotion"
    return "general"

# Example master dispatcher
def normalize_post(post: Dict, platform: str) -> Dict:
    if platform == "twitter":
        return normalize_twitter_kpi(post)
    elif platform == "instagram":
        return normalize_instagram_kpi(post)
    elif platform == "meta":  # Add support for meta platform
        return normalize_instagram_kpi(post)  # Treat meta same as Instagram
    elif platform == "ga4":
        return normalize_ga4_kpi(post)
    else:
        raise ValueError(f"Unsupported platform: {platform}")


