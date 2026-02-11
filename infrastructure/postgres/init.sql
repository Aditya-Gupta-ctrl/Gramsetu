# PostgreSQL initialization script
# Creates database schema for GramSetu

-- Create tables
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY,
    vle_id VARCHAR(50) NOT NULL,
    citizen_name VARCHAR(200) NOT NULL,
    citizen_phone VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL,
    scheme VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    result_data JSONB
);

CREATE TABLE IF NOT EXISTS consent_records (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    citizen_phone VARCHAR(20) NOT NULL,
    vle_id VARCHAR(50) NOT NULL,
    consent_text TEXT NOT NULL,
    audio_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    scheme VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    service_name VARCHAR(50)
);

-- Create indices
CREATE INDEX idx_jobs_vle_id ON jobs(vle_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_consent_job_id ON consent_records(job_id);
CREATE INDEX idx_audit_job_id ON audit_logs(job_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gramsetu_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gramsetu_user;
