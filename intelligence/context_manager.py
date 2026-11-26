"""
PROJECT NOVA - Conversation Intelligence & Multi-Turn Coreference Engine (Sprint 5.3)
===================================================================================
Maintains structured conversation state and resolves coreferences:
1. Multi-turn context preservation (Entities, Events, Years, Attributes)
2. Standalone query generation for search engines
3. Intent classification: NEW_TOPIC, FOLLOW_UP, YEAR_CHANGE, ENTITY_CHANGE, EVENT_CHANGE, ATTRIBUTE_CHANGE
4. Pronoun and demonstrative resolution (it, its, he, she, they, their, that movie, the games)
5. Topic-change boundary detection (prevents context contamination across unrelated questions)
"""

import logging
import re
import time
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from intelligence.schemas import FollowUpIntent, StructuredConversationState

logger = logging.getLogger("nova.context")

# Semantic domain signatures for topic boundary detection
DOMAIN_SIGNATURES = {
    "SPORTS": {
        "cricket", "world cup", "tournament", "trophy", "match", "final", "captain",
        "wickets", "runs", "batsman", "bowler", "scorecard", "fifa", "football",
        "uefa", "olympics", "ipl", "bbl", "nba", "tennis", "champion", "winner",
        "stadium", "super bowl", "semi-final", "quarter-final"
    },
    "ENTERTAINMENT": {
        "movie", "film", "directed", "director", "actor", "actress", "cinema", "oscar",
        "oppenheimer", "hollywood", "box office", "budget", "release date", "cast",
        "inception", "interstellar", "character", "soundtrack"
    },
    "TECH_CS": {
        "cpu", "gpu", "ram", "rom", "transformer", "neural", "python", "code",
        "algorithm", "binary tree", "quicksort", "linux", "compiler", "api",
        "framework", "docker", "kubernetes", "database", "sql", "architecture",
        "iphone", "playstation", "nintendo", "chip", "battery", "mah", "processor"
    },
    "SCIENCE_MATH": {
        "algebra", "calculus", "linear algebra", "derivative", "integral", "matrix",
        "physics", "chemistry", "formula", "molecule", "photosynthesis", "planet",
        "gravity", "solar system", "electron", "quantum", "biology", "speed of light",
        "penicillin", "nobel prize"
    },
    "BUSINESS_FINANCE": {
        "stock", "shares", "crypto", "bitcoin", "market cap", "revenue", "profit",
        "ceo", "acquisition", "valuation", "investor", "dividend", "nasdaq", "headquarters"
    },
    "POLITICS": {
        "prime minister", "president", "minister", "parliament", "congress", "senate",
        "election", "government", "office", "treaty", "united nations", "chancellor"
    },
    "GEOGRAPHY": {
        "capital", "country", "city", "river", "mountain", "ocean", "population",
        "border", "continent", "everest", "mariana trench", "height", "depth"
    },
    "EXAMS_ADMIN": {
        "jee", "neet", "exam", "admit card", "registration", "deadline", "counseling"
    }
}

PRONOUN_PATTERNS = [
    r"\b(it)\b",
    r"\b(its)\b",
    r"\b(their|theirs)\b",
    r"\b(his|him)\b",
    r"\b(her|hers)\b",
    r"\b(they|them)\b",
    r"\b(he|she)\b",
]

ELLIPTICAL_PATTERNS = [
    r"^(what|how)\s+about\b",
    r"^who\s+was\s+(the|their)\s+",
    r"^and\s+(in|at|on|for|with|who|what|when|where|how|why)\b",
    r"^(in|at|on|during|for)\s+what\s+(year|date|month|time|city|price|venue|budget)\b",
    r"^(in|at|on)\s+\d{4}\b",
    r"^how\s+many\s+(runs|wickets|goals|points|cores|transistors)\b",
    r"^when\s+was\s+it\b",
    r"^where\s+was\s+it\b",
    r"^who\s+is\s+(the|their)\s+(ceo|founder|director|actor|captain|coach)\b",
    r"^what\s+(was|is)\s+(the|its|his|her|their)\s+(price|budget|score|average|capacity|range|result|winner|revenue)\b",
    r"^(who|what)\s+(was|is)\s+(the|their)\s+(lead\s+actor|actor|actress|director|runner\s+up|captain|coach|ceo|founder|winner)\b",
    r"^(and\s+)?(its\s+)?(budget|price|director|release\s+date|lead\s+actor|running\s+time|runtime|score|captain|winner)\??$",
]

