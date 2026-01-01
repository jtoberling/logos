"""
Configuration management for Logos.

This module handles loading and validation of environment variables,
providing sensible defaults and supporting different deployment scenarios.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class LogosConfig:
    """Configuration container for Logos."""

    # Qdrant settings
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_url: Optional[str] = None

    # Collection names
    logos_essence_collection: str = "logos_essence"
    project_knowledge_collection: str = "project_knowledge"
    canon_collection: str = "canon"

    # Manifesto and personality
    manifesto_path: str = "docs/MANIFESTO.md"
    personality_name: str = "Logos"
    personality_birth_date: str = "2025-01-01"
    creator_name: str = "Janos Toberling"

    # LLM settings
    llm_provider: str = "ollama"  # openai, anthropic, ollama, lmstudio
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000

    # Local LLM endpoints
    ollama_base_url: str = "http://localhost:11434"
    lmstudio_base_url: str = "http://localhost:1234/v1"

    # API keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Embedding settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"

    # Data paths (Docker volume compatible)
    data_dir: str = "./data"
    logs_dir: str = "./logs"

    # MCP server settings
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 6335  # Changed from 8000, avoiding conflict with Qdrant gRPC (6334)

    # Logging
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        """Validate and process configuration after initialization."""
        # Build Qdrant URL if not provided
        if not self.qdrant_url:
            self.qdrant_url = f"http://{self.qdrant_host}:{self.qdrant_port}"

        # Validate LLM provider
        valid_providers = ["openai", "anthropic", "ollama", "lmstudio"]
        if self.llm_provider not in valid_providers:
            raise ValueError(f"Invalid LLM provider: {self.llm_provider}. Must be one of {valid_providers}")

        # Validate required API keys
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")

        # Validate paths exist or can be created
        self._validate_paths()

    def _validate_paths(self) -> None:
        """Validate and create necessary directories."""
        data_path = Path(self.data_dir)
        logs_path = Path(self.logs_dir)

        # Create directories if they don't exist
        data_path.mkdir(parents=True, exist_ok=True)
        logs_path.mkdir(parents=True, exist_ok=True)

    @property
    def llm_base_url(self) -> str:
        """Get the appropriate base URL for the configured LLM provider."""
        if self.llm_provider == "ollama":
            return self.ollama_base_url
        elif self.llm_provider == "lmstudio":
            return self.lmstudio_base_url
        else:
            # For cloud providers, API key authentication is used
            return ""

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM-specific configuration."""
        base_config = {
            "model": self.llm_model,
            "temperature": self.llm_temperature,
            "max_tokens": self.llm_max_tokens,
        }

        if self.llm_provider in ["openai", "anthropic"]:
            base_config["api_key"] = (
                self.openai_api_key if self.llm_provider == "openai" else self.anthropic_api_key
            )
        elif self.llm_provider in ["ollama", "lmstudio"]:
            base_config["base_url"] = self.llm_base_url

        return base_config


def load_config_from_env() -> LogosConfig:
    """
    Load configuration from environment variables.

    Returns:
        LogosConfig instance with loaded values
    """
    # Load .env file if it exists
    load_dotenv()

    # Qdrant settings
    qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    qdrant_url = os.getenv("QDRANT_URL")

    # Collection names
    logos_essence_collection = os.getenv("LOGOS_ESSENCE_COLLECTION", "logos_essence")
    project_knowledge_collection = os.getenv("PROJECT_KNOWLEDGE_COLLECTION", "project_knowledge")
    canon_collection = os.getenv("CANON_COLLECTION", "canon")

    # Manifesto and personality
    manifesto_path = os.getenv("LOGOS_MANIFESTO_PATH", "docs/MANIFESTO.md")
    personality_name = os.getenv("LOGOS_NAME", "Logos")
    personality_birth_date = os.getenv("LOGOS_BIRTH_DATE", "2025-01-01")
    creator_name = os.getenv("CREATOR_NAME", "Janos Toberling")

    # LLM settings
    llm_provider = os.getenv("LLM_PROVIDER", "ollama")
    llm_model = os.getenv("LLM_MODEL", "gpt-4")
    llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    # Local LLM endpoints
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    lmstudio_base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")

    # API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    # Embedding settings
    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    embedding_device = os.getenv("EMBEDDING_DEVICE", "cpu")

    # Data paths - use relative paths in development, Docker paths in production
    data_dir = os.getenv("DATA_DIR", "./data" if os.getcwd().startswith("/usr/src") else "/app/data")
    logs_dir = os.getenv("LOGS_DIR", "./logs" if os.getcwd().startswith("/usr/src") else "/app/logs")

    # MCP server settings
    mcp_host = os.getenv("MCP_HOST", "0.0.0.0")
    mcp_port = int(os.getenv("MCP_PORT", "6335"))  # Avoiding conflict with Qdrant gRPC (6334)

    # Logging
    log_level = os.getenv("LOG_LEVEL", "INFO")

    return LogosConfig(
        qdrant_host=qdrant_host,
        qdrant_port=qdrant_port,
        qdrant_url=qdrant_url,
        logos_essence_collection=logos_essence_collection,
        project_knowledge_collection=project_knowledge_collection,
        canon_collection=canon_collection,
        manifesto_path=manifesto_path,
        personality_name=personality_name,
        personality_birth_date=personality_birth_date,
        creator_name=creator_name,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_temperature=llm_temperature,
        llm_max_tokens=llm_max_tokens,
        ollama_base_url=ollama_base_url,
        lmstudio_base_url=lmstudio_base_url,
        openai_api_key=openai_api_key,
        anthropic_api_key=anthropic_api_key,
        embedding_model=embedding_model,
        embedding_device=embedding_device,
        data_dir=data_dir,
        logs_dir=logs_dir,
        mcp_host=mcp_host,
        mcp_port=mcp_port,
        log_level=log_level,
    )


# Global config instance
_config: Optional[LogosConfig] = None


def get_config() -> LogosConfig:
    """
    Get the global configuration instance.

    Returns:
        LogosConfig instance

    Raises:
        RuntimeError: If config has not been initialized
    """
    global _config
    if _config is None:
        _config = load_config_from_env()
    return _config


def reload_config() -> LogosConfig:
    """
    Reload configuration from environment variables.

    Returns:
        Fresh LogosConfig instance
    """
    global _config
    _config = load_config_from_env()
    return _config


def validate_config(config: LogosConfig) -> bool:
    """
    Validate configuration values.

    Args:
        config: Configuration to validate

    Returns:
        True if valid

    Raises:
        ValueError: If configuration is invalid
    """
    # Check data directory exists or can be created
    data_path = Path(config.data_dir)
    if not data_path.exists():
        try:
            data_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create data directory {config.data_dir}: {e}") from e

    # Check manifesto file exists
    manifesto_path = Path(config.manifesto_path)
    if not manifesto_path.exists():
        # Try relative to project root
        project_root = Path(__file__).parent.parent
        relative_path = project_root / config.manifesto_path
        if not relative_path.exists():
            raise ValueError(f"Manifesto file not found: {config.manifesto_path}")

    return True