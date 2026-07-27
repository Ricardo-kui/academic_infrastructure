"""
EmbeddingClient — wraps OpenAI-compatible API for text embeddings.
Defaults to Alibaba Cloud Bailian's Qwen3-Embedding endpoint, but any
compatible endpoint works.
"""

import os
from typing import Optional

import numpy as np
from openai import OpenAI


def _usable_key(value: Optional[str]) -> Optional[str]:
    """Return a configured API key, ignoring common placeholder values."""
    if not value:
        return None
    value = value.strip()
    if not value or "..." in value or value.lower() in {"sk", "sk-", "your_api_key"}:
        return None
    return value


class EmbeddingClient:
    """Client for embedding texts via OpenAI-compatible API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        batch_size: Optional[int] = None,
        dimensions: Optional[int] = None,
    ):
        self.base_url = base_url or os.getenv(
            "OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.api_key = (
            _usable_key(api_key)
            or _usable_key(os.getenv("OPENAI_API_KEY"))
            or _usable_key(os.getenv("DASHSCOPE_API_KEY"))
        )
        if not self.api_key:
            raise ValueError(
                "API key required. Set OPENAI_API_KEY or DASHSCOPE_API_KEY env var, or pass api_key."
            )
        self.model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-v4")
        self.batch_size = batch_size or int(os.getenv("EMBEDDING_BATCH_SIZE", "10"))
        env_dimensions = os.getenv("EMBEDDING_DIMENSIONS")
        self.dimensions = dimensions or (int(env_dimensions) if env_dimensions else None)
        self._client: Optional[OpenAI] = None

    def _embedding_kwargs(self, input_text):
        kwargs = {
            "model": self.model,
            "input": input_text,
        }
        if self.dimensions is not None:
            kwargs["dimensions"] = self.dimensions
        return kwargs

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
        return self._client

    def embed(self, text: str) -> np.ndarray:
        """Embed a single text."""
        resp = self.client.embeddings.create(**self._embedding_kwargs(text))
        return np.array(resp.data[0].embedding, dtype=np.float32)

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        """Embed a batch of texts."""
        results = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            resp = self.client.embeddings.create(**self._embedding_kwargs(batch))
            for d in resp.data:
                results.append(np.array(d.embedding, dtype=np.float32))
        return results
