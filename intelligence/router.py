"""
PROJECT NOVA - Intelligent Query Router (IQR) Engine
===================================================
Hybrid Multi-Stage Query Routing (HMSQR):
- Tier 0: 0ms Deterministic Heuristics
- Tier 1: SLM-driven Semantic Analysis & Volatility Scoring
- Tier 2: Hard Policy Overrides & Sub-Query Decomposition
- Dataset Logger: Automatically appends routing traces to data/routing_dataset.jsonl
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional

from config import settings
from core.base_model import BaseLLMAdapter
from intelligence.schemas import KnowledgeVolatility, QueryIntent, RouteType, RoutingDecision, SubQueryPlan
from intelligence.signals import analyze_signals
from models.ollama_adapter import OllamaAdapter

logger = logging.getLogger("nova.router")


def normalize_query(query: str) -> str:
    """
    Cleans typos, concatenated words, and punctuation to optimize search & routing.
    Examples:
      'wonlast' -> 'won last'
      'whois' -> 'who is'
      'whichis' -> 'which is'
      'whatis' -> 'what is'
      'tellme' -> 'tell me'
      'asiacup' -> 'asia cup'
      'inodi' -> 'in odi'
      'fastest200' -> 'fastest 200'
    """
    if not query:
        return ""

    text = query.strip()

    # 1. Split letter-number or number-letter boundaries (e.g. '200in' -> '200 in', 'odi2023' -> 'odi 2023')
    text = re.sub(r"([a-zA-Z]+)(\d+)", r"\1 \2", text)
    text = re.sub(r"(\d+)([a-zA-Z]+)", r"\1 \2", text)

    # 2. Specific domain & common concatenated words
    fused_pairs = [
        (r"\bwonlast\b", "won last"),
        (r"\blastwon\b", "last won"),
        (r"\bwhois\b", "who is"),
        (r"\bwhatis\b", "what is"),
        (r"\bwhichis\b", "which is"),
        (r"\btellme\b", "tell me"),
        (r"\bhowmany\b", "how many"),
        (r"\bhowmuch\b", "how much"),
        (r"\bscoreof\b", "score of"),
        (r"\bwinnerof\b", "winner of"),
        (r"\brecordof\b", "record of"),
        (r"\binodi\b", "in odi"),
        (r"\bintest\b", "in test"),
        (r"\bint20\b", "in t20"),
        (r"\basiacup\b", "asia cup"),
        (r"\bworldcup\b", "world cup"),
        (r"\blastmatch\b", "last match"),
        (r"\bnewmentor\b", "new mentor"),
        (r"\bcurrentscore\b", "current score"),
    ]
    for pattern, replacement in fused_pairs:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # 3. Clean up multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


ROUTER_SYSTEM_PROMPT = """You are NOVA's Intelligent Query Routing Engine.
Your job is to analyze the user's natural language query and determine the optimal knowledge route.

AVAILABLE ROUTES:
1. INTERNAL_LLM:
   - Stable concepts, definitions, explanations, mathematics, reasoning, creative writing, programming algorithms.
   - Low or very low knowledge volatility (e.g. "What is photosynthesis?", "Explain quicksort", "What does 'current' mean in electrical circuits?").
   - Does NOT require external search.

2. WEB_SEARCH:
   - Time-sensitive facts, recent events, sports results, tournament winners, breaking news, leadership changes, current software versions, prices, weather.
   - High or extreme volatility.
   - When web search is needed, generate 2 to 3 DIVERSE, targeted search queries covering different angles:
     Angle 1 (Canonical Outcome / Champions / Winners List): Official lists, historical records, or championship lists.
       * For tournaments/cups/records, ALWAYS include keywords like 'champions list', 'winners list', 'final scorecard', or 'record holder'.
       * Example: 'which team won last asia cup in cricket' -> 'Asia Cup cricket champions list winners'
     Angle 2 (Match Final / Result): The specific event final or climax.
       * Example: 'Asia Cup cricket final match winner result'
     Angle 3 (Disambiguated Context): Entity context with explicit sport / tournament name.
       * Example: 'Men Asia Cup cricket tournament history'
   - CRITICAL: Never generate a single query using only 'latest' (e.g. 'latest Asia Cup winner'), because search engines match fringe ongoing youth/blind tournaments or future schedules. Use 'champions list', 'winners list', 'final result' instead!

3. INTERNAL_RAG:
   - User's private or uploaded documents, internal company policies, resumes, personal notes.

