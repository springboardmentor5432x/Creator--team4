# Module 4 – Growth & Trend Analysis

Module 4 is responsible for monitoring creator growth, detecting content trends, analyzing hashtags, tracking content growth, and predicting future reach and audience growth.

The module uses the following MongoDB collections:

- `growth_metrics`
- `content_growth`
- `hashtags`
- `trend_scores`
- `predictions`

---

## `growth_metrics`

**Purpose:** Stores daily high-level growth and engagement metrics for each creator and platform.

| Field | Type | Description |
|---|---|---|
| `creator_id` | String | Creator ID |
| `platform` | String | Social media platform |
| `date` | Date | Date of the metric snapshot |
| `followers` | Number | Number of followers |
| `subscribers` | Number | Number of subscribers |
| `views` | Number | Number of views |
| `likes` | Number | Number of likes |
| `comments` | Number | Number of comments |
| `shares` | Number | Number of shares |
| `watch_time` | Number | Total watch time |
| `reach` | Number | Number of users reached |
| `engagement_rate` | Number | Engagement rate |
| `revenue` | Number | Revenue generated |
| `updated_at` | Date | Last update time |

**Index:** A unique index is maintained on `creator_id` and `date` to prevent duplicate daily growth records.

---

## `content_growth`

**Purpose:** Stores daily performance snapshots for individual content items to track content growth over time.

| Field | Type | Description |
|---|---|---|
| `content_id` | String | Content/Post ID |
| `creator_id` | String | Creator ID |
| `date` | Date | Date of the growth snapshot |
| `views` | Number | Number of views |
| `likes` | Number | Number of likes |
| `comments` | Number | Number of comments |
| `shares` | Number | Number of shares |
| `reach` | Number | Number of users reached |
| `engagement_rate` | Number | Engagement rate |
| `updated_at` | Date | Last update time |

**Index:** A unique index is maintained on `content_id` and `date` so that one daily growth record is maintained for each content item.

---

## `hashtags`

**Purpose:** Stores aggregated hashtag statistics used for hashtag analysis and identifying growing or high-performing hashtags.

| Field | Type | Description |
|---|---|---|
| `name` | String | Hashtag name |
| `usage_count` | Number | Number of times the hashtag was used |
| `total_views` | Number | Total views associated with the hashtag |
| `total_likes` | Number | Total likes associated with the hashtag |
| `total_comments` | Number | Total comments associated with the hashtag |
| `total_shares` | Number | Total shares associated with the hashtag |
| `avg_engagement_rate` | Number | Average engagement rate |
| `growth_percentage` | Number | Hashtag growth percentage |
| `updated_at` | Date | Last update time |

**Index:** A unique index is maintained on `name`, and an additional index is created on `growth_percentage` for efficient hashtag growth analysis.

---

## `trend_scores`

**Purpose:** Stores calculated trend scores and rankings for content identified as trending.

| Field | Type | Description |
|---|---|---|
| `content_id` | String | Content/Post ID |
| `trend_score` | Number | Calculated trend score |
| `platform` | String | Social media platform |
| `content_type` | String | Type of content |
| `views` | Number | Number of views |
| `likes` | Number | Number of likes |
| `shares` | Number | Number of shares |
| `comments` | Number | Number of comments |
| `engagement_rate` | Number | Engagement rate |
| `generated_at` | Date | Time when the trend score was generated |

The trend score is calculated using content performance metrics and normalized to a 0–100 scale.

**Index:** Indexes are maintained on `content_id`, `trend_score`, and `generated_at`. Trend score records are automatically removed after the configured expiry period.

---

## `predictions`

**Purpose:** Stores generated reach and audience growth predictions for future analysis.

| Field | Type | Description |
|---|---|---|
| `creator_id` | String | Creator ID |
| `prediction_type` | String | Type of prediction |
| `data` | Object | Prediction results |
| `platform` | String | Social media platform |
| `generated_at` | Date | Time when the prediction was generated |

Prediction data can contain predicted reach for different periods such as the next day, next week, and next month.

**Index:** Indexes are maintained on `creator_id` and `prediction_type`, along with an expiry index on `generated_at`.

---

## Module 4 MongoDB Collections Summary

| Collection | Purpose |
|---|---|
| `growth_metrics` | Stores daily creator and platform growth metrics |
| `content_growth` | Tracks daily growth of individual content |
| `hashtags` | Stores hashtag performance and growth statistics |
| `trend_scores` | Stores calculated content trend scores and rankings |
| `predictions` | Stores future reach and audience growth predictions |

---

