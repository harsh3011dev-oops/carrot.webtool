"""
PROJECT NOVA - Ollama Model Adapter
===================================
Concrete implementation of BaseLLMAdapter backed by local Ollama runtime.
Runs models like Qwen 2.5 (1.5B/3B) and Nomic-Embed locally on CPU/GPU.
"""

import json
import logging
import re
from typing import Generator, List, Optional, Type, TypeVar
import ollama
from pydantic import BaseModel, ValidationError

from config import settings
from core.base_model import BaseLLMAdapter

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger("nova.ollama")


class OllamaAdapter(BaseLLMAdapter):
    """
    Ollama-backed driver for Project NOVA.
    Supports generation, strict Pydantic JSON extraction, streaming, and embeddings.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model_name = model_name or settings.SYNTHESIS_MODEL
        self.embedding_model = embedding_model or settings.EMBEDDING_MODEL
        self.client = ollama.Client(host=self.base_url)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate plain text response using Ollama.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            options={
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        )
        return response["message"]["content"]

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
    ) -> T:
        """
        Generate structured output validated against a Pydantic schema.
        Includes automatic markdown-stripping and schema constraint injection.
        """
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)

        schema_instruction = (
            f"\n\nCRITICAL INSTRUCTION: You must respond ONLY with a valid JSON object matching this schema:\n"
            f"```json\n{schema_json}\n```\n"
            f"Do not include any intro, outro, markdown ticks or explanations outside the JSON."
        )

        full_system = (system_prompt or "") + schema_instruction
        messages = [
            {"role": "system", "content": full_system},
            {"role": "user", "content": prompt},
        ]

        # Use Ollama's native JSON mode
        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            format="json",
            options={
                "temperature": temperature,
                "num_predict": settings.MAX_TOKENS_ROUTER,
            },
        )

        raw_content = response["message"]["content"].strip()

        # Clean any accidental markdown codeblock wrappers and trailing commas
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_content)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)

        try:
            # Parse dict first so Pydantic model_validator(mode='before') can normalize fields
            parsed_dict = json.loads(cleaned)
            return response_model.model_validate(parsed_dict)
        except Exception as e:
            logger.warning(f"First JSON validation attempt failed: {e}. Raw content: {raw_content[:200]}")
            # Max 1 repair retry with explicit validation hint
            repair_prompt = (
                f"The following JSON was invalid or failed validation ({str(e)[:150]}):\n{cleaned}\n\n"
                f"Correct the values and return ONLY valid JSON matching this schema:\n{schema_json}"
            )
            try:
                retry_res = self.client.chat(
                    model=self.model_name,
                    messages=[{"role": "user", "content": repair_prompt}],
                    format="json",
                    options={"temperature": 0.0},
                )
                retry_content = retry_res["message"]["content"].strip()
                retry_cleaned = re.sub(r"^```(?:json)?\s*", "", retry_content)
                retry_cleaned = re.sub(r"\s*```$", "", retry_cleaned).strip()
                m2 = re.search(r"(\{.*\})", retry_cleaned, re.DOTALL)
                if m2:
                    retry_cleaned = m2.group(1).strip()
                retry_cleaned = re.sub(r",\s*([\]}])", r"\1", retry_cleaned)
                parsed_retry = json.loads(retry_cleaned)
                return response_model.model_validate(parsed_retry)
            except Exception as repair_err:
                logger.error(f"Structured repair pass also failed: {repair_err}. Raising to router fallback.")
                raise

    def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """
        Stream output tokens for real-time frontend display.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat(
            model=self.model_name,
            messages=messages,
            stream=True,
            options={
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        )

        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate dense vector embeddings using local Nomic-Embed model.
        """
        embeddings: List[List[float]] = []

        # Attempt batch embedding API if available
        try:
            if hasattr(self.client, "embed"):
                res = self.client.embed(model=self.embedding_model, input=texts)
                return res.get("embeddings", [])
        except Exception:
            pass

        # Fallback to sequential embeddings
        for text in texts:
            res = self.client.embeddings(model=self.embedding_model, prompt=text)
            embeddings.append(res["embedding"])

        return embeddings

