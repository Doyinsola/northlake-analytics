CREATE OR REPLACE TABLE NORTHLAKE_DB.RAW.raw_invoices(
    invoice_id VARCHAR,
    subscription_id VARCHAR,
    account_id VARCHAR,
    amount_usd VARCHAR,
    discount_pct VARCHAR,
    tax_usd VARCHAR,
    total_usd VARCHAR,
    currency VARCHAR,
    status VARCHAR,
    payment_method VARCHAR,
    issued_at VARCHAR,
    due_at VARCHAR,
    paid_at VARCHAR,
    period_start VARCHAR,
    period_end VARCHAR
);