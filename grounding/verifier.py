"""
PROJECT NOVA - Post-Synthesis Claim Verifier & Truth Engine (Sprint 5)
=====================================================================
Audits LLM generated responses:
1. Decomposes answer into atomic factual propositions
2. Verifies each claim against localized proposition windows (eliminates global bag-of-words trap)
3. Enforces proposition proximity: entity, event context, and numerical values must co-occur
4. Detects factual contradictions across semantic windows
5. Audits bracketed citations [1], [2] for actual evidentiary support
6. Emits one of four canonical states: VERIFIED, PARTIAL, UNVERIFIED, ABSTAIN
7. Enforces Strict RAG vs Hybrid knowledge policies
"""

import logging
import re
from typing import Dict, List, Optional, Set, Tuple

from grounding.schemas import ClaimVerification, ResponseState, VerifiedResponse, StructuredNumericalClaim
from retriever.entity_matcher import extract_entity_profile
from retriever.models import ExtractedDocument

logger = logging.getLogger("nova.verifier")

ABSTAIN_PATTERNS = [
    "does not contain any information",
    "cannot provide an answer",
    "could not be confirmed",
    "no information about",
    "no information related to",
    "not contain sufficient information",
    "none of them address",
    "cannot be verified",
    "claim cannot be verified",
    "evidence does not contain",
    "insufficient information to answer",
]

STOPWORDS = {
    "the", "a", "an", "is", "was", "are", "were", "and", "or", "in", "on", "at",
    "by", "for", "with", "about", "against", "to", "from", "of", "it", "its", "that",
    "what", "who", "which", "when", "where", "how", "has", "have", "had", "been"
}

MONTHS = {
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
}

EVENT_QUALIFIERS = [
    "final", "semi-final", "semifinal", "quarter-final", "quarterfinal",
    "group match", "group stage", "qualifier", "super 8", "super four"
]

COMMON_VARIANTS = [
    "standard range plus", "standard range rwd", "standard range awd", "standard range",
    "long range awd", "long range rwd", "long range", "dual motor awd", "dual motor",
    "single motor", "tri motor", "plaid", "performance",
    "rear-wheel drive", "all-wheel drive", "four-wheel drive", "front-wheel drive",
    "rwd", "awd", "4wd", "fwd",
    "pro max", "pro plus", "pro", "max", "plus", "ultra", "mini",
    "base model", "base", "standard",
    "plug-in hybrid", "hybrid", "electric", "ev", "diesel", "petrol",
    "cellular", "wi-fi", "wifi", "5g", "lte", "4g",
    "128gb", "256gb", "512gb", "1tb", "2tb"
]

COMPARISON_PATTERNS = [
    r"\b(?:more|greater|higher|longer|larger|faster|heavier)\s+than\b",
    r"\b(?:less|fewer|lower|shorter|smaller|slower|lighter)\s+than\b",
    r"\b(?:increased|decreased|rose|dropped|fell)\s+by\b",
    r"\b(?:difference of|gap of|margin of)\b",
    r"\bcompared to\b",
    r"\bexceeds\b",
]

ATTRIBUTE_DOMAINS = {
    "price": {"cost", "costs", "price", "priced", "$", "usd", "rs", "inr", "rupees", "eur", "msrp", "starting at", "launch price"},
    "score": {"score", "scored", "runs", "wickets", "goals", "points", "innings", "balls"},
    "launch": {"launch", "launched", "release", "released", "announced", "unveiled", "availability", "available", "sale", "on sale"},
    "landing": {"landing", "landed", "touchdown", "touched down"},
    "winner": {"winner", "won", "champions", "champion", "victory", "defeated", "beat", "title"},
    "quantity": {"units", "shipped", "sold", "volume", "sales", "produced", "bones", "bone", "count", "consists of", "individual", "teeth", "organs", "members"},
    "attendance": {"attendance", "spectators", "viewers", "fans", "crowd"},
    "power": {"charging", "fast charging", "wired", "wireless", "watts", "w", "wattage", "charger"},
    "battery": {"battery", "mah", "capacity"},
    "camera": {"camera", "sensor", "megapixels", "mp", "lens", "zoom"},
    "memory": {"ram", "vram", "storage", "gb", "tb", "mb", "gddr"},
    "author": {"author", "wrote", "written", "novelist", "creator", "penned"},
    "range": {"range", "distance", "miles", "km", "kilometers", "elevation", "height", "altitude", "depth", "deep", "tall", "meters", "metres", "ft", "feet"},
    "speed": {"speed", "top speed", "mph", "km/h", "kph", "0-60", "acceleration"},
    "financial": {"revenue", "valuation", "market cap", "earnings", "gdp", "profit", "net income", "billion", "trillion", "million"},
    "population": {"population", "residents", "citizens", "inhabitants", "employees", "workforce", "headcount"},
    "weight": {"weight", "weighs", "mass", "kg", "lbs", "pounds", "grams", "tons", "tonnes"},
    "temperature": {"temperature", "degrees", "celsius", "fahrenheit", "kelvin", "°c", "°f"},
    "duration": {"runtime", "duration", "hours", "minutes", "seconds", "mins", "hrs", "length"},
    "percentage": {"share", "market share", "percentage", "percent", "%", "margin", "growth", "rate"},
}


def extract_variant(text: str) -> Optional[str]:
    """Extracts variant or trim designation from text."""
    lower = text.lower()
    for v in COMMON_VARIANTS:
        pattern = r"(?:\b|_)" + re.escape(v) + r"(?:\b|_)"
        if re.search(pattern, lower):
            return v
    return None


