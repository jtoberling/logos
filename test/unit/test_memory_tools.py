"""
Unit tests for Memory Tools - MCP tools for letter protocol and memory management.

Tests the MCP tool interface for the Sophia methodology memory operations.
"""

import json
from unittest.mock import MagicMock

from src.tools.memory_tools import (
    create_letter_for_future_self,
    get_memory_statistics,
    retrieve_recent_memories,
    retrieve_memories_by_creator,
    initialize_memory_tools
)


class TestMemoryTools:
    """Test Memory Tools MCP functionality."""

    def test_initialize_memory_tools(self):
        """Test memory tools initialization."""
        mock_protocol = MagicMock()

        initialize_memory_tools(mock_protocol)

        # Verify the global variable is set
        # This would normally be tested by checking the actual tool functions

    def test_create_letter_for_future_self_success(self):
        """Test successful letter creation via MCP tool."""
        # Setup mock letter protocol
        mock_protocol = MagicMock()
        mock_letter = MagicMock()
        mock_letter.interaction_summary = "Test interaction"
        mock_letter.emotional_context = "productive"
        mock_letter.letter_id = "test-id-123"
        mock_letter.lesson_learned = "Systematic debugging is key"
        mock_letter.creator = "debug_session_456"
        mock_letter.timestamp = "2024-01-01T12:00:00Z"

        mock_protocol.create_letter.return_value = mock_letter
        mock_protocol.store_letter.return_value = True

        # Initialize tools with mock protocol
        initialize_memory_tools(mock_protocol)

        # Call the tool
        result = create_letter_for_future_self(
            interaction_summary="Helped user with debugging",
            emotional_context="productive",
            lesson_learned="Systematic debugging is key",
            creator="debug_session_456"
        )

        # Verify the protocol was called correctly
        mock_protocol.create_letter.assert_called_once_with(
            interaction_summary="Helped user with debugging",
            emotional_context="productive",
            lesson_learned="Systematic debugging is key",
            creator="debug_session_456"
        )
        mock_protocol.store_letter.assert_called_once()

        # Parse and verify result
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "letter_id" in parsed
        assert parsed["letter_id"] == "test-id-123"

    def test_create_letter_for_future_self_failure(self):
        """Test letter creation failure handling."""
        mock_protocol = MagicMock()
        mock_letter = MagicMock()
        mock_protocol.create_letter.return_value = mock_letter
        mock_protocol.store_letter.return_value = False
        initialize_memory_tools(mock_protocol)

        result = create_letter_for_future_self(
            interaction_summary="Failed interaction",
            emotional_context="challenging"
        )

        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "error" in parsed

    def test_create_letter_for_future_self_invalid_input(self):
        """Test handling of invalid letter input."""
        mock_protocol = MagicMock()
        initialize_memory_tools(mock_protocol)

        # Empty summary should fail
        result = create_letter_for_future_self(
            interaction_summary="",  # Invalid
            emotional_context="neutral"
        )

        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "error" in parsed

        # Protocol should not be called for invalid input
        mock_protocol.create_letter.assert_not_called()
        mock_protocol.store_letter.assert_not_called()

    def test_get_memory_statistics_success(self):
        """Test successful memory statistics retrieval."""
        mock_protocol = MagicMock()
        mock_stats = {
            "total_letters": 42,
            "collection_status": "exists",
            "last_updated": "2024-01-01T12:00:00Z"
        }
        mock_protocol.get_statistics.return_value = mock_stats
        initialize_memory_tools(mock_protocol)

        result = get_memory_statistics()

        parsed = json.loads(result)
        assert parsed["total_letters"] == 42
        assert parsed["collection_status"] == "exists"
        assert "last_updated" in parsed

        mock_protocol.get_statistics.assert_called_once()

    def test_get_memory_statistics_failure(self):
        """Test memory statistics failure handling."""
        mock_protocol = MagicMock()
        mock_protocol.get_statistics.side_effect = Exception("Stats error")
        initialize_memory_tools(mock_protocol)

        result = get_memory_statistics()

        parsed = json.loads(result)
        assert "error" in parsed
        assert "Stats error" in parsed["error"]

    def test_retrieve_recent_memories_success(self):
        """Test successful recent memories retrieval."""
        mock_protocol = MagicMock()
        initialize_memory_tools(mock_protocol)

        # Mock search results
        mock_result1 = MagicMock()
        mock_result1.payload = {
            "text": "Letter for the Future Self\nContext: productive\nSummary: Helped with code review",
            "type": "future_letter",
            "creator": "code_review_123",
            "timestamp": "2024-01-02T10:00:00Z"
        }
        mock_result1.score = 0.95

        mock_result2 = MagicMock()
        mock_result2.payload = {
            "text": "Letter for the Future Self\nContext: insightful\nSummary: Learned about design patterns",
            "type": "future_letter",
            "creator": "learning_session_456",
            "timestamp": "2024-01-01T15:00:00Z"
        }
        mock_result2.score = 0.87

        mock_protocol.get_recent_letters.return_value = [mock_result1, mock_result2]

        result = retrieve_recent_memories(limit=5)

        parsed = json.loads(result)
        assert len(parsed["memories"]) == 2
        assert parsed["count"] == 2
        assert parsed["memories"][0]["creator"] == "code_review_123"
        assert parsed["memories"][1]["creator"] == "learning_session_456"
        assert parsed["memories"][0]["score"] == 0.95

        mock_protocol.get_recent_letters.assert_called_once_with(limit=5)

    def test_retrieve_recent_memories_empty(self):
        """Test retrieving recent memories when none exist."""
        mock_protocol = MagicMock()
        mock_protocol.get_recent_letters.return_value = []
        initialize_memory_tools(mock_protocol)

        result = retrieve_recent_memories(limit=10)

        parsed = json.loads(result)
        assert parsed["memories"] == []
        assert parsed["count"] == 0

    def test_retrieve_recent_memories_failure(self):
        """Test recent memories retrieval failure."""
        mock_protocol = MagicMock()
        mock_protocol.get_recent_letters.side_effect = Exception("Retrieval failed")
        initialize_memory_tools(mock_protocol)

        result = retrieve_recent_memories(limit=3)

        parsed = json.loads(result)
        assert "error" in parsed
        assert "Retrieval failed" in parsed["error"]

    def test_retrieve_memories_by_creator_success(self):
        """Test successful creator-specific memory retrieval."""
        mock_protocol = MagicMock()
        mock_result = MagicMock()
        mock_result.payload = {
            "text": "Letter for the Future Self\nContext: collaborative\nSummary: Pair programming session",
            "type": "future_letter",
            "creator": "developer_alice",
            "timestamp": "2024-01-03T09:00:00Z"
        }
        mock_result.score = 0.92

        mock_protocol.get_letters_by_creator.return_value = [mock_result]
        initialize_memory_tools(mock_protocol)

        result = retrieve_memories_by_creator(creator="developer_alice", limit=10)

        parsed = json.loads(result)
        assert len(parsed["memories"]) == 1
        assert parsed["creator"] == "developer_alice"
        assert parsed["count"] == 1
        assert parsed["memories"][0]["creator"] == "developer_alice"

        mock_protocol.get_letters_by_creator.assert_called_once_with(creator="developer_alice", limit=10)

    def test_retrieve_memories_by_creator_no_results(self):
        """Test creator search with no results."""
        mock_protocol = MagicMock()
        mock_protocol.get_letters_by_creator.return_value = []
        initialize_memory_tools(mock_protocol)

        result = retrieve_memories_by_creator(creator="nonexistent_user", limit=5)

        parsed = json.loads(result)
        assert parsed["memories"] == []
        assert parsed["count"] == 0
        assert parsed["creator"] == "nonexistent_user"

    def test_retrieve_memories_by_creator_failure(self):
        """Test creator memory retrieval failure."""
        mock_protocol = MagicMock()
        mock_protocol.get_letters_by_creator.side_effect = Exception("Search failed")
        initialize_memory_tools(mock_protocol)

        result = retrieve_memories_by_creator(creator="test_user", limit=3)

        parsed = json.loads(result)
        assert "error" in parsed
        assert "Search failed" in parsed["error"]

    def test_tools_without_protocol_initialized(self):
        """Test tool behavior when protocol is not initialized."""
        # Reset global variable (simulate uninitialized state)
        import src.tools.memory_tools as mt
        mt._letter_protocol = None

        result = create_letter_for_future_self(
            interaction_summary="Test without protocol",
            emotional_context="neutral"
        )

        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "not properly initialized" in parsed["error"]

    def test_default_parameters(self):
        """Test default parameter values in tools."""
        # Test that the functions accept the expected parameters
        # This is more of a smoke test for the function signatures

        # These should not raise exceptions even without protocol
        try:
            create_letter_for_future_self("summary", "neutral")
            get_memory_statistics()
            retrieve_recent_memories()
            retrieve_memories_by_creator("test_creator")
            # If we get here, the signatures are correct
            assert True
        except TypeError:
            # TypeError would indicate wrong function signature
            assert False, "Function signature mismatch"

    def test_memory_tools_integration(self):
        """Test that memory tools work together as a system."""
        # Setup mock protocol
        mock_protocol = MagicMock()

        # Create a mock letter that behaves like a real Letter object
        mock_letter = MagicMock()
        mock_letter.letter_id = "integration-test-id"
        mock_letter.interaction_summary = "Integration test"
        mock_letter.emotional_context = "productive"
        mock_letter.lesson_learned = ""
        mock_letter.creator = "unknown"
        mock_letter.timestamp = "2024-01-01T12:00:00Z"

        mock_protocol.create_letter.return_value = mock_letter
        mock_protocol.store_letter.return_value = True
        mock_protocol.get_statistics.return_value = {"total_letters": 1}

        initialize_memory_tools(mock_protocol)

        # Create a letter
        create_result = create_letter_for_future_self("Integration test", "productive")
        create_parsed = json.loads(create_result)
        assert create_parsed["success"] is True

        # Check statistics
        stats_result = get_memory_statistics()
        stats_parsed = json.loads(stats_result)
        assert stats_parsed["total_letters"] == 1

        # Verify protocol interactions
        assert mock_protocol.create_letter.called
        assert mock_protocol.store_letter.called
        assert mock_protocol.get_statistics.called