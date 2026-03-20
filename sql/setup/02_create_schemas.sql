USE DATABASE NORTHLAKE_DB;

-- exact copy of source, never edited
CREATE SCHEMA IF NOT EXISTS RAW;   

 -- cleaned, typed, renamed
CREATE SCHEMA IF NOT EXISTS STAGING;  

 -- business-ready aggregations
CREATE SCHEMA IF NOT EXISTS MARTS;    