VARIANT_FAMILIES = {
    "rwd": {"rwd", "rear-wheel drive", "standard range rwd", "standard range", "standard range plus", "single motor", "base", "base model"},
    "awd": {"awd", "all-wheel drive", "four-wheel drive", "4wd", "long range awd", "long range", "long range rwd", "dual motor", "dual motor awd"},
    "performance": {"performance", "plaid", "tri motor"},
    "pro_max": {"pro max"},
    "pro": {"pro", "pro plus"},
    "plus": {"plus"},
    "base": {"base", "base model", "standard"},
    "mini": {"mini"},
}


def are_variants_compatible(v1: str, v2: str) -> bool:
    """Checks if two variant strings represent compatible specifications."""
    if not v1 or not v2:
        return False
    if v1 == v2:
        return True
    family1 = None
    family2 = None
    for family, members in VARIANT_FAMILIES.items():
        if v1 in members:
            family1 = family
        if v2 in members:
            family2 = family
    if family1 and family2:
        return family1 == family2
    if v1 in v2 or v2 in v1:
        return True
    return False


def are_variants_conflicting(v1: str, v2: str) -> bool:
    """Checks if two variants belong to mutually exclusive product tiers."""
    family1 = None
    family2 = None
    for family, members in VARIANT_FAMILIES.items():
        if v1 in members:
            family1 = family
        if v2 in members:
            family2 = family
    if family1 and family2:
        return family1 != family2
    return not are_variants_compatible(v1, v2)


def is_comparison_claim(text: str) -> bool:
    """Checks if claim involves a comparison or difference."""
    lower = text.lower()
    return any(re.search(p, lower) for p in COMPARISON_PATTERNS)


def parse_numerical_value(val_str: str) -> Optional[float]:
    """Parses raw number string into float, stripping commas."""
    try:
        clean = val_str.replace(",", "").rstrip("%").strip()
        return float(clean)
    except (ValueError, TypeError):
        return None


def is_likely_year(val: float) -> bool:
    """Checks if a numeric value represents a 4-digit calendar year."""
    return val.is_integer() and 1000 <= val <= 2100


def numbers_match_with_tolerance(val_c_str: str, val_w_str: str, tolerance: float = 0.005) -> bool:
    """
    Checks if two numerical strings match within relative tolerance or integer rounding.
    Default tolerance is 0.5% (0.005) to accommodate continuous physical measurements (e.g. 8848.86m vs 8849m).
    Calendar years (1000-2100) are strictly discrete and must match exactly.
    """
    c_clean = val_c_str.replace(",", "").rstrip("%").strip()
    w_clean = val_w_str.replace(",", "").rstrip("%").strip()
    if c_clean == w_clean:
        return True
    try:
        c_val = float(c_clean)
        w_val = float(w_clean)
    except ValueError:
        return False
    
    if c_val == w_val:
        return True
    if is_likely_year(c_val) or is_likely_year(w_val):
        return False
    if round(c_val) == round(w_val):
        return True
    max_val = max(abs(c_val), abs(w_val))
    if max_val > 0 and (abs(c_val - w_val) / max_val) <= tolerance:
        return True
    return False


def any_number_matches(c_vals: Set[str], w_vals: Set[str], tolerance: float = 0.005) -> bool:
    """Returns True if any number in c_vals matches any number in w_vals within tolerance."""
    for c in c_vals:
        for w in w_vals:
            if numbers_match_with_tolerance(c, w, tolerance):
                return True
    return False


def matches_domain_keyword(kw: str, text: str) -> bool:
    """Matches keywords with word boundary or exact currency symbol matching."""
    if kw in {"$", "€", "£", "₹"}:
        return kw in text
    return bool(re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE))


def extract_dates(text: str) -> Dict[str, str]:
    """
    Extracts date mappings: {month: day_of_month} from text.
    Handles 'September 20', '20 September', 'September 20th', etc.
    """
    pattern = (
        r"(?:(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?\b"
        r"|(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)\b)"
    )
    dates_map: Dict[str, str] = {}
    matches = re.findall(pattern, text.lower())
    for m in matches:
        m1, d1, d2, m2 = m
        month = m1 or m2
        day = d1 or d2
        if month and day:
            dates_map[month] = day
    return dates_map


def extract_quantified_units(text: str) -> Dict[str, Set[str]]:
    """
    Extracts mappings of {unit_noun: Set[normalized_number_values]} from text.
    Handles prefix currencies ($799, Rs 79,900) and suffix units (18 runs, 3.8 GHz, 5090 units, 92,453 spectators).
    Preserves exact currency identity (usd, inr, eur, gbp) to avoid cross-currency false equivalence.
    Uses word boundaries on text-based currency codes to prevent false matches (e.g. 'offers 272').
    """
    pattern = (
        r"(?:(?:\b(rs|inr|usd|eur|gbp)\b|([\$€£₹]))\s*(\d+(?:[,\.]\d+)*)"
        r"|(\d+(?:[,\.]\d+)*)\s*(runs?|wickets?|goals?|points?|balls?|overs?|units?|ghz|mhz|nits|cores?|vram|gb|mb|tb|bit|fps|hz|watts?|w|mah|dollars?|rupees?|percent|%|km|metres?|meters?|miles?|inch|inches?|ft|feet|spectators?|attendance|viewers?|fans?|people|billion|million|kg|lbs|pounds|mph|km/h|kph|bones?|teeth|members?|items?|organs?|players?|species)\b)"
    )
    CURRENCY_MAP = {
        "$": "usd",
        "usd": "usd",
        "dollars": "usd",
        "dollar": "usd",
        "rs": "inr",
        "inr": "inr",
        "₹": "inr",
        "rupees": "inr",
        "rupee": "inr",
        "€": "eur",
        "eur": "eur",
        "euros": "eur",
        "euro": "eur",
        "£": "gbp",
        "gbp": "gbp",
        "pounds": "gbp",
        "pound": "gbp",
    }
    units_map: Dict[str, Set[str]] = {}
    matches = re.findall(pattern, text, re.IGNORECASE)
    for m in matches:
        w_curr, s_curr, prefix_val, suffix_val, suffix_unit = m
        prefix_curr = w_curr or s_curr
        if prefix_curr and prefix_val:
            curr_code = CURRENCY_MAP.get(prefix_curr.lower(), prefix_curr.lower())
            norm_val = prefix_val.replace(",", "").lower()
            if curr_code not in units_map:
                units_map[curr_code] = set()
            units_map[curr_code].add(norm_val)
        elif suffix_val and suffix_unit:
            s_unit_clean = suffix_unit.lower().rstrip("s")
            curr_code = CURRENCY_MAP.get(suffix_unit.lower())
            unit_key = curr_code if curr_code else s_unit_clean
            norm_val = suffix_val.replace(",", "").lower()
            if unit_key not in units_map:
                units_map[unit_key] = set()
            units_map[unit_key].add(norm_val)
    return units_map


