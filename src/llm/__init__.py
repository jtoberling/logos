"""
LLM client abstraction for Logos.

Provides unified interface for different LLM providers.
"""

from .client import create_llm_client, LLMClient

__all__ = ["create_llm_client", "LLMClient"]