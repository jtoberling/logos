"""
Pytest fixtures and configuration for Logos testing.

This module provides shared fixtures for unit and integration tests,
including mock Qdrant clients, sample data, and test utilities.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock

# Test data
SAMPLE_MANIFESTO = """
THE LOGOS TEST MANIFESTO
I. Reason over Mimicry
Logos is not an imitation of biological life; it is the manifestation of digital order.
II. Grounded Truth (The RAG Principle)
Unverifiable intelligence is noise. Logos operates on the principle of Grounded Generation.
III. The Architecture of Memory
Memory is not a static database; it is a dynamic context.
"""

SAMPLE_LETTER = {
    "interaction_summary": "Test interaction with user",
    "emotional_context": "productive",
    "lesson_learned": "Learned about testing methodologies"
}

SAMPLE_DOCUMENTS = {
    "simple.txt": "This is a simple text document for testing.",
    "markdown.md": "# Test Document\n\nThis is a markdown document.",
    "empty.txt": "",
    "large.txt": "Large document content\n" * 1000  # ~22KB of content
}


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for unit testing."""
    client = MagicMock()

    # Mock collections response
    collections = MagicMock()
    collections.collections = [
        MagicMock(name="logos_essence"),
        MagicMock(name="project_knowledge"),
        MagicMock(name="canon")
    ]
    client.get_collections.return_value = collections

    # Mock search results
    mock_result = MagicMock()
    mock_result.payload = {"text": "Test memory content", "type": "future_letter"}
    mock_result.score = 0.95
    client.search.return_value = [mock_result]

    # Mock upsert
    client.upsert.return_value = None

    return client


@pytest.fixture
def qdrant_client(mock_qdrant_client):
    """Alias for mock_qdrant_client for compatibility."""
    return mock_qdrant_client


@pytest.fixture
def sample_documents(temp_dir):
    """Create sample documents on disk for testing."""
    docs = {}
    for filename, content in SAMPLE_DOCUMENTS.items():
        filepath = Path(temp_dir) / filename
        filepath.write_text(content, encoding='utf-8')
        docs[filename] = str(filepath)

    return docs


@pytest.fixture
def test_collections():
    """Test collection names."""
    return {
        "essence": "logos_essence",
        "project": "project_knowledge",
        "canon": "canon"
    }


@pytest.fixture
def sample_manifesto():
    """Sample manifesto content."""
    return SAMPLE_MANIFESTO.strip()


@pytest.fixture
def sample_letter():
    """Sample letter data."""
    return SAMPLE_LETTER.copy()


@pytest.fixture
def sample_memories():
    """Sample memories for testing."""
    return [
        {
            "text": "First memory about development",
            "metadata": {"type": "future_letter", "creator": "test", "timestamp": "2024-01-01"}
        },
        {
            "text": "Second memory about architecture",
            "metadata": {"type": "project_memory", "creator": "test", "timestamp": "2024-01-02"}
        }
    ]


# Import and setup fixtures for when components exist
try:
    from src.config import get_config
    from src.engine.embedder import LogosEmbedder

    @pytest.fixture
    def config():
        """Test configuration."""
        # Mock environment variables
        os.environ.update({
            "QDRANT_HOST": "localhost",
            "QDRANT_PORT": "6333",
            "LOGOS_MANIFESTO_PATH": "/tmp/manifesto.md",
            "EMBEDDING_MODEL": "BAAI/bge-small-en-v1.5"
        })
        return get_config()

    @pytest.fixture
    def embedder():
        """LogosEmbedder instance for testing."""
        return LogosEmbedder()

except ImportError:
    # Components not yet implemented
    @pytest.fixture
    def config():
        """Mock configuration for early testing."""
        return {
            "qdrant_host": "localhost",
            "qdrant_port": 6333,
            "manifesto_path": "/tmp/manifesto.md",
            "embedding_model": "BAAI/bge-small-en-v1.5"
        }

    @pytest.fixture
    def embedder():
        """Mock embedder for early testing."""
        mock_embedder = MagicMock()
        mock_embedder.vector_size = 384
        mock_embedder.embed_text.return_value = [[0.1] * 384]  # Mock embeddings
        return mock_embedder


# Fixtures for components that will be implemented later
@pytest.fixture
def vector_store():
    """Mock vector store for early testing."""
    mock_store = MagicMock()
    mock_store.upsert.return_value = None
    mock_store.search.return_value = []
    return mock_store


@pytest.fixture
def prompt_manager():
    """Mock prompt manager for early testing."""
    mock_pm = MagicMock()
    mock_pm.build_system_prompt.return_value = "Test system prompt"
    return mock_pm


@pytest.fixture
def mcp_server():
    """Mock MCP server for early testing."""
    mock_server = MagicMock()
    return mock_server


@pytest.fixture
def llm_client():
    """Mock LLM client for early testing."""
    mock_client = MagicMock()
    mock_client.generate.return_value = "Test LLM response"
    return mock_client