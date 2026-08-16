# Audience Analytics Module

## `audience_analytics`

**Purpose:** Stores follower growth, reach, impressions and engagement statistics.

| Field | Type | Description |
|---|---|---|
| `creatorId` | String | Creator ID |
| `platform` | String | Social media platform |
| `followers` | Number | Total followers |
| `newFollowers` | Number | Followers gained |
| `unfollowers` | Number | Followers lost |
| `reach` | Number | Number of users reached |
| `impressions` | Number | Total impressions |
| `engagementRate` | Number | Engagement percentage |
| `recordedAt` | Date | Date when the analytics were recorded |

**Sample document fields will be populated dynamically by the backend using API responses and user actions.**

---

## `audience_demographics`

**Purpose:** Stores audience demographic information.

| Field | Type | Description |
|---|---|---|
| `creatorId` | String | Creator ID |
| `platform` | String | Social media platform |
| `ageDistribution` | Object | Audience distribution by age |
| `genderDistribution` | Object | Audience distribution by gender |
| `geographicLocation` | Object | Audience location information |
| `deviceUsage` | Object | Devices used by the audience |
| `activeHours` | Array | Peak audience activity hours |
| `recordedAt` | Date | Date when the demographic data was recorded |

**Sample document fields will be populated dynamically by the backend using API responses and user actions.**

---

## `audience_behavior`

**Purpose:** Stores audience behaviour metrics.

| Field | Type | Description |
|---|---|---|
| `creatorId` | String | Creator ID |
| `platform` | String | Social media platform |
| `averageWatchTime` | Number | Average watch time |
| `returningViewers` | Number | Number of returning viewers |
| `newViewers` | Number | Number of new viewers |
| `averageSessionDuration` | Number | Average session duration |
| `clickThroughRate` | Number | Click-through rate (CTR) |
| `recordedAt` | Date | Date when the behaviour data was recorded |

**Sample document fields will be populated dynamically by the backend using API responses and user actions.**

---

## Relationship Flow

```text
Creator (PostgreSQL)
        |
        | creatorId
        |
        +--------------------> audience_analytics
        |
        +--------------------> audience_demographics
        |
        +--------------------> audience_behavior