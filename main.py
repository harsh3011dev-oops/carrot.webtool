"""
PROJECT NOVA - Interactive Terminal Orchestrator (Day 1)
========================================================
Brings together:
1. Base Model Adapter (Qwen 2.5 1.5B & 3B)
2. Intelligent Query Router (HMSQR - Static vs Dynamic vs Search)
3. Live Web Search Engine (DuckDuckGo - Zero Cost)
4. Noise-Free Content Extractor (Parallel Trafilatura)

Run this file to chat interactively with Project NOVA!
"""

import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings
from grounding.schemas import ResponseState, VerifiedResponse
from grounding.verifier import ClaimVerifier
from intelligence.context_manager import ConversationContextManager
from intelligence.router import IntelligentQueryRouter, normalize_query
from intelligence.schemas import RouteType, RoutingDecision
from models.ollama_adapter import OllamaAdapter
from retriever.chunker import select_top_evidence_chunks
from retriever.entity_matcher import extract_entity_profile
from retriever.extractor import WebContentExtractor
from retriever.models import ExtractedDocument
from retriever.news_db_retriever import LocalNewsRetriever
from retriever.relevance import filter_and_rank_documents, is_evidence_relevant, is_evidence_sufficient
from retriever.web_search import WebSearchEngine

# ANSI color codes for clean terminal presentation
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


