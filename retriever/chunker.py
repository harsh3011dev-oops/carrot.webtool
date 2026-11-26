"""
PROJECT NOVA - Paragraph-Aware Evidence Chunker & Multi-Signal Selector (Sprint 5)
==================================================================================
Eliminates the 1,200-character document head truncation blindness.
Features:
1. Paragraph-aware & heading-preserving chunking
2. Table preservation (prevents breaking structured markdown tables)
3. Multi-signal chunk ranking:
   - Lexical query overlap (BM25 style)
   - Strict Entity & Variant alignment (+40 exact match, -50 variant penalty)
   - Attribute & numerical anchor matching (dates, scores, prices, clock speeds)
   - Heading relevance & table boosts
4. Configurable token/character budget enforcement (~4,500 chars total)
5. Strict deduplication across overlapping sources
"""

import logging
import re
from typing import List, Optional, Set, Tuple

from retriever.entity_matcher import extract_entity_profile
from retriever.models import EvidenceChunk, ExtractedDocument

logger = logging.getLogger("nova.chunker")

STOPWORDS = {
    "the", "a", "an", "is", "was", "are", "were", "and", "or", "in", "on", "at",
    "by", "for", "with", "about", "against", "to", "from", "of", "it", "its", "that",
    "what", "who", "which", "when", "where", "how", "tell", "me", "find", "give"
}

AUTHORITATIVE_DOMAINS = [
    "wikipedia.org", "espncricinfo.com", "cricinfo.com", "bbc.com", "reuters.com",
    "thehindu.com", "indianexpress.com", "apple.com", "nvidia.com", "isro.gov.in"
]


def extract_paragraphs_and_headings(text: str) -> List[Tuple[Optional[str], str, bool]]:
    """
    Parses document into (heading, text_block, is_table) tuples.
    Preserves section headings and keeps markdown tables intact.
    """
    lines = text.split("\n")
    blocks: List[Tuple[Optional[str], str, bool]] = []
    
    current_heading = None
    current_lines: List[str] = []
    in_table = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_lines:
                block_text = "\n".join(current_lines).strip()
                if block_text:
                    blocks.append((current_heading, block_text, in_table))
                current_lines = []
                in_table = False
            continue

        # Check for markdown heading (# Heading)
        if re.match(r"^#{1,4}\s+", stripped):
            if current_lines:
                block_text = "\n".join(current_lines).strip()
                if block_text:
                    blocks.append((current_heading, block_text, in_table))
                current_lines = []
                in_table = False
            current_heading = re.sub(r"^#{1,4}\s+", "", stripped)
            continue

        # Check for markdown table line
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            current_lines.append(stripped)
            continue
        elif in_table:
            # Table ended
            block_text = "\n".join(current_lines).strip()
            if block_text:
                blocks.append((current_heading, block_text, True))
            current_lines = [stripped]
            in_table = False
            continue

        current_lines.append(stripped)

    if current_lines:
        block_text = "\n".join(current_lines).strip()
        if block_text:
            blocks.append((current_heading, block_text, in_table))

    return blocks


