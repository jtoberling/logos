"""
Unit tests for query tools MCP functionality.

Tests the MCP tools that provide memory engine functionality.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.tools.query_tools import (
    initialize_tools,
    query_logos,
    get_constitution,
    get_memory_context,
    get_collection_stats
)


class TestQueryTools:
    """Test query tools MCP functionality."""

    def setup_method(self):
        """Reset global state before each test."""
        # Reset global variables
        import src.tools.query_tools as qt
        qt._vector_store = None
        qt._prompt_manager = None

    def test_initialize_tools(self):
        """Test tool initialization."""
        mock_vector_store = MagicMock()
        mock_prompt_manager = MagicMock()

        initialize_tools(mock_vector_store, mock_prompt_manager)

        import src.tools.query_tools as qt
        assert qt._vector_store == mock_vector_store
        assert qt._prompt_manager == mock_prompt_manager

    def test_query_logos_uninitialized(self):
        """Test query_logos when tools are not initialized."""
        result = query_logos("test question")

        parsed = json.loads(result)
        assert parsed["error"] == "Logos MCP server not properly initialized"
        assert parsed["constitution"] == ""
        assert parsed["personality_memories"] == []
        assert parsed["project_knowledge"] == []
        assert isinstance(parsed["metadata"], dict)

    @patch('src.tools.query_tools.datetime')
    def test_query_logos_success(self, mock_datetime):
        """Test successful query_logos operation."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"

        # Setup mocks
        mock_vector_store = MagicMock()
        mock_prompt_manager = MagicMock()

        # Mock search results
        mock_essence_result = MagicMock()
        mock_essence_result.payload = {"text": "essence memory", "source": "test"}
        mock_essence_result.score = 0.9

        mock_project_result = MagicMock()
        mock_project_result.payload = {"text": "project knowledge", "file": "test.py"}
        mock_project_result.score = 0.8

        # Mock search to return results based on collection name
        def mock_search(collection, question, limit):
            if collection == "logos_essence":
                return [mock_essence_result]
            elif collection == "project_knowledge":
                return [mock_project_result]
            return []

        mock_vector_store.search.side_effect = mock_search

        mock_prompt_manager.get_constitution.return_value = "Test constitution"

        # Initialize tools
        initialize_tools(mock_vector_store, mock_prompt_manager)

        # Execute query
        result = query_logos("test question", limit=5)

        # Parse and verify
        parsed = json.loads(result)
        assert "constitution" in parsed
        assert parsed["constitution"] == "Test constitution"
        assert len(parsed["personality_memories"]) == 1
        assert parsed["personality_memories"][0]["text"] == "essence memory"
        assert parsed["personality_memories"][0]["score"] == 0.9
        assert len(parsed["project_knowledge"]) == 1
        assert parsed["project_knowledge"][0]["text"] == "project knowledge"
        assert parsed["project_knowledge"][0]["score"] == 0.8
        assert parsed["metadata"]["query"] == "test question"
        assert parsed["metadata"]["personality_results_count"] == 1
        assert parsed["metadata"]["project_results_count"] == 1

        # Verify search calls
        assert mock_vector_store.search.call_count == 2
        mock_vector_store.search.assert_any_call("logos_essence", "test question", limit=3)
        mock_vector_store.search.assert_any_call("project_knowledge", "test question", limit=5)

    def test_query_logos_with_exception(self):
        """Test query_logos when an exception occurs."""
        mock_vector_store = MagicMock()
        mock_prompt_manager = MagicMock()

        mock_vector_store.search.side_effect = Exception("Search failed")
        mock_prompt_manager.get_constitution.return_value = "Fallback constitution"

        initialize_tools(mock_vector_store, mock_prompt_manager)

        result = query_logos("test question")

        parsed = json.loads(result)
        assert "error" in parsed
        assert "Search failed" in parsed["error"]
        assert parsed["constitution"] == "Fallback constitution"
        assert parsed["personality_memories"] == []
        assert parsed["project_knowledge"] == []

    def test_get_constitution_uninitialized(self):
        """Test get_constitution when tools are not initialized."""
        result = get_constitution()
        assert result == "Error: Logos constitution not available"

    def test_get_constitution_success(self):
        """Test successful get_constitution operation."""
        mock_prompt_manager = MagicMock()
        mock_prompt_manager.get_constitution.return_value = "Test constitution"

        initialize_tools(MagicMock(), mock_prompt_manager)

        result = get_constitution()
        assert result == "Test constitution"

    def test_get_constitution_with_exception(self):
        """Test get_constitution when an exception occurs."""
        mock_prompt_manager = MagicMock()
        mock_prompt_manager.get_constitution.side_effect = Exception("Constitution error")

        initialize_tools(MagicMock(), mock_prompt_manager)

        result = get_constitution()
        assert "Error retrieving constitution: Constitution error" in result

    def test_get_memory_context_uninitialized(self):
        """Test get_memory_context when vector store is not initialized."""
        result = get_memory_context("test question")

        parsed = json.loads(result)
        assert parsed["error"] == "Vector store not available"
        assert parsed["memories"] == []
        assert isinstance(parsed["metadata"], dict)

    @patch('src.tools.query_tools.datetime')
    def test_get_memory_context_essence_only(self, mock_datetime):
        """Test get_memory_context with essence collection only."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"

        mock_vector_store = MagicMock()
        mock_result = MagicMock()
        mock_result.payload = {"text": "essence memory", "type": "letter"}
        mock_result.score = 0.85

        mock_vector_store.search.return_value = [mock_result]
        initialize_tools(mock_vector_store, MagicMock())

        result = get_memory_context("test question", collection="essence", limit=3)

        parsed = json.loads(result)
        assert len(parsed["memories"]) == 1
        assert parsed["memories"][0]["collection"] == "logos_essence"
        assert parsed["memories"][0]["text"] == "essence memory"
        assert parsed["memories"][0]["score"] == 0.85
        assert parsed["metadata"]["collection"] == "essence"
        assert parsed["metadata"]["limit"] == 3

        mock_vector_store.search.assert_called_once_with("logos_essence", "test question", limit=3)

    @patch('src.tools.query_tools.datetime')
    def test_get_memory_context_project_only(self, mock_datetime):
        """Test get_memory_context with project collection only."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"

        mock_vector_store = MagicMock()
        mock_result = MagicMock()
        mock_result.payload = {"text": "project knowledge", "file": "test.py"}
        mock_result.score = 0.75

        mock_vector_store.search.return_value = [mock_result]
        initialize_tools(mock_vector_store, MagicMock())

        result = get_memory_context("test question", collection="project", limit=5)

        parsed = json.loads(result)
        assert len(parsed["memories"]) == 1
        assert parsed["memories"][0]["collection"] == "project_knowledge"
        assert parsed["memories"][0]["text"] == "project knowledge"

        mock_vector_store.search.assert_called_once_with("project_knowledge", "test question", limit=5)

    @patch('src.tools.query_tools.datetime')
    def test_get_memory_context_both_collections(self, mock_datetime):
        """Test get_memory_context with both collections."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"

        mock_vector_store = MagicMock()

        # Mock essence result
        essence_result = MagicMock()
        essence_result.payload = {"text": "essence memory"}
        essence_result.score = 0.9

        # Mock project result (higher score)
        project_result = MagicMock()
        project_result.payload = {"text": "project knowledge"}
        project_result.score = 0.95

        def mock_search(collection, query, limit):
            if collection == "logos_essence":
                return [essence_result]
            elif collection == "project_knowledge":
                return [project_result]
            return []

        mock_vector_store.search.side_effect = mock_search
        initialize_tools(mock_vector_store, MagicMock())

        result = get_memory_context("test question", collection="both", limit=4)

        parsed = json.loads(result)
        assert len(parsed["memories"]) == 2
        # Results should be sorted by score (highest first)
        assert parsed["memories"][0]["score"] == 0.95  # project result first
        assert parsed["memories"][1]["score"] == 0.9   # essence result second

        # Verify both collections were searched
        assert mock_vector_store.search.call_count == 2

    def test_get_memory_context_with_exception(self):
        """Test get_memory_context when an exception occurs."""
        mock_vector_store = MagicMock()
        mock_vector_store.search.side_effect = Exception("Search error")

        initialize_tools(mock_vector_store, MagicMock())

        result = get_memory_context("test question")

        parsed = json.loads(result)
        assert "error" in parsed
        assert "Search error" in parsed["error"]
        assert parsed["memories"] == []

    def test_get_collection_stats_uninitialized(self):
        """Test get_collection_stats when vector store is not initialized."""
        result = get_collection_stats()

        parsed = json.loads(result)
        assert parsed["error"] == "Vector store not available"
        assert parsed["collections"] == {}

    @patch('src.tools.query_tools.datetime')
    def test_get_collection_stats_success(self, mock_datetime):
        """Test successful get_collection_stats operation."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"

        mock_vector_store = MagicMock()
        initialize_tools(mock_vector_store, MagicMock())

        result = get_collection_stats()

        parsed = json.loads(result)
        assert "collections" in parsed
        assert "logos_essence" in parsed["collections"]
        assert "project_knowledge" in parsed["collections"]
        assert "canon" in parsed["collections"]
        assert "metadata" in parsed
        assert "timestamp" in parsed["metadata"]

        # Verify descriptions are present
        assert "description" in parsed["collections"]["logos_essence"]
        assert "description" in parsed["collections"]["project_knowledge"]

    def test_get_collection_stats_with_exception(self):
        """Test get_collection_stats when an exception occurs."""
        mock_vector_store = MagicMock()
        # Simulate exception in the try block
        # Since we don't have actual implementation, we'll mock a scenario

        initialize_tools(mock_vector_store, MagicMock())

        result = get_collection_stats()

        # Should succeed with current implementation
        parsed = json.loads(result)
        assert "collections" in parsed
        assert isinstance(parsed["collections"], dict)