4. HYBRID:
   - Multi-part queries requiring both conceptual understanding and external web/doc verification.
   - Decompose into distinct sub-queries.

KNOWLEDGE VOLATILITY GUIDELINES:
- Math / Physics / Grammar: VERY_LOW
- Algorithms / Core CS concepts: LOW
- Product specs / Company leadership / Laws: MEDIUM
- Software versions / Policy changes / News: HIGH
- Stock / Crypto prices / Live weather / Sports scores: EXTREME

CRITICAL PRINCIPLES:
- A query containing the word 'current' is NOT necessarily a web search if it refers to electrical current or general meaning!
- Distinguish between a conceptual question and a live fact question.
- SEARCH QUERIES MUST BE TARGETED KEYWORDS: Include the primary entities and the target outcome (e.g. 'winner', 'champions list', 'result', 'record holder').
"""


class IntelligentQueryRouter:
    """
    Orchestrates the multi-tier query routing pipeline.
    """

    def __init__(self, llm_adapter: Optional[BaseLLMAdapter] = None):
        # By default, use the fast Router SLM (Qwen 2.5 1.5B)
        self.llm = llm_adapter or OllamaAdapter(model_name=settings.ROUTER_MODEL)
        self.dataset_path = settings.DATA_DIR / "routing_dataset.jsonl"
        self._ensure_dataset_dir()

    def _ensure_dataset_dir(self):
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

    def route(self, query: str) -> RoutingDecision:
        """
        Executes the cascading routing pipeline:
        Tier 0 (Rules) -> Tier 1 (SLM Semantic) -> Tier 2 (Policy Gatekeeper)
        """
        cleaned_query = normalize_query(query)
        logger.info(f"Routing query: '{cleaned_query}' (original: '{query}')")

        # =========================================================================
        # TIER 0: Deterministic Signal & Rule Analysis (0ms Latency)
        # =========================================================================
        signal_result = analyze_signals(cleaned_query)
        if signal_result.is_conclusive and signal_result.decision:
            logger.info(f"Tier 0 Conclusive Route: {signal_result.decision.primary_route}")
            self._log_decision(signal_result.decision)
            return signal_result.decision

        # =========================================================================
        # TIER 1: Semantic SLM Classification (Knowledge Volatility & Decomposition)
        # =========================================================================
        user_prompt = f"Analyze and classify this query for routing:\nQuery: \"{cleaned_query}\""

        try:
            decision = self.llm.generate_structured(
                prompt=user_prompt,
                response_model=RoutingDecision,
                system_prompt=ROUTER_SYSTEM_PROMPT,
                temperature=settings.ROUTER_TEMPERATURE,
            )
            decision.tier_source = "TIER_1_SLM"
        except Exception as e:
            logger.error(f"Tier 1 SLM classification failed: {e}. Falling back to default policy.")
            # Fallback if SLM fails
            decision = self._create_fallback_decision(cleaned_query, signal_result)

        # =========================================================================
        # TIER 2: Hard Policy Gatekeeper & Freshness Overrides
        # =========================================================================
        decision = self._apply_policy_overrides(decision, signal_result)

        # Ensure search_queries are populated and multi-angled if route requires WEB_SEARCH
        if decision.primary_route in [RouteType.WEB_SEARCH, RouteType.HYBRID]:
            if not decision.search_queries:
                decision.search_queries = [cleaned_query]

            # Augment queries if looking for winner/champions/records
            norm_lower = cleaned_query.lower()
            needs_outcome_expansion = any(w in norm_lower for w in ["won", "winner", "champion", "champions", "record", "score", "cup", "trophy", "final"])
            has_list_query = any(any(k in sq.lower() for k in ["champions list", "winners list", "record holder", "scorecard", "final result", "winners"]) for sq in decision.search_queries)

            if needs_outcome_expansion and not has_list_query:
                # Add a high-precision canonical list query
                canonical = re.sub(r"^(who\s+won|which\s+team\s+won|tell\s+me\s+who\s+has\s+the\s+record\s+of|what\s+is\s+the\s+score\s+of)\s*", "", cleaned_query, flags=re.IGNORECASE).strip()
                if "cup" in norm_lower or "trophy" in norm_lower or "tournament" in norm_lower:
                    decision.search_queries.append(f"{canonical} champions list winners")
                elif "record" in norm_lower:
                    decision.search_queries.append(f"{canonical} record holder")
                elif "score" in norm_lower:
                    decision.search_queries.append(f"{canonical} scorecard live match result")

            # Deduplicate while preserving order, cap at 3
            seen = set()
            unique_queries = []
            for q in decision.search_queries:
                q_clean = q.strip()
                if q_clean and q_clean.lower() not in seen:
                    seen.add(q_clean.lower())
                    unique_queries.append(q_clean)
            decision.search_queries = unique_queries[:3]

        # Log decision to training dataset for future custom model fine-tuning
        self._log_decision(decision)

        return decision

    def _apply_policy_overrides(self, decision: RoutingDecision, signals) -> RoutingDecision:
        """
        Enforces safety and correctness policies:
        - If query has explicit temporal trigger (e.g. 'latest in 2026') but was routed to INTERNAL,
          override to WEB_SEARCH.
        - High volatility facts (stock/weather/versions) MUST route to WEB_SEARCH.
        """
        # Policy A: Explicit Freshness Override
        if signals.has_temporal_trigger and decision.primary_route == RouteType.INTERNAL_LLM:
            decision.primary_route = RouteType.WEB_SEARCH
            decision.is_time_sensitive = True
            decision.requires_citations = True
            decision.tier_source = "TIER_2_POLICY_OVERRIDE"
            decision.reasoning += " [Policy Override: Query contains explicit temporal markers requiring fresh web evidence.]"
            if not decision.search_queries:
                decision.search_queries = [decision.original_query]

        # Policy B: Extreme Volatility Protection
        if decision.volatility == KnowledgeVolatility.EXTREME and decision.primary_route == RouteType.INTERNAL_LLM:
            decision.primary_route = RouteType.WEB_SEARCH
            decision.is_time_sensitive = True
            decision.requires_citations = True
            decision.tier_source = "TIER_2_POLICY_OVERRIDE"
            decision.reasoning += " [Policy Override: Extreme knowledge volatility mandates external verification.]"

        # Policy C: Private Document Protection
        if signals.has_document_trigger and decision.primary_route == RouteType.INTERNAL_LLM:
            decision.primary_route = RouteType.INTERNAL_RAG
            decision.tier_source = "TIER_2_POLICY_OVERRIDE"

        return decision

    def _create_fallback_decision(self, query: str, signals, reason: str = "SLM validation failure") -> RoutingDecision:
        """
        Failure-specific deterministic fallback policy:
        Treats document triggers, code/math queries, and temporal queries distinctly.
        """
        if signals.has_document_trigger:
            return RoutingDecision(
                original_query=query,
                primary_route=RouteType.INTERNAL_RAG,
                intent=QueryIntent.FACTUAL,
                volatility=KnowledgeVolatility.MEDIUM,
                is_time_sensitive=False,
                requires_citations=True,
                confidence=0.85,
                reasoning=f"Deterministic fallback ({reason}): User query references attached document/file.",
                tier_source="FALLBACK_DOCUMENT_POLICY",
                search_queries=[],
            )

        if signals.has_temporal_trigger:
            return RoutingDecision(
                original_query=query,
                primary_route=RouteType.WEB_SEARCH,
                intent=QueryIntent.FACTUAL,
                volatility=KnowledgeVolatility.HIGH,
                is_time_sensitive=True,
                requires_citations=True,
                confidence=0.80,
                reasoning=f"Deterministic fallback ({reason}): Query contains temporal freshness triggers.",
                tier_source="FALLBACK_TEMPORAL_POLICY",
                search_queries=[query],
            )

        # General safety default for factual uncertainty
        return RoutingDecision(
            original_query=query,
            primary_route=RouteType.WEB_SEARCH,
            intent=QueryIntent.FACTUAL,
            volatility=KnowledgeVolatility.MEDIUM,
            is_time_sensitive=True,
            requires_citations=True,
            confidence=0.75,
            reasoning=f"Deterministic fallback ({reason}): Defaulting safely to external retrieval.",
            tier_source="FALLBACK_DEFAULT_POLICY",
            search_queries=[query],
        )

    def _log_decision(self, decision: RoutingDecision):
        """
        Persists every routing decision as a JSONL entry.
        Builds the 2,000-5,000 training dataset for your future proprietary model!
        """
        try:
            with open(self.dataset_path, "a", encoding="utf-8") as f:
                f.write(decision.model_dump_json() + "\n")
        except Exception as e:
            logger.warning(f"Failed to append to routing dataset: {e}")

