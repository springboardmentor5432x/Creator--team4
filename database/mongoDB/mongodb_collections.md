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

---
