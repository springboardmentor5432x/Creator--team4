## Module 6 – Platform Synchronization

### `platform_analytics_raw`

**Purpose:** Stores analytics data fetched from different social media platform APIs for each creator.

| Field | Type | Description |
|---|---|---|
| `_id` | ObjectId | Unique MongoDB document ID |
| `creatorId` | String | ID of the creator |
| `platform` | String | Social media platform |
| `date` | String | Date of the analytics data |
| `followers` | Number | Number of followers |
| `views` | Number | Number of views |
| `watchTime` | Number | Total watch time |
| `likes` | Number | Number of likes |
| `comments` | Number | Number of comments |
| `shares` | Number | Number of shares |
| `reach` | Number | Number of users reached |
| `source` | String | API from which the data was obtained |
| `createdAt` | Date | Date and time when the record was created |

**Example platforms:**

- YouTube
- Instagram
- Facebook
- LinkedIn
- Twitter

**Example API sources:**

- YouTube Data API
- Instagram Graph API
- Facebook Graph API
- LinkedIn API
- X API (Twitter API)
---

### `content_sync_state`

**Purpose:** Tracks the synchronization status of content fetched from different social media platforms.

| Field | Type | Description |
|---|---|---|
| `_id` | ObjectId | Unique MongoDB document ID |
| `creatorId` | String | ID of the creator |
| `platform` | String | Social media platform |
| `lastSync` | Date | Date and time of the last synchronization |
| `nextPageToken` | String | Token used to fetch the next page of data from APIs such as YouTube |
| `nextCursor` | String | Cursor used to continue fetching data from APIs such as Instagram |
| `status` | String | Current synchronization status |

**Example synchronization statuses:**

- `completed`
- `in_progress`
- `failed`

---

### Module 6 MongoDB Collections Summary

| Collection | Purpose |
|---|---|
| `platform_analytics_raw` | Stores platform-specific analytics data fetched from external APIs |
| `content_sync_state` | Tracks the last synchronization state and pagination information for each platform |