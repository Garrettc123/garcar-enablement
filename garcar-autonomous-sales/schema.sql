CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE deal_stage AS ENUM ('DISCOVERED','PITCHED','NEGOTIATING','CLOSED_WON','FULFILLED','SUPPRESSED');

CREATE TABLE IF NOT EXISTS suppression_list (
    domain VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255),
    reason VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS deals (
    lead_id VARCHAR(64) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    sku_id VARCHAR(64) NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents > 0),
    estimated_monthly_leak_usd INTEGER NOT NULL CHECK (estimated_monthly_leak_usd > 0),
    identified_bottlenecks JSONB NOT NULL DEFAULT '[]'::jsonb,
    confidence_score NUMERIC(4,3) NOT NULL CHECK (confidence_score >= 0.850),
    approval_id VARCHAR(128) UNIQUE NOT NULL,
    stripe_session_id VARCHAR(255),
    checkout_url TEXT NOT NULL,
    stage deal_stage NOT NULL DEFAULT 'PITCHED',
    last_message_id VARCHAR(255),
    portal_access_token VARCHAR(128),
    deliverable_markdown TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fulfilled_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS webhook_events (
    event_id VARCHAR(255) PRIMARY KEY,
    event_type VARCHAR(128) NOT NULL,
    lead_id VARCHAR(64) REFERENCES deals(lead_id),
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id VARCHAR(64) REFERENCES deals(lead_id),
    action VARCHAR(128) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deals_domain ON deals(domain);
CREATE INDEX IF NOT EXISTS idx_deals_email ON deals(contact_email);
CREATE INDEX IF NOT EXISTS idx_deals_stage ON deals(stage);
