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


# ---------------------------------------------------------------------------
# Growth Analytics Utilities
# ---------------------------------------------------------------------------

def calculate_trend_score(metrics: dict) -> float:
    """
    Calculate trend score for a content item.

    Formula:
        trend_score = 0.30*views + 0.20*likes + 0.20*shares
                    + 0.15*comments + 0.15*engagement_rate

    Args:
        metrics: Dict with keys: views, likes, shares, comments, engagement_rate.

    Returns:
        Raw (un-normalized) trend score.
    """
    views = metrics.get("views", 0)
    likes = metrics.get("likes", 0)
    shares = metrics.get("shares", 0)
    comments = metrics.get("comments", 0)
    engagement_rate = metrics.get("engagementRate", metrics.get("engagement_rate", 0))

    return (
        0.30 * views
        + 0.20 * likes
        + 0.20 * shares
        + 0.15 * comments
        + 0.15 * engagement_rate
    )


def normalize_scores(scores: list) -> list:
    """
    Min-max normalization to a 0–100 scale.

    Args:
        scores: List of raw numeric scores.

    Returns:
        List of normalized scores. Returns all zeros if all inputs are equal.
    """
    if not scores:
        return []
    min_val = min(scores)
    max_val = max(scores)
    if max_val == min_val:
        return [0.0] * len(scores)
    return [round(((s - min_val) / (max_val - min_val)) * 100, 2) for s in scores]


def calculate_moving_average(values: list, window: int) -> float:
    """
    Simple Moving Average over the last `window` values.

    Args:
        values: List of numeric values (chronologically ordered).
        window: Number of most recent values to average.

    Returns:
        The average of the last `window` values, or 0.0 if empty.
    """
    if not values:
        return 0.0
    window = min(window, len(values))
    subset = values[-window:]
    return sum(subset) / len(subset)


def calculate_confidence(values: list) -> float:
    """
    Confidence based on coefficient of variation (CV).

    confidence = (1 - CV) * 100, clamped to [0, 100].
    Where CV = std_dev / mean.

    Higher consistency (lower CV) yields higher confidence.

    Args:
        values: List of numeric values.

    Returns:
        Confidence percentage (0–100).
    """
    if not values or len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std_dev = variance ** 0.5
    cv = std_dev / abs(mean)
    confidence = (1 - cv) * 100
    return round(max(0.0, min(100.0, confidence)), 2)


def determine_trend(values: list) -> str:
    """
    Determine overall trend direction using simple linear slope.

    Uses least-squares slope of values over their index positions.

    Args:
        values: List of numeric values (chronologically ordered).

    Returns:
        'increasing', 'decreasing', or 'stable'.
    """
    if not values or len(values) < 2:
        return "stable"

    n = len(values)
    x_mean = (n - 1) / 2.0
    y_mean = sum(values) / n

    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return "stable"

    slope = numerator / denominator

    # Use a relative threshold: slope must be > 1% of the mean value per step
    threshold = abs(y_mean) * 0.01 if y_mean != 0 else 0.01
    if slope > threshold:
        return "increasing"
    elif slope < -threshold:
        return "decreasing"
    return "stable"