def chunk_document(
    doc: ExtractedDocument,
    target_chunk_size: int = 700,
    overlap_chars: int = 100
) -> List[EvidenceChunk]:
    """
    Decomposes an extracted document into paragraph-aware EvidenceChunks.
    Preserves headings, tables, and sentence boundaries.
    """
    raw_text = doc.clean_text or ""
    if not raw_text.strip():
        return []

    blocks = extract_paragraphs_and_headings(raw_text)
    chunks: List[EvidenceChunk] = []
    
    current_chunk_text = ""
    current_heading = None
    contains_table = False
    start_char = 0
    chunk_index = 1

    for heading, block_text, is_table in blocks:
        # If this is a table, preserve it as a dedicated chunk or distinct block
        if is_table:
            if current_chunk_text:
                # Flush current accumulator
                end_char = start_char + len(current_chunk_text)
                chunks.append(
                    EvidenceChunk(
                        chunk_id=f"doc{doc.source_index}_chunk{chunk_index}",
                        source_index=doc.source_index,
                        title=doc.title,
                        url=doc.url,
                        text=current_chunk_text.strip(),
                        start_char=start_char,
                        end_char=end_char,
                        heading=current_heading,
                        contains_table=contains_table,
                        published_date=doc.published_date,
                        author=doc.author
                    )
                )
                chunk_index += 1
                start_char = end_char
                current_chunk_text = ""
                contains_table = False

            # Add table chunk directly
            end_char = start_char + len(block_text)
            chunks.append(
                EvidenceChunk(
                    chunk_id=f"doc{doc.source_index}_chunk{chunk_index}",
                    source_index=doc.source_index,
                    title=doc.title,
                    url=doc.url,
                    text=block_text.strip(),
                    start_char=start_char,
                    end_char=end_char,
                    heading=heading or current_heading,
                    contains_table=True,
                    published_date=doc.published_date,
                    author=doc.author
                )
            )
            chunk_index += 1
            start_char = end_char
            continue

        # If section heading changes and we have accumulated content, flush current chunk
        if heading and current_heading and heading != current_heading and current_chunk_text.strip():
            end_char = start_char + len(current_chunk_text)
            chunks.append(
                EvidenceChunk(
                    chunk_id=f"doc{doc.source_index}_chunk{chunk_index}",
                    source_index=doc.source_index,
                    title=doc.title,
                    url=doc.url,
                    text=current_chunk_text.strip(),
                    start_char=start_char,
                    end_char=end_char,
                    heading=current_heading,
                    contains_table=contains_table,
                    published_date=doc.published_date,
                    author=doc.author
                )
            )
            chunk_index += 1
            start_char = end_char
            current_chunk_text = ""
            contains_table = False

        if heading:
            current_heading = heading

        # If adding block exceeds target_chunk_size and we already have content
        if len(current_chunk_text) + len(block_text) > target_chunk_size and len(current_chunk_text) > 200:
            end_char = start_char + len(current_chunk_text)
            chunks.append(
                EvidenceChunk(
                    chunk_id=f"doc{doc.source_index}_chunk{chunk_index}",
                    source_index=doc.source_index,
                    title=doc.title,
                    url=doc.url,
                    text=current_chunk_text.strip(),
                    start_char=start_char,
                    end_char=end_char,
                    heading=current_heading,
                    contains_table=contains_table,
                    published_date=doc.published_date,
                    author=doc.author
                )
            )
            chunk_index += 1
            start_char = end_char
            # Take last sentence as overlap
            sentences = re.split(r"(?<=[.!?])\s+", current_chunk_text.strip())
            current_chunk_text = (sentences[-1] + "\n\n") if len(sentences) > 1 and len(sentences[-1]) < 200 else ""
            contains_table = False

        current_chunk_text += block_text + "\n\n"

    if current_chunk_text.strip():
        end_char = start_char + len(current_chunk_text)
        chunks.append(
            EvidenceChunk(
                chunk_id=f"doc{doc.source_index}_chunk{chunk_index}",
                source_index=doc.source_index,
                title=doc.title,
                url=doc.url,
                text=current_chunk_text.strip(),
                start_char=start_char,
                end_char=end_char,
                heading=current_heading,
                contains_table=contains_table,
                published_date=doc.published_date,
                author=doc.author
            )
        )

    return chunks


