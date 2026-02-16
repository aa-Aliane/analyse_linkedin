create or replace DATABASE LINKEDIN;
create or replace SCHEMA ANALYTICS;


alter warehouse COMPUTE_WH set warehouse_size='SMALL';

use role ACCOUNTADMIN;
use warehouse COMPUTE_WH;
use DATABASE LINKEDIN;
use schema ANALYTICS;

use schema PUBLIC;

CREATE OR REPLACE STAGE linked_s3
  URL = 's3://snowflake-lab-bucket/'
  FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"' SKIP_HEADER = 1);



CREATE OR REPLACE FILE FORMAT csv_linkedin_format
  type = 'CSV'
  field_delimiter = ','
  record_delimiter = '\n'
  skip_header = 1
  field_optionally_enclosed_by = '\042'
  null_if = (''); 

CREATE OR REPLACE FILE FORMAT json_linkedin_format
  TYPE = JSON
  STRIP_OUTER_ARRAY = TRUE;



-- JOB_POSTINGS
CREATE OR REPLACE TABLE job_postings (
    job_id BIGINT PRIMARY KEY,
    company_id BIGINT,
    title VARCHAR,
    description TEXT,
    max_salary FLOAT,
    med_salary FLOAT,
    min_salary FLOAT,
    pay_period VARCHAR,
    formatted_work_type VARCHAR,
    location VARCHAR,
    applies INTEGER,
    original_listed_time BIGINT,
    remote_allowed INTEGER,  
    views INTEGER,
    job_posting_url VARCHAR,
    application_url VARCHAR,
    application_type VARCHAR,
    expiry BIGINT,
    closed_time BIGINT,
    formatted_experience_level VARCHAR,
    skills_desc TEXT,
    listed_time BIGINT,
    posting_domain VARCHAR,
    sponsored INTEGER,
    work_type VARCHAR,
    currency VARCHAR,
    compensation_type VARCHAR
);

-- Recharger
COPY INTO job_postings
FROM @linked_s3/job_postings.csv
FILE_FORMAT = csv_linkedin_format;

-- BENEFITS
CREATE OR REPLACE TABLE benefits (
    job_id BIGINT,
    inferred BOOLEAN,
    type VARCHAR
);

-- EMPLOYEE_COUNTS
CREATE OR REPLACE TABLE employee_counts (
    company_id BIGINT,
    employee_count INTEGER,
    follower_count INTEGER,
    time_recorded BIGINT
);

-- JOB_SKILLS
CREATE OR REPLACE TABLE job_skills (
    job_id BIGINT,
    skill_abr VARCHAR
);

-- companies
CREATE OR REPLACE TABLE companies_json (data VARIANT);

copy into companies_json
from @linked_s3
file_format = json_linkedin_format
pattern = '.*\.json.*';

CREATE OR REPLACE TABLE companies AS
SELECT
    data:company_id::BIGINT AS company_id,
    data:name::VARCHAR AS name,
    data:description::TEXT AS description,
    data:company_size::INTEGER AS company_size,
    data:state::VARCHAR AS state,
    data:country::VARCHAR AS country,
    data:city::VARCHAR AS city,
    data:zip_code::VARCHAR AS zip_code,
    data:address::VARCHAR AS address,
    data:url::VARCHAR AS url
FROM companies_json;

select * from companies;


-- COMPANY_INDUSTRIES
CREATE OR REPLACE TABLE company_industries_json (data VARIANT);
copy into company_industries_json
from @linked_s3/company_industries.json
file_format = json_linkedin_format;


CREATE OR REPLACE TABLE company_industries AS
SELECT
    data:company_id::BIGINT AS company_id,
    data:industry::VARCHAR AS industry
FROM company_industries_json;

SELECT * FROM company_industries;

-- Job Industries
CREATE OR REPLACE TABLE job_industries_json (data VARIANT);

COPY INTO job_industries_json FROM @linked_s3/job_industries.json FILE_FORMAT = json_linkedin_format;

CREATE OR REPLACE TABLE job_industries AS
SELECT
    data:industry_id::BIGINT AS industry_id,
    data:job_id::BIGINT      AS job_id
FROM job_industries_json;

select * from job_industries;


-- Company Specialities
CREATE OR REPLACE TABLE company_specialities_json (data VARIANT);

COPY INTO company_specialities_json FROM @linked_s3/company_specialities.json FILE_FORMAT = json_linkedin_format;

CREATE OR REPLACE TABLE company_specialities AS
SELECT
    data:company_id::BIGINT  AS company_id,
    data:speciality::VARCHAR AS speciality
FROM company_specialities_json;

select * from company_specialities;

list @linked_s3;

-- job_postings
COPY INTO job_postings
FROM @linked_s3/job_postings.csv
FILE_FORMAT = csv_linkedin_format;



-- benefits
COPY INTO benefits
FROM @linked_s3/benefits.csv
FILE_FORMAT = csv_linkedin_format;

-- employee_counts
COPY INTO employee_counts
FROM @linked_s3/employee_counts.csv
FILE_FORMAT = csv_linkedin_format;


-- job_skills
COPY INTO job_skills
FROM @linked_s3/job_skills.csv
FILE_FORMAT = csv_linkedin_format;




