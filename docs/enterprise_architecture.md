# AI Claims Assistant Platform — Enterprise SaaS Blueprint

## 1) High-level architecture (diagram explained)

**Control plane + data plane split:**
- **Edge/API Layer:** API Gateway (WAF + rate limits + auth), Web App (customer/adjuster/supervisor), Partner API.
- **Application Services:**
  - Claim Intake Service (FastAPI)
  - Orchestration Service (LangGraph workers)
  - Retrieval Service (policy/endorsement search)
  - Payout Service (deterministic rules engine)
  - Fraud Service (ML inference + feature store)
  - Document Service (OCR + parsing + storage)
  - Notification Service (email/SMS/webhook)
  - Audit & Explainability Service
  - Tenant Admin/Billing Service
- **Data Layer:**
  - PostgreSQL (OLTP, multi-tenant logical isolation + RLS)
  - PGVector/Pinecone (tenant-isolated indexes)
  - Redis (workflow state, locks, idempotency)
  - Object Storage (claims docs/images/PDF decisions)
  - Event Bus (Kafka/SNS+SQS style) for async fan-out
- **Observability/SecOps:** OpenTelemetry collector, Prometheus/Grafana, SIEM, secrets vault, key management.

**Primary request flow:**
1. Claim submitted with files/images.
2. Intake writes canonical claim + emits `claim.received`.
3. LangGraph orchestrator executes RAG + corrective steps + self-review.
4. Deterministic payout microservice computes amount.
5. Fraud service computes risk.
6. Finalizer decides auto-approve/deny/escalate.
7. Decision package (reasoning, evidence, scores, versions) is persisted and exportable.

---

## 2) Microservices breakdown

1. **api-gateway**
   - JWT validation, RBAC claims, tenant routing, API throttling.
2. **claim-intake-service**
   - Claim CRUD, file upload pre-sign URLs, schema validation.
3. **orchestration-service**
   - LangGraph engine + retry/timeout/circuit breaker policies.
4. **retrieval-service**
   - Embedding + hybrid search (BM25+vector), re-ranking, corrective evaluation.
5. **policy-ingestion-service**
   - Policy parsing/chunking/versioning and tenant index build.
6. **payout-engine-service**
   - Deterministic rules; versioned rule sets; reproducible calculations.
7. **fraud-ml-service**
   - Feature extraction + model inference + SHAP explanations.
8. **document-intelligence-service**
   - OCR, invoice extraction, image damage classifier.
9. **audit-explainability-service**
   - Immutable event trail and explainability bundles.
10. **tenant-admin-billing-service**
   - Plans, usage metering (per claim), invoices, white-label settings.

---

## 3) Database schema design (core entities)

- `tenants(id, name, status, plan, created_at)`
- `users(id, tenant_id, email, role, mfa_enabled, status)`
- `policies(id, tenant_id, policy_number, version, effective_date, metadata_json)`
- `policy_chunks(id, tenant_id, policy_id, chunk_text, embedding_ref, checksum)`
- `claims(id, tenant_id, claimant_id, policy_id, status, submitted_at, channel, currency)`
- `claim_items(id, claim_id, type, amount_claimed, normalized_json)`
- `claim_documents(id, claim_id, doc_type, object_key, ocr_text, hash)`
- `retrieval_runs(id, claim_id, index_namespace, top_k, confidence, latency_ms)`
- `retrieval_evidence(id, retrieval_run_id, chunk_id, score, rank)`
- `ai_decisions(id, claim_id, decision, rationale_json, confidence, prompt_version, model_version)`
- `fraud_assessments(id, claim_id, model_version, score, reason_codes_json)`
- `payout_calculations(id, claim_id, ruleset_version, gross_amount, deductible, net_amount, breakdown_json)`
- `human_reviews(id, claim_id, reviewer_id, action, comment, override_payload_json)`
- `audit_events(id, tenant_id, claim_id, actor_type, actor_id, event_type, event_json, created_at)`
- `usage_metering(id, tenant_id, claim_id, tokens_in, tokens_out, vector_reads, amount_usd)`

