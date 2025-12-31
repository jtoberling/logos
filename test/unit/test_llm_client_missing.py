"""
Additional unit tests for LLM client missing coverage.

Tests ImportError paths when packages are not available.
"""

import pytest
from unittest.mock import patch

from src.llm.client import (
    OpenAIClient, AnthropicClient, OllamaClient, LMStudioClient, GeminiClient,
    HTTPX_AVAILABLE
)


class TestLLMClientImportErrors:
    """Test ImportError handling in LLM clients."""

    def test_openai_client_import_error(self):
        """Test OpenAI client when openai package is not available."""
        with patch.dict('sys.modules', {'openai': None}):
            with pytest.raises(ImportError, match="openai package not installed"):
                OpenAIClient(api_key="test")

    def test_anthropic_client_import_error(self):
        """Test Anthropic client when anthropic package is not available."""
        with patch.dict('sys.modules', {'anthropic': None}):
            with pytest.raises(ImportError, match="anthropic package not installed"):
                AnthropicClient(api_key="test")

    def test_ollama_client_httpx_not_available(self):
        """Test Ollama client when httpx is not available."""
        with patch('src.llm.client.HTTPX_AVAILABLE', False):
            with pytest.raises(ImportError, match="httpx package not installed"):
                OllamaClient()

    def test_lmstudio_client_httpx_not_available(self):
        """Test LMStudio client when httpx is not available."""
        with patch('src.llm.client.HTTPX_AVAILABLE', False):
            with pytest.raises(ImportError, match="httpx package not installed"):
                LMStudioClient()

    def test_gemini_client_import_error(self):
        """Test Gemini client when google.genai package is not available."""
        with patch.dict('sys.modules', {'google.genai': None}):
            with pytest.raises(ImportError, match="google.genai package not installed"):
                GeminiClient(api_key="test")
