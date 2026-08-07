# CreatorIQ Database

This directory contains the database design and scripts for the CreatorIQ project.

## PostgreSQL

The PostgreSQL folder contains SQL scripts for creating and testing the relational database.

### Module 1 - User Management

#### Tables

- `roles`
- `users`
- `creator_profiles`
- `agency_profiles`
- `account_settings`
- `agency_creators`

#### Files

- `create_tables_for_module-1.sql` – Creates all required database tables.
- `insert_data_for_module-1.sql` – Inserts sample data into the tables.

---

### Module 5 - Revenue Analytics

#### Tables

- `sponsorships`
- `revenue_transactions`
- `subscription_revenue`
- `financial_summary`
- `brand_collaborations`

#### Files

- `table_creation_for_module-5.sql` – Creates Module 5 revenue tables.
- `inserting_data_for_module-5.sql` – Inserts mock financial data.

---

### Module 6 - API Integration Support

#### Tables

- `sync_history`

#### Files

- `Module-6.sql` – Creates synchronization tracking table for API integration.

---

### Module 7 - Notifications & Reports

#### Tables

- `notifications`
- `generated_reports`

#### Files

- `table_creation_for_module-7.sql` – Creates notifications and reports tables.
- `inserting_data_for_module-7.sql` – Inserts sample notifications and reports.

---

## MongoDB

The MongoDB folder contains the NoSQL database design for content and analytics.

### Module 2 Collections

- `social_accounts`
- `content_posts`
- `content_metrics`
- `engagement_history`
- `analytics_summary`
- `performance_trends`

### Module 3 Collections

- `audience_analytics`
- `audience_demographics`
- `audience_behavior`

### Module 6 Collections

- `platform_analytics_raw`
- `content_sync_state`

The MongoDB collections are documented in `mongodb_collections.md`. These collections are populated dynamically by the backend using API responses and user actions.

---

## Database Technologies

- PostgreSQL (Relational Database)
- MongoDB (NoSQL Database)

---

## Contribution

This module includes:

- PostgreSQL database schema
- PostgreSQL sample data
- MongoDB collection design
- MongoDB documentation
- Audience Analytics database design
- Revenue Analytics database design
- Notifications & Reports database design
- API synchronization database design
- Mock data for backend development and testing
