CREATE OR REPLACE TABLE NORTHLAKE_DB.RAW.raw_subscriptions(
    subscription_id VARCHAR, 
    account_id VARCHAR, 
    plan_id VARCHAR, 
    status VARCHAR, 
    trial_start VARCHAR, 
    trial_end VARCHAR, 
    subscription_start VARCHAR, 
    subscription_end VARCHAR, 
    canceled_at VARCHAR, 
    seats_purchased VARCHAR, 
    discount_pct VARCHAR, 
    created_at VARCHAR, 
    updated_at VARCHAR
);