CREATE TABLE tenants (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL,
  plan TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE claims (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  policy_id TEXT NOT NULL,
  status TEXT NOT NULL,
  submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  channel TEXT NOT NULL,
  currency TEXT NOT NULL DEFAULT 'USD'
);

CREATE TABLE ai_decisions (
  id UUID PRIMARY KEY,
  claim_id UUID NOT NULL REFERENCES claims(id),
  decision TEXT NOT NULL,
  rationale_json JSONB NOT NULL,
  confidence NUMERIC(5,4) NOT NULL,
  fraud_score NUMERIC(5,4) NOT NULL,
  prompt_version TEXT NOT NULL,
  model_version TEXT NOT NULL,
  processing_ms INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_events (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  claim_id UUID,
  actor_type TEXT NOT NULL,
  actor_id TEXT,
  event_type TEXT NOT NULL,
  event_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
