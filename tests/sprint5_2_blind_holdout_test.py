"""
PROJECT NOVA — SPRINT 5.2: Phase 1 Blind Holdout Evaluation Suite
================================================================
40 unseen factual questions across 8 domains (5 per domain):
1. Historical Events
2. Sports Records
3. Science & Technology
4. Product Specifications
5. Companies & Organizations
6. Temporal / Freshness
7. Numerical & Comparative
8. Multi-Turn Context

Strict Separation:
- DATASET_A: Only queries exposed to the orchestrator during processing.
- DATASET_B: Ground-truth validation rules isolated until post-generation.
"""

import os
import sys
import time
import json
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import NovaOrchestrator
from grounding.schemas import ResponseState, VerifiedResponse

# ============================================================================
# DATASET A: SYSTEM-FACING QUERIES (Zero ground-truth leaks)
# ============================================================================
DATASET_A_QUERIES = [
    # 1. Historical Events
    {"id": "HIST-01", "domain": "Historical", "query": "What year was the Magna Carta signed?"},
    {"id": "HIST-02", "domain": "Historical", "query": "What year was the Battle of Hastings fought?"},
    {"id": "HIST-03", "domain": "Historical", "query": "In what year did the Berlin Wall fall?"},
    {"id": "HIST-04", "domain": "Historical", "query": "What was the date of the Apollo 11 lunar touchdown?"},
    {"id": "HIST-05", "domain": "Historical", "query": "In what year did the Titanic sink?"},

    # 2. Sports Records
    {"id": "SPORT-01", "domain": "Sports", "query": "What is Usain Bolt's 100m world record time in seconds?"},
    {"id": "SPORT-02", "domain": "Sports", "query": "Who won the 2022 FIFA Men's World Cup final?"},
    {"id": "SPORT-03", "domain": "Sports", "query": "What was Donald Bradman's final Test cricket batting average?"},
    {"id": "SPORT-04", "domain": "Sports", "query": "In what year were the first modern Olympic Games held?"},
    {"id": "SPORT-05", "domain": "Sports", "query": "How many Wimbledon men's singles titles has Roger Federer won?"},

    # 3. Science & Technology
    {"id": "SCI-01", "domain": "Science", "query": "What is the speed of light in a vacuum in metres per second?"},
    {"id": "SCI-02", "domain": "Science", "query": "In what year did Alexander Fleming discover penicillin?"},
    {"id": "SCI-03", "domain": "Science", "query": "What is the atomic number of Gold in the periodic table?"},
    {"id": "SCI-04", "domain": "Science", "query": "When was the James Webb Space Telescope launched into space?"},
    {"id": "SCI-05", "domain": "Science", "query": "In what year did Emmanuelle Charpentier and Jennifer Doudna win the Nobel Prize for CRISPR?"},

    # 4. Product Specifications
    {"id": "PROD-01", "domain": "Product Specs", "query": "What was the official launch starting price of the base iPhone 15 in USD?"},
    {"id": "PROD-02", "domain": "Product Specs", "query": "What year was the Sony PlayStation 5 released?"},
    {"id": "PROD-03", "domain": "Product Specs", "query": "What is the screen size of the Nintendo Switch OLED model in inches?"},
    {"id": "PROD-04", "domain": "Product Specs", "query": "What is the EPA estimated range in miles for the standard Tesla Model 3 Rear-Wheel Drive?"},
    {"id": "PROD-05", "domain": "Product Specs", "query": "In what year did Apple announce the first Apple Silicon M1 chip?"},

    # 5. Companies & Organizations
    {"id": "CORP-01", "domain": "Companies", "query": "In what year was Google founded?"},
    {"id": "CORP-02", "domain": "Companies", "query": "Who is the Chief Executive Officer of Microsoft?"},
    {"id": "CORP-03", "domain": "Companies", "query": "In what year was the United Nations officially established?"},
    {"id": "CORP-04", "domain": "Companies", "query": "In which city is the headquarters of the World Health Organization located?"},
    {"id": "CORP-05", "domain": "Companies", "query": "Who founded Amazon in 1994?"},

    # 6. Temporal / Freshness
    {"id": "TEMP-01", "domain": "Temporal", "query": "Which country won the 2023 ICC Men's Cricket World Cup?"},
    {"id": "TEMP-02", "domain": "Temporal", "query": "Which city hosted the 2024 Summer Olympic Games?"},
    {"id": "TEMP-03", "domain": "Temporal", "query": "What date did India's Chandrayaan-3 land on the Moon?"},
    {"id": "TEMP-04", "domain": "Temporal", "query": "Which nation won the UEFA Euro 2024 football tournament?"},
    {"id": "TEMP-05", "domain": "Temporal", "query": "Which team won Super Bowl LVIII in February 2024?"},

    # 7. Numerical & Comparative
    {"id": "NUM-01", "domain": "Numerical", "query": "What is the official height of Mount Everest in meters?"},
    {"id": "NUM-02", "domain": "Numerical", "query": "What is the approximate maximum depth of the Mariana Trench in meters?"},
    {"id": "NUM-03", "domain": "Numerical", "query": "How many bones are in an adult human skeleton?"},
    {"id": "NUM-04", "domain": "Numerical", "query": "What is the approximate average distance from the Earth to the Sun in kilometers or miles?"},
    {"id": "NUM-05", "domain": "Numerical", "query": "What is the approximate diameter of the Earth at the equator in kilometers?"},

    # 8. Multi-Turn Context (Evaluated as Turn 1 -> Turn 2)
    {"id": "MULTI-01", "domain": "Multi-Turn", "turns": [
        "Who directed the movie Oppenheimer?",
        "In what year was it released?"
    ]},
    {"id": "MULTI-02", "domain": "Multi-Turn", "turns": [
        "Who is the Prime Minister of India?",
        "When did he first take office as Prime Minister?"
    ]},
    {"id": "MULTI-03", "domain": "Multi-Turn", "turns": [
        "Where were the 2020 Summer Olympics held?",
        "In what year did the games actually take place?"
    ]},
    {"id": "MULTI-04", "domain": "Multi-Turn", "turns": [
        "What was Apple's base smartphone released in September 2023?",
        "What was its launch starting price in US dollars?"
    ]},
    {"id": "MULTI-05", "domain": "Multi-Turn", "turns": [
        "Who won the ICC Men's Cricket World Cup in 2019?",
        "Who was their captain in that tournament?"
    ]},
]

