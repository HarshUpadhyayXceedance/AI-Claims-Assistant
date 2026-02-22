from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ClaimState:
    claim_id: str
    tenant_id: str
    policy_id: str

    parsed_claim: dict[str, Any] = field(default_factory=dict)
    retrieved_clauses: list[dict[str, Any]] = field(default_factory=list)

    retrieval_confidence: float = 0.0
    review_confidence: float = 0.0
    fraud_risk_score: float = 0.0

    exclusion_applies: bool = False
    coverage_eligible: bool = False

    payout_amount: float = 0.0
    payout_currency: str = "USD"

    decision: str = "pending"
    escalate_to_human: bool = False
    escalation_reason: str | None = None

    reasoning_trace: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    retries: dict[str, int] = field(default_factory=dict)

    prompt_version: str = "claims-v1"
    model_version: str = "gpt-5.2-codex"
