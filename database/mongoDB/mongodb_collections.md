# MongoDB Database Design - CreatorIQ

## Overview

This document describes the MongoDB collections used for storing content and analytics in the CreatorIQ platform. PostgreSQL is used for authentication, authorization, and user management.

---

# 1. social_accounts

## Purpose
Stores the social media accounts connected by creators.

| Field | Type | Description |
|-------|------|-------------|
| creatorId | String | Generated creator ID |
| platform | String | Social media platform |
| accountName | String | Display name of the account |
| accountId | String | Platform account ID |
| profileUrl | String | Profile URL |
| followers | Number | Number of followers |
| connectedAt | Date | Date when the account was connected |
| isActive | Boolean | Indicates whether the account is active |

> **Note:** Sample document fields will be populated dynamically by the backend using API responses and user actions.

---

# 2. content_posts

## Purpose
Stores all content published by creators across different social media platforms.

| Field | Type | Description |
|-------|------|-------------|
| creatorId | String | Creator ID |
| socialAccountId | ObjectId | Reference to `social_accounts` |
| platform | String | Social media platform |
| platformPostId | String | Platform-specific post ID |
| title | String | Title of the content |
| description | String | Content description |
| contentType | String | Video / Reel / Post |
| contentUrl | String | URL of the content |
| thumbnailUrl | String | Thumbnail image URL |
| publishedAt | Date | Date and time the content was published |

> **Note:** Sample document fields will be populated dynamically by the backend using API responses and user actions.

---

# 3. content_metrics

## Purpose
Stores performance metrics for each content post.

| Field | Type | Description |
|-------|------|-------------|
| postId | ObjectId | Reference to `content_posts` |
| views | Number | Total views |
| likes | Number | Total likes |
| comments | Number | Total comments |
| shares | Number | Total shares |
| saves | Number | Total saves |
| watchTime | Number | Total watch time |
| reach | Number | Total reach |
| engagementRate | Number | Engagement rate |
| recordedAt | Date | Date and time when metrics were recorded |

> **Note:** Sample document fields will be populated dynamically by the backend using API responses and user actions.

---

# 4. engagement_history

## Purpose
Stores historical engagement data for posts.

| Field | Type | Description |
|-------|------|-------------|
| postId | ObjectId | Reference to `content_posts` |
| engagementRate | Number | Engagement rate |
| likes | Number | Number of likes |
| comments | Number | Number of comments |
| shares | Number | Number of shares |
| recordedDate | Date | Date of the recorded metrics |

> **Note:** Sample document fields will be populated dynamically by the backend using API responses and user actions.

---

# 5. analytics_summary

## Purpose
Stores aggregated analytics for each creator.

| Field | Type | Description |
|-------|------|-------------|
| creatorId | String | Creator ID |
| totalViews | Number | Total views |
| totalLikes | Number | Total likes |
| totalComments | Number | Total comments |
| totalShares | Number | Total shares |
| totalFollowers | Number | Total followers |
| totalReach | Number | Total reach |
| averageEngagementRate | Number | Average engagement rate |
| lastUpdated | Date | Last updated timestamp |

> **Note:** Sample document fields will be populated dynamically by the backend using API responses and user actions.

---

# 6. performance_trends

## Purpose
Stores creator performance trends over time.

| Field | Type | Description |
|-------|------|-------------|
| creatorId | String | Creator ID |
| trendDate | Date | Date of the trend |
| views | Number | Views |
| likes | Number | Likes |
| comments | Number | Comments |
| shares | Number | Shares |
| followers | Number | Followers gained |

> **Note:** Sample document fields will be populated dynamically by the backend using API responses and user actions.

---

# Database Responsibilities

### PostgreSQL
- User Authentication
- User Authorization
- Roles
- Creator Profiles
- Agency Profiles
- Account Settings

### MongoDB
- Social Media Accounts
- Content Posts
- Content Metrics
- Engagement History
- Analytics Summary
- Performance Trends
- **Growth Metrics** *(NEW)*
- **Content Growth** *(NEW)*
- **Hashtags** *(NEW)*
- **Trend Scores** *(NEW)*
- **Predictions** *(NEW)*

---

# Growth Analytics Module — New Collections

---

# 7. growth_metrics

