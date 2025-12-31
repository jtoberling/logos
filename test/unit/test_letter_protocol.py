"""
Unit tests for Letter Protocol - Letters for Future Self.

Tests the Sophia methodology's memory creation mechanism.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.memory.letter_protocol import LetterProtocol, Letter


class TestLetterProtocol:
    """Test Letter Protocol functionality."""

    def test_letter_creation_basic(self):
        """Test basic letter creation."""
        letter = Letter(
            interaction_summary="Helped user with Python debugging",
            emotional_context="productive",
            lesson_learned="Debugging requires systematic approach",
            creator="user_session_123"
        )

        assert letter.interaction_summary == "Helped user with Python debugging"
        assert letter.emotional_context == "productive"
        assert letter.lesson_learned == "Debugging requires systematic approach"
        assert letter.creator == "user_session_123"
        assert letter.timestamp is not None
        assert isinstance(letter.letter_id, str)
        assert len(letter.letter_id) > 0

    def test_letter_creation_minimal(self):
        """Test letter creation with minimal required fields."""
        letter = Letter(
            interaction_summary="Quick chat about APIs",
            emotional_context="neutral"
        )

        assert letter.interaction_summary == "Quick chat about APIs"
        assert letter.emotional_context == "neutral"
        assert letter.lesson_learned == ""
        assert letter.creator == "unknown"

    def test_letter_to_dict(self):
        """Test letter serialization to dictionary."""
        letter = Letter(
            interaction_summary="Test interaction",
            emotional_context="insightful",
            lesson_learned="Always test edge cases",
            creator="test_session"
        )

        data = letter.to_dict()
        assert data["interaction_summary"] == "Test interaction"
        assert data["emotional_context"] == "insightful"
        assert data["lesson_learned"] == "Always test edge cases"
        assert data["creator"] == "test_session"
        assert "timestamp" in data
        assert "letter_id" in data

    def test_letter_from_dict(self):
        """Test letter deserialization from dictionary."""
        data = {
            "interaction_summary": "Test interaction",
            "emotional_context": "insightful",
            "lesson_learned": "Always test edge cases",
            "creator": "test_session",
            "timestamp": "2024-01-01T12:00:00Z",
            "letter_id": "test-id-123"
        }

        letter = Letter.from_dict(data)

        assert letter.interaction_summary == "Test interaction"
        assert letter.emotional_context == "insightful"
        assert letter.lesson_learned == "Always test edge cases"
        assert letter.creator == "test_session"
        assert letter.letter_id == "test-id-123"

    def test_letter_formatting(self):
        """Test letter text formatting."""
        letter = Letter(
            interaction_summary="Helped user refactor code",
            emotional_context="productive",
            lesson_learned="Refactoring improves maintainability",
            creator="cursor_session_456"
        )

        formatted = letter.format_letter()

        assert "Letter for the Future Self" in formatted
        assert "Context: productive" in formatted
        assert "Helped user refactor code" in formatted
        assert "Refactoring improves maintainability" in formatted
        assert "cursor_session_456" in formatted

    @patch('src.memory.letter_protocol.uuid')
    def test_letter_id_generation(self, mock_uuid):
        """Test that letter IDs are properly generated."""
        mock_uuid.uuid4.return_value = MagicMock()
        mock_uuid.uuid4.return_value.__str__ = MagicMock(return_value="test-uuid-123")

        letter = Letter("test", "neutral")

        assert letter.letter_id == "test-uuid-123"
        mock_uuid.uuid4.assert_called_once()

    def test_letter_validation(self):
        """Test letter field validation."""
        # Valid letter
        letter = Letter("summary", "neutral")
        assert letter.is_valid()

        # Invalid - empty summary
        letter2 = Letter("", "neutral")
        assert not letter2.is_valid()

        # Invalid - empty emotional context
        letter3 = Letter("summary", "")
        assert not letter3.is_valid()


class TestLetterProtocolClass:
    """Test the LetterProtocol class functionality."""

    def test_protocol_initialization(self):
        """Test protocol initialization with vector store."""
        mock_vector_store = MagicMock()

        protocol = LetterProtocol(vector_store=mock_vector_store)

        assert protocol.vector_store == mock_vector_store

    def test_create_letter_basic(self):
        """Test basic letter creation through protocol."""
        mock_vector_store = MagicMock()
        protocol = LetterProtocol(vector_store=mock_vector_store)

        letter = protocol.create_letter(
            interaction_summary="User asked about TDD",
            emotional_context="educational",
            lesson_learned="TDD prevents bugs",
            creator="test_user"
        )

        assert isinstance(letter, Letter)
        assert letter.interaction_summary == "User asked about TDD"
        assert letter.emotional_context == "educational"
        assert letter.lesson_learned == "TDD prevents bugs"
        assert letter.creator == "test_user"

    def test_store_letter_success(self):
        """Test successful letter storage."""
        mock_vector_store = MagicMock()
        protocol = LetterProtocol(vector_store=mock_vector_store)

        letter = protocol.create_letter("test", "neutral")

        # Store the letter
        result = protocol.store_letter(letter)

        assert result is True

        # Verify vector store was called correctly
        mock_vector_store.upsert.assert_called_once()
        call_args = mock_vector_store.upsert.call_args
        assert call_args.kwargs["collection_name"] == "logos_essence"  # Should store in personality collection

        # Check that letter text was stored
        stored_texts = call_args.kwargs["texts"]
        assert len(stored_texts) == 1
        assert "Letter for the Future Self" in stored_texts[0]

        # Check metadata
        stored_metadata = call_args.kwargs["metadatas"]
        assert len(stored_metadata) == 1
        assert stored_metadata[0]["type"] == "future_letter"
        assert "letter_id" in stored_metadata[0]

    def test_store_letter_failure(self):
        """Test letter storage failure handling."""
        mock_vector_store = MagicMock()
        mock_vector_store.upsert.side_effect = Exception("Storage failed")

        protocol = LetterProtocol(vector_store=mock_vector_store)
        letter = protocol.create_letter("test", "neutral")

        result = protocol.store_letter(letter)

        assert result is False
        mock_vector_store.upsert.assert_called_once()

    def test_create_and_store_letter(self):
        """Test the combined create and store operation."""
        mock_vector_store = MagicMock()
        protocol = LetterProtocol(vector_store=mock_vector_store)

        result = protocol.create_and_store_letter(
            interaction_summary="User learned about design patterns",
            emotional_context="insightful",
            lesson_learned="Design patterns solve common problems",
            creator="design_session_789"
        )

        assert result is True

        # Verify both create and store were called
        mock_vector_store.upsert.assert_called_once()

        # Check stored content
        call_args = mock_vector_store.upsert.call_args
        stored_texts = call_args.kwargs["texts"]
        assert "User learned about design patterns" in stored_texts[0]
        assert "Design patterns solve common problems" in stored_texts[0]

    def test_create_and_store_invalid_letter(self):
        """Test handling of invalid letters."""
        mock_vector_store = MagicMock()
        protocol = LetterProtocol(vector_store=mock_vector_store)

        # Try to create invalid letter (empty summary)
        result = protocol.create_and_store_letter(
            interaction_summary="",
            emotional_context="neutral"
        )

        assert result is False
        mock_vector_store.upsert.assert_not_called()

    def test_bulk_store_letters(self):
        """Test storing multiple letters at once."""
        mock_vector_store = MagicMock()
        protocol = LetterProtocol(vector_store=mock_vector_store)

        letters = [
            protocol.create_letter("Interaction 1", "productive", "Lesson 1", "creator1"),
            protocol.create_letter("Interaction 2", "challenging", "Lesson 2", "creator2"),
            protocol.create_letter("Interaction 3", "insightful", "Lesson 3", "creator3")
        ]

        result = protocol.store_letters_bulk(letters)

        assert result is True

        # Should call upsert once with all letters
        mock_vector_store.upsert.assert_called_once()
        call_args = mock_vector_store.upsert.call_args
        assert call_args.kwargs["collection_name"] == "logos_essence"
        assert len(call_args.kwargs["texts"]) == 3  # 3 texts
        assert len(call_args.kwargs["metadatas"]) == 3  # 3 metadata entries

    def test_bulk_store_with_failure(self):
        """Test bulk storage with some failures."""
        mock_vector_store = MagicMock()
        mock_vector_store.upsert.side_effect = Exception("Bulk storage failed")

        protocol = LetterProtocol(vector_store=mock_vector_store)

        letters = [
            protocol.create_letter("Test 1", "neutral"),
            protocol.create_letter("Test 2", "neutral")
        ]

        result = protocol.store_letters_bulk(letters)

        assert result is False
        mock_vector_store.upsert.assert_called_once()

    def test_get_recent_letters(self):
        """Test retrieving recent letters."""
        mock_vector_store = MagicMock()
        # Mock search results
        mock_result1 = MagicMock()
        mock_result1.payload = {"text": "Recent letter 1", "type": "future_letter", "timestamp": "2024-01-02"}
        mock_result2 = MagicMock()
        mock_result2.payload = {"text": "Recent letter 2", "type": "future_letter", "timestamp": "2024-01-01"}

        mock_vector_store.search.return_value = [mock_result1, mock_result2]

        protocol = LetterProtocol(vector_store=mock_vector_store)

        letters = protocol.get_recent_letters(limit=5)

        assert len(letters) == 2
        assert letters[0].payload["text"] == "Recent letter 1"
        assert letters[1].payload["text"] == "Recent letter 2"

        mock_vector_store.search.assert_called_once_with(collection_name="logos_essence", query_text="future_letter", limit=5)

    def test_get_letters_by_creator(self):
        """Test retrieving letters by creator."""
        mock_vector_store = MagicMock()

        # Mock search that filters by creator
        def mock_search(**kwargs):
            query = kwargs.get("query_text", "")
            if "creator:test_user" in query:
                mock_result = MagicMock()
                mock_result.payload = {"text": "User's letter", "creator": "test_user"}
                return [mock_result]
            return []

        mock_vector_store.search.side_effect = mock_search

        protocol = LetterProtocol(vector_store=mock_vector_store)

        letters = protocol.get_letters_by_creator("test_user", limit=10)

        assert len(letters) == 1
        assert letters[0].payload["creator"] == "test_user"

        mock_vector_store.search.assert_called_once_with(collection_name="logos_essence", query_text="future_letter creator:test_user", limit=10)

    def test_statistics(self):
        """Test getting letter statistics."""
        mock_vector_store = MagicMock()

        # Mock collection info
        mock_info = {
            "points_count": 42,
            "status": "exists"
        }
        mock_vector_store.get_collection_info.return_value = mock_info

        protocol = LetterProtocol(vector_store=mock_vector_store)

        stats = protocol.get_statistics()

        assert stats["total_letters"] == 42
        assert stats["collection_status"] == "exists"

        mock_vector_store.get_collection_info.assert_called_once_with("logos_essence")

    def test_protocol_without_vector_store(self):
        """Test protocol behavior without vector store (for testing)."""
        protocol = LetterProtocol()

        letter = protocol.create_letter("test", "neutral")

        assert isinstance(letter, Letter)
        assert letter.interaction_summary == "test"

        # Storage operations should fail gracefully
        result = protocol.store_letter(letter)
        assert result is False