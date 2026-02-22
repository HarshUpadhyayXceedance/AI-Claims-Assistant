from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PayoutRequest:
    claim_id: str
    policy_id: str
    coverage_items: list[dict]


@dataclass
class PayoutResponse:
    gross_amount: float
    deductible: float
    net_amount: float
    ruleset_version: str


def calculate_payout(request: PayoutRequest) -> PayoutResponse:
    """Stub for deterministic payout engine integration.

    In production this would call a dedicated microservice with signed internal auth.
    """
    gross = sum(float(item.get("amount", 0)) for item in request.coverage_items)
    deductible = 500.0
    return PayoutResponse(
        gross_amount=gross,
        deductible=deductible,
        net_amount=max(gross - deductible, 0.0),
        ruleset_version="claims-rules-v1",
    )
