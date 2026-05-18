#!/usr/bin/env python3
"""
llm_client.py — Generic OpenAI-compatible LLM client for Agentic Observer/Reflector.

Supports any OpenAI-compatible API: DeepSeek, Kimi, OpenRouter, SiliconFlow, etc.
Configure via .env: LLM_API_KEY, LLM_BASE_URL, LLM_MODEL.

Usage:
    from llm_client import LLMClient
    client = LLMClient()
    response = client.chat_completion(messages=[...])
"""

import json
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore

INFRA_DIR = Path("C:/Users/admin/.claude/academic_infrastructure")

# Provider presets
PROVIDERS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "input_price": 2.0,      # CNY per 1M tokens
        "output_price": 8.0,     # CNY per 1M tokens
        "currency": "CNY",
    },
    "kimi": {
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-128k",
        "input_price": 4.2,      # ~$0.60 USD
        "output_price": 17.5,    # ~$2.50 USD
        "currency": "CNY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-4o-mini",
        "input_price": 0.15,
        "output_price": 0.60,
        "currency": "USD",
    },
}

DEFAULT_PROVIDER = "deepseek"


@dataclass(frozen=True)
class LLMResponse:
    content: str
    usage_prompt: int
    usage_completion: int
    model: str


def _load_env() -> None:
    for env_path in [
        INFRA_DIR / "tools" / "semantic_search" / ".env",
        INFRA_DIR / ".env",
    ]:
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
            break


class LLMClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        provider: str | None = None,
    ):
        _load_env()

        # Detect provider from env or argument
        self.provider_name = provider or os.environ.get("LLM_PROVIDER", DEFAULT_PROVIDER)
        preset = PROVIDERS.get(self.provider_name, {})

        self.api_key = api_key or os.environ.get("LLM_API_KEY") or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("KIMI_API_KEY")
        self.base_url = base_url or os.environ.get("LLM_BASE_URL") or preset.get("base_url", "")
        self.model = model or os.environ.get("LLM_MODEL") or preset.get("model", "")
        self.pricing = {
            "input": preset.get("input_price", 0),
            "output": preset.get("output_price", 0),
            "currency": preset.get("currency", "CNY"),
        }

        if not self.api_key:
            raise RuntimeError(
                f"API key not found. Set LLM_API_KEY (or DEEPSEEK_API_KEY / KIMI_API_KEY) in .env"
            )
        if not self.base_url:
            raise RuntimeError(f"Base URL not found for provider '{self.provider_name}'")
        if not self.model:
            raise RuntimeError(f"Model not found for provider '{self.provider_name}'")

        if OpenAI is not None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self._client = None

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int | None = None,
        stream: bool = False,
    ) -> LLMResponse | Iterator[str]:
        use_model = model or self.model

        if self._client is not None:
            response = self._client.chat.completions.create(
                model=use_model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )
            if stream:
                return (chunk.choices[0].delta.content or "" for chunk in response if chunk.choices)
            return LLMResponse(
                content=response.choices[0].message.content or "",
                usage_prompt=response.usage.prompt_tokens if response.usage else 0,
                usage_completion=response.usage.completion_tokens if response.usage else 0,
                model=use_model,
            )
        else:
            return self._raw_http_chat(messages, use_model, temperature, max_tokens, stream)

    def _raw_http_chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int | None,
        stream: bool,
    ) -> LLMResponse:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        choice = data["choices"][0]
        content = choice["message"]["content"]
        usage = data.get("usage", {})
        return LLMResponse(
            content=content,
            usage_prompt=usage.get("prompt_tokens", 0),
            usage_completion=usage.get("completion_tokens", 0),
            model=model,
        )

    def estimate_cost(self, response: LLMResponse) -> tuple[float, str]:
        input_cost = response.usage_prompt / 1_000_000 * self.pricing["input"]
        output_cost = response.usage_completion / 1_000_000 * self.pricing["output"]
        return input_cost + output_cost, self.pricing["currency"]


def main() -> int:
    client = LLMClient()
    cost_str, currency = client.estimate_cost(LLMResponse("", 100000, 20000, ""))
    print(f"[*] LLM client initialized")
    print(f"    Provider: {client.provider_name}")
    print(f"    Model: {client.model}")
    print(f"    Base URL: {client.base_url}")
    print(f"    Pricing: input ¥{client.pricing['input']}/M, output ¥{client.pricing['output']}/M")
    print(f"    Example cost (100K in + 20K out): {cost_str:.4f} {currency}")

    try:
        resp = client.chat_completion(
            messages=[
                {"role": "system", "content": "你是一个学术研究助手。"},
                {"role": "user", "content": "请回复一句话确认API连接正常。"},
            ],
            temperature=0.0,
        )
        if isinstance(resp, LLMResponse):
            print(f"[*] OK: {resp.content}")
            print(f"[*] Usage: prompt={resp.usage_prompt}, completion={resp.usage_completion}")
            cost, curr = client.estimate_cost(resp)
            print(f"[*] Est. cost: {cost:.6f} {curr}")
    except Exception as e:
        print(f"[!] Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