## Purpose
Stores daily aggregated growth metrics per creator per platform. One record per day per creator.

| Field | Type | Description |
|-------|------|-------------|
| creator_id | String | Creator ID |
| platform | String | Social media platform |
| date | Date | Date of the metric snapshot |
| followers | Number | Total followers |
| subscribers | Number | Total subscribers |
| views | Number | Total views |
| likes | Number | Total likes |
| comments | Number | Total comments |
| shares | Number | Total shares |
| watch_time | Number | Total watch time in seconds |
| reach | Number | Total reach |
| engagement_rate | Number | Engagement rate percentage |
| updated_at | Date | Last update timestamp |

### Indexes
- `(creator_id, date)` — Unique
- `(creator_id, platform, date)` — Compound

---

# 8. content_growth

## Purpose
Stores daily metric snapshots for individual content items to track per-content growth over time.

| Field | Type | Description |
|-------|------|-------------|
| content_id | String | Content post ID |
| creator_id | String | Creator ID |
| date | Date | Date of the snapshot |
| views | Number | Views on that day |
| likes | Number | Likes on that day |
| comments | Number | Comments on that day |
| shares | Number | Shares on that day |
| reach | Number | Reach on that day |
| engagement_rate | Number | Engagement rate on that day |
| updated_at | Date | Last update timestamp |

### Indexes
- `(content_id, date)` — Unique
- `(creator_id, date)` — Compound

---

# 9. hashtags

## Purpose
Stores aggregated hashtag statistics computed from content_posts and content_metrics.

