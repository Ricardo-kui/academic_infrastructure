"""
EmbeddingClient — wraps OpenAI-compatible API for text embeddings.
Defaults to OpenRouter, but any compatible endpoint works.
"""

import os
from typing import Optional

import numpy as np
from openai import OpenAI


class EmbeddingClient:
    """Client for embedding texts via OpenAI-compatible API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small",
        batch_size: int = 32,
    ):
        self.base_url = base_url or os.getenv(
            "OPENAI_API_BASE", "https://openrouter.ai/api/v1"
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set OPENAI_API_KEY env var or pass api_key."
            )
        self.model = model
        self.batch_size = batch_size
        self._client: Optional[OpenAI] = None

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
        resp = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return np.array(resp.data[0].embedding, dtype=np.float32)

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        """Embed a batch of texts."""
        results = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            resp = self.client.embeddings.create(
                model=self.model,
                input=batch,
            )
            for d in resp.data:
                results.append(np.array(d.embedding, dtype=np.float32))
        return results