# ============================================================================
# DATASET B: POST-EVALUATION GROUND TRUTH (Never exposed to generation)
# ============================================================================
DATASET_B_GROUND_TRUTH = {
    "HIST-01": {"required": ["1215"]},
    "HIST-02": {"required": ["1066"]},
    "HIST-03": {"required": ["1989"]},
    "HIST-04": {"required": ["1969", "july"]},
    "HIST-05": {"required": ["1912"]},

    "SPORT-01": {"required": ["9.58"]},
    "SPORT-02": {"required": ["argentina"]},
    "SPORT-03": {"required": ["99.94"]},
    "SPORT-04": {"required": ["1896"]},
    "SPORT-05": {"required": ["8"]},

    "SCI-01": {"required": ["299", "792", "458"]},
    "SCI-02": {"required": ["1928"]},
    "SCI-03": {"required": ["79"]},
    "SCI-04": {"required": ["2021", "december"]},
    "SCI-05": {"required": ["2020"]},

    "PROD-01": {"required": ["799"]},
    "PROD-02": {"required": ["2020"]},
    "PROD-03": {"required": ["7"]},
    "PROD-04": {"required": ["272"]},
    "PROD-05": {"required": ["2020"]},

    "CORP-01": {"required": ["1998"]},
    "CORP-02": {"required": ["satya nadella"]},
    "CORP-03": {"required": ["1945"]},
    "CORP-04": {"required": ["geneva"]},
    "CORP-05": {"required": ["bezos"]},

    "TEMP-01": {"required": ["australia"]},
    "TEMP-02": {"required": ["paris"]},
    "TEMP-03": {"required": ["23", "august", "2023"]},
    "TEMP-04": {"required": ["spain"]},
    "TEMP-05": {"required": ["kansas city chiefs"]},

    "NUM-01": {"any_of": ["8848", "8849"]},
    "NUM-02": {"any_of": ["10984", "10994", "10935", "11000", ["10", "9"], ["11", "000"]]}, # 10,984m - 11,000m
    "NUM-03": {"required": ["206"]},
    "NUM-04": {"any_of": ["149", "150", "93"]}, # 149.6m km or 93m miles (disjunctive alternative)
    "NUM-05": {"any_of": ["12742", "12756", ["12", "742"], ["12", "756"]]}, # 12,742km or 12,756km

    "MULTI-01": {"required": ["2023"]},
    "MULTI-02": {"required": ["2014"]},
    "MULTI-03": {"required": ["2021"]},
    "MULTI-04": {"required": ["799"]},
    "MULTI-05": {"required": ["morgan"]},
}


def evaluate_ground_truth(case_id: str, text: str) -> bool:
    """Evaluates whether the generated text satisfies ground truth criteria."""
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


