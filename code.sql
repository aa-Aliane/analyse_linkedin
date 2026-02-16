-- ========================================
-- CONFIGURATION INITIALE
-- ========================================
CREATE OR REPLACE DATABASE LINKEDIN;
CREATE OR REPLACE SCHEMA ANALYTICS;
ALTER WAREHOUSE COMPUTE_WH SET warehouse_size='SMALL';
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE LINKEDIN;
USE SCHEMA PUBLIC;  -- Correction: une seule ligne USE SCHEMA

-- ========================================
-- STAGE ET FILE FORMATS
-- ========================================
CREATE OR REPLACE STAGE linked_s3
  URL = 's3://snowflake-lab-bucket/'
  FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"' SKIP_HEADER = 1);

CREATE OR REPLACE FILE FORMAT csv_linkedin_format
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  RECORD_DELIMITER = '\n'
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '\042'
  NULL_IF = (''); 

CREATE OR REPLACE FILE FORMAT json_linkedin_format
  TYPE = JSON
  STRIP_OUTER_ARRAY = TRUE;

-- ========================================
-- TABLE COMPANIES 
-- ========================================
CREATE OR REPLACE TABLE companies_json (data VARIANT);

COPY INTO companies_json
FROM @linked_s3
FILE_FORMAT = json_linkedin_format
PATTERN = '.*\.json.*';

CREATE OR REPLACE TABLE companies (
    company_id BIGINT PRIMARY KEY,
    name VARCHAR,
    description TEXT,
    company_size INTEGER,
    state VARCHAR,
    country VARCHAR,
    city VARCHAR,
    zip_code VARCHAR,
    address VARCHAR,
    url VARCHAR,
    is_generated_id BOOLEAN
);

INSERT INTO companies
SELECT
    COALESCE(
        data:company_id::BIGINT, 
        -1 * ROW_NUMBER() OVER (ORDER BY data:name, data:url)
    ) AS company_id,
    data:name::VARCHAR AS name,
    data:description::TEXT AS description,
    data:company_size::INTEGER AS company_size,
    data:state::VARCHAR AS state,
    data:country::VARCHAR AS country,
    data:city::VARCHAR AS city,
    data:zip_code::VARCHAR AS zip_code,
    data:address::VARCHAR AS address,
    data:url::VARCHAR AS url,
    CASE WHEN data:company_id IS NULL THEN TRUE ELSE FALSE END AS is_generated_id
FROM companies_json;

-- ========================================
-- TABLE JOB_POSTINGS 
-- ========================================
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
    compensation_type VARCHAR,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

COPY INTO job_postings
FROM @linked_s3/job_postings.csv
FILE_FORMAT = csv_linkedin_format
ON_ERROR = 'CONTINUE';

-- ========================================
-- TABLES LIÉES AUX COMPANIES
-- ========================================

-- EMPLOYEE_COUNTS
CREATE OR REPLACE TABLE employee_counts (
    company_id BIGINT,
    employee_count INTEGER,
    follower_count INTEGER,
    time_recorded BIGINT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

COPY INTO employee_counts
FROM @linked_s3/employee_counts.csv
FILE_FORMAT = csv_linkedin_format
ON_ERROR = 'CONTINUE';

-- COMPANY_INDUSTRIES
CREATE OR REPLACE TABLE company_industries_json (data VARIANT);

COPY INTO company_industries_json
FROM @linked_s3/company_industries.json
FILE_FORMAT = json_linkedin_format;

CREATE OR REPLACE TABLE company_industries (
    company_id BIGINT,
    industry VARCHAR,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

INSERT INTO company_industries
SELECT
    data:company_id::BIGINT AS company_id,
    data:industry::VARCHAR AS industry
FROM company_industries_json
WHERE data:company_id IS NOT NULL 
  AND EXISTS (SELECT 1 FROM companies WHERE company_id = data:company_id::BIGINT);

-- COMPANY_SPECIALITIES
CREATE OR REPLACE TABLE company_specialities_json (data VARIANT);

COPY INTO company_specialities_json 
FROM @linked_s3/company_specialities.json 
FILE_FORMAT = json_linkedin_format;

CREATE OR REPLACE TABLE company_specialities (
    company_id BIGINT,
    speciality VARCHAR,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

INSERT INTO company_specialities
SELECT
    data:company_id::BIGINT AS company_id,
    data:speciality::VARCHAR AS speciality
FROM company_specialities_json
WHERE data:company_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM companies WHERE company_id = data:company_id::BIGINT);

-- ========================================
-- TABLES LIÉES AUX JOB_POSTINGS
-- ========================================

-- BENEFITS
CREATE OR REPLACE TABLE benefits (
    job_id BIGINT,
    inferred BOOLEAN,
    type VARCHAR,
    FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
);

COPY INTO benefits
FROM @linked_s3/benefits.csv
FILE_FORMAT = csv_linkedin_format
ON_ERROR = 'CONTINUE';

-- JOB_SKILLS
CREATE OR REPLACE TABLE job_skills (
    job_id BIGINT,
    skill_abr VARCHAR,
    FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
);

COPY INTO job_skills
FROM @linked_s3/job_skills.csv
FILE_FORMAT = csv_linkedin_format
ON_ERROR = 'CONTINUE';

-- JOB_INDUSTRIES
CREATE OR REPLACE TABLE job_industries_json (data VARIANT);

COPY INTO job_industries_json 
FROM @linked_s3/job_industries.json 
FILE_FORMAT = json_linkedin_format;

CREATE OR REPLACE TABLE job_industries (
    industry_id BIGINT,
    job_id BIGINT,
    FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
);

INSERT INTO job_industries
SELECT
    data:industry_id::BIGINT AS industry_id,
    data:job_id::BIGINT AS job_id
FROM job_industries_json
WHERE data:job_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM job_postings WHERE job_id = data:job_id::BIGINT);

-- ========================================
-- VÉRIFICATION FINALE
-- ========================================

-- Statistiques des tables
SELECT 'companies' AS table_name, COUNT(*) AS row_count FROM companies
UNION ALL
SELECT 'job_postings', COUNT(*) FROM job_postings
UNION ALL
SELECT 'benefits', COUNT(*) FROM benefits
UNION ALL
SELECT 'employee_counts', COUNT(*) FROM employee_counts
UNION ALL
SELECT 'job_skills', COUNT(*) FROM job_skills
UNION ALL
SELECT 'company_industries', COUNT(*) FROM company_industries
UNION ALL
SELECT 'job_industries', COUNT(*) FROM job_industries
UNION ALL
SELECT 'company_specialities', COUNT(*) FROM company_specialities;