def score_chunk(query: str, chunk: EvidenceChunk) -> float:
    """
    Calculates multi-dimensional relevance score for an evidence chunk.
    Signals:
    1. Substantive term overlap (BM25 lexical)
    2. Exact entity vs variant match (+40 / -50)
    3. Attribute & numerical match (dates, scores, prices)
    4. Heading keyword match (+25)
    5. Table boost (+20)
    6. Source authority (+15)
    """
    clean_q = query.lower()
    clean_text = chunk.text.lower()
    score = 0.0

    # 1. Lexical Substantive Term Overlap
    q_words = [w for w in re.findall(r"\b[a-zA-Z]{3,}\b", clean_q) if w not in STOPWORDS]
    if q_words:
        matches = sum(1 for w in q_words if w in clean_text)
        overlap_ratio = matches / len(q_words)
        score += overlap_ratio * 40.0

    # 2. Strict Entity & Variant Alignment
    query_ent = extract_entity_profile(query)
    chunk_ent = extract_entity_profile(chunk.text)

    if query_ent.model_or_number and chunk_ent.model_or_number:
        if query_ent.model_or_number == chunk_ent.model_or_number:
            score += 30.0
            # Strict variant check
            if query_ent.variant == chunk_ent.variant:
                score += 20.0
            elif query_ent.variant != chunk_ent.variant:
                # Penalize conflicting variant (e.g. iPhone 16 vs 16e)
                score -= 50.0

    if query_ent.year and chunk_ent.year:
        if query_ent.year == chunk_ent.year:
            score += 25.0
        else:
            score -= 30.0

    # 3. Attribute & Numerical Anchor Matching
    q_numbers = set(re.findall(r"\b\d+[\.\d]*%?\b", clean_q))
    if q_numbers:
        matched_nums = sum(1 for n in q_numbers if n in clean_text)
        score += (matched_nums / len(q_numbers)) * 25.0

    # Common answer attributes
    attribute_keywords = [
        "score", "price", "date", "launch", "release", "captain", "winner",
        "result", "specification", "spec", "clock", "speed", "ram", "memory",
        "vram", "core", "cores", "tdp", "bus", "refresh", "battery", "display"
    ]
    for ak in attribute_keywords:
        if ak in clean_q and ak in clean_text:
            score += 15.0

    # 4. Heading Relevance Boost
    if chunk.heading:
        h_lower = chunk.heading.lower()
        if any(w in h_lower for w in q_words if len(w) > 3):
            score += 25.0

    # 5. Structured Table Boost
    if chunk.contains_table:
        table_interest = any(k in clean_q for k in [
            "spec", "score", "price", "winner", "result", "comparison", "list",
            "clock", "speed", "core", "cores", "vram", "tdp", "memory", "bus",
            "display", "refresh", "rate", "battery", "storage", "hardware"
        ])
        if table_interest or (q_words and matches > 0):
            score += 20.0

    # 6. Source Authority
    if any(auth in chunk.url.lower() for auth in AUTHORITATIVE_DOMAINS):
        score += 15.0

    return round(score, 2)


def select_top_evidence_chunks(
    query: str,
    docs: List[ExtractedDocument],
    max_chunks: int = 4,
    max_total_chars: int = 4500
) -> List[EvidenceChunk]:
    """
    Chunks all retrieved documents, ranks chunks by multi-signal score,
    deduplicates overlapping text, and fits top chunks into the context budget.
    """
    all_chunks: List[EvidenceChunk] = []

    for doc in docs:
        doc_chunks = chunk_document(doc)
        for c in doc_chunks:
            c.relevance_score = score_chunk(query, c)
            all_chunks.append(c)

    if not all_chunks:
        return []

    # Sort chunks descending by relevance score
    all_chunks.sort(key=lambda x: x.relevance_score, reverse=True)

    # Deduplication and budget packing
    selected: List[EvidenceChunk] = []
    seen_snippets: List[Set[str]] = []
    total_chars = 0

    for chunk in all_chunks:
        if chunk.relevance_score <= 5.0 and len(selected) >= 2:
            # Don't pack low-relevance filler if we already have 2 solid chunks
            continue

        # Check lexical similarity against already selected chunks (>70% overlap = duplicate)
        chunk_words = set(re.findall(r"\b[a-z]{4,}\b", chunk.text.lower())[:50])
        is_dup = False
        for s in seen_snippets:
            if chunk_words and s:
                intersect = len(chunk_words.intersection(s))
                if (intersect / max(len(chunk_words), 1)) > 0.70:
                    is_dup = True
                    break

        if is_dup:
            continue

        # Check character budget
        if total_chars + len(chunk.text) > max_total_chars and selected:
            continue

        selected.append(chunk)
        seen_snippets.append(chunk_words)
        total_chars += len(chunk.text)

        if len(selected) >= max_chunks:
            break

    # If no chunk cleared high threshold, take top 2 by score
    if not selected:
        selected = all_chunks[:min(2, len(all_chunks))]

    # Sort selected chunks logically: by source_index, then by start_char in that document
    selected.sort(key=lambda c: (c.source_index, c.start_char))
    return selected
