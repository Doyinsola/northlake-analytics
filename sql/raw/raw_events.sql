CREATE OR REPLACE TABLE NORTHLAKE_DB.RAW.raw_events(
    event_id VARCHAR, 
    contact_id VARCHAR, 
    account_id VARCHAR, 
    event_name VARCHAR, 
    platform VARCHAR, 
    session_id VARCHAR, 
    occurred_at VARCHAR, 
    properties VARCHAR, 
    ip_address VARCHAR
);