DEMONSTRATIVE_PATTERNS = [
    r"\b(that|this)\s+(match|game|tournament|cup|team|player|device|phone|company|model|chip|movie|film|event)\b",
    r"\bthe\s+(final|winner|captain|event|launch|games|olympics|movie|film)\b",
    r"\bin\s+that\s+(tournament|match|year|event|movie|film)\b",
]


NON_PERSON_KEYWORDS = {
    "moon", "mars", "sun", "earth", "jupiter", "saturn", "venus", "mercury", "neptune", "uranus", "pluto",
    "apollo", "voyager", "curiosity", "perseverance", "chandrayaan", "artemis", "iss", "hubble", "falcon", "starship",
    "everest", "himalayas", "mariana trench", "pacific", "atlantic", "amazon", "nile", "ganges", "alps", "sahara", "antarctica",
    "india", "america", "usa", "france", "england", "australia", "germany", "japan", "china", "russia", "spain", "argentina",
    "delhi", "mumbai", "london", "paris", "tokyo", "new york", "washington", "ahmedabad",
    "apple", "google", "microsoft", "amazon", "tesla", "sony", "nintendo", "meta", "openai", "samsung",
    "cup", "world cup", "olympics", "tournament", "championship", "super bowl", "final", "match", "games",
    "iphone", "ipad", "macbook", "playstation", "xbox", "model 3", "model y", "movie", "film", "book", "oppenheimer", "inception"
}


def make_possessive(entity: str) -> str:
    """Formats entity into grammatical possessive, preventing double possessives."""
    clean = entity.strip()
    if clean.endswith("'s") or clean.endswith("’s"):
        return clean
    if clean.endswith("'") or clean.endswith("’"):
        return clean
    if clean.endswith("s") or clean.endswith("S"):
        return clean + "'"
    return clean + "'s"


def is_person_entity(name: str) -> bool:
    """Checks whether an entity name represents a human person rather than a place, object, or organization."""
    if not name or name.isdigit():
        return False
    lower = name.lower().strip()
    for npk in NON_PERSON_KEYWORDS:
        if lower == npk or lower.startswith(npk + " ") or lower.endswith(" " + npk):
            return False
    if re.search(r"\b(cup|world|stadium|games|olympic|apple|google|microsoft|amazon|movie|film|device|phone|trench|mountain|planet|mission)\b", lower):
        return False
    words = name.split()
    if len(words) >= 2 and all(w[0].isupper() for w in words):
        return True
    return len(words) == 1 and words[0][0].isupper() and lower not in NON_PERSON_KEYWORDS


class ConversationTurn(BaseModel):
    """Snapshot of a single conversational turn."""
    turn_id: int
    user_query: str
    resolved_query: str
    response_text: str = ""
    primary_entity: Optional[str] = None
    all_entities: List[str] = Field(default_factory=list)
    topic_domain: str = "GENERAL"
    timestamp: float = Field(default_factory=time.time)


