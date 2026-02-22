from __future__ import annotations

import time
from typing import Callable

from langgraph.graph import END, START, StateGraph

from app.langgraph.state import ClaimState

MAX_RETRIES_PER_NODE = 2
RETRIEVAL_CONF_THRESHOLD = 0.80
REVIEW_CONF_THRESHOLD = 0.75
FRAUD_HIGH_THRESHOLD = 0.85
SUPERVISOR_PAYOUT_THRESHOLD = 10000


def with_timeout_and_retry(node_name: str, fn: Callable[[ClaimState], ClaimState]) -> Callable[[ClaimState], ClaimState]:
    def _wrapped(state: ClaimState) -> ClaimState:
        attempts = state.retries.get(node_name, 0)
        started = time.time()
        try:
            result = fn(state)
            elapsed_ms = int((time.time() - started) * 1000)
            result.reasoning_trace.append(f"node={node_name} status=ok latency_ms={elapsed_ms}")
            return result
        except Exception as exc:
            attempts += 1
            state.retries[node_name] = attempts
            state.errors.append(f"{node_name} failed: {exc}")
            state.reasoning_trace.append(f"node={node_name} status=error retry={attempts}")
            if attempts <= MAX_RETRIES_PER_NODE:
                return _wrapped(state)
            state.escalate_to_human = True
            state.escalation_reason = f"{node_name}_retries_exceeded"
            return state

    return _wrapped


def parse_claim(state: ClaimState) -> ClaimState:
    return state


def retrieve_policy(state: ClaimState) -> ClaimState:
    return state


def evaluate_relevance(state: ClaimState) -> ClaimState:
    return state


def coverage_analysis(state: ClaimState) -> ClaimState:
    return state


def check_exclusions(state: ClaimState) -> ClaimState:
    return state


def fraud_risk_analysis(state: ClaimState) -> ClaimState:
    return state


def payout_calculation(state: ClaimState) -> ClaimState:
    """Call deterministic payout microservice; no LLM math allowed."""
    return state


def self_review(state: ClaimState) -> ClaimState:
    return state


def finalize_decision(state: ClaimState) -> ClaimState:
    if state.escalate_to_human:
        state.decision = "escalated"
    elif state.exclusion_applies:
        state.decision = "denied_exclusion"
    elif state.coverage_eligible:
        state.decision = "approved"
    else:
        state.decision = "manual_review"
    return state


def retrieval_gate(state: ClaimState) -> str:
    return "retrieve_policy" if state.retrieval_confidence < RETRIEVAL_CONF_THRESHOLD else "coverage_analysis"


def exclusion_gate(state: ClaimState) -> str:
    return "fraud_risk_analysis" if not state.exclusion_applies else "finalize_decision"


def fraud_gate(state: ClaimState) -> str:
    if state.fraud_risk_score >= FRAUD_HIGH_THRESHOLD:
        state.escalate_to_human = True
        state.escalation_reason = "high_fraud_risk"
        return "finalize_decision"
    return "payout_calculation"


def payout_gate(state: ClaimState) -> str:
    if state.payout_amount > SUPERVISOR_PAYOUT_THRESHOLD:
        state.escalate_to_human = True
        state.escalation_reason = "supervisor_threshold"
    return "self_review"


def review_gate(state: ClaimState) -> str:
    if state.review_confidence < REVIEW_CONF_THRESHOLD:
        return "coverage_analysis"
    return "finalize_decision"


def build_claim_graph():
    graph = StateGraph(ClaimState)

    graph.add_node("parse_claim", with_timeout_and_retry("parse_claim", parse_claim))
    graph.add_node("retrieve_policy", with_timeout_and_retry("retrieve_policy", retrieve_policy))
    graph.add_node("evaluate_relevance", with_timeout_and_retry("evaluate_relevance", evaluate_relevance))
    graph.add_node("coverage_analysis", with_timeout_and_retry("coverage_analysis", coverage_analysis))
    graph.add_node("check_exclusions", with_timeout_and_retry("check_exclusions", check_exclusions))
    graph.add_node("fraud_risk_analysis", with_timeout_and_retry("fraud_risk_analysis", fraud_risk_analysis))
    graph.add_node("payout_calculation", with_timeout_and_retry("payout_calculation", payout_calculation))
    graph.add_node("self_review", with_timeout_and_retry("self_review", self_review))
    graph.add_node("finalize_decision", with_timeout_and_retry("finalize_decision", finalize_decision))

    graph.add_edge(START, "parse_claim")
    graph.add_edge("parse_claim", "retrieve_policy")
    graph.add_edge("retrieve_policy", "evaluate_relevance")

    graph.add_conditional_edges("evaluate_relevance", retrieval_gate)
    graph.add_edge("coverage_analysis", "check_exclusions")
    graph.add_conditional_edges("check_exclusions", exclusion_gate)
    graph.add_conditional_edges("fraud_risk_analysis", fraud_gate)
    graph.add_conditional_edges("payout_calculation", payout_gate)
    graph.add_conditional_edges("self_review", review_gate)

    graph.add_edge("finalize_decision", END)

    return graph.compile()
