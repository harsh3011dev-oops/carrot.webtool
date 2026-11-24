"""
PROJECT NOVA - Intelligent Query Router (IQR) Schemas
Defines core data contracts, enums, and Pydantic models for routing decisions.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


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
    route: RouteType = Field(description="Target route for this specific sub-question")
    reasoning: str = Field(description="Why this specific route was selected")


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

