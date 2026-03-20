# Northlake Analytics — Analytics Engineering Portfolio Project

> A full analytics engineering project built to learn and demonstrate production-grade
> data modelling using **Python** , **Snowflake** , **SQL** , and eventually **dbt** .

---

## The Business

**Northlake HQ** is a fictional B2B SaaS company selling a project management tool.
200 accounts across SMB, Mid-Market, and Enterprise segments. Six plans across monthly
and annual billing cycles.

This project simulates the real work of an analytics engineer: receiving raw data from
multiple operational sources, cleaning and modelling it into reliable, tested, documented
marts that stakeholders can actually trust.

---

## Data Sources

All raw data is synthetically generated using Python (`data/generate_data.py`).

| File                  | Rows    | Description                                           |
| --------------------- | ------- | ----------------------------------------------------- |
| `accounts.csv`        | 200     | Company accounts — the core business entity           |
| `contacts.csv`        | 600     | Individual users linked to accounts                   |
| `plans.csv`           | 6       | Subscription plan definitions and pricing             |
| `subscriptions.csv`   | 220     | Account subscription records and lifecycle status     |
| `events.csv`          | ~12,000 | Product usage events (logins, feature use, API calls) |
| `support_tickets.csv` | 800     | Customer support interactions                         |
| `invoices.csv`        | 220     | Billing invoices linked to subscriptions              |

---

## Data Quality Issues (intentionally baked in)

This is not clean data. These problems were designed in to reflect real-world conditions:

| #   | Problem                                      | Source          |
| --- | -------------------------------------------- | --------------- |
| 1   | ~5% blank `industry`, ~3% NULL `region`      | accounts        |
| 2   | ~20% soft-deleted rows (`is_deleted = True`) | accounts        |
| 3   | ~4% malformed emails (missing `@`)           | contacts        |
| 4   | ~8% NULL `job_title`, ~10% NULL `last_login` | contacts        |
| 5   | ~3% NULL `plan_id`                           | subscriptions   |
| 6   | ~1% duplicate rows (same `event_id`)         | events          |
| 7   | ~5% NULL `platform`, ~10% NULL `properties`  | events          |
| 8   | ~20% NULL `first_response_at`                | support_tickets |
| 9   | Mixed currencies (USD, EUR, GBP, CAD)        | invoices        |

---

## Project Architecture

```
Raw CSVs (data/raw/)
    │
    ▼
Snowflake RAW schema         ← exact 1:1 load, everything VARCHAR
    │
    ▼
Snowflake STAGING schema     ← cleaned, typed, renamed (stg_ prefix)
    │                           no joins, no business logic
    ▼
Snowflake MARTS schema       ← business-facing aggregations
                                one row per business entity
```

### Repo Structure

```
northlake-analytics/
├── README.md
├── .gitignore
│
├── data/
│   ├── raw/                      # CSVs live here locally (gitignored)
│   └── generate_data.py          # synthetic data generator
│
├── ingestion/                    # scripts to load CSVs → Snowflake
│
├── cleaning/                     # Python data cleaning scripts
│
├── sql/
│   ├── setup/                    # database, schema, warehouse, file format DDL
│   ├── raw/                      # CREATE TABLE statements for RAW schema
│   ├── staging/                  # stg_ transformation queries
│   ├── intermediate/             # int_ join and enrichment queries
│   └── marts/                    # final business-facing models
│       ├── finance/
│       ├── product/
│       └── customer_success/
│
└── docs/
    └── data_dictionary.md        # column definitions per table
```

---

## Snowflake Setup

Three schemas following the medallion architecture:

```sql
CREATE DATABASE IF NOT EXISTS NORTHLAKE_DB;

CREATE SCHEMA IF NOT EXISTS RAW;       -- exact copy of source, never edited
CREATE SCHEMA IF NOT EXISTS STAGING;   -- cleaned, typed, renamed
CREATE SCHEMA IF NOT EXISTS MARTS;     -- business-ready aggregations
```

---

## Progress Tracker

- [x] Generate raw synthetic data
- [ ] Snowflake setup (database, schemas, warehouse, file format)
- [ ] Load CSVs into RAW schema
- [ ] Write staging SQL (clean, cast, rename)
- [ ] Write intermediate SQL (joins, enrichment)
- [ ] Build marts (MRR, DAU, churn, ticket SLA)
- [ ] Data dictionary
- [ ] dbt migration

---

## Planned Marts

| Mart                     | Description                                                |
| ------------------------ | ---------------------------------------------------------- |
| `mrr_by_month`           | Monthly recurring revenue, expansions, contractions, churn |
| `invoice_summary`        | Payment status, overdue rates, revenue by currency         |
| `daily_active_users`     | Product engagement trends                                  |
| `feature_adoption`       | Which features are used and by whom                        |
| `churn_risk`             | Accounts showing disengagement signals                     |
| `ticket_sla_performance` | First response time, resolution time, CSAT by category     |

---

## Tools

- **Python** — data generation and ingestion scripts
- **Snowflake** — cloud data warehouse
- **SQL** — all transformation logic written by hand
- **dbt** — coming after the SQL layer is established
- **GitHub** — version control and project tracking