class ConversationContextManager:
    """
    Stateful conversational memory and coreference resolution engine (Sprint 5.3).
    Maintains structured multi-turn conversation state and performs context-aware query resolution.
    """

    def __init__(self, max_history_turns: int = 8):
        self.max_history_turns = max_history_turns
        self.history: List[ConversationTurn] = []
        self.state = StructuredConversationState()

    def clear(self):
        """Clears conversational history and resets structured state."""
        self.history.clear()
        self.state = StructuredConversationState()

    def classify_domain(self, text: str) -> str:
        """Classifies text into high-level knowledge domain."""
        lower = text.lower()
        scores = {}
        for domain, keywords in DOMAIN_SIGNATURES.items():
            matched = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", lower))
            if matched > 0:
                scores[domain] = matched

        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return "GENERAL"

    def detect_topic_change(self, query: str) -> bool:
        """
        Determines whether the new query switches to a completely disjoint topic.
        Guards against false topic resets when query contains pronouns or elliptical follow-ups.
        """
        if not self.history:
            return False

        # If query is clearly a follow-up, do NOT trigger a topic change
        if self.detect_follow_up(query):
            return False

        last_turn = self.history[-1]
        current_domain = self.classify_domain(query)
        last_domain = last_turn.topic_domain

        # If both belong to specific non-general domains and they are completely different
        if current_domain != "GENERAL" and last_domain != "GENERAL":
            if current_domain != last_domain:
                return True

        # Check substantive word overlap with last turn
        stopwords = {
            "the", "a", "an", "is", "was", "are", "were", "and", "or", "in", "on", "at",
            "to", "from", "of", "what", "who", "which", "tell", "me", "explain", "how", "about"
        }
        current_words = {w for w in re.findall(r"\b[a-zA-Z]{3,}\b", query.lower()) if w not in stopwords}
        last_words = {w for w in re.findall(r"\b[a-zA-Z]{3,}\b", (last_turn.user_query + " " + last_turn.response_text).lower()) if w not in stopwords}

        overlap = current_words.intersection(last_words)
        
        # If query has zero overlap with previous turn and is a self-contained multi-word query
        if len(overlap) == 0 and len(current_words) >= 3:
            # If current query introduces its own distinct proper entity
            proper_ents = re.findall(r"\b[A-Z][a-zA-Z0-9']*(?:\s+[A-Z][a-zA-Z0-9']*)*\b", query)
            banned = {"Who", "What", "Which", "When", "Where", "How", "Tell"}
            real_ents = [p for p in proper_ents if p not in banned]
            if real_ents:
                return True

        return False

    def detect_follow_up(self, query: str) -> bool:
        """
        Detects if query contains pronouns, elliptical questions, or relative demonstratives
        indicating it depends on prior turns.
        """
        lower = query.lower().strip()

        # 1. Pronoun presence (including 'it' and 'its')
        for pat in PRONOUN_PATTERNS:
            if re.search(pat, lower):
                return True

        # 2. Elliptical questions ("What about the final?", "In what year was it released?", "And in 2028?")
        for pat in ELLIPTICAL_PATTERNS:
            if re.search(pat, lower):
                return True

        # 3. Relative demonstratives ("that match", "this team", "the games")
        for pat in DEMONSTRATIVE_PATTERNS:
            if re.search(pat, lower):
                return True

        # 4. Ultra-short follow-up queries (<= 4 words without independent subject)
        words = lower.split()
        if len(words) <= 4:
            proper_ents = [p for p in re.findall(r"\b[A-Z][a-zA-Z0-9']*\b", query) if p not in {"Who", "What", "Which", "When", "Where", "How", "Why", "Tell", "Can", "And", "In", "At", "On"}]
            if not proper_ents and any(w in words for w in ["who", "what", "when", "where", "how", "why", "and", "in", "at"]):
                return True

        return False

    def classify_intent(self, query: str) -> FollowUpIntent:
        """
        Classifies user query into canonical follow-up intent enum.
        Considers structured state, domain shifts, and coreference cues.
        """
        if not self.history:
            return FollowUpIntent.NEW_TOPIC

        if self.detect_topic_change(query):
            return FollowUpIntent.NEW_TOPIC

        lower = query.lower().strip()

        # 1. Year Change: "What about in 2011?", "In 2018?", "And in 2028?"
        if re.search(r"(?:what|how)\s+about\s+(?:in\s+)?\b(19\d\d|20\d\d)\b", lower) or re.search(r"^(?:and\s+)?(?:in\s+)?\b(19\d\d|20\d\d)\??$", lower):
            return FollowUpIntent.YEAR_CHANGE

        # 2. Event Change: "What about the semi-final?", "In the 2024 T20 World Cup?"
        if re.search(r"\b(semi-final|semifinal|quarter-final|quarterfinal|group stage|super 8)\b", lower):
            return FollowUpIntent.EVENT_CHANGE

        # 3. Entity Change: "Who was the lead actor?", "What about the Pro Max?", "Who was the runner up?"
        if re.search(r"\b(lead actor|actor|actress|runner up|pro max|plus|ultra|opponent)\b", lower):
            return FollowUpIntent.ENTITY_CHANGE

        # 4. Attribute Change: "What about its budget?", "What was its starting price?"
        if re.search(r"\b(budget|price|cost|revenue|battery|specs|camera|runtime|net worth)\b", lower):
            return FollowUpIntent.ATTRIBUTE_CHANGE

        # 5. Check ambiguity: multiple persons in history with generic "he" / "she"
        person_entities = [e for e in self.state.related_entities if not e.isdigit() and not re.search(r"(cup|world|stadium|games|olympic|apple|google|microsoft|amazon)", e, re.IGNORECASE)]
        if len(person_entities) > 1 and re.search(r"\b(he|him|his|she|her)\b", lower):
            if not any(p.lower() in lower for p in person_entities):
                return FollowUpIntent.AMBIGUOUS_FOLLOW_UP

        if self.detect_follow_up(query):
            return FollowUpIntent.FOLLOW_UP

        return FollowUpIntent.NEW_TOPIC

    def extract_entities_from_text(self, text: str) -> List[str]:
        """
        Extracts salient entities (Proper nouns, capitalized entities, years, models).
        Handles contractions and compound titles like "ICC Men's Cricket World Cup".
        """
        candidates = re.findall(r"\b[A-Z][a-zA-Z0-9']*(?:\s+[A-Z][a-zA-Z0-9']*)*\b", text)
        banned = {"Who", "What", "Which", "When", "Where", "How", "Tell", "Explain", "Can", "User", "Query", "Project", "Nova"}
        entities = [c for c in candidates if c not in banned and len(c) > 2]
        
        # Extract years (e.g. 2023, 2024)
        years = re.findall(r"\b(19\d\d|20\d\d)\b", text)
        for y in years:
            if y not in entities:
                entities.append(y)

        return entities

    def rewrite_to_standalone(self, query: str) -> str:
        """
        Resolves coreferences and transforms dependent follow-ups into standalone queries.
        Preserves entities, events, years, and attributes from structured state.
        """
        if not self.history:
            return query

        last_turn = self.history[-1]
        lower_q = query.lower().strip()
        rewritten = query

        active_entity = self.state.active_entity or last_turn.primary_entity
        tournament = self.state.active_event
        active_year = self.state.relevant_year

        # 1. Year Change: "What about in 2011?" / "And in 2028?" / "In 2018?"
        year_match = re.search(r"\b(19\d\d|20\d\d)\b", lower_q)
        if year_match and (re.search(r"^(what|how)\s+about", lower_q) or re.search(r"^(and\s+)?(in\s+)?\d{4}", lower_q)):
            target_year = year_match.group(1)
            # Swap previous year in resolved query
            if last_turn and re.search(r"\b(19\d\d|20\d\d)\b", last_turn.resolved_query):
                return re.sub(r"\b(19\d\d|20\d\d)\b", target_year, last_turn.resolved_query)
            elif tournament:
                return f"Who won the {target_year} {tournament}?"
            elif active_entity:
                return f"What was {active_entity} in {target_year}?"

        # 2. Pronoun Substitutions: it / its
        if active_entity:
            # Replace its with entity's (using make_possessive to prevent double possessives)
            rewritten = re.sub(r"\bits\b", make_possessive(active_entity), rewritten, flags=re.IGNORECASE)
            # Replace it with entity
            rewritten = re.sub(r"\bit\b", active_entity, rewritten, flags=re.IGNORECASE)

        # 3. Person Pronoun Substitutions: he / him / his, she / her / hers
        person = None
        for ent in [active_entity] + self.state.related_entities:
            if ent and is_person_entity(ent):
                person = ent
                break

        if person:
            rewritten = re.sub(r"\bhis\b", make_possessive(person), rewritten, flags=re.IGNORECASE)
            rewritten = re.sub(r"\b(he|him)\b", person, rewritten, flags=re.IGNORECASE)
            rewritten = re.sub(r"\bhers\b", make_possessive(person), rewritten, flags=re.IGNORECASE)
            rewritten = re.sub(r"\b(she|her)\b", person, rewritten, flags=re.IGNORECASE)
        elif re.search(r"\b(he|she|him|his|her)\b", lower_q) and last_turn:
            # If no named person found, resolve from role description in prior turn
            role_match = re.search(r"\b(the\s+(?:first\s+)?(?:astronaut|person|human|man|woman|director|captain|actor|actress|author|scientist|president|minister))\b", last_turn.resolved_query, re.IGNORECASE)
            if role_match:
                role = role_match.group(1)
                rewritten = re.sub(r"\bhis\b", make_possessive(role), rewritten, flags=re.IGNORECASE)
                rewritten = re.sub(r"\b(he|him)\b", role, rewritten, flags=re.IGNORECASE)
                rewritten = re.sub(r"\bhers\b", make_possessive(role), rewritten, flags=re.IGNORECASE)
                rewritten = re.sub(r"\b(she|her)\b", role, rewritten, flags=re.IGNORECASE)

        # 4. Organization / Team Pronoun Substitutions: they / them / their / theirs
        team_or_org = None
        for ent in [active_entity] + self.state.related_entities:
            if ent and re.search(r"(australia|india|england|south africa|pakistan|apple|microsoft|google|amazon|chiefs|spain|argentina)", ent, re.IGNORECASE):
                team_or_org = ent
                break
        if not team_or_org and active_entity:
            team_or_org = active_entity

        if team_or_org:
            rewritten = re.sub(r"\btheir\b", make_possessive(team_or_org), rewritten, flags=re.IGNORECASE)
            rewritten = re.sub(r"\btheirs\b", make_possessive(team_or_org), rewritten, flags=re.IGNORECASE)
            rewritten = re.sub(r"\bthey\b", team_or_org, rewritten, flags=re.IGNORECASE)
            rewritten = re.sub(r"\bthem\b", team_or_org, rewritten, flags=re.IGNORECASE)

        # 5. Demonstrative Substitutions: "that movie", "that match", "the games", "in that tournament"
        if active_entity:
            rewritten = re.sub(r"\b(that|this)\s+(movie|film|book|novel)\b", active_entity, rewritten, flags=re.IGNORECASE)
            rewritten = re.sub(r"\b(that|this)\s+(device|phone|smartphone|console)\b", active_entity, rewritten, flags=re.IGNORECASE)
        if tournament:
            rewritten = re.sub(r"\b(that match|the final)\b", f"the {tournament} final match", rewritten, flags=re.IGNORECASE)
            rewritten = re.sub(r"\b(that|the)\s+tournament\b", f"the {tournament}", rewritten, flags=re.IGNORECASE)
            rewritten = re.sub(r"\bin\s+that\s+tournament\b", f"in the {tournament}", rewritten, flags=re.IGNORECASE)
            rewritten = re.sub(r"\bthe\s+games\b", f"the {tournament}", rewritten, flags=re.IGNORECASE)

        # 6. Elliptical questions: "Who was their captain?", "Who was the lead actor?", "What was the budget?"
        if re.search(r"\b(lead actor|actor|actress|director)\b", lower_q) and active_entity and active_entity.lower() not in rewritten.lower():
            rewritten = f"{rewritten.rstrip('?')} in {active_entity}?"

        if re.search(r"who\s+was\s+(?:their|the)\s+captain", lower_q):
            if team_or_org and tournament:
                return f"Who was {team_or_org}'s captain in the {tournament}?"
            elif team_or_org:
                return f"Who was {team_or_org}'s captain?"
            elif tournament:
                return f"Who was the winning captain in the {tournament}?"

        if re.search(r"who\s+was\s+the\s+runner\s+up", lower_q):
            if tournament:
                return f"Who was the runner up in the {tournament}?"

        # Short elliptical: "What about the final?", "Score?"
        if re.search(r"^(what|how)\s+about\s+the\s+final", lower_q):
            if tournament:
                return f"Scorecard and result of {tournament} final match"
            elif team_or_org:
                return f"{team_or_org} final match result"

        # Short 2-word follow-up: "And budget?" / "Release date?"
        if re.search(r"^(and\s+)?(its\s+)?(budget|price|cost|release\s+date|runtime|founder|ceo)\??$", lower_q) and active_entity:
            attr = re.sub(r"^(and\s+)?(its\s+)?", "", lower_q).rstrip("?").strip()
            rewritten = f"What was the {attr} of {active_entity}?"

        # Clean double possessives (e.g. Apple's's -> Apple's)
        rewritten = re.sub(r"('s)+'s", "'s", rewritten)
        rewritten = re.sub(r"('s)'", "'s", rewritten)
        rewritten = re.sub(r"\b(\w+)'s's\b", r"\1's", rewritten)

        return rewritten

    def resolve_turn(self, user_query: str) -> Tuple[str, bool, bool]:
        """
        Primary interface called before routing:
        Returns: (effective_query, is_follow_up, topic_changed)
        """
        intent = self.classify_intent(user_query)

        if intent == FollowUpIntent.NEW_TOPIC:
            logger.info(f"Topic change detected. Clearing previous conversational context.")
            self.clear()
            return user_query, False, True

        # Dependent follow-up
        rewritten = self.rewrite_to_standalone(user_query)
        logger.info(
            f"Context Resolved | Intent: {intent.value} | Entity: {self.state.active_entity} | "
            f"Event: {self.state.active_event} | Year: {self.state.relevant_year} | "
            f"'{user_query}' -> '{rewritten}'"
        )
        return rewritten, True, False

    def add_turn(
        self,
        user_query: str,
        resolved_query: str,
        response_text: str = "",
        primary_entity: Optional[str] = None
    ):
        """
        Appends turn to history, extracts salient entities, updates structured state.
        """
        all_ents = self.extract_entities_from_text(resolved_query)
        if response_text:
            all_ents.extend(self.extract_entities_from_text(response_text[:400]))

        # Deduplicate while preserving order
        seen = set()
        dedup_ents = []
        for e in all_ents:
            if e.lower() not in seen:
                seen.add(e.lower())
                dedup_ents.append(e)

        # Detect active event and year
        years = re.findall(r"\b(19\d\d|20\d\d)\b", resolved_query)
        active_year = years[0] if years else None

        active_event = None
        for e in dedup_ents:
            if re.search(r"(world cup|olympics|olympic games|championship|super bowl|euro \d{4}|final)", e, re.IGNORECASE):
                active_event = e
                break

        # Priority entity selection (specific product/movie/person over generic company)
        if not primary_entity and dedup_ents:
            candidates = [e for e in dedup_ents if not e.isdigit() and e != active_event]
            if candidates:
                # If question asked "Who...", prioritize person entities
                if re.match(r"^who\b", user_query.strip(), re.IGNORECASE):
                    persons = [c for c in candidates if is_person_entity(c)]
                    if persons:
                        candidates = persons + [c for c in candidates if c not in persons]
                # Prefer movie/product/person over company
                preferred = [c for c in candidates if not re.search(r"^(Apple|Google|Microsoft|Amazon)$", c, re.IGNORECASE)]
                primary_entity = preferred[0] if preferred else candidates[0]
            else:
                primary_entity = dedup_ents[0]

        # Update structured conversation state
        self.state.active_topic = self.classify_domain(resolved_query)
        self.state.active_entity = primary_entity
        self.state.related_entities = dedup_ents
        self.state.active_event = active_event
        self.state.relevant_year = active_year
        self.state.previous_user_question = user_query
        self.state.previous_resolved_query = resolved_query
        self.state.previous_answer = response_text
        self.state.ambiguity_status = "CLEAR"

        turn = ConversationTurn(
            turn_id=len(self.history) + 1,
            user_query=user_query,
            resolved_query=resolved_query,
            response_text=response_text,
            primary_entity=primary_entity,
            all_entities=dedup_ents,
            topic_domain=self.state.active_topic,
        )

        self.history.append(turn)
        if len(self.history) > self.max_history_turns:
            self.history.pop(0)
