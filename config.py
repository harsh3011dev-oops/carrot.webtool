"""
PROJECT NOVA - Global Configuration
Central configuration management using Pydantic Settings.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base Directories
    BASE_DIR: Path = Path(__file__).resolve().parent
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Local Model Runtime (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Asymmetric Model Selection:
    # 1. Fast SLM for Routing, Intent & Claim Extraction (Ultra-low latency on CPU)
    ROUTER_MODEL: str = "qwen2.5:1.5b"
    # 2. Reasoning SLM for Grounded Answer Synthesis & Citations
    SYNTHESIS_MODEL: str = "qwen2.5-coder:latest"
    # 3. Embedding Model for Local Vector Search
    EMBEDDING_MODEL: str = "nomic-embed-text"
    
    # Model Generation Parameters
    ROUTER_TEMPERATURE: float = 0.0      # Deterministic classification
    SYNTHESIS_TEMPERATURE: float = 0.2   # Strict factual adherence
    MAX_TOKENS_ROUTER: int = 512
    MAX_TOKENS_SYNTHESIS: int = 1024
    
    # Web Retrieval Settings
    MAX_SEARCH_RESULTS: int = 4
    SEARCH_TIMEOUT_SECONDS: int = 8
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    
    # Verification & Grounding Thresholds
    MIN_CITATION_CONFIDENCE: float = 0.65
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Global settings singleton
settings = Settings()

