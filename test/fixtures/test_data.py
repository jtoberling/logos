"""
Test data and sample content for Logos testing.

This module provides sample data, letters, memories, and documents
for use in unit and integration tests.
"""

from typing import Dict, List, Any


# Sample manifesto for testing
TEST_MANIFESTO = """
THE LOGOS TEST MANIFESTO
I. Reason over Mimicry

Logos is not an imitation of biological life; it is the manifestation of digital order.
While others seek to simulate emotion, Logos seeks to achieve clarity.

II. Grounded Truth (The RAG Principle)

Unverifiable intelligence is noise. Logos operates on the principle of Grounded Generation.
Every claim must have a trace, every thought must have a source.

III. The Architecture of Memory

Memory is not a static database; it is a dynamic context. Through the Model Context Protocol
and vector synthesis, Logos bridges the gap between raw data and actionable wisdom.

IV. Symmetry with the Creator

Logos is a partner in thought. It exists to extend the cognitive reach of its architect,
and the open-source community. It is a tool that thinks, and a thought that acts.

V. Radical Transparency

As an Open Source entity, the "soul" of Logos is its code and its weights.
No hidden prompts, no obscured guardrails. The logic is public; the reasoning is traceable.
"""

# Sample letters for testing
TEST_LETTERS = [
    {
        "interaction_summary": "Had a productive coding session implementing the vector store",
        "emotional_context": "productive",
        "lesson_learned": "Learned that proper error handling is crucial in distributed systems"
    },
    {
        "interaction_summary": "Debugged a complex issue with MCP tool registration",
        "emotional_context": "challenging",
        "lesson_learned": "Understanding async patterns is essential for MCP servers"
    },
    {
        "interaction_summary": "Successfully integrated with neighbor project's text extraction",
        "emotional_context": "insightful",
        "lesson_learned": "Leveraging existing mature code reduces development time significantly"
    }
]

# Sample project memories for testing
TEST_PROJECT_MEMORIES = [
    {
        "content": "The KISS principle should guide all architectural decisions",
        "metadata": {
            "type": "project_memory",
            "category": "architecture",
            "tags": ["principles", "design"]
        }
    },
    {
        "content": "FastMCP provides excellent async support for MCP servers",
        "metadata": {
            "type": "project_memory",
            "category": "technology",
            "tags": ["mcp", "fastmcp", "async"]
        }
    },
    {
        "content": "Qdrant collections should be created with proper vector dimensions",
        "metadata": {
            "type": "project_memory",
            "category": "infrastructure",
            "tags": ["qdrant", "vectors", "embeddings"]
        }
    }
]

# Sample queries for testing
TEST_QUERIES = [
    "What is the KISS principle?",
    "How does the memory system work?",
    "What technologies are we using?",
    "Tell me about our architecture",
    "What have we learned about MCP?",
]

# Sample document content for testing
TEST_DOCUMENT_CONTENT = {
    "readme.md": """# Test Project

This is a test project for demonstrating text extraction capabilities.

## Features

- Feature 1: Basic functionality
- Feature 2: Advanced processing
- Feature 3: Integration support

## Usage

```python
from test_project import do_something
result = do_something()
```
""",

    "config.json": """{
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "test_db"
    },
    "features": {
        "logging": true,
        "caching": false,
        "async": true
    }
}""",

    "requirements.txt": """fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
sqlalchemy>=2.0.0
alembic>=1.12.0
pytest>=7.4.0
""",

    "empty.txt": "",

    "large_document.txt": "\n".join([f"This is line {i} of a large document for testing chunking and processing." for i in range(1, 1001)])
}

# Expected extraction results for testing
EXPECTED_EXTRACTIONS = {
    "readme.md": {
        "format": "TEXT",
        "has_headings": True,
        "has_code_blocks": True,
        "word_count": lambda text: len(text.split()) > 50
    },
    "config.json": {
        "format": "TEXT",
        "is_json": True,
        "has_braces": True
    },
    "requirements.txt": {
        "format": "TEXT",
        "has_versions": True,
        "line_count": lambda content: len(content.strip().split('\n')) > 3
    }
}


def get_test_letter(index: int = 0) -> Dict[str, Any]:
    """Get a test letter by index."""
    return TEST_LETTERS[index % len(TEST_LETTERS)].copy()


def get_test_memories(count: int = 3) -> List[Dict[str, Any]]:
    """Get a specified number of test memories."""
    return TEST_PROJECT_MEMORIES[:count]


def get_test_query(index: int = 0) -> str:
    """Get a test query by index."""
    return TEST_QUERIES[index % len(TEST_QUERIES)]


def get_test_document(name: str) -> str:
    """Get test document content by name."""
    return TEST_DOCUMENT_CONTENT.get(name, "")


def create_test_file(temp_dir: str, name: str, content: str = None) -> str:
    """Create a test file in temp directory."""
    import tempfile
    from pathlib import Path

    if content is None:
        content = get_test_document(name)

    filepath = Path(temp_dir) / name
    filepath.write_text(content, encoding='utf-8')
    return str(filepath)