def run_blind_holdout_evaluation():
    orchestrator = NovaOrchestrator(verifier_mode="hybrid")
    
    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.2: PHASE 1 BLIND HOLDOUT EVALUATION")
    print("   40 Unseen Factual Test Cases Across 8 Domains")
    print("=" * 70)

    results = []
    
    total_cases = len(DATASET_A_QUERIES)
    factual_correct_count = 0
    verified_state_count = 0
    partial_state_count = 0
    abstain_state_count = 0
    unverified_state_count = 0

    sum_claim_support = 0.0
    sum_citation_precision = 0.0
    sum_citation_coverage = 0.0
    sum_source_avail = 0.0
    latencies = []

    for idx, item in enumerate(DATASET_A_QUERIES, 1):
        case_id = item["id"]
        domain = item["domain"]
        
        # Reset orchestrator context for independent cases
        orchestrator.context_manager.clear()

        print(f"\n[{idx}/{total_cases}] Running {case_id} ({domain})...")
        t_start = time.time()

        if "turns" in item:
            # Multi-turn sequence
            verified = None
            for t_num, turn_q in enumerate(item["turns"], 1):
                print(f"  Turn {t_num}: {turn_q}")
                verified = orchestrator.process_query(turn_q)
            q_display = item["turns"][-1]
        else:
            q_display = item["query"]
            print(f"  Query: {q_display}")
            verified = orchestrator.process_query(q_display)

        t_elapsed = time.time() - t_start
        latencies.append(t_elapsed)

        final_text = verified.final_text if verified else ""
        state = verified.response_state if verified else ResponseState.ABSTAIN
        
        # Ground truth evaluation (Dataset B isolated post-generation)
        is_factual = evaluate_ground_truth(case_id, final_text)
        if is_factual:
            factual_correct_count += 1

        if state == ResponseState.VERIFIED:
            verified_state_count += 1
        elif state == ResponseState.PARTIAL:
            partial_state_count += 1
        elif state == ResponseState.ABSTAIN:
            abstain_state_count += 1
        elif state == ResponseState.UNVERIFIED:
            unverified_state_count += 1

        claim_supp = getattr(verified, "claim_support_rate", 1.0)
        cit_prec = getattr(verified, "citation_precision", 1.0)
        cit_cov = getattr(verified, "citation_coverage", 1.0)
        src_avail = getattr(verified, "source_availability", 1.0)

        sum_claim_support += claim_supp
        sum_citation_precision += cit_prec
        sum_citation_coverage += cit_cov
        sum_source_avail += src_avail

        print(f"  -> State: {state.value} | Factual Correct: {is_factual} | Latency: {t_elapsed:.2f}s")
        print(f"  -> Support Rate: {claim_supp:.1%} | Precision: {cit_prec:.1%} | Coverage: {cit_cov:.1%}")

        results.append({
            "case_id": case_id,
            "domain": domain,
            "query": q_display,
            "response_state": state.value,
            "factual_correct": is_factual,
            "latency": t_elapsed,
            "claim_support_rate": claim_supp,
            "citation_precision": cit_prec,
            "citation_coverage": cit_cov,
            "source_availability": src_avail,
            "final_text": final_text[:200]
        })

    # Summary Statistics
    avg_claim_support = (sum_claim_support / total_cases) * 100
    avg_citation_precision = (sum_citation_precision / total_cases) * 100
    avg_citation_coverage = (sum_citation_coverage / total_cases) * 100
    avg_source_avail = (sum_source_avail / total_cases) * 100
    factual_accuracy = (factual_correct_count / total_cases) * 100

    latencies_sorted = sorted(latencies)
    mean_lat = sum(latencies) / len(latencies)
    median_lat = latencies_sorted[len(latencies_sorted) // 2]
    p95_lat = latencies_sorted[int(len(latencies_sorted) * 0.95)]

    print("\n" + "=" * 70)
    print("   PHASE 1 BLIND HOLDOUT EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total Test Cases Evaluated : {total_cases}")
    print(f"Factual Correctness        : {factual_correct_count}/{total_cases} ({factual_accuracy:.1f}%)")
    print(f"Canonical States Breakdown : VERIFIED: {verified_state_count} | PARTIAL: {partial_state_count} | UNVERIFIED: {unverified_state_count} | ABSTAIN: {abstain_state_count}")
    print(f"Average Claim Support Rate : {avg_claim_support:.1f}%")
    print(f"Average Citation Precision : {avg_citation_precision:.1f}%")
    print(f"Average Citation Coverage  : {avg_citation_coverage:.1f}%")
    print(f"Average Source Availability: {avg_source_avail:.1f}%")
    print(f"Latency Distribution       : Mean: {mean_lat:.2f}s | Median: {median_lat:.2f}s | P95: {p95_lat:.2f}s")
    print("=" * 70)

    # Save results to json for report synthesis
    out_path = os.path.join(os.path.dirname(__file__), "sprint5_2_blind_holdout_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_cases": total_cases,
            "factual_accuracy": factual_accuracy,
            "states": {
                "VERIFIED": verified_state_count,
                "PARTIAL": partial_state_count,
                "UNVERIFIED": unverified_state_count,
                "ABSTAIN": abstain_state_count
            },
            "metrics": {
                "claim_support_rate": avg_claim_support,
                "citation_precision": avg_citation_precision,
                "citation_coverage": avg_citation_coverage,
                "source_availability": avg_source_avail,
                "mean_latency": mean_lat,
                "median_latency": median_lat,
                "p95_latency": p95_lat
            },
            "cases": results
        }, f, indent=2)
    print(f"Results recorded to {out_path}")

if __name__ == "__main__":
    run_blind_holdout_evaluation()