**Multi-tenant pattern:** shared DB + strict `tenant_id` + PostgreSQL RLS; sensitive tenants can be moved to dedicated DB/index.

---

## 4) LangGraph production skeleton

See `backend/app/langgraph/state.py` and `backend/app/langgraph/workflow.py` for typed state, nodes, conditional edges, retries, timeout wrapper, and escalation routing.

---

## 5) API design (representative)

- `POST /v1/claims` submit claim
- `POST /v1/claims/{id}/documents:upload-url`
- `POST /v1/claims/{id}/run-ai`
- `GET /v1/claims/{id}`
- `GET /v1/claims/{id}/decision`
- `POST /v1/claims/{id}/override` supervisor override
- `POST /v1/claims/{id}/rerun` re-run orchestration
- `GET /v1/claims/{id}/explanations` evidence + confidence breakdown
- `GET /v1/admin/tenants` / `POST /v1/admin/tenants`
- `GET /v1/billing/usage`

---

## 6) Folder structure

```text
backend/
  app/
    api/routes/
    core/
    langgraph/
      nodes/
      state.py
      workflow.py
    models/
    services/
infra/
  terraform/
  k8s/
docs/
  enterprise_architecture.md
  runbooks/
frontend/
  apps/customer-portal
  apps/adjuster-dashboard
  apps/supervisor-dashboard
```

---

## 7) SaaS architecture breakdown

- **Tenant onboarding:** create tenant record, provision namespace/index, seed policy templates, configure model/provider limits, configure branding and SSO.
- **Tenant isolation:**
  - DB RLS + encryption-at-rest + per-tenant KMS keys for high tier.
  - Vector index namespace per tenant (`tenant_{id}_policy_{version}`).
  - Signed, scoped object-store paths (`tenant/{id}/claims/{claim_id}`).
- **Tenant-specific model config:**
  - Prompt templates, tool access, model allow-list, max token budgets.
- **White-label:** theming + custom domain + email templates per tenant.

---

## 8) Deployment strategy (dev/staging/prod)

- **Dev:** ephemeral env per PR, synthetic data.
- **Staging:** production-like data contracts, load/perf tests, chaos drills.
- **Prod:** blue/green or canary deploy, DB migration gates, model rollout with shadow mode.

---

## 9) Monitoring & observability

- SLIs: claim processing latency, auto-decision rate, escalation rate, retrieval precision proxy, fraud model drift.
- Tracing: end-to-end trace ID across services + workflow node spans.
- Alerts: payout anomaly spikes, fraud score distribution drift, index miss ratio, timeout rates.

---

## 10) Security & compliance

- SOC2/ISO27001-ready controls, encryption in transit/at rest.
- RBAC + ABAC, MFA, SSO (OIDC/SAML), least privilege IAM.
- PII minimization, retention policies, right-to-delete workflows.
- Prompt/response logging with redaction and legal hold.

---

## 11) Cost optimization

- Route simple claims to smaller models.
- Cache frequent retrievals by policy hash.
- Batch embedding jobs; compress vectors where possible.
- Hard token budgets and per-tenant spend guardrails.

---

## 12) Commercial viability

- **Pricing:** base platform fee + per-claim usage + premium fraud module.
- **Value:** faster cycle times, lower leakage, documented explainability for regulators.
- **Moat:** tenant-specific policy intelligence + deterministic payout + auditable AI chain.

---

## 13) Resume-level impact

- Demonstrate production concerns: RLS, auditability, deterministic payout microservice, HITL controls.
- Include reliability metrics, security posture, and measurable business KPIs.

---

## 14) Startup pitch framing

- “Stripe-for-claims-decisioning”: API-first, explainable, insurer-configurable AI co-pilot.
- Land with mid-size insurers via FNOL + triage, expand to full adjudication and fraud intelligence.
