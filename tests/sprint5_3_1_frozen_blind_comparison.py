"""
PROJECT NOVA — SPRINT 5.3.1: FROZEN BLIND DATASET COMPARISON SUITE
==================================================================
Runs the exact 40-case frozen blind dataset from Sprint 5.2.
Decomposes performance across:
1. Overall Factual Correctness
2. Numerical & Comparison
3. Multi-turn Context
4. Science & Technology
5. Companies & Organizations
6. Temporal / Freshness
7. Historical Events & Sports
8. Abstention Categorization (ABSTENTION_CORRECT vs ABSTENTION_FAILURE)
9. Truth State Distributions & Citation Metrics
Compares results directly with the Sprint 5.2 baseline (30/40, 75.0%).
"""

import os
import sys
import time
import json
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import NovaOrchestrator
from grounding.schemas import ResponseState, VerifiedResponse
from tests.sprint5_2_blind_holdout_test import (
    DATASET_A_QUERIES,
    DATASET_B_GROUND_TRUTH,
    evaluate_ground_truth
)

# Unanswerable or counterfactual test cases (for abstention classification)
UNANSWERABLE_OR_COUNTERFACTUAL_CASES = {
    "COUNTER-01", "COUNTER-02", "FUTURE-01"
}


def classify_abstention(case_id: str, state: ResponseState) -> str:
    """Distinguishes correct abstentions on unanswerable/counterfactual queries from retrieval failures."""
    if state != ResponseState.ABSTAIN:
        return "NON_ABSTENTION"
    if case_id in UNANSWERABLE_OR_COUNTERFACTUAL_CASES:
        return "ABSTENTION_CORRECT"
    return "ABSTENTION_FAILURE"


