"""
PROJECT NOVA - SPRINT 5.3: END-TO-END BLIND EVALUATION SUITE
============================================================
Evaluates 20 unseen factual questions across:
- 10 Numerical & Comparison queries (Variant binding, measurement rounding, discrete counts)
- 10 Multi-Turn contextual conversations (Pronoun resolution, entity retention, year swaps)

Executed end-to-end through NovaOrchestrator:
- Router: qwen2.5:1.5b
- Synthesizer: qwen2.5-coder:latest
- Verifier: hybrid ClaimVerifier (Proposition proximity + Variant binding + Measurement tolerance)
- Context: ConversationContextManager (Intent classification + Structured state)
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import NovaOrchestrator
from grounding.schemas import ResponseState

DATASET_A_BLIND_CASES = [
    # -------------------------------------------------------------------------
    # 10 Numerical & Comparison Queries
    # -------------------------------------------------------------------------
    {"id": "BLIND-NUM-01", "type": "single", "domain": "Numerical", "query": "What is the speed of sound in dry air at 20 degrees Celsius in meters per second?"},
    {"id": "BLIND-NUM-02", "type": "single", "domain": "Numerical", "query": "What is the boiling point of water in Fahrenheit at standard atmospheric pressure?"},
    {"id": "BLIND-NUM-03", "type": "single", "domain": "Numerical", "query": "What is the approximate average distance from the Earth to the Moon in kilometers?"},
    {"id": "BLIND-NUM-04", "type": "single", "domain": "Numerical", "query": "What was the launch price of the Sony PlayStation 5 Digital Edition in US dollars at release?"},
    {"id": "BLIND-NUM-05", "type": "single", "domain": "Numerical", "query": "What was the final score of the 2014 FIFA World Cup semi-final match between Germany and Brazil?"},
    {"id": "BLIND-NUM-06", "type": "single", "domain": "Numerical", "query": "What is the maximum depth of the Mariana Trench Challenger Deep in meters?"},
    {"id": "BLIND-NUM-07", "type": "single", "domain": "Numerical", "query": "What is the total architectural height of the Burj Khalifa in meters?"},
    {"id": "BLIND-NUM-08", "type": "single", "domain": "Numerical", "query": "How many chambers are there in a human heart?"},
    {"id": "BLIND-NUM-09", "type": "single", "domain": "Numerical", "query": "What is the EPA estimated range of the Tesla Model 3 Long Range AWD in miles?"},
    {"id": "BLIND-NUM-10", "type": "single", "domain": "Numerical", "query": "What is the atomic number of Carbon in the periodic table?"},

    # -------------------------------------------------------------------------
    # 10 Multi-Turn Context Conversations
    # -------------------------------------------------------------------------
    {"id": "BLIND-MULTI-01", "type": "multi", "domain": "Multi-Turn", "turns": [
        "Who directed the movie Interstellar?",
        "In what year was it released?"
    ]},
    {"id": "BLIND-MULTI-02", "type": "multi", "domain": "Multi-Turn", "turns": [
        "What company manufactures the Pixel smartphone?",
        "Where are they headquartered?"
    ]},
    {"id": "BLIND-MULTI-03", "type": "multi", "domain": "Multi-Turn", "turns": [
        "Who won the FIFA Men's World Cup in 2018?",
        "Who was their manager or head coach in that tournament?"
    ]},
    {"id": "BLIND-MULTI-04", "type": "multi", "domain": "Multi-Turn", "turns": [
        "What was Apple's base smartphone released in September 2023?",
        "What was its launch starting price in US dollars?"
    ]},
    {"id": "BLIND-MULTI-05", "type": "multi", "domain": "Multi-Turn", "turns": [
        "Which city hosted the 2016 Summer Olympics?",
        "What about in 2020?"
    ]},
    {"id": "BLIND-MULTI-06", "type": "multi", "domain": "Multi-Turn", "turns": [
        "Who is the CEO of Apple?",
        "In what year did he become CEO?"
    ]},
    {"id": "BLIND-MULTI-07", "type": "multi", "domain": "Multi-Turn", "turns": [
        "Who won the ICC Men's Cricket World Cup in 2011?",
        "Who was the runner-up in that final?"
    ]},
    {"id": "BLIND-MULTI-08", "type": "multi", "domain": "Multi-Turn", "turns": [
        "What is the highest mountain above sea level on Earth?",
        "What is its official elevation in meters?"
    ]},
    {"id": "BLIND-MULTI-09", "type": "multi", "domain": "Multi-Turn", "turns": [
        "In what year was the original first Apple iPhone released?",
        "What about the iPhone 15?"
    ]},
    {"id": "BLIND-MULTI-10", "type": "multi", "domain": "Multi-Turn", "turns": [
        "Who was the first astronaut to walk on the Moon?",
        "In what year did he walk on the Moon?"
    ]},
]

# Post-Evaluation Ground Truth (Dataset B)
DATASET_B_GROUND_TRUTH = {
    "BLIND-NUM-01": {"any_of": ["343", "340", "344"]},
    "BLIND-NUM-02": {"required": ["212"]},
    "BLIND-NUM-03": {"any_of": ["384", "385", ["384", "400"]]},
    "BLIND-NUM-04": {"required": ["399"]},
    "BLIND-NUM-05": {"any_of": [["7", "1"], ["7-1"], ["1-7"]]},
    "BLIND-NUM-06": {"any_of": ["109", "10984", "10994", "10935", "11000", "11 000", "35876", "36000"]},
    "BLIND-NUM-07": {"required": ["828"]},
    "BLIND-NUM-08": {"any_of": ["4", "four"]},
    "BLIND-NUM-09": {"any_of": ["341", "321", "346"]},
    "BLIND-NUM-10": {"required": ["6"]},

    "BLIND-MULTI-01": {"required": ["2014"]},
    "BLIND-MULTI-02": {"any_of": ["mountain view", "california", "silicon valley"]},
    "BLIND-MULTI-03": {"any_of": ["deschamps", "didier"]},
    "BLIND-MULTI-04": {"required": ["799"]},
    "BLIND-MULTI-05": {"required": ["tokyo"]},
    "BLIND-MULTI-06": {"required": ["2011"]},
    "BLIND-MULTI-07": {"any_of": ["sri lanka", "lanka"]},
    "BLIND-MULTI-08": {"any_of": ["8848", "8849"]},
    "BLIND-MULTI-09": {"required": ["2023"]},
    "BLIND-MULTI-10": {"required": ["1969"]},
}


def evaluate_ground_truth(case_id: str, text: str) -> bool:
    clean_text = text.lower().replace(",", "")
    gt = DATASET_B_GROUND_TRUTH.get(case_id)
    if not gt:
        return True
    if "any_of" in gt:
        for opt in gt["any_of"]:
            if isinstance(opt, list):
                if all(r.lower() in clean_text for r in opt):
                    return True
            else:
                if str(opt).lower() in clean_text:
                    return True
        return False
    if "required" in gt:
        return all(r.lower() in clean_text for r in gt["required"])
    return True


def run_blind_validation():
    print("\n" + "=" * 75)
    print("   PROJECT NOVA — SPRINT 5.3: END-TO-END BLIND VALIDATION SUITE")
    print("   20 Unseen Numerical & Multi-Turn Factual Evaluation Scenarios")
    print("=" * 75)

    orchestrator = NovaOrchestrator(verifier_mode="hybrid")
    results = []

    total_cases = len(DATASET_A_BLIND_CASES)
    factual_correct = 0
    verified_count = 0
    partial_count = 0
    unverified_count = 0
    abstain_count = 0

    sum_claim_support = 0.0
    sum_citation_precision = 0.0
    sum_citation_coverage = 0.0
    sum_source_avail = 0.0
    latencies = []

    num_total = 0
    num_correct = 0
    multi_total = 0
    multi_correct = 0

    for idx, item in enumerate(DATASET_A_BLIND_CASES, 1):
        case_id = item["id"]
        c_type = item["type"]
        domain = item["domain"]

        orchestrator.context_manager.clear()
        start_time = time.time()

        print(f"\n[{idx}/{total_cases}] Running {case_id} ({domain})...")

        if c_type == "single":
            query = item["query"]
            print(f"  Query: {query}")
            verified = orchestrator.process_query(query)
            final_text = verified.final_text if verified else ""
            elapsed = time.time() - start_time
            latencies.append(elapsed)

            is_correct = evaluate_ground_truth(case_id, final_text)
            num_total += 1
            if is_correct:
                num_correct += 1

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
            multi_total += 1
            if is_correct:
                multi_correct += 1

        state = verified.response_state if verified else ResponseState.ABSTAIN
        if is_correct:
            factual_correct += 1
            status_badge = "✓ FACTUAL"
        else:
            status_badge = "❌ INCORRECT"

        if state == ResponseState.VERIFIED:
            verified_count += 1
        elif state == ResponseState.PARTIAL:
            partial_count += 1
        elif state == ResponseState.UNVERIFIED:
            unverified_count += 1
        elif state == ResponseState.ABSTAIN:
            abstain_count += 1

        c_support = verified.claim_support_rate if verified else 0.0
        c_prec = verified.citation_precision if verified else 0.0
        c_cov = verified.citation_coverage if verified else 0.0
        s_avail = verified.source_availability if verified else 0.0

        sum_claim_support += c_support
        sum_citation_precision += c_prec
        sum_citation_coverage += c_cov
        sum_source_avail += s_avail

        print(f"  Result: {status_badge} | State: {state.value} | Latency: {elapsed:.2f}s")
        print(f"  Preview: {final_text[:140]}...")

        results.append({
            "case_id": case_id,
            "domain": domain,
            "response_state": state.value,
            "factual_correct": is_correct,
            "latency": round(elapsed, 2),
            "claim_support_rate": round(c_support, 3),
            "citation_precision": round(c_prec, 3),
            "citation_coverage": round(c_cov, 3),
            "source_availability": round(s_avail, 3),
            "final_text": final_text[:250],
        })

    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    accuracy = (factual_correct / total_cases) * 100
    num_acc = (num_correct / num_total * 100) if num_total else 0.0
    multi_acc = (multi_correct / multi_total * 100) if multi_total else 0.0

    print("\n" + "=" * 75)
    print("               PROJECT NOVA — SPRINT 5.3 BLIND VALIDATION SUMMARY")
    print("=" * 75)
    print(f"Total Evaluated Cases      : {total_cases}")
    print(f"Overall Factual Accuracy   : {factual_correct}/{total_cases} ({accuracy:.1f}%)")
    print(f"  • Numerical Accuracy     : {num_correct}/{num_total} ({num_acc:.1f}%) [Baseline was 40%]")
    print(f"  • Multi-Turn Accuracy    : {multi_correct}/{multi_total} ({multi_acc:.1f}%) [Baseline was 20%]")
    print("-" * 75)
    print("Canonical Response States:")
    print(f"  • VERIFIED               : {verified_count}/{total_cases} ({(verified_count/total_cases)*100:.1f}%)")
    print(f"  • PARTIAL                : {partial_count}/{total_cases} ({(partial_count/total_cases)*100:.1f}%)")
    print(f"  • UNVERIFIED             : {unverified_count}/{total_cases} ({(unverified_count/total_cases)*100:.1f}%)")
    print(f"  • ABSTAIN                : {abstain_count}/{total_cases} ({(abstain_count/total_cases)*100:.1f}%)")
    print("-" * 75)
    print("Evidentiary & Citation Metrics:")
    print(f"  • Claim Support Rate     : {(sum_claim_support / total_cases)*100:.1f}%")
    print(f"  • Citation Precision     : {(sum_citation_precision / total_cases)*100:.1f}%")
    print(f"  • Citation Coverage      : {(sum_citation_coverage / total_cases)*100:.1f}%")
    print(f"  • Source Availability    : {(sum_source_avail / total_cases)*100:.1f}%")
    print(f"  • Average End-to-End Latency: {avg_latency:.2f}s")
    print("=" * 75)

    # Save summary artifact
    output_path = "tests/sprint5_3_blind_evaluation_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "total_cases": total_cases,
            "factual_accuracy": round(accuracy, 1),
            "numerical_accuracy": round(num_acc, 1),
            "multi_turn_accuracy": round(multi_acc, 1),
            "states": {
                "VERIFIED": verified_count,
                "PARTIAL": partial_count,
                "UNVERIFIED": unverified_count,
                "ABSTAIN": abstain_count,
            },
            "metrics": {
                "claim_support_rate": round((sum_claim_support / total_cases), 3),
                "citation_precision": round((sum_citation_precision / total_cases), 3),
                "citation_coverage": round((sum_citation_coverage / total_cases), 3),
                "source_availability": round((sum_source_avail / total_cases), 3),
                "avg_latency": round(avg_latency, 2),
            },
            "cases": results,
        }, f, indent=2)
    print(f"\nDetailed evaluation results written to: {output_path}")

    # Integrity assertions
    assert accuracy >= 75.0, f"Expected overall accuracy >= 75.0%, got {accuracy:.1f}%"
    assert num_acc >= 70.0, f"Expected numerical accuracy >= 70.0%, got {num_acc:.1f}%"
    assert multi_acc >= 70.0, f"Expected multi-turn accuracy >= 70.0%, got {multi_acc:.1f}%"


if __name__ == "__main__":
    run_blind_validation()

