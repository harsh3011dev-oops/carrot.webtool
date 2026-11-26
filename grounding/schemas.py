"""
PROJECT NOVA - Grounding & Truth Engine Schemas (Sprint 3)
==========================================================
Data contracts for response states, claim verification, and citation audits.
"""

from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

from retriever.models import ExtractedDocument


class ResponseState(str, Enum):
    """
    Canonical 4-state response truth framework.
    Every answer in NOVA must have exactly one machine-readable state.
    """
    VERIFIED = "VERIFIED"        # 100% of factual statements are corroborated by retrieved evidence
    PARTIAL = "PARTIAL"          # Core claims verified, but some secondary details are uncertain/unsupported
    UNVERIFIED = "UNVERIFIED"    # Answer generated from internal parametric knowledge (no verified search)
    ABSTAIN = "ABSTAIN"          # Retrieval was insufficient, system explicitly refuses to guess


class StructuredNumericalClaim(BaseModel):
    """
    Structured representation of a numerical claim (Sprint 5.3).
    Binds numbers strictly to entity, variant/trim, attribute domain, and units.
    """
    entity: Optional[str] = Field(default=None, description="Subject entity name")
    variant: Optional[str] = Field(default=None, description="Variant or trim qualifier (e.g. RWD, Long Range AWD, Pro Max)")
    attribute: Optional[str] = Field(default=None, description="Attribute domain (e.g. range, price, height, score)")
    raw_value: Optional[str] = Field(default=None, description="Raw extracted numerical string")
    numeric_value: Optional[float] = Field(default=None, description="Parsed floating point value")
    unit: Optional[str] = Field(default=None, description="Physical unit or dimension")
    currency: Optional[str] = Field(default=None, description="Currency ISO or symbol")
    event: Optional[str] = Field(default=None, description="Event or tournament qualifier")
    year: Optional[str] = Field(default=None, description="Associated calendar year")
    is_comparison: bool = Field(default=False, description="Whether claim represents a difference or comparative relation")
    comparison_target: Optional[str] = Field(default=None, description="Target entity or baseline of comparison")


class ClaimVerification(BaseModel):
    """Factual claim extracted from generated answer and checked against evidence."""
    claim_text: str = Field(description="The atomic factual proposition")
    is_supported: bool = Field(description="Whether retrieved evidence corroborates this claim")
    supporting_source_indices: List[int] = Field(default_factory=list, description="List of source indices e.g. [1, 2]")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Support confidence score")
    reasoning: str = Field(default="", description="Why claim was accepted or flagged")
    entity: Optional[str] = Field(default=None, description="Extracted entity name")
    attribute: Optional[str] = Field(default=None, description="Extracted attribute or property")
    numerical_values: List[str] = Field(default_factory=list, description="Extracted numbers/dates")
    contradiction_detected: bool = Field(default=False, description="Whether direct contradiction was found")
    supporting_passage: Optional[str] = Field(default=None, description="Exact local passage corroborating the claim")
    char_span: Optional[Tuple[int, int]] = Field(default=None, description="(start_idx, end_idx) in response text")
    structured_numerical: Optional[StructuredNumericalClaim] = Field(default=None, description="Structured numerical claim details")


class VerifiedResponse(BaseModel):
    """
    Final output contract produced by the Truth Engine.
    """
    final_text: str = Field(description="The final cleaned, verified, and cited response text")
    response_state: ResponseState = Field(description="The canonical truth state: VERIFIED, PARTIAL, UNVERIFIED, ABSTAIN")
    claims: List[ClaimVerification] = Field(default_factory=list, description="List of atomic claims verified")
    unsupported_claims_count: int = Field(default=0, description="Count of unsupported claims flagged or pruned")
    verified_sources: List[ExtractedDocument] = Field(default_factory=list, description="Verified sources cited")
    citation_support_rate: float = Field(default=1.0, description="Percentage of bracketed citations that are valid")
    claim_support_rate: float = Field(default=1.0, description="Percentage of atomic claims corroborated by evidence")
    citation_precision: float = Field(default=1.0, description="Percentage of bracketed citations that accurately corroborate cited claim")
    citation_coverage: float = Field(default=1.0, description="Percentage of supported claims that have valid bracketed citations")
    source_availability: float = Field(default=1.0, description="Percentage of sources successfully retrieved and parsed")

