"""
PROJECT NOVA - Retrieval Quality Gatekeeper (Sprint 2)
======================================================
Multi-dimensional evidence gatekeeper:
1. Strict Entity & Variant Matching (iPhone 16 vs 16e, Senior vs Youth/Blind)
2. Decoupled Topic Relevance vs Answer Sufficiency Assessment
3. Semantic Date & Entity Attribution (Event date vs Publication date)
4. Domain Authority & Source Quality Ranking
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from retriever.entity_matcher import extract_entity_profile, match_entity, EntityProfile
from retriever.models import ExtractedDocument

logger = logging.getLogger("nova.gatekeeper")

# Tier-1 Authoritative and Primary Reference Domains
AUTHORITATIVE_DOMAINS = {
    "wikipedia.org": 15.0,
    "en.wikipedia.org": 15.0,
    "simple.wikipedia.org": 12.0,
    "whitehouse.gov": 15.0,
    "nasa.gov": 15.0,
    "esa.int": 15.0,
    "uefa.com": 15.0,
    "fifa.com": 15.0,
    "icc-cricket.com": 15.0,
    "espncricinfo.com": 14.0,
    "cricinfo.com": 14.0,
    "reuters.com": 12.0,
    "apnews.com": 12.0,
    "bbc.com": 12.0,
    "bloomberg.com": 12.0,
    "apple.com": 14.0,
    "microsoft.com": 14.0,
    "nvidia.com": 14.0,
    "thehindu.com": 10.0,
    "indianexpress.com": 10.0,
    "crictracker.com": 9.0,
}

# Generic aggregators or low-density repost blogs to penalize
AGGREGATOR_INDICATORS = [
    "tech.yahoo.com/articles",
    "news.yahoo.com/articles",
    "msn.com/en-",
    "aol.com",
    "newsnow.com",
    "dailyhunt.in",
]


COMMON_ACRONYMS = {
    "cpu": "central processing unit",
    "ram": "random access memory",
    "rom": "read only memory",
    "gpu": "graphics processing unit",
    "os": "operating system",
    "ai": "artificial intelligence",
    "ml": "machine learning",
}


def evaluate_relevance(query: str, doc: ExtractedDocument) -> float:
    """
    Evaluates whether the document discusses the query topic (0.0 to 100.0).
    Independent of whether it contains the exact final answer.
    """
    query_lower = query.lower()
    title_lower = doc.title.lower()
    url_lower = doc.url.lower()
    content_lower = doc.clean_text[:1200].lower()

    stopwords = {
        "which", "what", "who", "when", "where", "how", "tell", "me", "is", "was",
        "the", "in", "of", "a", "an", "for", "to", "and", "exact", "maximum", "did",
        "it", "does", "can", "you", "find", "official", "announcement", "component"
    }
    query_tokens = [w for w in re.findall(r"\b[a-zA-Z0-9\-]+\b", query_lower) if w not in stopwords and len(w) > 1]

    if not query_tokens:
        return 50.0

    # Title match (with acronym expansion support)
    title_matches = 0
    for t in query_tokens:
        if t in title_lower or (t in COMMON_ACRONYMS and COMMON_ACRONYMS[t] in title_lower):
            title_matches += 1

    # URL match
    url_matches = sum(1 for t in query_tokens if t in url_lower)

    # Content match
    content_matches = 0
    for t in query_tokens:
        if t in content_lower or (t in COMMON_ACRONYMS and COMMON_ACRONYMS[t] in content_lower):
            content_matches += 1

    # Base entity bonus
    profile = extract_entity_profile(query)
    base_bonus = 0.0
    if profile.base_name and (profile.base_name in title_lower or profile.base_name in url_lower):
        base_bonus += 20.0

    title_score = (title_matches / len(query_tokens)) * 45.0
    url_score = (url_matches / len(query_tokens)) * 20.0
    content_score = (content_matches / len(query_tokens)) * 35.0

    return min(100.0, title_score + url_score + content_score + base_bonus)


def evaluate_sufficiency(query: str, doc: ExtractedDocument, requested_attr: Optional[str] = None) -> Tuple[bool, float, str]:
    """
    Evaluates whether the document contains the required evidence to ANSWER the query.
    Decoupled from topic relevance.
    Example: A page about CPUs may be 100% relevant, but if the user asks for clock speed
    and no clock speed is present, sufficiency is False.
    """
    # 0. A completely off-topic document cannot be sufficient
    rel_score = evaluate_relevance(query, doc)
    if rel_score < 30.0:
        return False, 0.0, "Document is completely off-topic."

    text_lower = (doc.title + " " + doc.clean_text).lower()
    profile = extract_entity_profile(query)
    target_attr = requested_attr or profile.requested_attribute

    # 1. Launch Date / Release Date
    if target_attr == "launch_date":
        # Look for explicit date formats near release/launch keywords
        date_patterns = [
            r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(st|nd|rd|th)?,\s+\d{4}\b",
            r"\b\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b",
            r"\b(released|launched|announced|available)\s+(on|in)\s+[a-z0-9,\s]{3,25}\b",
        ]
        has_date_pattern = any(re.search(p, text_lower) for p in date_patterns)
        if has_date_pattern:
            return True, 85.0, "Document contains explicit release/launch date statements."
        return False, 20.0, "Document discusses entity but lacks specific release/launch dates."

    # 1B. Lunar / Planetary Landing Date
    if target_attr == "landing_date":
        if re.search(r"\b(land(ed|ing)?|touchdown)\b", text_lower) and re.search(r"\b\d{4}\b", text_lower):
            return True, 85.0, "Document contains landing date details."
        return False, 15.0, "Document lacks landing date details."

    # 1C. Clock Speed / Frequency
    if target_attr == "clock_speed":
        if re.search(r"\b(\d+(\.\d+)?\s*(ghz|mhz)|clock\s+speed)\b", text_lower):
            return True, 85.0, "Document contains clock speed/frequency specifications."
        return False, 15.0, "Document discusses architecture but lacks clock speed figures."

    # 2. Tournament Winner / Champion
    if target_attr == "winner":
        winner_patterns = [
            r"\b(won|winner|champions|defeated|beat|secured\s+their|title|lifted\s+the\s+trophy)\b",
            r"\b\d+[-–]\d+\b",  # Scores like 2-0
            r"\bby\s+\d+\s+(wickets|runs|goals)\b",
        ]
        has_winner = any(re.search(p, text_lower) for p in winner_patterns)
        if has_winner:
            return True, 90.0, "Document contains tournament winner/outcome statements."
        return False, 25.0, "Document discusses tournament but lacks final winner outcome."

    # 3. Match Final Score
    if target_attr == "score":
        score_patterns = [
            r"\b\d+\s*[-–]\s*\d+\b",
            r"\b\d+\s+for\s+\d+\b",
            r"\b\d+\s*runs\b",
            r"\b\d+\s*wickets\b",
        ]
        has_score = any(re.search(p, text_lower) for p in score_patterns)
        if has_score:
            return True, 90.0, "Document contains match scorecard details."
        return False, 20.0, "Document mentions match but lacks final numerical score."

    # 4. Definition / Full Form / Function
    if target_attr == "definition":
        def_patterns = [
            r"\b(stands\s+for|full\s+form|is\s+defined\s+as|is\s+the\s+primary|primary\s+function|responsible\s+for|executes?\s+instructions)\b",
            r"\b(central\s+processing\s+unit|random\s+access\s+memory|read\s+only\s+memory|graphics\s+processing)\b",
        ]
        has_def = any(re.search(p, text_lower) for p in def_patterns)
        if has_def:
            return True, 85.0, "Document contains definition / functional description."
        return False, 30.0, "Document mentions term but lacks definition or primary function."

    # 5. Founder / Founding Year
    if target_attr == "founder":
        founder_patterns = [
            r"\b(founded|co-founded|established|started)\s+(by|in|on)\b",
            r"\b(bill\s+gates|paul\s+allen|steve\s+jobs|elon\s+musk)\b",
            r"\b(19\d{2}|20\d{2})\b",
        ]
        has_founder = any(re.search(p, text_lower) for p in founder_patterns)
        if has_founder:
            return True, 90.0, "Document contains founder or founding year information."
        return False, 20.0, "Document mentions company but lacks founding history."

    # 6. Registration Date / Exam Schedule
    if target_attr == "registration_date":
        reg_patterns = [
            r"\b(registration|deadline|closing\s+date|last\s+date|session\s+1)\b",
            r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b",
        ]
        has_reg = any(re.search(p, text_lower) for p in reg_patterns)
        if has_reg:
            return True, 85.0, "Document contains registration schedule/dates."
        return False, 20.0, "Document discusses exam but lacks specific registration dates."

    # Default general sufficiency heuristic based on substantive word count
    if doc.word_count >= 60:
        return True, 60.0, "Document contains substantive textual coverage."
    return False, 30.0, "Document content is too sparse to verify answer."


def extract_attributed_event_date(entity_profile: EntityProfile, doc: ExtractedDocument) -> Optional[str]:
    """
    Disambiguates between the Article's Publication Date and the Entity's Event Date.
    Prevents assigning the article publication date (e.g. Feb 19, 2025) as a product's launch date.
    """
    text = doc.clean_text
    base = entity_profile.base_name.lower()
    model = (entity_profile.model_or_number or "").lower()

    # Look for sentences containing entity + release/launch verbs + date
    sentences = re.split(r"[.\n]", text)
    date_regex = re.compile(
        r"\b(?:on\s+)?((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4})\b",
        re.IGNORECASE
    )

    for s in sentences:
        s_lower = s.lower()
        entity_matches = (base in s_lower) or any(part in s_lower for part in base.split("-") if len(part) > 3)
        if entity_matches and (not model or model in s_lower):
            if any(v in s_lower for v in ["released", "launched", "announced", "available", "landed", "founded"]):
                m = date_regex.search(s)
                if m:
                    return m.group(1).strip()

    return None


def score_document(query: str, doc: ExtractedDocument) -> Tuple[float, Dict[str, Any]]:
    """
    Multi-Dimensional Composite Quality Scorer:
    Composite = (Entity Match * 0.35) + (Relevance * 0.25) + (Sufficiency * 0.25) + (Authority * 0.15)
    """
    query_profile = extract_entity_profile(query)
    
    # 1. Entity & Variant Match
    entity_result = match_entity(query_profile, doc.title, doc.clean_text)
    entity_score = 50.0 + entity_result.score_delta

    # 2. Topic Relevance
    relevance_score = evaluate_relevance(query, doc)

    # 3. Answer Sufficiency
    is_sufficient, sufficiency_score, suff_reason = evaluate_sufficiency(query, doc, query_profile.requested_attribute)

    # 4. Domain Authority
    domain_score = 0.0
    try:
        domain = urlparse(doc.url).netloc.lower()
        for auth_d, bonus in AUTHORITATIVE_DOMAINS.items():
            if auth_d in domain:
                domain_score = bonus * 5.0  # Scale up to ~75 max
                break
        # Aggregator penalty
        for agg in AGGREGATOR_INDICATORS:
            if agg in doc.url.lower():
                domain_score -= 20.0
                break
    except Exception:
        pass

    # Total weighted composite
    composite_score = (
        (entity_score * 0.35) +
        (relevance_score * 0.25) +
        (sufficiency_score * 0.25) +
        (domain_score * 0.15)
    )

    # Hard rejection penalty if there is a detected variant conflict (e.g. 16 vs 16e)
    if entity_result.has_variant_conflict:
        composite_score -= 40.0

    breakdown = {
        "entity_score": entity_score,
        "is_variant_conflict": entity_result.has_variant_conflict,
        "relevance_score": relevance_score,
        "is_sufficient": is_sufficient,
        "sufficiency_score": sufficiency_score,
        "domain_score": domain_score,
        "composite_score": composite_score,
        "reasoning": entity_result.reasoning,
    }
    return composite_score, breakdown


def filter_and_rank_documents(
    query: str,
    docs: List[ExtractedDocument],
    max_return: int = 3
) -> List[ExtractedDocument]:
    """
    Ranks documents by multi-dimensional composite score, filters out conflicting variants,
    and re-indexes contiguous source numbers [1], [2], [3]...
    """
    if not docs:
        return []

    scored_items = []
    for doc in docs:
        score, meta = score_document(query, doc)
        scored_items.append((score, doc, meta))

    # Sort descending by composite quality score
    scored_items.sort(key=lambda x: x[0], reverse=True)

    # Filter out documents with severe variant conflicts if we have clean candidates
    valid_candidates = [d for s, d, m in scored_items if not m["is_variant_conflict"]]
    if valid_candidates:
        selected = valid_candidates[:max_return]
    else:
        selected = [d for s, d, m in scored_items[:max_return]]

    final_docs = []
    for i, doc in enumerate(selected, start=1):
        doc.source_index = i
        final_docs.append(doc)

    return final_docs


def is_evidence_relevant(query: str, docs: List[ExtractedDocument], min_top_score: float = 40.0) -> bool:
    """
    Checks if at least one retrieved document is genuinely relevant to the query topic.
    """
    if not docs:
        return False
    scores = [evaluate_relevance(query, d) for d in docs]
    return max(scores) >= min_top_score


def is_evidence_sufficient(query: str, docs: List[ExtractedDocument]) -> Tuple[bool, str]:
    """
    Sprint 2 Decoupled Gatekeeper:
    Checks if the retrieved documents contain sufficient evidence to formulate the answer.
    """
    if not docs:
        return False, "No documents available."

    for doc in docs:
        is_suff, score, reason = evaluate_sufficiency(query, doc)
        if is_suff and score >= 70.0:
            return True, f"Found sufficient evidence in source [{doc.source_index}]: {reason}"

    return False, "Available documents lack the specific requested attribute."
