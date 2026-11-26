"""
PROJECT NOVA - Intelligent Query Router (IQR) Schemas
Defines core data contracts, enums, and Pydantic models for routing decisions.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, model_validator


class RouteType(str, Enum):
    """The four primary routing destinations in NOVA."""
    INTERNAL_LLM = "INTERNAL_LLM"      # Stable concepts, reasoning, code, math
    WEB_SEARCH = "WEB_SEARCH"          # Volatile facts, live events, fresh information
    INTERNAL_RAG = "INTERNAL_RAG"      # Private documents, user-uploaded PDFs
    HYBRID = "HYBRID"                  # Multi-part: combines concepts with live search/docs


class KnowledgeVolatility(str, Enum):
    """How quickly the factual state of this information changes over time."""
    VERY_LOW = "VERY_LOW"      # Math, physics laws, grammar, history
    LOW = "LOW"                # Established algorithms, core programming concepts
    MEDIUM = "MEDIUM"          # Company leadership, product features, regulations
    HIGH = "HIGH"              # Software version releases, current policies, news
    EXTREME = "EXTREME"        # Stock prices, weather, crypto, live game scores


class QueryIntent(str, Enum):
    """The fundamental goal of the user's query."""
    FACTUAL = "FACTUAL"
    CONCEPTUAL = "CONCEPTUAL"
    ANALYTICAL = "ANALYTICAL"
    CREATIVE = "CREATIVE"
    PROCEDURAL = "PROCEDURAL"
    CONVERSATIONAL = "CONVERSATIONAL"


class SubQueryPlan(BaseModel):
    """Atomic sub-query for hybrid / decomposed multi-part questions."""
    sub_query: str = Field(description="The atomic sub-question to answer")
    route: RouteType = Field(default=RouteType.WEB_SEARCH, description="Target route for this specific sub-question")
    reasoning: str = Field(default="Decomposed sub-query", description="Why this specific route was selected")

    @model_validator(mode="before")
    @classmethod
    def normalize_sub_query(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"sub_query": data, "route": RouteType.WEB_SEARCH, "reasoning": "Normalized from string"}
        if isinstance(data, dict):
            # Normalize route if string
            r = data.get("route")
            if isinstance(r, str):
                r_clean = r.strip().upper()
                if r_clean in RouteType.__members__:
                    data["route"] = RouteType[r_clean]
                else:
                    data["route"] = RouteType.WEB_SEARCH
        return data


class RoutingDecision(BaseModel):
    """
    Complete output of NOVA's Intelligent Query Routing engine.
    """
    original_query: str = Field(description="The original user question")
    primary_route: RouteType = Field(description="The chosen primary route")
    intent: QueryIntent = Field(description="Classified user intent")
    volatility: KnowledgeVolatility = Field(description="Estimated knowledge volatility")
    is_time_sensitive: bool = Field(description="Whether the query requires up-to-date real-time evidence")
    requires_citations: bool = Field(description="Whether factual claims must have traceable citations")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Routing confidence score")
    reasoning: str = Field(description="Clear explanation of why this route was selected")
    sub_queries: List[SubQueryPlan] = Field(default_factory=list, description="Decomposed sub-queries for hybrid tasks")
    search_queries: List[str] = Field(
        default_factory=list,
        description="1 to 3 crisp keyword-optimized search queries (if web retrieval is needed)"
    )
    tier_source: str = Field(default="TIER_1_SLM", description="Which tier made the decision: TIER_0_RULES, TIER_1_SLM, TIER_2_POLICY")

    @model_validator(mode="before")
    @classmethod
    def normalize_decision_fields(cls, data: Any) -> Any:
        """
        Defensive pre-validator for SLM output variability (e.g. Qwen 1.5B).
        Normalizes string sub_queries into canonical SubQueryPlan objects,
        normalizes enum string variations, and guarantees required fields.
        """
        if not isinstance(data, dict):
            return data

        # 1. Normalize sub_queries: convert raw strings to SubQueryPlan dicts
        raw_subs = data.get("sub_queries")
        if isinstance(raw_subs, list):
            norm_subs = []
            for item in raw_subs:
                if isinstance(item, str):
                    item_str = item.strip()
                    if item_str:
                        norm_subs.append({
                            "sub_query": item_str,
                            "route": RouteType.WEB_SEARCH,
                            "reasoning": "Normalized from string"
                        })
                elif isinstance(item, dict):
                    norm_subs.append(item)
            data["sub_queries"] = norm_subs
        elif raw_subs is None:
            data["sub_queries"] = []

        # 2. Normalize search_queries: ensure list of clean strings
        raw_searches = data.get("search_queries")
        if isinstance(raw_searches, list):
            data["search_queries"] = [str(s).strip() for s in raw_searches if str(s).strip()]
        elif isinstance(raw_searches, str):
            data["search_queries"] = [raw_searches.strip()] if raw_searches.strip() else []
        else:
            data["search_queries"] = []

        # 3. Normalize primary_route
        pr = data.get("primary_route")
        if isinstance(pr, str):
            pr_clean = pr.strip().upper()
            if pr_clean in RouteType.__members__:
                data["primary_route"] = RouteType[pr_clean]
            else:
                data["primary_route"] = RouteType.WEB_SEARCH

        # 4. Normalize intent
        it = data.get("intent")
        if isinstance(it, str):
            it_clean = it.strip().upper()
            if it_clean in QueryIntent.__members__:
                data["intent"] = QueryIntent[it_clean]
            else:
                data["intent"] = QueryIntent.FACTUAL

        # 5. Normalize volatility
        vol = data.get("volatility")
        if isinstance(vol, str):
            vol_clean = vol.strip().upper()
            if vol_clean in KnowledgeVolatility.__members__:
                data["volatility"] = KnowledgeVolatility[vol_clean]
            else:
                data["volatility"] = KnowledgeVolatility.MEDIUM

        # 6. Normalize confidence (ensure float between 0.0 and 1.0)
        conf = data.get("confidence")
        if conf is not None:
            try:
                data["confidence"] = max(0.0, min(1.0, float(conf)))
            except (ValueError, TypeError):
                data["confidence"] = 1.0

        return data


class FollowUpIntent(str, Enum):
    """Classification of multi-turn conversational follow-up intent."""
    NEW_TOPIC = "NEW_TOPIC"
    FOLLOW_UP = "FOLLOW_UP"
    ENTITY_CHANGE = "ENTITY_CHANGE"
    YEAR_CHANGE = "YEAR_CHANGE"
    EVENT_CHANGE = "EVENT_CHANGE"
    ATTRIBUTE_CHANGE = "ATTRIBUTE_CHANGE"
    AMBIGUOUS_FOLLOW_UP = "AMBIGUOUS_FOLLOW_UP"


class StructuredConversationState(BaseModel):
    """
    Maintains structured multi-turn conversation context across queries.
    Prevents context loss on short/elliptical follow-ups while isolating topic shifts.
    """
    active_topic: str = "GENERAL"
    active_entity: Optional[str] = None
    related_entities: List[str] = Field(default_factory=list)
    active_event: Optional[str] = None
    relevant_year: Optional[str] = None
    active_attribute: Optional[str] = None
    previous_user_question: Optional[str] = None
    previous_resolved_query: Optional[str] = None
    previous_answer: Optional[str] = None
    evidence_references: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    ambiguity_status: str = "CLEAR"  # "CLEAR" or "AMBIGUOUS"


