# CreatorIQ Database

This directory contains the database design and scripts for the CreatorIQ project.

## PostgreSQL

The PostgreSQL folder contains SQL scripts for creating and testing the relational database.

### Tables

- `roles`
- `users`
- `creator_profiles`
- `agency_profiles`
- `account_settings`
- `agency_creators`

### Files

- `create_tables.sql` – Creates all required database tables.
- `insert_data.sql` – Inserts sample data into the tables.
- `test_queries.sql` – Contains SQL queries to verify the database.

## MongoDB

The MongoDB folder contains the NoSQL database design for content and analytics.

### Collections

- `social_accounts`
- `content_posts`
- `content_metrics`
- `engagement_history`
- `analytics_summary`
- `performance_trends`

The MongoDB collections are documented in `mongodb_collections.md`. These collections will be populated dynamically by the backend using API responses and user actions.

## Database Technologies

- PostgreSQL (Relational Database)
- MongoDB (NoSQL Database)

## Contribution

This module includes:

- PostgreSQL database schema
- PostgreSQL sample data
- PostgreSQL test queries
- MongoDB collection design
- MongoDB documentation
