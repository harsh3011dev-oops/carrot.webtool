"""
PROJECT NOVA - Strict Entity & Variant Matcher (Sprint 2)
=========================================================
Prevents entity substitution and variant confusion:
- Distinguishes base models from variants (iPhone 16 vs 16e, Galaxy S24 vs S24 Ultra)
- Distinguishes senior tournaments from youth/fringe categories (Asia Cup vs Blind/U19 Asia Cup)
- Extracts requested attributes (launch date, winner, score, full form, CEO)
"""

import logging
import re
from typing import List, Optional, Set
from pydantic import BaseModel, Field

logger = logging.getLogger("nova.entity_matcher")

KNOWN_VARIANTS = {
    "e", "pro", "max", "plus", "mini", "ultra", "lite", "fe", "se",
    "blind", "u19", "under-19", "rising stars", "women", "womens", "a"
}

KNOWN_PRODUCTS = {
    "iphone", "ipad", "macbook", "pixel", "galaxy", "playstation", "xbox",
    "gpt", "claude", "gemini", "llama", "deepseek", "qwen",
    "cpu", "processor", "gpu", "ram", "rom", "chandrayaan", "apollo"
}

KNOWN_COMPETITIONS = {
    "asia cup", "world cup", "champions trophy", "champions league",
    "ipl", "bbl", "psl", "premier league", "super bowl", "olympics"
}


class EntityProfile(BaseModel):
    """Structured representation of the core entity in a query or document."""
    raw_text: str
    base_name: str
    model_or_number: Optional[str] = None
    variant: Optional[str] = None
    year: Optional[str] = None
    requested_attribute: Optional[str] = None


class EntityMatchResult(BaseModel):
    """Evaluation result comparing query entity against candidate document."""
    is_match: bool
    has_variant_conflict: bool
    confidence: float
    score_delta: float
    reasoning: str


def extract_entity_profile(text: str) -> EntityProfile:
    """
    Parses text to extract base entity name, model/version number,
    specialized variant tags, year, and requested attribute.
    """
    clean = text.lower().strip()
    
    # 1. Detect Year (2000-2029 or 1970-1999)
    year = None
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", clean)
    if year_match:
        year = year_match.group(1)

    # 2. Detect Requested Attribute
    attr = None
    if re.search(r"\b(launch\s+date|release\s+date|when\s+was\s+it\s+(launched|released)|date\s+of\s+launch)\b", clean):
        attr = "launch_date"
    elif re.search(r"\b(landing\s+date|when\s+did\s+it\s+land|date\s+did\s+it\s+land|lunar\s+landing)\b", clean):
        attr = "landing_date"
    elif re.search(r"\b(clock\s+speed|ghz|mhz|frequency)\b", clean):
        attr = "clock_speed"
    elif re.search(r"\b(who\s+won|winner|champions|who\s+is\s+the\s+champion)\b", clean):
        attr = "winner"
    elif re.search(r"\b(final\s+score|score\s+of|scorecard)\b", clean):
        attr = "score"
    elif re.search(r"\b(full\s+form|what\s+does\s+\w+\s+stand\s+for|definition|primary\s+function)\b", clean):
        attr = "definition"
    elif re.search(r"\b(who\s+founded|founder|in\s+which\s+year\s+was\s+it\s+founded)\b", clean):
        attr = "founder"
    elif re.search(r"\b(closing\s+date|registration\s+date|deadline)\b", clean):
        attr = "registration_date"

    # 3. Detect Competitions / Tournaments
    for comp in KNOWN_COMPETITIONS:
        if comp in clean:
            # Check for variant (e.g. blind, u19, women)
            variant = None
            if "blind" in clean:
                variant = "blind"
            elif re.search(r"\b(u19|under-19|u-19)\b", clean):
                variant = "u19"
            elif "rising stars" in clean:
                variant = "rising stars"
            elif "women" in clean:
                variant = "women"

            return EntityProfile(
                raw_text=text,
                base_name=comp,
                model_or_number=None,
                variant=variant,
                year=year,
                requested_attribute=attr,
            )

    # 4. Detect Tech Products (e.g. iPhone 16, Galaxy S24, GPT-4)
    for prod in KNOWN_PRODUCTS:
        pattern = rf"\b{prod}\s*([a-z0-9\.\-]+)?\b"
        match = re.search(pattern, clean)
        if match:
            specifier = match.group(1) if match.group(1) else ""
            
            # Check for specific model number and variant
            # Examples: '16e', '16 pro', 'xr', '4o', '4.1', 's24'
            model = None
            variant = None
            
            # Sub-pattern: e.g. '16e' -> model='16', variant='e'
            model_variant_match = re.match(r"^(\d+)([a-z]+)$", specifier)
            if model_variant_match:
                model = model_variant_match.group(1)
                variant = model_variant_match.group(2)
            else:
                # E.g. '16 pro' or 'xr'
                words = specifier.split()
                if words:
                    model = words[0]
                    if len(words) > 1 and words[1] in KNOWN_VARIANTS:
                        variant = words[1]

            # Also check if variant appears nearby e.g. 'iphone 16 pro'
            for v in KNOWN_VARIANTS:
                if re.search(rf"\b{prod}\s+{model}\s+{v}\b", clean) or re.search(rf"\b{prod}\s+{v}\b", clean):
                    variant = v
                    break

            return EntityProfile(
                raw_text=text,
                base_name=prod,
                model_or_number=model,
                variant=variant,
                year=year,
                requested_attribute=attr,
            )

    # 5. Fallback for general entity (Filter out question stopwords to isolate real entity)
    stopwords = {
        "on", "what", "date", "did", "tell", "me", "which", "who", "when", "where",
        "how", "why", "find", "official", "announcement", "the", "in", "of", "a",
        "an", "for", "to", "is", "was", "are", "were", "and", "or", "exact", "maximum",
        "clock", "speed", "ghz", "mhz", "launch", "release", "winner", "founder", "price", "score"
    }
    meaningful_words = [w for w in re.findall(r"\b[a-zA-Z0-9\-]+\b", clean) if w not in stopwords and len(w) > 1]
    base = meaningful_words[0] if meaningful_words else clean
    return EntityProfile(
        raw_text=text,
        base_name=base,
        model_or_number=None,
        variant=None,
        year=year,
        requested_attribute=attr,
    )


