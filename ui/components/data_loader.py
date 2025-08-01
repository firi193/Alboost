import json
import codecs
from datetime import datetime
from typing import List, Dict

def load_json_with_platform(filepath: str, platform: str) -> list:
    """
    Load JSON data with robust encoding handling.
    """
    try:
        # Try UTF-8 first (most common for modern files)
        with codecs.open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        try:
            # Try UTF-8 with BOM
            with codecs.open(filepath, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except UnicodeDecodeError:
            # Last resort: try with error handling
            with codecs.open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
    
    # Attach platform field to each record
    for item in data:
        item.setdefault("platform", platform)
    
    return data

def filter_posts_by_date(posts: List[Dict], start_date, end_date, date_key=None) -> List[Dict]:
    """
    Filter posts by date range, automatically detecting the date field.
    """
    filtered = []
    
    for post in posts:
        # Auto-detect date key if not provided
        if date_key is None:
            if "created_at" in post:
                date_key = "created_at"
            elif "date" in post:
                date_key = "date"
            else:
                continue
        
        try:
            date_str = post[date_key]
            
            # Handle different date formats
            if "T" in date_str:  # ISO datetime format: "2025-06-30T10:45:00Z"
                post_date = datetime.fromisoformat(date_str.replace("Z", "")).date()
            else:  # Simple date format: "2025-07-30"
                post_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            if start_date <= post_date <= end_date:
                filtered.append(post)
                
        except Exception as e:
            continue
    
    return filtered

def filter_posts_by_platform(posts: List[Dict], platform: str) -> List[Dict]:
    """
    Filter posts by platform.
    """
    if platform == "all":
        return posts
    return [post for post in posts if post.get("platform") == platform]

def get_filtered_data(all_posts: List[Dict], platform: str, start_date, end_date) -> List[Dict]:
    """
    Apply both platform and date filters to posts.
    """
    # First filter by platform
    platform_filtered = filter_posts_by_platform(all_posts, platform)
    
    # Then filter by date
    date_filtered = filter_posts_by_date(platform_filtered, start_date, end_date)
    
    return date_filtered 