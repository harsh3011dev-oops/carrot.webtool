"""
PROJECT NOVA - Tier 0 Heuristic Signal Detector
Fast, regex-based, 0ms latency pre-classification.
Filters out obvious code, math, greetings, and private document queries before model inference.
"""

import re
from typing import Optional
from pydantic import BaseModel
from intelligence.schemas import KnowledgeVolatility, QueryIntent, RouteType, RoutingDecision


class SignalAnalysis(BaseModel):
    is_conclusive: bool = False
    decision: Optional[RoutingDecision] = None
    has_temporal_trigger: bool = False
    has_document_trigger: bool = False


# Regex patterns for deterministic checks
GREETING_PATTERN = re.compile(
    r"^(hi|hello|hey|good\s+(morning|afternoon|evening)|howdy|greetings|who\s+are\s+you|what\s+can\s+you\s+do)[\s!?.Ready]*$",
    re.IGNORECASE
)

DEFINITION_PATTERN = re.compile(
    r"^(what\s+does\s+(the\s+word\s+)?['\"]?(\w+)['\"]?\s+mean|define\s+['\"]?(\w+)['\"]?|definition\s+of\s+['\"]?(\w+)['\"]?)",
    re.IGNORECASE
)

MATH_PATTERN = re.compile(
    r"^(calculate|compute|solve|integrate|differentiate|what\s+is\s+the\s+derivative\s+of|evaluate|what\s+is\s+[\d+\-*/\^().\s=x]+$)",
    re.IGNORECASE
)

CODE_SYNTAX_PATTERN = re.compile(
    r"(\b(code|script|function|program|snippet|algo)\s+(for|to|in|of)\b|"
    r"^(give\s+me|write|create|provide|show\s+me|generate)\s+.*(code|function|program|script|snippet|implementation)|"
    r"how\s+to\s+(implement|write|code)|"
    r"palindrome|invert\s+binary\s+tree|quicksort|merge\s+sort|bubble\s+sort|reverse\s+(a\s+)?string|"
    r"regex\s+for|fix\s+(this\s+)?(error|bug|keyerror|syntaxerror|typeerror))",
    re.IGNORECASE
)

DOCUMENT_PATTERN = re.compile(
    r"(my\s+(uploaded\s+)?(pdf|document|file|notes|doc|resume)|in\s+the\s+attachment|summarize\s+this\s+file|according\s+to\s+my\s+doc)",
    re.IGNORECASE
)

# Strong temporal signals that indicate live internet search
TEMPORAL_PATTERNS = [
    r"\blatest\b",
    r"\btoday('s)?\b",
    r"\byesterday('s)?\b",
    r"\bright\s+now\b",
    r"\bwho\s+is\s+(the\s+)?(new|current)\b",
    r"\bnew\s+(mentor|coach|ceo|president|captain|leader|manager|signing|player|version|model|update|release|policy)\b",
    r"\bcurrent\s+(price|status|version|ceo|president|score|news|leader|release|mentor|coach)\b",
    r"\bbreaking\s+news\b",
    r"\blive\s+(score|updates?)\b",
    r"\bwho\s+won\s+the\b",
    r"\bweather\s+in\b",
    r"\bin\s+202[5-9]\b",  # Years 2025-2029 (post-cutoff)
]
TEMPORAL_REGEX = re.compile("|".join(TEMPORAL_PATTERNS), re.IGNORECASE)


def analyze_signals(query: str) -> SignalAnalysis:
    """
    Evaluates fast deterministic rules against the user query.
    Returns conclusive decision if possible, or flags signals for Tier 1 & 2.
    """
    clean_query = query.strip()
    
    # 1. Check for simple Conversational Greetings
    if GREETING_PATTERN.match(clean_query):
        return SignalAnalysis(
            is_conclusive=True,
            decision=RoutingDecision(
                original_query=query,
                primary_route=RouteType.INTERNAL_LLM,
                intent=QueryIntent.CONVERSATIONAL,
                volatility=KnowledgeVolatility.VERY_LOW,
                is_time_sensitive=False,
                requires_citations=False,
                confidence=1.0,
                reasoning="Tier 0: Conversational greeting does not require external retrieval.",
                tier_source="TIER_0_RULES",
            )
        )

    # 2. Check for Word Definitions / Language concepts (e.g. "What does the word current mean")
    if DEFINITION_PATTERN.search(clean_query) and not TEMPORAL_REGEX.search(clean_query):
        return SignalAnalysis(
            is_conclusive=True,
            decision=RoutingDecision(
                original_query=query,
                primary_route=RouteType.INTERNAL_LLM,
                intent=QueryIntent.CONCEPTUAL,
                volatility=KnowledgeVolatility.VERY_LOW,
                is_time_sensitive=False,
                requires_citations=False,
                confidence=1.0,
                reasoning="Tier 0: Linguistic definition / conceptual explanation of a word does not require live web search.",
                tier_source="TIER_0_RULES",
            )
        )

    # 3. Check for Math / Physics / Logic calculations
    if MATH_PATTERN.search(clean_query):
        return SignalAnalysis(
            is_conclusive=True,
            decision=RoutingDecision(
                original_query=query,
                primary_route=RouteType.INTERNAL_LLM,
                intent=QueryIntent.PROCEDURAL,
                volatility=KnowledgeVolatility.VERY_LOW,
                is_time_sensitive=False,
                requires_citations=False,
                confidence=1.0,
                reasoning="Tier 0: Pure mathematical / algorithmic logic can be resolved internally.",
                tier_source="TIER_0_RULES",
            )
        )

    # 3. Check for Code Generation / Algorithm implementation
    if CODE_SYNTAX_PATTERN.search(clean_query) and not TEMPORAL_REGEX.search(clean_query):
        return SignalAnalysis(
            is_conclusive=True,
            decision=RoutingDecision(
                original_query=query,
                primary_route=RouteType.INTERNAL_LLM,
                intent=QueryIntent.PROCEDURAL,
                volatility=KnowledgeVolatility.LOW,
                is_time_sensitive=False,
                requires_citations=False,
                confidence=0.98,
                reasoning="Tier 0: Standard code/algorithm implementation uses internal parametric knowledge.",
                tier_source="TIER_0_RULES",
            )
        )

    # 4. Check for Explicit Private Document triggers
    has_doc = bool(DOCUMENT_PATTERN.search(clean_query))
    if has_doc and not TEMPORAL_REGEX.search(clean_query):
        return SignalAnalysis(
            is_conclusive=True,
            decision=RoutingDecision(
                original_query=query,
                primary_route=RouteType.INTERNAL_RAG,
                intent=QueryIntent.FACTUAL,
                volatility=KnowledgeVolatility.MEDIUM,
                is_time_sensitive=False,
                requires_citations=True,
                confidence=0.95,
                reasoning="Tier 0: Explicit reference to user's uploaded document/file routes to Internal RAG.",
                tier_source="TIER_0_RULES",
            ),
            has_document_trigger=True,
        )

    # 5. Check for Temporal / Freshness triggers
    has_temporal = bool(TEMPORAL_REGEX.search(clean_query))

    return SignalAnalysis(
        is_conclusive=False,
        has_temporal_trigger=has_temporal,
        has_document_trigger=has_doc,
    )