def match_entity(query_profile: EntityProfile, candidate_title: str, candidate_text: str = "") -> EntityMatchResult:
    """
    Compares the entity from the query against a candidate article.
    Strictly checks for model, variant, and year match.
    Penalizes variant substitution (e.g. candidate is iPhone 16e when query is iPhone 16).
    """
    candidate_profile = extract_entity_profile(candidate_title)
    cand_lower = (candidate_title + " " + candidate_text[:400]).lower()

    # 1. Check Base Name Match
    if query_profile.base_name != "what" and query_profile.base_name not in cand_lower:
        return EntityMatchResult(
            is_match=False,
            has_variant_conflict=False,
            confidence=0.1,
            score_delta=-20.0,
            reasoning=f"Base entity '{query_profile.base_name}' not found in candidate title.",
        )

    # 2. Check Model / Number Mismatch (e.g. iPhone 16 vs iPhone 17)
    if query_profile.model_or_number:
        if candidate_profile.model_or_number and candidate_profile.model_or_number != query_profile.model_or_number:
            # Different model completely e.g. iPhone 17 instead of 16
            return EntityMatchResult(
                is_match=False,
                has_variant_conflict=True,
                confidence=0.1,
                score_delta=-35.0,
                reasoning=f"Model mismatch: query asked for {query_profile.base_name} {query_profile.model_or_number}, but candidate is {candidate_profile.model_or_number}.",
            )

    # 3. Check Variant Conflict (The iPhone 16 vs 16e and Asia Cup vs Blind bug!)
    # Case A: User wanted base model (variant is None), but Candidate has a specific variant (e.g. 16e, Pro, Blind)
    if query_profile.variant is None and candidate_profile.variant is not None:
        return EntityMatchResult(
            is_match=False,
            has_variant_conflict=True,
            confidence=0.2,
            score_delta=-30.0,
            reasoning=f"Variant conflict: User requested base {query_profile.base_name} {query_profile.model_or_number or ''}, but candidate discusses variant '{candidate_profile.variant}'.",
        )

    # Case B: User wanted specific variant (e.g. Pro), but Candidate is a different variant
    if query_profile.variant is not None and candidate_profile.variant is not None:
        if query_profile.variant != candidate_profile.variant:
            return EntityMatchResult(
                is_match=False,
                has_variant_conflict=True,
                confidence=0.1,
                score_delta=-35.0,
                reasoning=f"Variant mismatch: Requested '{query_profile.variant}', candidate is '{candidate_profile.variant}'.",
            )

    # 4. Check Year Conflict (if query explicitly specified a year e.g. 2023 World Cup vs 2024)
    if query_profile.year and candidate_profile.year:
        if query_profile.year != candidate_profile.year:
            # Different year tournament
            return EntityMatchResult(
                is_match=False,
                has_variant_conflict=True,
                confidence=0.3,
                score_delta=-20.0,
                reasoning=f"Year mismatch: Query specified {query_profile.year}, candidate is {candidate_profile.year}.",
            )

    # 5. Exact Match!
    bonus = 20.0
    if query_profile.model_or_number and query_profile.model_or_number in cand_lower:
        bonus += 10.0
    if query_profile.year and query_profile.year in cand_lower:
        bonus += 10.0

    return EntityMatchResult(
        is_match=True,
        has_variant_conflict=False,
        confidence=0.95,
        score_delta=bonus,
        reasoning=f"Exact entity match confirmed for '{query_profile.base_name} {query_profile.model_or_number or ''}'.",
    )
