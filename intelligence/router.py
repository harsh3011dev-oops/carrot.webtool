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
from pathlib import Path
from typing import Optional

from config import settings
from core.base_model import BaseLLMAdapter
from intelligence.schemas import KnowledgeVolatility, QueryIntent, RouteType, RoutingDecision, SubQueryPlan
from intelligence.signals import analyze_signals
from models.ollama_adapter import OllamaAdapter

logger = logging.getLogger("nova.router")

ROUTER_SYSTEM_PROMPT = """You are NOVA's Intelligent Query Routing Engine.
Your job is to analyze the user's natural language query and determine the optimal knowledge route.

AVAILABLE ROUTES:
1. INTERNAL_LLM:
   - Stable concepts, definitions, explanations, mathematics, reasoning, creative writing, programming algorithms.
   - Low or very low knowledge volatility (e.g. "What is photosynthesis?", "Explain quicksort", "What does 'current' mean in electrical circuits?").
   - Does NOT require external search.

2. WEB_SEARCH:
   - Time-sensitive facts, recent events, breaking news, leadership changes, current software versions, prices, weather.
   - High or extreme volatility (e.g. "Latest Bitcoin price", "Who won yesterday's match?", "Current CEO of Microsoft in 2026", "NASA Artemis launch updates").
   - When web search is needed, generate 1 to 3 crisp, keyword-optimized search queries (e.g., ["NASA Artemis launch date status", "Artemis 2 official announcement"]).

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
- SEARCH QUERIES MUST BE KEYWORDS ONLY. Never copy the conversational question with 'who is', 'what is', or question marks.
  Example: Query 'who is new mentor of chennai super kings?' -> search_queries: ['Chennai Super Kings new mentor', 'CSK mentor official announcement']
  Example: Query 'What is the current Bitcoin price?' -> search_queries: ['Bitcoin price USD live', 'BTC price today']

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
        cleaned_query = query.strip()
        logger.info(f"Routing query: '{cleaned_query}'")

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

        # Ensure search_queries are populated if route requires WEB_SEARCH
        if decision.primary_route in [RouteType.WEB_SEARCH, RouteType.HYBRID] and not decision.search_queries:
            decision.search_queries = [cleaned_query]

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

    def _create_fallback_decision(self, query: str, signals) -> RoutingDecision:
        """Safety fallback if model generation fails."""
        if signals.has_temporal_trigger:
            route = RouteType.WEB_SEARCH
            time_sensitive = True
            volatility = KnowledgeVolatility.HIGH
        else:
            route = RouteType.INTERNAL_LLM
            time_sensitive = False
            volatility = KnowledgeVolatility.LOW

        return RoutingDecision(
            original_query=query,
            primary_route=route,
            intent=QueryIntent.FACTUAL,
            volatility=volatility,
            is_time_sensitive=time_sensitive,
            requires_citations=time_sensitive,
            confidence=0.7,
            reasoning="Fallback decision triggered due to classification timeout/error.",
            tier_source="FALLBACK_POLICY",
            search_queries=[query] if time_sensitive else [],
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

