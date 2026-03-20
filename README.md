# Northlake Analytics — Analytics Engineering Portfolio Project

> A full analytics engineering simulation built to learn and demonstrate production-grade
> data modelling using **dbt**, **Snowflake**, **Python**, and **GitHub Actions**.

---

## The Business

**Northlake HQ** is a fictional B2B SaaS company selling a project management tool.
~75 accounts, mix of SMB, Mid-Market and Enterprise. Three plans: Starter, Growth, Enterprise.

This project simulates the real work of an analytics engineer: receiving raw data from
multiple operational sources, cleaning and modelling it into reliable, tested, documented
marts that stakeholders can actually trust.

---

## Data Sources

| Source     | Tool                   | Contains                             |
|------------|------------------------|--------------------------------------|
| App DB     | PostgreSQL             | Accounts, users, subscriptions       |
| Stripe     | Fivetran → Snowflake   | Payments, invoices                   |
| Hubspot    | Fivetran → Snowflake   | Contacts, deals, sales activity      |
| Mixpanel   | Fivetran → Snowflake   | Feature usage, logins, events        |
| Zendesk    | Fivetran → Snowflake   | Support tickets                      |

---

## Data Quality Issues (intentionally baked in)

This is not clean data. These problems were designed in to reflect real-world conditions:

| # | Problem | Source | Resolution |
|---|---------|--------|------------|
| 1 | NULL trial_end_date | Subscriptions | Tagged: freemium + extended trials are valid NULLs |
| 2 | Duplicate subscription rows | Subscriptions | Deduped on subscription_id using row_number() |
| 3 | Duplicate Stripe charges | Payments | Deduped on stripe_charge_id |
| 4 | Inconsistent segment names | Hubspot | Normalised via case statement in staging |
| 5 | Contacts not linked to accounts | Hubspot | Flagged with is_unlinked_contact |
| 6 | Duplicate Hubspot contacts | Hubspot | Deduplicated in intermediate layer |
| 7 | Late-arriving Mixpanel events | Mixpanel | Both timestamps preserved, occurred_at used for analysis |
| 8 | Tickets not linked to accounts | Zendesk | Flagged, excluded from account-level aggregations |

---

## dbt Model Architecture

```
Raw (Snowflake)
    │
    ▼
Staging (stg_)          ← 1:1 with source, cleaned and typed
    │                      No joins. No business logic.
    ▼
Intermediate (int_)     ← Joins across sources, rollups, enrichment
    │                      Building blocks, not stakeholder-facing
    ▼
Marts (mart_)           ← Wide, flat, tested, documented
                           One row per business entity
                           What stakeholders and BI tools query
```

### Models built

| Model | Layer | Description |
|-------|-------|-------------|
| `stg_postgres__accounts` | Staging | Cleaned accounts, soft-deletes excluded |
| `stg_postgres__subscriptions` | Staging | Deduplicated subscriptions, NULLs documented |
| `stg_mixpanel__events` | Staging | Event stream with late-arrival handling |
| `stg_hubspot__contacts` | Staging | Contacts with normalised segment names |
| `int_account_usage_summary` | Intermediate | Mixpanel events rolled up to account level |
| `mart_trial_conversion` | Mart | Trial accounts ranked by conversion likelihood |

---

## Key Design Decisions

**Why `QUALIFY row_number()` for deduplication instead of `DISTINCT`?**  
`DISTINCT` requires all columns to match. Our duplicates differ only in `_loaded_at`.
`row_number()` lets us pick the canonical row (earliest loaded) and discard the rest precisely.

**Why keep NULL trial_end_dates instead of filtering them?**  
Two valid business states produce NULLs: freemium accounts (no expiry) and sales-extended
trials (expiry not yet set). Filtering them would remove the most interesting conversion
candidates. Instead we tag them with `is_freemium` and `is_extended_trial`.

**Why use `occurred_at` instead of `_loaded_at` for Mixpanel analysis?**  
Late-arriving events still happened — they should count toward engagement metrics.
`_loaded_at` is preserved for pipeline monitoring, not user behaviour analysis.

**Why `coalesce(usage.logins, 0)` in the mart?**  
Accounts with zero Mixpanel events produce a NULL on left join. Coalescing to 0 keeps
them in the mart so sales can see them (a zero-engagement account is still actionable).

---

## Conversion Score

The `mart_trial_conversion` model scores every trialing account (0–100 pts):

| Signal | Points | Why |
|--------|--------|-----|
| Invited a teammate | +25 | 60% conversion rate vs 12% without |
| Added an integration | +20 | Strong stickiness signal |
| Logged in on Day 1 | +15 | Day-1 engagement predicts retention |
| Logged in on Day 3 | +10 | |
| Logged in on Day 7 | +10 | |
| Core feature uses | +1 each (max 15) | |
| Has open deal | +5 | Sales already engaged |

Score tiers: **High** ≥ 50 · **Medium** ≥ 25 · **Low** < 25

---

## How to Run This Project

### 1. Generate raw data

```bash
cd data_generation
python3 generate_data.py
# Creates CSVs in data_generation/raw_data/
```

### 2. Load to Snowflake

```bash
# Upload CSVs to Snowflake stages and copy into raw schema tables
# See data_generation/load_to_snowflake.sql for setup commands
```

### 3. Set up dbt

```bash
cd dbt_project
# Copy profiles.yml to ~/.dbt/profiles.yml and fill in your Snowflake credentials
cp profiles.yml ~/.dbt/profiles.yml

# Test connection
dbt debug

# Run all models
dbt run

# Run tests
dbt test

# Generate and serve docs
dbt docs generate
dbt docs serve
```

### 4. View the lineage DAG

After running `dbt docs serve`, open http://localhost:8080 and click the
**lineage graph** icon to see the full DAG from source to mart.

---

## What's Coming (Learning Roadmap)

- [ ] `mart_revenue` — MRR, ARR, NRR, churn rate by cohort  
- [ ] `mart_customers` — Full customer 360 view  
- [ ] Month 2 data drop — schema change + late data handling  
- [ ] Quarter close — CFO asks for ARR and Net Revenue Retention  
- [ ] GitHub Actions CI — dbt tests run on every PR  
- [ ] dbt docs hosted on GitHub Pages  

---

## Tools Used

- **dbt Core / dbt Fusion** — transformation and testing
- **Snowflake** — cloud data warehouse
- **Python** — data generation and ingestion scripts  
- **GitHub Actions** — CI/CD for dbt test runs
- **VS Code + dbt extension** — local development
