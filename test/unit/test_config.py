"""
Unit tests for configuration system.
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from config import LogosConfig, load_config_from_env, get_config, validate_config


class TestLogosConfig:
    """Test LogosConfig dataclass functionality."""

    def test_default_config(self):
        """Test default configuration values."""
        config = LogosConfig()

        assert config.qdrant_host == "qdrant"
        assert config.qdrant_port == 6333
        assert config.llm_provider == "ollama"
        assert config.logos_essence_collection == "logos_essence"
        assert config.project_knowledge_collection == "project_knowledge"
        assert config.personality_name == "Logos"

    def test_config_validation_qdrant_url(self):
        """Test that Qdrant URL is built correctly."""
        config = LogosConfig(qdrant_host="localhost", qdrant_port=6334)
        assert config.qdrant_url == "http://localhost:6334"

    def test_config_validation_custom_url(self):
        """Test custom Qdrant URL is preserved."""
        custom_url = "https://qdrant.example.com:6333"
        config = LogosConfig(qdrant_url=custom_url)
        assert config.qdrant_url == custom_url

    def test_config_validation_invalid_provider(self):
        """Test invalid LLM provider raises error."""
        with pytest.raises(ValueError, match="Invalid LLM provider"):
            LogosConfig(llm_provider="invalid_provider")

    def test_config_validation_missing_api_key_openai(self):
        """Test missing OpenAI API key raises error."""
        with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
            LogosConfig(llm_provider="openai", openai_api_key=None)

    def test_config_validation_missing_api_key_anthropic(self):
        """Test missing Anthropic API key raises error."""
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
            LogosConfig(llm_provider="anthropic", anthropic_api_key=None)

    def test_llm_base_url_ollama(self):
        """Test Ollama base URL."""
        config = LogosConfig(llm_provider="ollama", ollama_base_url="http://custom:11434")
        assert config.llm_base_url == "http://custom:11434"

    def test_llm_base_url_lmstudio(self):
        """Test LMStudio base URL."""
        config = LogosConfig(llm_provider="lmstudio", lmstudio_base_url="http://custom:1234/v1")
        assert config.llm_base_url == "http://custom:1234/v1"

    def test_llm_base_url_cloud_providers(self):
        """Test cloud providers return empty base URL."""
        for provider in ["openai", "anthropic"]:
            api_key = "test-key"
            if provider == "openai":
                config = LogosConfig(llm_provider=provider, openai_api_key=api_key)
            else:
                config = LogosConfig(llm_provider=provider, anthropic_api_key=api_key)
            assert config.llm_base_url == ""

    def test_get_llm_config_openai(self):
        """Test LLM config for OpenAI."""
        config = LogosConfig(
            llm_provider="openai",
            llm_model="gpt-4",
            openai_api_key="test-key",
            llm_temperature=0.5
        )
        llm_config = config.get_llm_config()

        assert llm_config["model"] == "gpt-4"
        assert llm_config["api_key"] == "test-key"
        assert llm_config["temperature"] == 0.5

    def test_get_llm_config_ollama(self):
        """Test LLM config for Ollama."""
        config = LogosConfig(
            llm_provider="ollama",
            llm_model="llama2",
            ollama_base_url="http://localhost:11434"
        )
        llm_config = config.get_llm_config()

        assert llm_config["model"] == "llama2"
        assert llm_config["base_url"] == "http://localhost:11434"


class TestConfigLoading:
    """Test configuration loading from environment."""

    def test_load_config_defaults(self):
        """Test loading config with all defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_vars = {
                "DATA_DIR": tmpdir,
                "LOGS_DIR": tmpdir,
            }
            with patch.dict(os.environ, env_vars, clear=True):
                config = load_config_from_env()

                assert config.qdrant_host == "qdrant"
                assert config.llm_provider == "ollama"  # Default is now ollama
                assert config.data_dir == tmpdir

    def test_load_config_custom_env(self):
        """Test loading config with custom environment variables."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_data_dir = str(Path(tmpdir) / "custom_data")

            env_vars = {
                "QDRANT_HOST": "custom-qdrant",
                "QDRANT_PORT": "9999",
                "LLM_PROVIDER": "ollama",
                "LLM_MODEL": "llama2",
                "OLLAMA_BASE_URL": "http://custom:11434",
                "DATA_DIR": custom_data_dir,
                "LOGS_DIR": custom_data_dir,
            }

            with patch.dict(os.environ, env_vars, clear=True):
                config = load_config_from_env()

                assert config.qdrant_host == "custom-qdrant"
                assert config.qdrant_port == 9999
                assert config.llm_provider == "ollama"
                assert config.llm_model == "llama2"
                assert config.ollama_base_url == "http://custom:11434"
                assert config.data_dir == custom_data_dir

    def test_load_config_api_keys(self):
        """Test loading API keys from environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_vars = {
                "LLM_PROVIDER": "openai",
                "OPENAI_API_KEY": "openai-key",
                "ANTHROPIC_API_KEY": "anthropic-key",
                "DATA_DIR": tmpdir,
                "LOGS_DIR": tmpdir,
            }

            with patch.dict(os.environ, env_vars, clear=True):
                config = load_config_from_env()

                assert config.openai_api_key == "openai-key"
                assert config.anthropic_api_key == "anthropic-key"


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_config_valid(self):
        """Test validation of valid configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create temporary manifesto file
            manifesto_path = Path(tmpdir) / "MANIFESTO.md"
            manifesto_path.write_text("Test manifesto")

            config = LogosConfig(
                manifesto_path=str(manifesto_path),
                data_dir=tmpdir
            )

            assert validate_config(config) is True

    def test_validate_config_missing_manifesto(self):
        """Test validation fails with missing manifesto."""
        config = LogosConfig(manifesto_path="/nonexistent/manifesto.md")

        with pytest.raises(ValueError, match="Manifesto file not found"):
            validate_config(config)

    def test_validate_config_creates_data_dir(self):
        """Test validation creates data directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir) / "new_data_dir"

            # Directory shouldn't exist initially
            assert not data_dir.exists()

            # Creating config should create the directory
            config = LogosConfig(data_dir=str(data_dir))
            assert data_dir.exists()


class TestGlobalConfig:
    """Test global configuration management."""

    def test_get_config_initialization(self):
        """Test get_config initializes on first call."""
        # Clear any existing config
        import src.config
        src.config._config = None

        with tempfile.TemporaryDirectory() as tmpdir:
            # Set environment variables for the test
            env_vars = {
                "DATA_DIR": tmpdir,
                "LOGS_DIR": tmpdir,
                "LLM_PROVIDER": "ollama"
            }
            with patch.dict(os.environ, env_vars):
                config = get_config()

                assert isinstance(config, LogosConfig)
                assert config.data_dir == tmpdir
                assert config.llm_provider == "ollama"

    def test_get_config_caching(self):
        """Test get_config returns cached instance."""
        # Clear any existing config
        import src.config
        src.config._config = None

        with tempfile.TemporaryDirectory() as tmpdir:
            # Set environment variables for the test
            env_vars = {
                "DATA_DIR": tmpdir,
                "LOGS_DIR": tmpdir,
                "LLM_PROVIDER": "ollama"
            }
            with patch.dict(os.environ, env_vars):
                # First call
                config1 = get_config()
                # Second call should use cache
                config2 = get_config()

                assert config1 is config2  # Same instance returned
                assert isinstance(config1, LogosConfig)