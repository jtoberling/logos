"""
LLM client for Logos CLI.

Wrapper around the core LLM client abstraction to provide CLI-specific functionality.
"""

from typing import Optional, Dict, Any

# Import from core LLM client
try:
    from src.llm.client import create_llm_client as core_create_llm_client, LLMClient
except ImportError:
    # Fallback for when running from CLI directory
    import sys
    import os
    # Add the parent directory to path to find src
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    try:
        from src.llm.client import create_llm_client as core_create_llm_client, LLMClient
    except ImportError:
        # If still not found, create a mock for development
        class MockLLMClient:
            def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=1000):
                return f"Mock response to: {prompt[:50]}..."

        class MockLLMClientType:
            def __init__(self, **kwargs):
                pass
            def generate(self, *args, **kwargs):
                return "Mock LLM response - install dependencies for real functionality"

        def core_create_llm_client(provider, model, **kwargs):
            return MockLLMClientType(**kwargs)

        LLMClient = MockLLMClient


def create_llm_client(provider: str, model: str, **kwargs) -> LLMClient:
    """
    Create LLM client using the core abstraction.

    This is a wrapper around the core create_llm_client function
    to provide CLI-specific functionality and error handling.
    """
    try:
        return core_create_llm_client(provider, model, **kwargs)
    except ImportError as e:
        raise ImportError(f"LLM provider '{provider}' not available: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to create {provider} client: {e}")


def get_available_providers() -> list[str]:
    """
    Get list of available LLM providers.

    Returns:
        List of supported provider names
    """
    return ["openai", "anthropic", "ollama", "lmstudio", "gemini"]


def validate_provider(provider: str) -> bool:
    """
    Validate that a provider is supported.

    Args:
        provider: Provider name to validate

    Returns:
        True if provider is supported
    """
    return provider in get_available_providers()