def run_frozen_blind_comparison():
    orchestrator = NovaOrchestrator(verifier_mode="hybrid")

    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.3.1: FROZEN BLIND DATASET COMPARISON")
    print("   40 Frozen Cases from Sprint 5.2 (Controlled Execution)")
    print("=" * 70)

    # Load baseline results from Sprint 5.2
    baseline_path = os.path.join(os.path.dirname(__file__), "sprint5_2_blind_holdout_results.json")
    baseline_data = {}
    if os.path.exists(baseline_path):
        with open(baseline_path, "r", encoding="utf-8") as f:
            baseline_data = json.load(f)

    baseline_cases_map = {c["case_id"]: c for c in baseline_data.get("cases", [])}

    results = []
    domain_stats = {}
    states_count = {"VERIFIED": 0, "PARTIAL": 0, "UNVERIFIED": 0, "ABSTAIN": 0}
    abstention_stats = {"ABSTENTION_CORRECT": 0, "ABSTENTION_FAILURE": 0}

    latencies = []
    factual_correct_count = 0
    sum_claim_support = 0.0
    sum_citation_precision = 0.0
    sum_citation_coverage = 0.0
    sum_source_avail = 0.0

    total_cases = len(DATASET_A_QUERIES)

    for idx, item in enumerate(DATASET_A_QUERIES, 1):
        case_id = item["id"]
        domain = item["domain"]
        
        # Reset orchestrator context for independent cases
        orchestrator.context_manager.clear()

        if domain not in domain_stats:
            domain_stats[domain] = {"total": 0, "correct": 0, "baseline_correct": 0}
        domain_stats[domain]["total"] += 1

        baseline_item = baseline_cases_map.get(case_id, {})
        if baseline_item.get("factual_correct"):
            domain_stats[domain]["baseline_correct"] += 1

        print(f"\n[{idx}/{total_cases}] Evaluating {case_id} ({domain})...", flush=True)

        start_time = time.time()

        if "query" in item:
            query = item["query"]
            print(f"  Query: {query}")
            verified = orchestrator.process_query(query)
            final_text = verified.final_text if verified else ""
        else:
            turns = item["turns"]
            final_text = ""
            verified = None
            for t_idx, turn_query in enumerate(turns, 1):
                print(f"  Turn {t_idx}: {turn_query}")
                verified = orchestrator.process_query(turn_query)
            final_text = verified.final_text if verified else ""

        elapsed = time.time() - start_time
        latencies.append(elapsed)

        is_correct = evaluate_ground_truth(case_id, final_text)
        if is_correct:
            factual_correct_count += 1
            domain_stats[domain]["correct"] += 1
            status_badge = "✓ FACTUAL"
        else:
            status_badge = "❌ INCORRECT"

        state = verified.response_state if verified else ResponseState.ABSTAIN
        states_count[state.value] = states_count.get(state.value, 0) + 1

        # Classify abstention
        abs_type = classify_abstention(case_id, state)
        if abs_type in abstention_stats:
            abstention_stats[abs_type] += 1

        c_support = verified.claim_support_rate if verified else 0.0
        c_prec = verified.citation_precision if verified else 0.0
        c_cov = verified.citation_coverage if verified else 0.0
        s_avail = verified.source_availability if verified else 0.0

        sum_claim_support += c_support
        sum_citation_precision += c_prec
        sum_citation_coverage += c_cov
        sum_source_avail += s_avail

        print(f"  Result: {status_badge} | State: {state.value} | Latency: {elapsed:.2f}s")
        print(f"  Sanitized Text: {final_text[:120]}...")

        results.append({
            "case_id": case_id,
            "domain": domain,
            "response_state": state.value,
            "factual_correct": is_correct,
            "baseline_correct": baseline_item.get("factual_correct", False),
            "baseline_state": baseline_item.get("response_state", "UNKNOWN"),
            "abstention_type": abs_type,
            "latency": round(elapsed, 2),
            "claim_support_rate": round(c_support, 3),
            "citation_precision": round(c_prec, 3),
            "citation_coverage": round(c_cov, 3),
            "source_availability": round(s_avail, 3),
            "final_text": final_text[:250],
        })

        # Save incremental progress
        out_file = os.path.join(os.path.dirname(__file__), "sprint5_3_1_frozen_blind_comparison_results.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({
                "progress": f"{idx}/{total_cases}",
                "factual_correct_so_far": factual_correct_count,
                "current_accuracy": round((factual_correct_count / idx) * 100, 2),
                "states": states_count,
                "abstention_classification": abstention_stats,
                "domain_breakdown": domain_stats,
                "cases": results,
            }, f, indent=2)

    # Summary calculations
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    accuracy = (factual_correct_count / total_cases) * 100
    baseline_accuracy = baseline_data.get("factual_accuracy", 75.0)

    comparison_report = {
        "evaluation_title": "PROJECT NOVA - SPRINT 5.3.1 FROZEN BLIND DATASET COMPARISON",
        "total_cases": total_cases,
        "factual_accuracy": round(accuracy, 2),
        "baseline_accuracy": baseline_accuracy,
        "accuracy_delta": round(accuracy - baseline_accuracy, 2),
        "states": states_count,
        "abstention_classification": abstention_stats,
        "domain_breakdown": domain_stats,
        "metrics": {
            "claim_support_rate": round((sum_claim_support / total_cases) * 100, 2),
            "citation_precision": round((sum_citation_precision / total_cases) * 100, 2),
            "citation_coverage": round((sum_citation_coverage / total_cases) * 100, 2),
            "source_availability": round((sum_source_avail / total_cases) * 100, 2),
            "mean_latency": round(avg_latency, 2),
        },
        "cases": results,
    }

    out_file = os.path.join(os.path.dirname(__file__), "sprint5_3_1_frozen_blind_comparison_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(comparison_report, f, indent=2)

    print("\n" + "=" * 70)
    print("   SPRINT 5.3.1 FROZEN BLIND COMPARISON RESULTS")
    print("=" * 70)
    print(f"  Current Factual Accuracy : {factual_correct_count}/{total_cases} ({accuracy:.1f}%)")
    print(f"  Sprint 5.2 Baseline      : 30/40 ({baseline_accuracy:.1f}%)")
    print(f"  Delta                    : {accuracy - baseline_accuracy:+.1f}%")
    print("\n  Domain Breakdown (Current vs Baseline):")
    for dom, s in domain_stats.items():
        curr_pct = (s["correct"] / s["total"]) * 100
        base_pct = (s["baseline_correct"] / s["total"]) * 100
        print(f"    • {dom:15s}: {s['correct']}/{s['total']} ({curr_pct:.1f}%) vs Baseline {s['baseline_correct']}/{s['total']} ({base_pct:.1f}%)")
    print(f"\n  Truth States: {states_count}")
    print(f"  Abstentions : {abstention_stats}")
    print(f"  Results saved to {out_file}")
    print("=" * 70)


if __name__ == "__main__":
    run_frozen_blind_comparison()

