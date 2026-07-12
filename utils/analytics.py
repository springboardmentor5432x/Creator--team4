def calculate_engagement_rate(metrics: dict, platform: str) -> float:
    """
    Calculate Engagement Rate.
    Formula:
    ((likes + comments + shares + saves) / reach) * 100
    or
    ((likes + comments + shares) / views) * 100
    depending on platform.
    """
    likes = metrics.get('likes', 0)
    comments = metrics.get('comments', 0)
    shares = metrics.get('shares', 0)
    saves = metrics.get('saves', 0)
    reach = metrics.get('reach', 0)
    views = metrics.get('views', 0)

    # Simplified platform logic: Instagram/TikTok use reach, YouTube uses views
    if platform.lower() in ['instagram', 'tiktok', 'facebook'] and reach > 0:
        return ((likes + comments + shares + saves) / reach) * 100
    elif views > 0:
        return ((likes + comments + shares) / views) * 100
    
    return 0.0

def calculate_performance_score(metrics: dict) -> float:
    """
    Performance Score Calculation:
    Views * 0.30
    Likes * 0.25
    Comments * 0.20
    Shares * 0.15
    Watch Time * 0.10
    """
    views = metrics.get('views', 0)
    likes = metrics.get('likes', 0)
    comments = metrics.get('comments', 0)
    shares = metrics.get('shares', 0)
    watch_time = metrics.get('watchTime', 0)

    score = (views * 0.30) + (likes * 0.25) + (comments * 0.20) + (shares * 0.15) + (watch_time * 0.10)
    return score

def calculate_growth_percentage(current_value: float, previous_value: float) -> float:
    """
    Calculate Growth %.
    """
    if previous_value == 0:
        return 100.0 if current_value > 0 else 0.0
    return ((current_value - previous_value) / previous_value) * 100.0