def extract_proposition_windows(doc: ExtractedDocument, window_size: int = 3, stride: int = 2) -> List[Tuple[str, Optional[str]]]:
    """
    Decomposes an extracted document into localized proposition windows.
    Each window is a sliding set of 2-3 consecutive sentences within a paragraph,
    preserving local semantic proximity and preventing cross-paragraph false corroboration.
    """
    text = doc.clean_text or ""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    windows: List[Tuple[str, Optional[str]]] = []

    if doc.title:
        windows.append((doc.title.strip(), "Title"))

    current_heading = None
    for p in paragraphs:
        if re.match(r"^#{1,4}\s+", p):
            lines = p.split("\n", 1)
            current_heading = re.sub(r"^#{1,4}\s+", "", lines[0]).strip()
            p = lines[1].strip() if len(lines) > 1 else ""
            if not p:
                continue

        # Split paragraph into sentences
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]
        if not sentences:
            continue

        if len(sentences) <= window_size:
            windows.append((" ".join(sentences), current_heading))
        else:
            for i in range(0, len(sentences), stride):
                w_sents = sentences[i : i + window_size]
                if w_sents:
                    windows.append((" ".join(w_sents), current_heading))

    return windows


class ClaimVerifier:
    """
    Automated post-generation factual auditor.
    """

    def __init__(self, mode: str = "hybrid"):
        self.mode = mode  # "strict" or "hybrid"

    def extract_claims(self, text: str) -> List[str]:
        """
        Decomposes response text into atomic factual propositions.
        Filters out formatting, meta-chatter, and source listings.
        Splits compound sentences on coordinate and contrastive clauses.
        """
        results_with_spans = self.extract_claims_with_spans(text)
        return [c for c, _, _ in results_with_spans]

    def extract_claims_with_spans(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Decomposes response text into atomic propositions and records (claim, start_idx, end_idx).
        Splits compound sentences on coordinate and contrastive conjunctions, em-dashes, and semicolons.
        Preserves short factual claims (>= 6 chars).
        """
        # Remove markdown headers and URLs for processing, but track spans accurately
        cleaned = re.sub(r"#{1,6}\s+.*", "", text)
        cleaned = re.sub(r"https?://\S+", "", cleaned)
        cleaned = re.sub(r"\bSources?:.*", "", cleaned, flags=re.IGNORECASE | re.DOTALL)

        # Split into sentences or numbered bullet lines
        raw_lines = re.split(r"(?<=[.!?])\s+|\n+", cleaned)
        claims_with_spans: List[Tuple[str, int, int]] = []

        # Split pattern for compound propositions
        COMPOUND_SPLIT = re.compile(
            r"(?:\s*;\s*|\s+[—–]\s*|,\s*(?:whereas|while|but|although|yet)\s+|,\s+and\s+(?=[a-z0-9A-Z])|\s+and\s+(?=(?:later\s+|subsequently\s+)?(?:launched|acquired|defeated|released|announced|founded|introduced|expanded|scored|won|achieved|built|developed|created|signed|reported|stated|produced|purchased|sold|merged|features|costs|reached|joined|retired)\b))",
            re.IGNORECASE
        )
        VERB_PATTERN = re.compile(
            r"^(?:later\s+|subsequently\s+)?(?:launched|acquired|defeated|released|announced|founded|introduced|expanded|scored|won|achieved|built|developed|created|signed|reported|stated|produced|purchased|sold|merged|features|costs|reached|joined|retired|became|was|is|has|had)\b",
            re.IGNORECASE
        )

        for line in raw_lines:
            s = line.strip()
            # Strip markdown list markers and bullet numbers
            s = re.sub(r"^(\*|-|\d+\.)\s+", "", s).strip()
            if not s:
                continue

            # Strip leading meta-framing
            if re.match(r"^(based on|according to|in summary|the following|verified sources|as of).*", s, re.IGNORECASE):
                s = re.sub(r"^(based on (the )?(provided )?evidence,?\s*|according to \[\d+\],?\s*)", "", s, flags=re.IGNORECASE).strip()
                if not s:
                    continue

            # Check leading subordinate clauses (e.g. "Although X, Y")
            lead_sub = re.match(r"^(?:Although|While|Whereas|Even though|Though)\s+(.*)", s, re.IGNORECASE)
            if lead_sub and "," in lead_sub.group(1):
                parts = lead_sub.group(1).split(",", 1)
                sub_clauses = [parts[0].strip(), parts[1].strip()]
            else:
                sub_clauses = COMPOUND_SPLIT.split(s)

            if len(sub_clauses) > 1:
                # Extract main entity from clause 1
                c1_clean = re.sub(r"^(?:The|A|An|This|That)\s+", "", sub_clauses[0].strip(), flags=re.IGNORECASE)
                ent_match = re.search(r"\b[A-Z][a-zA-Z0-9]*(?:\s+[A-Za-z0-9]+)*\b", c1_clean)
                main_entity = None
                if ent_match:
                    tokens = ent_match.group(0).split()
                    entity_tokens = []
                    for t in tokens:
                        if t[0].isupper() or (t.isalnum() and any(c.isdigit() for c in t)):
                            entity_tokens.append(t)
                        else:
                            break
                    main_entity = " ".join(entity_tokens) if entity_tokens else ent_match.group(0)

                for idx, sc in enumerate(sub_clauses):
                    sc_clean = sc.strip()
                    # Strip leading connectives from secondary clauses
                    sc_clean = re.sub(r"^(?:and|but|while|whereas|yet|although)\s+", "", sc_clean, flags=re.IGNORECASE).strip()
                    if len(sc_clean) < 6:
                        continue

                    # Subject context inheritance for secondary clauses
                    if idx > 0 and main_entity:
                        pron_match = re.match(r"^(it|he|she|they)\b\s*", sc_clean, re.IGNORECASE)
                        if pron_match:
                            sc_clean = f"{main_entity} " + sc_clean[pron_match.end():]
                        elif VERB_PATTERN.match(sc_clean):
                            sc_clean = f"{main_entity} {sc_clean}"

                    sc_prop = sc_clean[0].upper() + sc_clean[1:]
                    start_idx = text.find(sc.strip()) if sc.strip() in text else 0
                    end_idx = start_idx + len(sc.strip()) if start_idx >= 0 else 0
                    claims_with_spans.append((sc_prop, start_idx, end_idx))
            else:
                if len(s) < 6:
                    continue
                start_idx = text.find(s) if s in text else 0
                end_idx = start_idx + len(s) if start_idx >= 0 else 0
                claims_with_spans.append((s, start_idx, end_idx))

        return claims_with_spans

    def verify_single_claim(self, claim: str, docs: List[ExtractedDocument]) -> ClaimVerification:
        """
        Verifies if an individual claim is corroborated by retrieved documents.
        Enforces proposition-level co-occurrence: entity, event context, and numerical
        values must co-occur within the same localized proposition window.
        Detects factual contradictions.
        """
        if not docs:
            return ClaimVerification(
                claim_text=claim,
                is_supported=False,
                supporting_source_indices=[],
                confidence=0.0,
                reasoning="No retrieved evidence available to corroborate claim."
            )

        cited_indices = [int(m) for m in re.findall(r"\[(\d+)\]", claim)]
        claim_clean = re.sub(r"\[\d+\]", "", claim).strip()
        claim_lower = claim_clean.lower()

        # 1. Extract Numerical Tokens
        raw_number_tokens = re.findall(r"\b\d+(?:[,\.]\d+)*%?\b", claim_clean)
        number_tokens: Set[str] = set()
        for num in raw_number_tokens:
            number_tokens.add(num.lower())
            number_tokens.add(num.replace(",", "").lower())

        # 2. Extract Substantive Terms & Months
        word_tokens = [w for w in re.findall(r"\b[a-zA-Z]{3,}\b", claim_lower) if w not in STOPWORDS]
        claim_months = {w for w in word_tokens if w in MONTHS}

        # 3. Extract Entity Profile & Context Qualifiers
        ent_profile = extract_entity_profile(claim_clean)
        claim_event_qualifiers = [eq for eq in EVENT_QUALIFIERS if re.search(r"\b" + re.escape(eq) + r"\b", claim_lower)]
        if any(sf in claim_event_qualifiers for sf in ["semi-final", "semifinal", "quarter-final", "quarterfinal"]):
            claim_event_qualifiers = [eq for eq in claim_event_qualifiers if eq != "final"]
        
        PROPER_NOUN_STOPWORDS = {
            "the", "this", "that", "these", "those", "there", "here", "in", "on", "at", "for", "with",
            "by", "from", "to", "of", "about", "against", "what", "when", "where", "who", "whom",
            "why", "how", "which", "according", "based", "as", "it", "its", "they", "their", "he",
            "his", "she", "her", "we", "our", "you", "your", "if", "although", "however", "moreover",
            "furthermore", "meanwhile", "earlier", "later", "during", "since", "until", "after",
            "before", "while", "some", "many", "most", "all", "both", "each", "every", "another",
            "other", "such", "no", "not", "only", "also", "just", "even", "still", "already", "soon",
            "now", "then", "yes", "source", "sources", "note", "warning", "match", "final", "matches",
            "innings", "total", "official", "world", "cup", "men", "mens", "women", "womens"
        }
        multi_pns_raw = [pn.lower() for pn in re.findall(r"\b[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)+\b", claim_clean)]
        multi_pns = []
        for pn in multi_pns_raw:
            clean_pn = re.sub(r"^(the|this|that|these|those|an|a)\s+", "", pn, flags=re.IGNORECASE).strip()
            if clean_pn and clean_pn not in PROPER_NOUN_STOPWORDS:
                multi_pns.append(clean_pn)
        single_pns = [pn.lower() for pn in re.findall(r"\b[A-Z][a-zA-Z0-9]{2,}\b", claim_clean) if pn.lower() not in PROPER_NOUN_STOPWORDS]
        candidate_entities = set(multi_pns)
        for s in single_pns:
            if not any(s in m for m in multi_pns):
                candidate_entities.add(s)

        TOURNAMENT_MARKERS = ["world cup", "champions trophy", "olympic", "super bowl", "premier league", "champions league"]
        specific_named_entities = [
            e for e in candidate_entities
            if not any(tm in e for tm in TOURNAMENT_MARKERS) and not extract_variant(e)
        ]

        # 4. Extract Active Attribute Domains & Quantified Units / Dates
        active_domains = []
        for domain, kw_set in ATTRIBUTE_DOMAINS.items():
            if any(matches_domain_keyword(kw, claim_lower) for kw in kw_set):
                active_domains.append((domain, kw_set))

        claim_quantified = extract_quantified_units(claim_clean)
        claim_dates = extract_dates(claim_clean)
        claim_variant = extract_variant(claim_clean)
        is_comp = is_comparison_claim(claim_clean)
        structured_num = None
        if number_tokens:
            primary_num = sorted(list(number_tokens), key=len, reverse=True)[0]
            structured_num = StructuredNumericalClaim(
                entity=ent_profile.base_name,
                variant=claim_variant,
                attribute=ent_profile.requested_attribute or (active_domains[0][0] if active_domains else None),
                raw_value=primary_num,
                numeric_value=parse_numerical_value(primary_num),
                unit=list(claim_quantified.keys())[0] if claim_quantified else None,
                currency=list(claim_quantified.keys())[0] if any(k in ["usd", "inr", "eur", "gbp"] for k in claim_quantified.keys()) else None,
                event=claim_event_qualifiers[0] if claim_event_qualifiers else None,
                is_comparison=is_comp,
            )

        supporting_indices: List[int] = []
        best_passage: Optional[str] = None
        best_confidence: float = 0.0
        contradiction_detected = False
        contradiction_reason = ""

        # Numbers associated with entity names/models (e.g. Model 3, Boeing 737) or years
        ignored_entity_nums = set()
        if ent_profile.model_or_number:
            ignored_entity_nums.add(ent_profile.model_or_number)
        if ent_profile.year:
            ignored_entity_nums.add(ent_profile.year)
        model_num_match = re.search(r"\b(?:model|iphone|ipad|galaxy|playstation|xbox|pixel|boeing|airbus)\s+(\d+)\b", claim_lower)
        if model_num_match:
            ignored_entity_nums.add(model_num_match.group(1))

        attr_numbers_in_claim = {n for n in number_tokens if n not in ignored_entity_nums}
        target_check_nums = attr_numbers_in_claim if attr_numbers_in_claim else number_tokens

        # Test each document
        for doc in docs:
            windows = extract_proposition_windows(doc)
            doc_supported = False

            for w_text, heading in windows:
                combined_w = f"{doc.title or ''} {heading or ''} {w_text}".lower()

                # A. Event Qualifier Check:
                # If claim is specific to an event (e.g. "final"), window must also mention it
                if claim_event_qualifiers:
                    matched_qualifiers = False
                    for eq in claim_event_qualifiers:
                        if eq == "final":
                            if re.search(r"(?<!semi-)(?<!semi )(?<!quarter-)(?<!quarter )\bfinal\b", combined_w):
                                matched_qualifiers = True
                                break
                        else:
                            if re.search(r"\b" + re.escape(eq) + r"\b", combined_w):
                                matched_qualifiers = True
                                break
                    if not matched_qualifiers:
                        continue

                # A2. Specific Named Entity Gate:
                # If claim introduces specific named entities (e.g. "Clive Lloyd", "England"),
                # ALL specific named entities MUST be present in the corroborating evidence window
                if specific_named_entities:
                    if not all(sne in combined_w for sne in specific_named_entities):
                        continue

                # B. Numerical / Date Verification & Contradiction Detection
                if number_tokens:
                    # B0. Variant Binding Check:
                    # If claim is specific to a variant (e.g. "standard range rwd" vs "long range awd"),
                    # verify that the claimed numerical value belongs to THIS variant, not a competing variant in the same window.
                    if claim_variant:
                        w_clauses = re.split(r"(?:(?<!\d),(?!\d)|[;—–\n]|\bwhereas\b|\bwhile\b|\bbut\b|\band\b)", combined_w)
                        variant_clause_found = False
                        competing_variant_match = False
                        
                        for wc in w_clauses:
                            wc_variant = extract_variant(wc)
                            wc_raw_nums = set(re.findall(r"\b\d+(?:[,\.]\d+)*%?\b", wc))
                            wc_nums = set()
                            for n in wc_raw_nums:
                                wc_nums.add(n.lower())
                                wc_nums.add(n.replace(",", "").lower())
                            wc_attr_nums = {n for n in wc_nums if n not in ignored_entity_nums}
                            target_wc_nums = wc_attr_nums if wc_attr_nums else wc_nums

                            if wc_variant and are_variants_compatible(wc_variant, claim_variant):
                                variant_clause_found = True
                                # If quantified units exist, check whether numbers in this clause represent the same unit
                                wc_quantified = extract_quantified_units(wc)
                                common_units = set(claim_quantified.keys()) & set(wc_quantified.keys())
                                if common_units:
                                    c_unit_vals = set.union(*(claim_quantified[u] for u in common_units))
                                    w_unit_vals = set.union(*(wc_quantified[u] for u in common_units))
                                    if not any_number_matches(c_unit_vals, w_unit_vals):
                                        contradiction_detected = True
                                        contradiction_reason = f"Source [{doc.source_index}] states {w_unit_vals} for variant '{claim_variant}', which contradicts claimed {c_unit_vals}."
                                elif not claim_quantified and active_domains:
                                    wc_has_same_domain = any(any(matches_domain_keyword(kw, wc) for kw in kw_set) for _, kw_set in active_domains)
                                    if wc_has_same_domain and not any_number_matches(target_check_nums, target_wc_nums):
                                        contradiction_detected = True
                                        contradiction_reason = f"Source [{doc.source_index}] states {target_wc_nums} for variant '{claim_variant}', which contradicts claimed {target_check_nums}."
                            elif wc_variant and are_variants_conflicting(wc_variant, claim_variant):
                                wc_quantified = extract_quantified_units(wc)
                                common_units = set(claim_quantified.keys()) & set(wc_quantified.keys())
                                if common_units:
                                    c_unit_vals = set.union(*(claim_quantified[u] for u in common_units))
                                    w_unit_vals = set.union(*(wc_quantified[u] for u in common_units))
                                    if any_number_matches(c_unit_vals, w_unit_vals) and not variant_clause_found:
                                        competing_variant_match = True
                                elif any_number_matches(target_check_nums, target_wc_nums) and not variant_clause_found:
                                    competing_variant_match = True

                        if (competing_variant_match and not variant_clause_found) or contradiction_detected:
                            contradiction_detected = True
                            if not contradiction_reason:
                                contradiction_reason = f"Source [{doc.source_index}] associates value {target_check_nums} with another variant, not '{claim_variant}'."
                            continue

                    # Check for contradiction:
                    # If this window shares core entity AND (event context OR attribute domain),
                    # but mentions conflicting numbers (e.g. Kapil Dev 15 vs 175, iPhone 16 Rs 79,900 vs Rs 59,900)
                    has_entity = False
                    if ent_profile.base_name and ent_profile.base_name in combined_w:
                        has_entity = True
                    if any(pn in combined_w for pn in candidate_entities):
                        has_entity = True
                    if ent_profile.model_or_number and ent_profile.model_or_number not in combined_w:
                        has_entity = False

                    has_event = bool(claim_event_qualifiers and any(
                        (re.search(r"(?<!semi-)(?<!semi )(?<!quarter-)(?<!quarter )\bfinal\b", combined_w) if eq == "final" else re.search(r"\b" + re.escape(eq) + r"\b", combined_w))
                        for eq in claim_event_qualifiers
                    ))
                    has_attr = bool(active_domains and any(any(matches_domain_keyword(kw, combined_w) for kw in kw_set) for _, kw_set in active_domains))

                    # Quantified Unit Consistency Check (Executed before number ratio filter)
                    # Uses tolerance to avoid false contradictions on continuous physical measurements (e.g. 8848.86m vs 8849m)
                    w_quantified = extract_quantified_units(combined_w)
                    unit_conflict = False
                    for u_name, c_vals in claim_quantified.items():
                        if u_name in w_quantified:
                            w_vals = w_quantified[u_name]
                            if not any_number_matches(c_vals, w_vals):
                                unit_conflict = True
                                if has_entity or has_event or has_attr:
                                    w_variant = extract_variant(combined_w)
                                    if claim_variant and w_variant and are_variants_conflicting(claim_variant, w_variant):
                                        pass
                                    elif claim_variant and not w_variant:
                                        pass
                                    else:
                                        contradiction_detected = True
                                        contradiction_reason = f"Source [{doc.source_index}] states {w_vals} {u_name}, which contradicts claimed {c_vals} {u_name}."
                                break
                    if unit_conflict:
                        continue

                    # Date Consistency Check (Specific day of the month)
                    w_dates = extract_dates(combined_w)
                    date_conflict = False
                    if has_entity and (has_event or has_attr):
                        for month, c_day in claim_dates.items():
                            if month in w_dates:
                                w_day = w_dates[month]
                                if c_day != w_day:
                                    contradiction_detected = True
                                    contradiction_reason = f"Source [{doc.source_index}] states {month.capitalize()} {w_day}, which contradicts claimed {month.capitalize()} {c_day}."
                                    date_conflict = True
                                    break
                    if date_conflict:
                        continue

                    ignored_entity_nums = set()
                    if ent_profile.model_or_number:
                        ignored_entity_nums.add(ent_profile.model_or_number)
                    if ent_profile.year:
                        ignored_entity_nums.add(ent_profile.year)

                    attr_numbers_in_claim = {n for n in number_tokens if n not in ignored_entity_nums}

                    w_raw_nums = re.findall(r"\b\d+(?:[,\.]\d+)*%?\b", combined_w)
                    w_norm_nums = set()
                    for n in w_raw_nums:
                        w_norm_nums.add(n.lower())
                        w_norm_nums.add(n.replace(",", "").lower())
                    w_attr_nums = {n for n in w_norm_nums if n not in ignored_entity_nums}

                    if has_entity and (has_event or has_attr):
                        # If claim specifies an attribute value, but window has competing value
                        if attr_numbers_in_claim and w_attr_nums:
                            if not any_number_matches(attr_numbers_in_claim, w_attr_nums):
                                w_variant = extract_variant(combined_w)
                                if claim_variant and w_variant and are_variants_conflicting(claim_variant, w_variant):
                                    pass
                                elif claim_variant and not w_variant:
                                    pass
                                else:
                                    contradiction_detected = True
                                    context_label = claim_event_qualifiers[0] if has_event else (active_domains[0][0] if active_domains else "context")
                                    contradiction_reason = f"Source [{doc.source_index}] discusses {ent_profile.base_name or 'entity'} ({context_label}) with conflicting numbers: claimed {attr_numbers_in_claim} vs evidence {w_attr_nums}."

                    nums_matching = sum(1 for n in number_tokens if any_number_matches({n}, w_norm_nums) or n in combined_w)
                    num_ratio = nums_matching / len(number_tokens)
                    if num_ratio < 0.65:
                        continue

                    # If claim specifies distinct attribute numbers, at least one must co-occur in the window (exact or within tolerance)
                    if attr_numbers_in_claim and not any(any_number_matches({n}, w_norm_nums) or n in combined_w for n in attr_numbers_in_claim):
                        continue

                # C. Month Check
                if claim_months:
                    window_words = set(re.findall(r"\b[a-z]+\b", combined_w))
                    if not claim_months.issubset(window_words):
                        continue

                # D. Attribute Domain Alignment
                # If claim asserts a specific attribute (e.g. price, landing, score),
                # the window must corroborate that attribute domain, not substitute another
                domain_mismatch = False
                for domain, kw_set in active_domains:
                    if not any(matches_domain_keyword(kw, combined_w) for kw in kw_set):
                        domain_mismatch = True
                        break
                if domain_mismatch:
                    continue

                # F. Substantive Lexical Overlap within Window
                matched_words = sum(1 for w in word_tokens if w in combined_w)
                overlap_ratio = matched_words / max(len(word_tokens), 1)

                threshold = 0.40 if number_tokens else 0.50
                if overlap_ratio >= threshold:
                    doc_supported = True
                    if not best_passage or overlap_ratio > best_confidence:
                        best_passage = w_text
                        best_confidence = overlap_ratio
                    break

            if doc_supported:
                supporting_indices.append(doc.source_index)

        # Check contradiction first
        if contradiction_detected and not supporting_indices:
            return ClaimVerification(
                claim_text=claim,
                is_supported=False,
                supporting_source_indices=[],
                confidence=0.0,
                contradiction_detected=True,
                reasoning=f"Contradiction detected: {contradiction_reason}",
                entity=ent_profile.base_name,
                attribute=ent_profile.requested_attribute,
                numerical_values=list(number_tokens),
                structured_numerical=structured_num,
            )

        # Corroboration via cited source
        if cited_indices:
            corroborated_citations = [idx for idx in cited_indices if idx in supporting_indices]
            if corroborated_citations:
                return ClaimVerification(
                    claim_text=claim,
                    is_supported=True,
                    supporting_source_indices=corroborated_citations,
                    confidence=0.95,
                    reasoning=f"Claim corroborated by localized proposition window in cited source(s) {corroborated_citations}.",
                    entity=ent_profile.base_name,
                    attribute=ent_profile.requested_attribute,
                    numerical_values=list(number_tokens),
                    supporting_passage=best_passage,
                    structured_numerical=structured_num,
                )

        if supporting_indices:
            return ClaimVerification(
                claim_text=claim,
                is_supported=True,
                supporting_source_indices=supporting_indices,
                confidence=0.85,
                reasoning=f"Claim corroborated by localized proposition window in source(s) {supporting_indices}.",
                entity=ent_profile.base_name,
                attribute=ent_profile.requested_attribute,
                numerical_values=list(number_tokens),
                supporting_passage=best_passage,
                structured_numerical=structured_num,
            )

        return ClaimVerification(
            claim_text=claim,
            is_supported=False,
            supporting_source_indices=[],
            confidence=0.2,
            reasoning="Key facts, context qualifiers, or numbers in this claim were not corroborated in any localized evidence window.",
            entity=ent_profile.base_name,
            attribute=ent_profile.requested_attribute,
            numerical_values=list(number_tokens),
            structured_numerical=structured_num,
        )

    def verify_citations(
        self,
        text: str,
        docs: List[ExtractedDocument],
        claim_verifications: Optional[List[ClaimVerification]] = None
    ) -> Tuple[float, List[int]]:
        """
        Audits bracketed citations [1], [2] in response text.
        Computes citation support rate based on actual claim-evidence linkage:
        A citation is valid ONLY if the cited document actually corroborates the claim.
        """
        cited_indices = [int(m) for m in re.findall(r"\[(\d+)\]", text)]
        if not cited_indices:
            return 1.0, []

        valid_docs = {d.source_index for d in docs}
        
        # If claim verifications are available, check claim-evidence linkage
        if claim_verifications:
            total_citations = 0
            valid_citations = 0
            for cv in claim_verifications:
                cv_cites = [int(m) for m in re.findall(r"\[(\d+)\]", cv.claim_text)]
                for c in cv_cites:
                    total_citations += 1
                    if c in valid_docs and c in cv.supporting_source_indices:
                        valid_citations += 1

            if total_citations > 0:
                support_rate = valid_citations / total_citations
                return support_rate, list(set(cited_indices))

        # Fallback to document existence
        valid_count = sum(1 for idx in cited_indices if idx in valid_docs)
        support_rate = valid_count / len(cited_indices)
        return support_rate, list(set(cited_indices))

    def audit_and_verify_response(
        self,
        user_query: str,
        response_text: str,
        docs: List[ExtractedDocument],
        is_internal_generation: bool = False
    ) -> VerifiedResponse:
        """
        Audits complete response, verifies every claim, assigns ResponseState,
        and enforces Strict vs Hybrid operational policies.
        """
        # Case 1: Explicit Refusal / Abstention
        lower_resp = response_text.lower()
        if any(p in lower_resp for p in ABSTAIN_PATTERNS):
            return VerifiedResponse(
                final_text=response_text,
                response_state=ResponseState.ABSTAIN,
                claims=[],
                unsupported_claims_count=0,
                verified_sources=[],
                citation_support_rate=1.0,
                claim_support_rate=1.0,
                citation_precision=1.0,
                citation_coverage=1.0,
                source_availability=1.0,
            )

        # Case 2: Internal Parametric Knowledge (Zero Web Evidence)
        if is_internal_generation or not docs:
            if self.mode == "strict":
                return VerifiedResponse(
                    final_text="Strict RAG Mode: No verified external evidence was retrieved. System abstains from unverified factual generation.",
                    response_state=ResponseState.ABSTAIN,
                    claims=[],
                    unsupported_claims_count=0,
                    verified_sources=[],
                    citation_support_rate=1.0,
                    claim_support_rate=0.0,
                    citation_precision=1.0,
                    citation_coverage=0.0,
                    source_availability=0.0,
                )
            else:
                banner = "\n> ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**\n> This answer was generated from model training data without live retrieval verification.\n\n"
                return VerifiedResponse(
                    final_text=banner + response_text.strip(),
                    response_state=ResponseState.UNVERIFIED,
                    claims=[],
                    unsupported_claims_count=0,
                    verified_sources=[],
                    citation_support_rate=1.0,
                    claim_support_rate=0.0,
                    citation_precision=1.0,
                    citation_coverage=0.0,
                    source_availability=0.0,
                )

        # Case 3: Retrieval-Backed Synthesis Verification
        claims = self.extract_claims(response_text)
        claim_verifications = [self.verify_single_claim(c, docs) for c in claims]
        
        supported_claims = [cv for cv in claim_verifications if cv.is_supported]
        unsupported_claims = [cv for cv in claim_verifications if not cv.is_supported]
        
        cit_rate, cited_indices = self.verify_citations(response_text, docs, claim_verifications)
        used_sources = [d for d in docs if d.source_index in cited_indices] or docs

        # Total verification ratio & decomposed metrics
        total_claims = len(claims)
        supported_count = len(supported_claims)
        unsupported_count = len(unsupported_claims)
        claim_support_rate = (supported_count / total_claims) if total_claims > 0 else 0.0

        # Check if any direct contradiction was flagged
        has_contradiction = any(cv.contradiction_detected for cv in claim_verifications)

        # Decomposed Citation & Source metrics
        total_citations = 0
        valid_citations = 0
        supported_with_valid_citations = 0
        valid_doc_indices = {d.source_index for d in docs}

        for cv in claim_verifications:
            cv_cites = [int(m) for m in re.findall(r"\[(\d+)\]", cv.claim_text)]
            cv_valid = [c for c in cv_cites if c in valid_doc_indices and c in cv.supporting_source_indices]
            total_citations += len(cv_cites)
            valid_citations += len(cv_valid)
            if cv.is_supported and len(cv_valid) > 0:
                supported_with_valid_citations += 1

        citation_precision = (valid_citations / total_citations) if total_citations > 0 else 1.0
        citation_coverage = (supported_with_valid_citations / supported_count) if supported_count > 0 else 1.0
        
        accessible_sources = sum(1 for d in docs if (d.clean_text and len(d.clean_text.strip()) > 30))
        source_availability = (accessible_sources / len(docs)) if docs else 1.0

        # Truth-state and Answer Sanitization Logic:
        # Case 1: Zero claims extracted (empty response or non-assertive text)
        if total_claims == 0:
            if self.mode == "strict":
                state = ResponseState.ABSTAIN
                final_text = "Strict RAG Mode: The retrieved evidence was insufficient or contradictory to substantiate the factual claims."
            else:
                state = ResponseState.UNVERIFIED
                if not response_text.strip():
                    final_text = "No factual claims could be extracted or verified from the response."
                else:
                    warning = "\n\n> ⚠️ *Warning: Response contains unverified statements relative to retrieved evidence.*"
                    final_text = response_text + warning

        # Case 2: Strict 100% corroboration rule for VERIFIED (Zero unsupported claims & zero contradictions)
        elif unsupported_count == 0 and not has_contradiction:
            state = ResponseState.VERIFIED
            final_text = response_text

        # Case 3: Mixed support (at least 1 supported claim, but with unsupported claims or contradictions)
        elif supported_count > 0:
            state = ResponseState.PARTIAL
            # Phase 4 Answer Sanitization:
            # Construct verified output strictly from corroborated claims, pruning hallucinations and contradictions
            verified_segments = []
            for cv in supported_claims:
                c_text = cv.claim_text.strip()
                if c_text and not any(c_text in vs for vs in verified_segments):
                    if not re.search(r"[.!?]$", c_text):
                        c_text += "."
                    verified_segments.append(c_text)
            sanitized_body = " ".join(verified_segments) if verified_segments else response_text
            warning = "\n\n> ℹ️ *Note: Some statements in this response could not be fully verified from retrieved sources.*"
            final_text = sanitized_body + warning

        # Case 4: Zero supported claims (100% unsupported or contradicted)
        else:
            if self.mode == "strict":
                state = ResponseState.ABSTAIN
                final_text = "Strict RAG Mode: The retrieved evidence was insufficient or contradictory to substantiate the factual claims."
            else:
                if has_contradiction:
                    state = ResponseState.ABSTAIN
                    warning = "\n\n> ⚠️ *Warning: Response contains unverified or contradictory statements relative to retrieved evidence.*"
                    final_text = "Retrieved evidence contradicts the generated claims. Unable to provide a verified answer." + warning
                else:
                    state = ResponseState.UNVERIFIED
                    warning = "\n\n> ⚠️ *Warning: Response contains unverified or contradictory statements relative to retrieved evidence.*"
                    final_text = response_text + warning

        return VerifiedResponse(
            final_text=final_text,
            response_state=state,
            claims=claim_verifications,
            unsupported_claims_count=unsupported_count,
            verified_sources=used_sources,
            citation_support_rate=cit_rate,
            claim_support_rate=claim_support_rate,
            citation_precision=citation_precision,
            citation_coverage=citation_coverage,
            source_availability=source_availability,
        )
