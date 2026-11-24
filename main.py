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

import sys
import time
from pathlib import Path
from typing import List

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings
from intelligence.router import IntelligentQueryRouter
from intelligence.schemas import RouteType, RoutingDecision
from models.ollama_adapter import OllamaAdapter
from retriever.extractor import WebContentExtractor
from retriever.models import ExtractedDocument
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

    def __init__(self):
        print(f"{CYAN}Initializing Project NOVA Core Engines...{RESET}")
        self.router = IntelligentQueryRouter()
        self.search_engine = WebSearchEngine(max_results=settings.MAX_SEARCH_RESULTS)
        self.extractor = WebContentExtractor(max_chars_per_page=3000)
        # Synthesizer model: Qwen 2.5 3B (Reasoning and Citations)
        self.synthesizer = OllamaAdapter(model_name=settings.SYNTHESIS_MODEL)
        print(f"{GREEN}✓ NOVA Ready: Router ({settings.ROUTER_MODEL}) | Synthesizer ({settings.SYNTHESIS_MODEL}){RESET}\n")

    def process_query(self, user_query: str):
        """
        End-to-end processing pipeline for a single user turn.
        """
        start_total = time.time()
        print(f"\n{BOLD}User Query:{RESET} {user_query}")
        print(f"{YELLOW}------------------------------------------------------------{RESET}")

        # -------------------------------------------------------------
        # 1. INTELLIGENT QUERY ROUTING
        # -------------------------------------------------------------
        start_route = time.time()
        decision: RoutingDecision = self.router.route(user_query)
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
            # Stream response in real-time
            for token in self.synthesizer.stream(user_query, system_prompt=system_prompt):
                sys.stdout.write(token)
                sys.stdout.flush()
            print()

        # -------------------------------------------------------------
        # 3. DISPATCH: WEB SEARCH & EXTRACTION
        # -------------------------------------------------------------
        elif decision.primary_route in [RouteType.WEB_SEARCH, RouteType.HYBRID]:
            search_queries = decision.search_queries or [user_query]
            print(f"\n{CYAN}[LIVE WEB SEARCH]{RESET} -> Searching keywords: {search_queries}")

            # 3A. Search DuckDuckGo
            search_results = self.search_engine.multi_search(search_queries, max_total_results=3)

            if not search_results:
                print(f"{YELLOW}Warning: No web search results returned. Falling back to internal knowledge.{RESET}")
                print(f"{BOLD}\nNOVA Response:{RESET}\n")
                for token in self.synthesizer.stream(user_query):
                    sys.stdout.write(token)
                    sys.stdout.flush()
                print()
                return

            print(f"  • Found {len(search_results)} relevant sources. Extracting clean content...")

            # 3B. Parallel Trafilatura Content Extraction
            start_extract = time.time()
            extracted_docs: List[ExtractedDocument] = self.extractor.extract_batch(search_results)
            extract_time = time.time() - start_extract
            print(f"  • Extracted {len(extracted_docs)} web pages in {extract_time:.2f}s")

            # 3C. Construct Grounded Evidence Context
            evidence_context = self._format_evidence_context(extracted_docs)

            # 3D. Grounded Synthesis Prompt
            grounded_system_prompt = (
                "You are Project NOVA (Neural Orchestrator for Verified Answers).\n"
                "You MUST answer the user's question based strictly on the provided Web Evidence.\n\n"
                "CITATION RULES:\n"
                "1. Every factual statement or claim MUST cite its source using bracketed numbers, e.g. [1] or [2].\n"
                "2. If evidence presents conflicting information, explicitly state the conflict.\n"
                "3. If the evidence does not contain sufficient information, state clearly what could not be verified.\n"
                "4. At the very end of your answer, include a 'Sources:' section listing each cited URL."
            )

            synthesis_prompt = (
                f"USER QUESTION: {user_query}\n\n"
                f"WEB EVIDENCE:\n{evidence_context}\n\n"
                f"Please synthesize a clear, grounded response with inline bracketed citations [1], [2]:"
            )

            print(f"{BOLD}\nNOVA Grounded Response (With Citations):{RESET}\n")
            for token in self.synthesizer.stream(synthesis_prompt, system_prompt=grounded_system_prompt):
                sys.stdout.write(token)
                sys.stdout.flush()
            print()

            # Always display clean verified source links below the answer
            print(f"\n{BOLD}Verified Sources:{RESET}")
            for doc in extracted_docs:
                meta = f" (Date: {doc.published_date})" if doc.published_date else ""
                print(f"  [{doc.source_index}] {doc.title}{meta} -> {CYAN}{doc.url}{RESET}")

        # -------------------------------------------------------------
        # 4. DISPATCH: INTERNAL RAG (Day 2 Preview)
        # -------------------------------------------------------------
        elif decision.primary_route == RouteType.INTERNAL_RAG:
            print(f"\n{YELLOW}[INTERNAL RAG]{RESET} (Private Document Retrieval - Scheduled for Day 2)")
            print("Note: Document Vector Store will be linked tomorrow in Day 2. Answering with current context:")
            print(f"{BOLD}\nNOVA Response:{RESET}\n")
            for token in self.synthesizer.stream(user_query):
                sys.stdout.write(token)
                sys.stdout.flush()
            print()

        total_time = time.time() - start_total
        print(f"\n{YELLOW}------------------------------------------------------------{RESET}")
        print(f"{CYAN}✓ Total Execution Latency: {total_time:.2f}s{RESET}\n")

    def _format_evidence_context(self, docs: List[ExtractedDocument]) -> str:
        """Formats clean extracted web documents into standardized evidence blocks."""
        blocks = []
        for doc in docs:
            snippet = doc.clean_text[:1200]  # Cap each source snippet for optimal token budget
            meta_parts = []
            if doc.published_date:
                meta_parts.append(f"Date: {doc.published_date}")
            if doc.author:
                meta_parts.append(f"Author: {doc.author}")
            meta_str = f" ({', '.join(meta_parts)})" if meta_parts else ""

            block = (
                f"--- SOURCE [{doc.source_index}]: {doc.title}{meta_str} ---\n"
                f"URL: {doc.url}\n"
                f"CONTENT:\n{snippet}\n"
            )
            blocks.append(block)
        return "\n".join(blocks)


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

            orchestrator.process_query(query)

        except KeyboardInterrupt:
            print(f"\n{CYAN}Session ended.{RESET}")
            break
        except Exception as e:
            print(f"\n{YELLOW}Error processing query: {e}{RESET}")


if __name__ == "__main__":
    main()
