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
    r"^(calculate|compute|solve|integrate|differentiate|what\s+is\s+the\s+derivative\s+of|evaluate|"
    r"what\s+is\s+[\d+\-*/\^().\s=x]+$|"
    r".*\b(\d+[\.\d]*)\s*(multiplied\s+by|times|divided\s+by|plus|minus|\+|\*|/|-)\s*(\d+[\.\d]*)|"
    r".*\b\d+%\s+of\s+\d+|"
    r".*\bconvert\s+[\d\.]+\s*(kilometres?|kilometers?|km|metres?|meters?|m|miles?|kg|grams?|pounds?|lbs?)\s+(in|into|to)\s+\w+|"
    r".*\bbinary\s+(number\s+)?[01]+\s+in\s+decimal|"
    r".*\bhow\s+many\s+sides\s+does\s+a\s+(triangle|quadrilateral|pentagon|hexagon|heptagon|octagon|nonagon|decagon)\s+have)",
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

# Static high-confidence facts & conceptual definitions for Tier-0 Fast-Path (0ms search latency)
STATIC_SCIENCE_PATTERNS = [
    r"chemical\s+formula\s+(of|for)\s+[\w\s]+",
    r"formula\s+(of|for)\s+(water|carbon\s+dioxide|salt|methane|glucose|ozone|table\s+salt)",
    r"((largest|smallest|hottest|coldest|closest|nearest)\s+planet|planet\s+(is\s+)?(the\s+)?(largest|smallest|hottest|coldest|closest|nearest))\s+(in|to)\s+(our\s+|the\s+)?(solar\s+system|earth|sun)",
    r"(speed\s+of\s+light|value\s+of\s+pi|atomic\s+number\s+of\s+\w+|boiling\s+point\s+of\s+\w+|freezing\s+point\s+of\s+\w+)",
    r"how\s+many\s+(planets|continents|bones\s+in\s+human\s+body)\b",
    r"photosynthesis(\s+in\s+simple\s+words)?",
    r"newton's\s+(first|second|third)\s+law(\s+of\s+motion)?",
]
STATIC_SCIENCE_REGEX = re.compile("|".join(STATIC_SCIENCE_PATTERNS), re.IGNORECASE)

STATIC_TECH_PATTERNS = [
    r"full\s+form\s+of\s+(cpu|ram|rom|gpu|html|http|https|api|url|bios|os|ip|tcp|udp|lan|wan|sql|ssd|hdd)",
    r"(primary|main)\s+function\s+of\s+(cpu|ram|rom|gpu|operating\s+system)",
    r"what\s+does\s+(a\s+)?(cpu|gpu|ram|rom)\s+do",
    r"difference\s+between\s+(an?\s+)?(ram\s+and\s+rom|tcp\s+and\s+udp|compiler\s+and\s+(an?\s+)?interpreter|ipv4\s+and\s+ipv6)",
    r"what\s+is\s+(the\s+difference\s+between\s+)?(ram|rom|cpu|gpu|binary\s+search|quicksort|merge\s+sort|bubble\s+sort|recursion)\b",
    r"define\s+an?\s+algorithm|what\s+is\s+an?\s+algorithm",
]
STATIC_TECH_REGEX = re.compile("|".join(STATIC_TECH_PATTERNS), re.IGNORECASE)

STATIC_GEO_PATTERNS = [
    r"capital\s+of\s+(france|germany|italy|spain|india|japan|australia|canada|brazil|russia|china|united\s+kingdom|uk|usa|united\s+states)",
    r"(highest\s+mountain|longest\s+river|deepest\s+ocean)\s+(in\s+the\s+world|on\s+earth)",
]
STATIC_GEO_REGEX = re.compile("|".join(STATIC_GEO_PATTERNS), re.IGNORECASE)


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

    # 4. Check for Static Science / Tech / Geography Fast-Path (0ms latency, zero search overhead)
    # Strict Guardrail: Temporal/freshness triggers MUST NOT be present
    has_temporal_guard = bool(TEMPORAL_REGEX.search(clean_query)) or bool(
        re.search(r"\b(202[4-9]|latest|today|yesterday|live|score|current|new|who\s+won)\b", clean_query, re.IGNORECASE)
    )
    if not has_temporal_guard:
        if STATIC_SCIENCE_REGEX.search(clean_query):
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
                    reasoning="Tier 0 Fast-Path: High-confidence static scientific fact resolves internally.",
                    tier_source="TIER_0_FAST_PATH",
                ),
                has_temporal_trigger=False,
            )

        if STATIC_TECH_REGEX.search(clean_query):
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
                    reasoning="Tier 0 Fast-Path: Standard technical concept/abbreviation definition resolves internally.",
                    tier_source="TIER_0_FAST_PATH",
                ),
                has_temporal_trigger=False,
            )

        if STATIC_GEO_REGEX.search(clean_query):
            return SignalAnalysis(
                is_conclusive=True,
                decision=RoutingDecision(
                    original_query=query,
                    primary_route=RouteType.INTERNAL_LLM,
                    intent=QueryIntent.FACTUAL,
                    volatility=KnowledgeVolatility.VERY_LOW,
                    is_time_sensitive=False,
                    requires_citations=False,
                    confidence=1.0,
                    reasoning="Tier 0 Fast-Path: Stable geographical/historical fact resolves internally.",
                    tier_source="TIER_0_FAST_PATH",
                ),
                has_temporal_trigger=False,
            )

    # 5. Check for Explicit Private Document triggers
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
