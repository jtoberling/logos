"""
LLM client abstraction for Logos.

Provides unified interface for different LLM providers including
OpenAI, Anthropic, Ollama, LMStudio, and Gemini.
"""

import os
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    # Mock for testing
    class httpx:
        class Client:
            pass
        @staticmethod
        def post(*args, **kwargs):
            raise ImportError("httpx not available")


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, model: str = "gpt-3.5-turbo", **kwargs):
        self.model = model

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate response from LLM."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client."""

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None, **kwargs):
        super().__init__(model, **kwargs)
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    """Anthropic Claude API client."""

    def __init__(self, model: str = "claude-3-sonnet-20240229", api_key: Optional[str] = None, **kwargs):
        super().__init__(model, **kwargs)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text


class OllamaClient(LLMClient):
    """Ollama local LLM client."""

    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(model, **kwargs)
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx package not installed. Install with: pip install httpx")
        self.base_url = base_url.rstrip('/')

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        response = httpx.post(url, json=payload, timeout=60.0)
        response.raise_for_status()

        result = response.json()
        return result.get("response", "")


class LMStudioClient(LLMClient):
    """LMStudio local LLM client."""

    def __init__(self, model: str = "local-model", base_url: str = "http://localhost:1234/v1", **kwargs):
        super().__init__(model, **kwargs)
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx package not installed. Install with: pip install httpx")
        self.base_url = base_url.rstrip('/')
        self.api_key = "lm-studio"  # LMStudio uses a dummy API key

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        url = f"{self.base_url}/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = httpx.post(url, json=payload, headers=headers, timeout=60.0)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]


class GeminiClient(LLMClient):
    """Google Gemini API client."""

    def __init__(self, model: str = "gemini-pro", api_key: Optional[str] = None, **kwargs):
        super().__init__(model, **kwargs)
        try:
            import google.genai as genai
            self.client = genai.Client(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        except ImportError:
            raise ImportError("google.genai package not installed. Install with: pip install google.genai")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        # Combine system prompt with user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
            config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )

        return response.text


def create_llm_client(provider: str, model: str, **kwargs) -> LLMClient:
    """
    Factory function to create LLM client.

    Args:
        provider: LLM provider name ('openai', 'anthropic', 'ollama', 'lmstudio', 'gemini')
        model: Model name
        **kwargs: Additional arguments for the client

    Returns:
        LLMClient instance

    Raises:
        ValueError: If provider is unknown
    """
    providers = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "ollama": OllamaClient,
        "lmstudio": LMStudioClient,
        "gemini": GeminiClient,
    }

    if provider not in providers:
        available = ", ".join(providers.keys())
        raise ValueError(f"Unknown LLM provider: {provider}. Available: {available}")

    return providers[provider](model=model, **kwargs)