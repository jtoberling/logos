"""
Unit tests for LLM client abstraction.

Tests the unified interface for different LLM providers.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.llm.client import create_llm_client, LLMClient


class TestLLMClient:
    """Test LLM client abstraction."""

    def test_create_llm_client_openai(self):
        """Test creating OpenAI client."""
        with patch('src.llm.client.OpenAIClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            client = create_llm_client("openai", "gpt-4", api_key="test-key")

            mock_client.assert_called_once_with(
                model="gpt-4",
                api_key="test-key"
            )
            assert client == mock_instance

    def test_create_llm_client_anthropic(self):
        """Test creating Anthropic client."""
        with patch('src.llm.client.AnthropicClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            client = create_llm_client("anthropic", "claude-3", api_key="test-key")

            mock_client.assert_called_once_with(
                model="claude-3",
                api_key="test-key"
            )
            assert client == mock_instance

    def test_create_llm_client_ollama(self):
        """Test creating Ollama client."""
        with patch('src.llm.client.OllamaClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            client = create_llm_client("ollama", "llama2", base_url="http://test:11434")

            mock_client.assert_called_once_with(
                model="llama2",
                base_url="http://test:11434"
            )
            assert client == mock_instance

    def test_create_llm_client_lmstudio(self):
        """Test creating LMStudio client."""
        with patch('src.llm.client.LMStudioClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            client = create_llm_client("lmstudio", "local-model", base_url="http://test:1234")

            mock_client.assert_called_once_with(
                model="local-model",
                base_url="http://test:1234"
            )
            assert client == mock_instance

    def test_create_llm_client_gemini(self):
        """Test creating Gemini client."""
        with patch('src.llm.client.GeminiClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            client = create_llm_client("gemini", "gemini-pro", api_key="test-key")

            mock_client.assert_called_once_with(
                model="gemini-pro",
                api_key="test-key"
            )
            assert client == mock_instance

    def test_create_llm_client_unknown_provider(self):
        """Test error for unknown provider."""
        with pytest.raises(ValueError, match="Unknown LLM provider: unknown"):
            create_llm_client("unknown", "model")

    def test_openai_client_generate(self):
        """Test OpenAI client generate method."""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            mock_response = MagicMock()
            mock_response.choices[0].message.content = "Test response"
            mock_client.chat.completions.create.return_value = mock_response

            from src.llm.client import OpenAIClient
            client = OpenAIClient(model="gpt-4", api_key="test-key")

            response = client.generate("Test prompt", "Test system", temperature=0.8, max_tokens=100)

            assert response == "Test response"
            mock_client.chat.completions.create.assert_called_once()

    def test_anthropic_client_generate(self):
        """Test Anthropic client generate method."""
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client

            mock_response = MagicMock()
            mock_response.content[0].text = "Test response"
            mock_client.messages.create.return_value = mock_response

            from src.llm.client import AnthropicClient
            client = AnthropicClient(model="claude-3", api_key="test-key")

            response = client.generate("Test prompt", "Test system", temperature=0.8, max_tokens=100)

            assert response == "Test response"
            mock_client.messages.create.assert_called_once()

    def test_ollama_client_generate(self):
        """Test Ollama client generate method."""
        with patch('src.llm.client.httpx.post') as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"response": "Test response"}
            mock_post.return_value = mock_response

            from src.llm.client import OllamaClient
            client = OllamaClient(model="llama2", base_url="http://test:11434")

            response = client.generate("Test prompt", "Test system", temperature=0.8, max_tokens=100)

            assert response == "Test response"
            mock_post.assert_called_once()

    def test_lmstudio_client_generate(self):
        """Test LMStudio client generate method."""
        with patch('src.llm.client.httpx.post') as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}
            mock_post.return_value = mock_response

            from src.llm.client import LMStudioClient
            client = LMStudioClient(model="local-model", base_url="http://test:1234")

            response = client.generate("Test prompt", "Test system", temperature=0.8, max_tokens=100)

            assert response == "Test response"
            mock_post.assert_called_once()

    def test_gemini_client_generate(self):
        """Test Gemini client generate method."""
        with patch('google.genai.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.text = "Test response"
            mock_client.models.generate_content.return_value = mock_response

            from src.llm.client import GeminiClient
            client = GeminiClient(model="gemini-pro", api_key="test-key")

            response = client.generate("Test prompt", "Test system", temperature=0.8, max_tokens=100)

            assert response == "Test response"
            mock_client.models.generate_content.assert_called_once_with(
                model="gemini-pro",
                contents="Test system\n\nTest prompt",
                config={
                    "temperature": 0.8,
                    "max_output_tokens": 100
                }
            )

    def test_client_error_handling(self):
        """Test error handling in LLM clients."""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            from src.llm.client import OpenAIClient
            client = OpenAIClient(model="gpt-4", api_key="test-key")

            with pytest.raises(Exception, match="API Error"):
                client.generate("Test prompt")

    def test_ollama_error_handling(self):
        """Test error handling in Ollama client."""
        with patch('src.llm.client.httpx.post') as mock_post:
            mock_post.side_effect = Exception("Connection Error")

            from src.llm.client import OllamaClient
            client = OllamaClient(model="llama2")

            with pytest.raises(Exception, match="Connection Error"):
                client.generate("Test prompt")

    def test_default_parameters(self):
        """Test default parameter values."""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            mock_response = MagicMock()
            mock_response.choices[0].message.content = "Response"
            mock_client.chat.completions.create.return_value = mock_response

            from src.llm.client import OpenAIClient
            client = OpenAIClient(model="gpt-4")

            client.generate("Test prompt")

            # Check that defaults were used
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]["temperature"] == 0.7  # default
            assert call_args[1]["max_tokens"] == 1000   # default