| Field | Type | Description |
|-------|------|-------------|
| name | String | Hashtag name (lowercase, without #) |
| frequency | Number | Number of times the hashtag was used |
| average_reach | Number | Average reach across associated content |
| average_engagement | Number | Average engagement rate |
| growth_percentage | Number | Growth percentage over analysis period |
| updated_at | Date | Last recalculation timestamp |

### Indexes
- `(name)` — Unique
- `(growth_percentage)` — Descending (for trending queries)

---

# 10. trend_scores

## Purpose
Stores computed trend rankings for content items. Auto-expires after 7 days via TTL index.

| Field | Type | Description |
|-------|------|-------------|
| content_id | String | Content post ID |
| trend_score | Number | Normalized trend score (0–100) |
| views | Number | Views at time of calculation |
| likes | Number | Likes at time of calculation |
| shares | Number | Shares at time of calculation |
| comments | Number | Comments at time of calculation |
| engagement_rate | Number | Engagement rate at time of calculation |
| platform | String | Social media platform |
| content_type | String | Type of content (video, reel, post) |
| generated_at | Date | When the score was calculated |

### Indexes
- `(content_id)` — Single
- `(trend_score)` — Descending (for top trending queries)
- `(generated_at)` — TTL: 7 days

### Trend Score Formula
```
trend_score = 0.30*views + 0.20*likes + 0.20*shares + 0.15*comments + 0.15*engagement_rate
```

---

# 11. predictions

## Purpose
Stores reach predictions and audience forecasts for audit trail and caching. Auto-expires after 30 days via TTL index.

| Field | Type | Description |
|-------|------|-------------|
| creator_id | String | Creator ID |
| prediction_type | String | 'reach' or 'audience' |
| predicted_value | Object | Full prediction result data |
| confidence | Number | Confidence percentage (0-100) |
| generated_at | Date | When the prediction was generated |

### Indexes
- `(creator_id, prediction_type)` — Compound
- `(generated_at)` — TTL: 30 days

---

# 12. platform_analytics_raw

## Purpose
Stores normalized, per-platform analytics snapshots fetched from each platform API. One record per creator per platform per day. This is the primary data source for the multi-platform analytics dashboard.

| Field | Type | Description |
|-------|------|-------------|
| creatorId | String | Creator profile ID |
| platform | String | `youtube` / `instagram` / `facebook` / `linkedin` / `x` |
| accountId | String | Platform-specific account/channel/page ID |
| snapshotDate | Date | UTC date of this snapshot (date-only, truncated to midnight) |
| periodDays | Number | Number of days this snapshot covers (e.g. 30) |
| followers | Number | Followers / subscribers at snapshot time |
| views | Number | Total or period views |
| likes | Number | Total or period likes |
| comments | Number | Total or period comments |
| shares | Number | Total or period shares |
| reach | Number | Reach (Instagram, Facebook, X) |
| impressions | Number | Impressions (Instagram, Facebook, LinkedIn) |
| watchTime | Number | Watch time in minutes (YouTube only) |
| profileVisits | Number | Profile visits (Instagram only) |
| reelPlays | Number | Reel plays (Instagram only) |
| storyViews | Number | Story impressions (Instagram only) |
| pageLikes | Number | Page likes (Facebook only) |
| postImpressions | Number | Post impressions (LinkedIn only) |
| tweetImpressions | Number | Tweet impressions (X only) |
| reposts | Number | Retweets/reposts (X only) |
| engagementRate | Number | Calculated engagement rate percentage |
| recordedAt | Date | UTC timestamp when this document was inserted/updated |

### Indexes
- `(creatorId, platform, snapshotDate)` — Unique (one snapshot per platform per day)
- `(creatorId, snapshotDate DESC)` — Multi-platform dashboard queries
- `(platform, snapshotDate DESC)` — Platform-wide aggregation queries

---

# 13. content_sync_state

## Purpose
Tracks the last content-fetch timestamp per creator per platform. Used by the sync service to resume from where the last fetch left off, avoiding re-fetching all historical content on every sync cycle.

| Field | Type | Description |
|-------|------|-------------|
| creatorId | String | Creator profile ID |
| platform | String | Social media platform |
| lastFetchedAt | Date | Timestamp of the last successful content fetch |
| totalPostsFetched | Number | Running total of posts ever fetched for this account |
| oldestPostDate | Date | Date of the oldest post currently stored |
| newestPostDate | Date | Date of the most recent post currently stored |
| updatedAt | Date | When this document was last modified |

### Indexes
- `(creatorId, platform)` — Unique

---

# 14. report_snapshots

## Purpose
Stores full JSON snapshots of generated performance and revenue reports (weekly, monthly, quarterly, annual) for fast frontend rendering and report history previews.

| Field | Type | Description |
|-------|------|-------------|
| reportId | Number | Reference to `generated_reports.id` in PostgreSQL |
| creatorId | String | Creator profile ID |
| reportType | String | `weekly` / `monthly` / `quarterly` / `annual` / `custom` |
| periodLabel | String | Human-readable period (e.g., "Week 31, 2026", "July 2026") |
| summaryMetrics | Object | Aggregated total views, followers gained, engagement, revenue |
| bestContent | Object | Details of the top performing post in the period |
| topPlatform | Object | Details of the highest performing platform |
| platformBreakdown | List | Per-platform statistics |
| revenueSummary | Object | Financial totals, sponsorship, ad, affiliate breakdowns |
| audienceSummary | Object | Audience metrics overview |
| createdAt | Date | Timestamp when snapshot was saved |

### Indexes
- `(reportId)` — Unique
- `(creatorId, createdAt DESC)` — Creator timeline lookup

---

# Database Responsibilities (Updated)

### PostgreSQL
- User Authentication
- User Authorization
- Roles
- Creator Profiles
- Agency Profiles
- Account Settings
- **Sync History** *(audit log for analytics syncs)*
- **Notifications** *(NEW — in-app notification center & alerts)*
- **Generated Reports** *(NEW — metadata & file pointers for report history)*

### MongoDB
- Social Media Accounts (`social_accounts`)
- Content Posts (`content_posts`)
- Content Metrics (`content_metrics`)
- Engagement History (`engagement_history`)
- Analytics Summary (`analytics_summary`)
- Performance Trends (`performance_trends`)
- Growth Metrics (`growth_metrics`)
- Content Growth (`content_growth`)
- Hashtags (`hashtags`)
- Trend Scores (`trend_scores`)
- Predictions (`predictions`)
- Audience Analytics (`audience_analytics`)
- Audience Demographics (`audience_demographics`)
- Audience Behavior (`audience_behavior`)
- **Platform Analytics Raw** *(normalized per-platform daily snapshots)*
- **Content Sync State** *(fetch-cursor tracking per creator/platform)*
- **Report Snapshots** *(NEW — JSON report data for instant UI rendering)*
