"""
Test Model Adapter: Verifies that OllamaAdapter satisfies BaseLLMAdapter.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import BaseModel, Field
from config import settings
from models.ollama_adapter import OllamaAdapter


class SampleAnalysis(BaseModel):
    category: str = Field(description="Category of the question, e.g. 'science', 'math', 'news'")
    is_time_sensitive: bool = Field(description="Whether the question needs up-to-date real-time information")
    summary: str = Field(description="One-sentence summary of the user's intent")


def test_ollama_adapter():
    print(f"Testing OllamaAdapter with Router Model: {settings.ROUTER_MODEL}...")
    adapter = OllamaAdapter(model_name=settings.ROUTER_MODEL)

    # 1. Test Text Generation
    print("\n--- 1. Testing Text Generation ---")
    response = adapter.generate(
        prompt="Reply with the single word 'READY' and nothing else.",
        temperature=0.0,
        max_tokens=10,
    )
    print(f"Model output: {response.strip()}")
    assert len(response.strip()) > 0

    # 2. Test Structured Pydantic Output
    print("\n--- 2. Testing Structured JSON Extraction ---")
    query = "What is the latest stock price of Apple right now?"
    structured_result = adapter.generate_structured(
        prompt=f"Analyze this query: '{query}'",
        response_model=SampleAnalysis,
        system_prompt="You are a query analysis classifier.",
        temperature=0.0,
    )
    print(f"Category: {structured_result.category}")
    print(f"Time Sensitive: {structured_result.is_time_sensitive}")
    print(f"Summary: {structured_result.summary}")
    assert isinstance(structured_result, SampleAnalysis)
    assert structured_result.is_time_sensitive is True

    # 3. Test Embeddings
    print("\n--- 3. Testing Embedding Generation ---")
    vectors = adapter.get_embeddings(["Project NOVA is an intelligent hybrid AI system."])
    print(f"Vector count: {len(vectors)}, Dimensions: {len(vectors[0])}")
    assert len(vectors) == 1
    assert len(vectors[0]) > 0

    print("\n>>> ALL ADAPTER TESTS PASSED PERFECTLY! <<<")


if __name__ == "__main__":
    test_ollama_adapter()