class NovaOrchestrator:
    """
    Main coordinator for Project NOVA.
    Dispatches queries based on intelligent routing decisions.
    """

    def __init__(self, verifier_mode: str = "hybrid"):
        print(f"{CYAN}Initializing Project NOVA Core Engines...{RESET}")
        self.router = IntelligentQueryRouter()
        self.search_engine = WebSearchEngine(max_results=settings.MAX_SEARCH_RESULTS)
        self.extractor = WebContentExtractor(max_chars_per_page=3000)
        self.news_db = LocalNewsRetriever()
        # Synthesizer model: Qwen 2.5 Coder (High-Reasoning and Citations)
        self.synthesizer = OllamaAdapter(model_name=settings.SYNTHESIS_MODEL)
        # Truth and Grounding Engine (Sprint 3)
        self.verifier = ClaimVerifier(mode=verifier_mode)
        # Conversation Intelligence & Memory (Sprint 4)
        self.context_manager = ConversationContextManager()
        print(f"{GREEN}✓ NOVA Ready: Router ({settings.ROUTER_MODEL}) | Synthesizer ({settings.SYNTHESIS_MODEL}) | Verifier ({verifier_mode}) | Context Memory Ready{RESET}\n")

    def _display_truth_state(self, verified: VerifiedResponse):
        """Displays standard machine-readable truth badge and factual metrics."""
        RED = "\033[91m"
        color_map = {
            ResponseState.VERIFIED: GREEN,
            ResponseState.PARTIAL: YELLOW,
            ResponseState.UNVERIFIED: MAGENTA,
            ResponseState.ABSTAIN: RED,
        }
        color = color_map.get(verified.response_state, YELLOW)
        print(f"\n{color}[TRUTH STATE: {verified.response_state.value}]{RESET}")
        if verified.claims:
            supported_count = len(verified.claims) - verified.unsupported_claims_count
            print(f"  • Claims Audited: {len(verified.claims)} | Supported: {supported_count} | Unsupported: {verified.unsupported_claims_count}")
            print(f"  • Citation Support Rate: {verified.citation_support_rate * 100:.1f}%")
        elif verified.response_state == ResponseState.UNVERIFIED:
            print("  • Source: Internal Parametric Knowledge (Uncorroborated by retrieval)")
        elif verified.response_state == ResponseState.ABSTAIN:
            print("  • Reason: Insufficient evidence to substantiate factual claims")

    def process_query(self, user_query: str, conversation_context: Optional[Dict] = None) -> Optional[VerifiedResponse]:
        """
        End-to-end processing pipeline for a single user turn.
        Accepts optional conversation_context for multi-turn coreference resolution (Sprint 4 hook).
        Returns VerifiedResponse contract for testability and inspection.
        """
        start_total = time.time()
        print(f"\n{BOLD}User Query:{RESET} {user_query}")
        print(f"{YELLOW}------------------------------------------------------------{RESET}")

        # -------------------------------------------------------------
        # 0. MULTI-TURN CONTEXT RESOLUTION & STANDALONE QUERY GENERATION
        # -------------------------------------------------------------
        effective_query, is_follow_up, topic_changed = self.context_manager.resolve_turn(user_query)
        if is_follow_up:
            print(f"{CYAN}⚡ [CONTEXT RESOLUTION] Multi-turn follow-up detected.{RESET}")
            print(f"  • Raw User Query  : {user_query}")
            print(f"  • Standalone Form : {BOLD}{effective_query}{RESET}")
        elif topic_changed:
            print(f"{MAGENTA}[TOPIC SHIFT] New independent topic detected. Context cleared.{RESET}")

        # -------------------------------------------------------------
        # 1. INTELLIGENT QUERY ROUTING
        # -------------------------------------------------------------
        start_route = time.time()
        decision: RoutingDecision = self.router.route(effective_query)
        route_time = time.time() - start_route

        print(f"{MAGENTA}[ROUTER DECISION]{RESET}")
        print(f"  • Primary Route   : {BOLD}{decision.primary_route.value}{RESET}")
        print(f"  • Tier Decision   : {decision.tier_source} ({route_time:.2f}s)")
        print(f"  • Volatility      : {decision.volatility.value}")
        print(f"  • Time Sensitive  : {decision.is_time_sensitive}")
        print(f"  • Rationale       : {decision.reasoning}")

        # -------------------------------------------------------------
        # 2. DISPATCH: INTERNAL LLM (No Web Search Needed)
        # -------------------------------------------------------------
        if decision.primary_route == RouteType.INTERNAL_LLM:
            print(f"\n{CYAN}[INTERNAL GENERATION]{RESET} (Pretrained knowledge, zero search cost)")
            system_prompt = (
                "You are Project NOVA, an intelligent, concise, and helpful AI assistant. "
                "Provide a direct, accurate, and structured answer to the user's question."
            )
            print(f"{BOLD}\nNOVA Response:{RESET}\n")
            tokens = []
            for token in self.synthesizer.stream(effective_query, system_prompt=system_prompt):
                tokens.append(token)
                sys.stdout.write(token)
                sys.stdout.flush()
            print()
            raw_response = "".join(tokens)
            verified = self.verifier.audit_and_verify_response(
                effective_query, raw_response, docs=[], is_internal_generation=True
            )
            self._display_truth_state(verified)
            self.context_manager.add_turn(user_query, effective_query, response_text=verified.final_text)
            total_time = time.time() - start_total
            print(f"\n{YELLOW}------------------------------------------------------------{RESET}")
            print(f"{CYAN}✓ Total Execution Latency: {total_time:.2f}s{RESET}\n")
            return verified

        # -------------------------------------------------------------
        # 3. DISPATCH: LOCAL NEWS DATABASE & WEB SEARCH
        # -------------------------------------------------------------
        elif decision.primary_route in [RouteType.WEB_SEARCH, RouteType.HYBRID]:
            search_queries = decision.search_queries or [effective_query]

            # 3A. Query 24/7 Local News Intelligence Database first (0.00s FTS5)
            start_db = time.time()
            local_docs: List[ExtractedDocument] = self.news_db.search(effective_query, limit=3)
            db_time = time.time() - start_db

            if local_docs:
                print(f"\n{GREEN}[LOCAL NEWS INTELLIGENCE DATABASE]{RESET} -> Found {len(local_docs)} candidate articles in {db_time:.2f}s (Zero Web Latency!)")
                ranked_local = filter_and_rank_documents(effective_query, local_docs, max_return=3)
                is_local_relevant = is_evidence_relevant(effective_query, ranked_local)
                is_local_sufficient, local_reason = is_evidence_sufficient(effective_query, ranked_local)

                if is_local_relevant and is_local_sufficient:
                    response_text = self._synthesize_grounded_answer(effective_query, ranked_local)
                    verified = self.verifier.audit_and_verify_response(effective_query, response_text, ranked_local)
                    if verified.response_state != ResponseState.ABSTAIN:
                        self._print_sources(ranked_local)
                        self._display_truth_state(verified)
                        self.context_manager.add_turn(user_query, effective_query, response_text=verified.final_text)
                        total_time = time.time() - start_total
                        print(f"\n{YELLOW}------------------------------------------------------------{RESET}")
                        print(f"{CYAN}✓ Total Execution Latency: {total_time:.2f}s{RESET}\n")
                        return verified

                print(f"\n{YELLOW}⚡ [CORRECTIVE RAG] Local Database had insufficient evidence. Escalating to Live Web Search...{RESET}")

            # 3B. Live Web Search (Attempt 1 - Multi-Angle Queries & Entity Gatekeeper)
            web_docs = self._perform_live_web_search(effective_query, search_queries)
            is_attempt1_relevant = is_evidence_relevant(effective_query, web_docs) if web_docs else False
            is_attempt1_sufficient, suff_reason = is_evidence_sufficient(effective_query, web_docs) if web_docs else (False, "")

            needs_retry = False
            if web_docs and is_attempt1_relevant and is_attempt1_sufficient:
                response_text = self._synthesize_grounded_answer(effective_query, web_docs)
                verified = self.verifier.audit_and_verify_response(effective_query, response_text, web_docs)
                if verified.response_state == ResponseState.ABSTAIN:
                    needs_retry = True
                else:
                    self._print_sources(web_docs)
                    self._display_truth_state(verified)
                    self.context_manager.add_turn(user_query, effective_query, response_text=verified.final_text)
                    total_time = time.time() - start_total
                    print(f"\n{YELLOW}------------------------------------------------------------{RESET}")
                    print(f"{CYAN}✓ Total Execution Latency: {total_time:.2f}s{RESET}\n")
                    return verified
            else:
                needs_retry = True

            # 3C. Corrective Web Search Retry (Attempt 2 - Canonical Query Reformulation)
            if needs_retry:
                retry_queries = self._formulate_retry_queries(effective_query)
                print(f"\n{YELLOW}⚡ [CORRECTIVE RAG - RETRY] Initial evidence was off-target or incomplete. Reformulating canonical queries...{RESET}")
                retry_docs = self._perform_live_web_search(effective_query, retry_queries)
                if retry_docs:
                    print(f"{BOLD}\nNOVA Corrected Grounded Response:{RESET}\n")
                    response_text = self._synthesize_grounded_answer(effective_query, retry_docs)
                    verified = self.verifier.audit_and_verify_response(effective_query, response_text, retry_docs)
                    self._print_sources(retry_docs)
                    self._display_truth_state(verified)
                    self.context_manager.add_turn(user_query, effective_query, response_text=verified.final_text)
                    total_time = time.time() - start_total
                    print(f"\n{YELLOW}------------------------------------------------------------{RESET}")
                    print(f"{CYAN}✓ Total Execution Latency: {total_time:.2f}s{RESET}\n")
                    return verified

            # Fallback if both Local and Web attempts yielded zero usable evidence
            print(f"{YELLOW}Warning: External retrieval could not verify evidence. Falling back to internal knowledge.{RESET}")
            print(f"{BOLD}\nNOVA Response:{RESET}\n")
            tokens = []
            for token in self.synthesizer.stream(effective_query):
                tokens.append(token)
                sys.stdout.write(token)
                sys.stdout.flush()
            print()
            raw_fallback = "".join(tokens)
            verified = self.verifier.audit_and_verify_response(
                effective_query, raw_fallback, docs=[], is_internal_generation=True
            )
            self._display_truth_state(verified)
            self.context_manager.add_turn(user_query, effective_query, response_text=verified.final_text)
            total_time = time.time() - start_total
            print(f"\n{YELLOW}------------------------------------------------------------{RESET}")
            print(f"{CYAN}✓ Total Execution Latency: {total_time:.2f}s{RESET}\n")
            return verified

        # -------------------------------------------------------------
        # 4. DISPATCH: INTERNAL RAG (Day 2 Preview)
        # -------------------------------------------------------------
        elif decision.primary_route == RouteType.INTERNAL_RAG:
            print(f"\n{YELLOW}[INTERNAL RAG]{RESET} (Private Document Retrieval - Scheduled for Day 2)")
            print("Note: Document Vector Store will be linked tomorrow in Day 2. Answering with current context:")
            print(f"{BOLD}\nNOVA Response:{RESET}\n")
            tokens = []
            for token in self.synthesizer.stream(effective_query):
                tokens.append(token)
                sys.stdout.write(token)
                sys.stdout.flush()
            print()
            raw_resp = "".join(tokens)
            verified = self.verifier.audit_and_verify_response(
                effective_query, raw_resp, docs=[], is_internal_generation=True
            )
            self._display_truth_state(verified)
            self.context_manager.add_turn(user_query, effective_query, response_text=verified.final_text)
            total_time = time.time() - start_total
            print(f"\n{YELLOW}------------------------------------------------------------{RESET}")
            print(f"{CYAN}✓ Total Execution Latency: {total_time:.2f}s{RESET}\n")
            return verified

        total_time = time.time() - start_total
        print(f"\n{YELLOW}------------------------------------------------------------{RESET}")
        print(f"{CYAN}✓ Total Execution Latency: {total_time:.2f}s{RESET}\n")

    def _format_evidence_context(self, user_query: str, docs: List[ExtractedDocument]) -> str:
        """
        Formats evidence blocks using multi-signal paragraph chunks (Sprint 5).
        Selects exact answer-bearing passages anywhere in the document (eliminating 1,200-char blindness).
        """
        chunks = select_top_evidence_chunks(user_query, docs, max_chunks=4, max_total_chars=4500)
        if not chunks:
            # Fallback to direct document text if chunking produced empty
            blocks = []
            for doc in docs:
                blocks.append(f"--- SOURCE [{doc.source_index}]: {doc.title} ---\nURL: {doc.url}\nCONTENT:\n{doc.clean_text[:2000]}\n")
            return "\n".join(blocks)

        blocks = []
        for c in chunks:
            meta_parts = []
            if c.published_date:
                meta_parts.append(f"Date: {c.published_date}")
            if c.author:
                meta_parts.append(f"Author: {c.author}")
            if c.heading:
                meta_parts.append(f"Section: {c.heading}")
            meta_str = f" ({', '.join(meta_parts)})" if meta_parts else ""

            block = (
                f"--- SOURCE [{c.source_index}]: {c.title}{meta_str} ---\n"
                f"URL: {c.url}\n"
                f"CONTENT:\n{c.text}\n"
            )
            blocks.append(block)
        return "\n".join(blocks)

    def _formulate_retry_queries(self, user_query: str) -> List[str]:
        """
        Intent-Specific Corrective RAG Retry Query Generator (Sprint 5).
        Generates targeted queries focused on the specific missing entity and attribute.
        """
        clean = normalize_query(user_query)
        # Strip conversational question framing
        clean_core = re.sub(
            r"^(who\s+(won|is|was|has|have)|which\s+(team|country|player)\s+won|what\s+is|tell\s+me\s+(about\s+)?(who\s+was\s+)?|explain\s+(how\s+)?|can\s+you\s+tell\s+me\s+)\s*",
            "",
            clean,
            flags=re.IGNORECASE
        )
        clean_core = re.sub(r"\b(won\s+last|last\s+won|won|latest|recent)\b", "", clean_core, flags=re.IGNORECASE)
        clean_core = re.sub(r"[?!.,]+$", "", clean_core).strip()
        clean_core = re.sub(r"\s+", " ", clean_core)
        if len(clean_core) < 3:
            clean_core = clean

        lower_q = clean.lower()
        ent_prof = extract_entity_profile(clean)

        def matches_kw(keywords: List[str]) -> bool:
            return any(re.search(r"\b" + re.escape(k) + r"\b", lower_q) for k in keywords)

        # 0. TARGETED ENTITY + ATTRIBUTE OVERRIDE (Sprint 5 High Precision)
        if ent_prof.requested_attribute and ent_prof.base_name:
            if ent_prof.requested_attribute == "score":
                return [
                    f"{ent_prof.base_name} {clean_core} scorecard score",
                    f"{clean_core} match result Wikipedia",
                ]
            elif ent_prof.requested_attribute == "launch_date":
                model_str = f" {ent_prof.model_or_number}" if ent_prof.model_or_number else ""
                var_str = f" {ent_prof.variant}" if ent_prof.variant else ""
                return [
                    f"{ent_prof.base_name}{model_str}{var_str} official launch release date",
                    f"{clean_core} specifications Wikipedia",
                ]
            elif ent_prof.requested_attribute == "landing_date":
                return [
                    f"{ent_prof.base_name} lunar landing date ISRO official",
                    f"{clean_core} Wikipedia",
                ]

        # 1. SPORTS INTENT: Tournaments, match results, cups, scores
        sports_keywords = ["cup", "tournament", "trophy", "match", "vs", "score", "cricket", "football", "fifa", "uefa", "champion", "olympics", "ipl", "bbl"]
        if matches_kw(sports_keywords):
            return [
                f"{clean_core} official match result scorecard",
                f"{clean_core} tournament winners final Wikipedia",
            ]

        # 2. TECHNOLOGY / ARCHITECTURE: Models, hardware, protocols, software
        tech_keywords = ["cpu", "gpu", "ram", "rom", "transformer", "model", "token", "gpt", "algorithm", "python", "software", "api", "framework", "architecture", "apple", "nvidia", "openai"]
        if matches_kw(tech_keywords):
            return [
                f"{clean_core} technical documentation architecture",
                f"{clean_core} Wikipedia overview",
            ]

        # 3. EXAMS / ADMISSIONS / OFFICIAL DATES
        exam_keywords = ["jee", "neet", "exam", "registration", "admission", "deadline", "closing date", "syllabus", "admit card", "session"]
        if matches_kw(exam_keywords):
            return [
                f"{clean_core} official notification registration dates",
                f"{clean_core} official schedule portal",
            ]

        # 4. SCIENCE / GENERAL ACADEMIC FACTS
        science_keywords = ["formula", "chemical", "planet", "solar system", "physics", "element", "biology", "molecule", "temperature"]
        if matches_kw(science_keywords):
            return [
                f"{clean_core} scientific definition formula",
                f"{clean_core} Wikipedia reference",
            ]

        # 5. NEWS / RECENT EVENTS
        news_keywords = ["news", "announcement", "minister", "president", "ceo", "policy", "launched", "event"]
        if matches_kw(news_keywords):
            return [
                f"{clean_core} official press announcement report",
                f"{clean_core} latest verified news",
            ]

        # 6. GENERAL ENCYCLOPEDIC
        return [
            f"{clean_core} Wikipedia",
            f"{clean_core} official overview facts",
        ]

    def _perform_live_web_search(self, user_query: str, search_queries: List[str]) -> List[ExtractedDocument]:
        print(f"\n{CYAN}[LIVE WEB SEARCH]{RESET} -> Searching DuckDuckGo keywords: {search_queries}")
        search_results = self.search_engine.multi_search(search_queries, max_total_results=settings.MAX_SEARCH_RESULTS)
        if not search_results:
            return []
        print(f"  • Found {len(search_results)} candidate sources. Extracting clean content...")
        start_extract = time.time()
        docs = self.extractor.extract_batch(search_results)
        extract_time = time.time() - start_extract
        print(f"  • Extracted {len(docs)} web pages in {extract_time:.2f}s")
        # Apply pre-LLM relevance filtering and ranking
        ranked_docs = filter_and_rank_documents(user_query, docs, max_return=3)
        return ranked_docs

    def _synthesize_grounded_answer(self, user_query: str, docs: List[ExtractedDocument]) -> str:
        evidence_context = self._format_evidence_context(user_query, docs)
        grounded_system_prompt = (
            "You are Project NOVA (Neural Orchestrator for Verified Answers).\n"
            "Your task is to answer the user's question accurately, concisely, and strictly based on the provided Evidence Passages.\n\n"
            "CORE GROUNDING RULES:\n"
            "1. DIRECT ANSWER FIRST: Directly answer the user's specific question in the very first sentence. Keep the answer concise and to the point.\n"
            "2. STRICT EVIDENCE FIDELITY: Every factual statement (dates, numbers, entities, scores, prices, technical specifications) must be directly supported by the retrieved Evidence. Do NOT invent or assume facts beyond what is explicitly stated in the evidence passages.\n"
            "3. NO FORCED OR INVENTED CITATIONS: Only attach inline bracketed citations [source_index] (e.g. [1]) to a sentence if that specific source chunk directly states that fact. Do NOT invent citations or attach citations merely to satisfy formatting.\n"
            "4. STRICT ENTITY & VARIANT INTEGRITY: Attribute facts ONLY to the exact entity requested. Do NOT substitute base models with variants (e.g. iPhone 16 is NOT iPhone 16e, Galaxy S24 is NOT S24 Ultra). Do NOT confuse an article's publication date with the product's actual launch/event date.\n"
            "5. INSUFFICIENT EVIDENCE HANDLING: If the provided evidence does not contain sufficient information to answer the question, state: 'The provided evidence does not contain sufficient information to answer.' Do NOT fabricate an answer.\n"
            "6. CONFLICTING EVIDENCE: If evidence passages present conflicting numbers or facts, explicitly report the conflict.\n"
            "7. SOURCES SECTION: At the very end of your response, include a 'Sources:' section listing each cited URL."
        )

        synthesis_prompt = (
            f"USER QUESTION: {user_query}\n\n"
            f"EVIDENCE PASSAGES:\n{evidence_context}\n\n"
            f"Synthesize a direct, grounded answer with inline citations [1], [2] where directly supported:"
        )

        tokens = []
        for token in self.synthesizer.stream(synthesis_prompt, system_prompt=grounded_system_prompt):
            tokens.append(token)
            sys.stdout.write(token)
            sys.stdout.flush()
        print()
        return "".join(tokens)

    def _print_sources(self, docs: List[ExtractedDocument]):
        print(f"\n{BOLD}Verified Sources:{RESET}")
        for doc in docs:
            meta = f" (Date: {doc.published_date})" if doc.published_date else ""
            print(f"  [{doc.source_index}] {doc.title}{meta} -> {CYAN}{doc.url}{RESET}")


def main():
    print("=" * 70)
    print(f"{BOLD}           PROJECT NOVA - HYBRID AI ASSISTANT (DAY 1){RESET}")
    print("      Neural Orchestrator for Verified Answers | Local-First")
    print("=" * 70)

    orchestrator = NovaOrchestrator()

    # Interactive REPL
    print(f"{GREEN}Type your question below (or type 'exit' / 'quit' to stop):{RESET}\n")

    while True:
        try:
            query = input(f"{BOLD}Ask NOVA >> {RESET}").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print(f"\n{CYAN}Goodbye from Project NOVA!{RESET}")
                break
            if query.lower() in ["/reset", "/clear", "reset"]:
                orchestrator.context_manager.clear()
                print(f"\n{CYAN}✓ Conversational memory and entity context cleared.{RESET}\n")
                continue

            orchestrator.process_query(query)

        except KeyboardInterrupt:
            print(f"\n{CYAN}Session ended.{RESET}")
            break
        except Exception as e:
            print(f"\n{YELLOW}Error processing query: {e}{RESET}")


if __name__ == "__main__":
    main()
