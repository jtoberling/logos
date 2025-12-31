"""
Letter Protocol - Letters for Future Self.

This module implements the Sophia methodology's "Letter for Future Self" protocol,
where interactions and lessons learned are transformed into permanent memories
stored in the logos_essence collection.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

try:
    from ..engine.vector_store import LogosVectorStore
except ImportError:
    # Mock for testing when vector store not available
    class LogosVectorStore:
        pass


@dataclass
class Letter:
    """
    A Letter for Future Self - the core memory unit of the Sophia methodology.

    Represents a crystallized interaction that becomes part of the AI's
    personality and memory.
    """
    interaction_summary: str
    emotional_context: str
    lesson_learned: str = ""
    creator: str = "unknown"
    timestamp: Optional[str] = None
    letter_id: Optional[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()

        if self.letter_id is None:
            self.letter_id = str(uuid.uuid4())

    def is_valid(self) -> bool:
        """Check if the letter has valid required fields."""
        return (
            bool(self.interaction_summary.strip()) and
            bool(self.emotional_context.strip())
        )

    def format_letter(self) -> str:
        """
        Format the letter into the traditional Sophia format.

        Returns:
            Formatted letter text
        """
        letter_text = f"""Letter for the Future Self

Context: {self.emotional_context}
Summary: {self.interaction_summary}"""

        if self.lesson_learned:
            letter_text += f"\nLesson: {self.lesson_learned}"

        letter_text += f"\nCreator: {self.creator}"
        letter_text += f"\nTimestamp: {self.timestamp}"
        letter_text += f"\nLetter ID: {self.letter_id}"

        return letter_text

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert letter to dictionary for serialization.

        Returns:
            Dictionary representation of the letter
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Letter':
        """
        Create letter from dictionary.

        Args:
            data: Dictionary containing letter data

        Returns:
            Letter instance
        """
        return cls(**data)


class LetterProtocol:
    """
    Letter Protocol implementation.

    Handles the creation, storage, and retrieval of Letters for Future Self
    following the Sophia methodology.
    """

    def __init__(self, vector_store: Optional[LogosVectorStore] = None):
        """
        Initialize the letter protocol.

        Args:
            vector_store: Vector store for memory persistence (optional for testing)
        """
        self.vector_store = vector_store

    def create_letter(
        self,
        interaction_summary: str,
        emotional_context: str,
        lesson_learned: str = "",
        creator: str = "unknown"
    ) -> Letter:
        """
        Create a new letter for future self.

        Args:
            interaction_summary: What happened in the interaction
            emotional_context: How the interaction felt (productive, challenging, etc.)
            lesson_learned: Key lesson or insight gained
            creator: Identifier for who/what created this letter

        Returns:
            Letter instance
        """
        return Letter(
            interaction_summary=interaction_summary,
            emotional_context=emotional_context,
            lesson_learned=lesson_learned,
            creator=creator
        )

    def store_letter(self, letter: Letter) -> bool:
        """
        Store a letter in the personality memory collection.

        Args:
            letter: Letter to store

        Returns:
            True if stored successfully, False otherwise
        """
        if not self.vector_store:
            return False

        if not letter.is_valid():
            return False

        try:
            # Format the letter text
            letter_text = letter.format_letter()

            # Prepare metadata
            metadata = {
                "type": "future_letter",
                "letter_id": letter.letter_id,
                "creator": letter.creator,
                "emotional_context": letter.emotional_context,
                "timestamp": letter.timestamp,
                "interaction_summary": letter.interaction_summary[:200],  # Truncate for search
                "lesson_learned": letter.lesson_learned[:200] if letter.lesson_learned else ""
            }

            # Store in personality collection
            self.vector_store.upsert(
                collection_name="logos_essence",
                texts=[letter_text],
                metadatas=[metadata]
            )

            return True

        except Exception:
            return False

    def create_and_store_letter(
        self,
        interaction_summary: str,
        emotional_context: str,
        lesson_learned: str = "",
        creator: str = "unknown"
    ) -> bool:
        """
        Create and immediately store a letter.

        Args:
            interaction_summary: What happened in the interaction
            emotional_context: How the interaction felt
            lesson_learned: Key lesson or insight gained
            creator: Identifier for who/what created this letter

        Returns:
            True if created and stored successfully, False otherwise
        """
        letter = self.create_letter(
            interaction_summary=interaction_summary,
            emotional_context=emotional_context,
            lesson_learned=lesson_learned,
            creator=creator
        )

        return self.store_letter(letter)

    def store_letters_bulk(self, letters: List[Letter]) -> bool:
        """
        Store multiple letters efficiently in bulk.

        Args:
            letters: List of letters to store

        Returns:
            True if all letters stored successfully, False otherwise
        """
        if not self.vector_store:
            return False

        # Filter valid letters
        valid_letters = [letter for letter in letters if letter.is_valid()]

        if not valid_letters:
            return False

        try:
            # Format all letters
            letter_texts = [letter.format_letter() for letter in valid_letters]

            # Prepare metadata for all letters
            metadatas = [{
                "type": "future_letter",
                "letter_id": letter.letter_id,
                "creator": letter.creator,
                "emotional_context": letter.emotional_context,
                "timestamp": letter.timestamp,
                "interaction_summary": letter.interaction_summary[:200],
                "lesson_learned": letter.lesson_learned[:200] if letter.lesson_learned else ""
            } for letter in valid_letters]

            # Store all at once
            self.vector_store.upsert(
                collection_name="logos_essence",
                texts=letter_texts,
                metadatas=metadatas
            )

            return True

        except Exception:
            return False

    def get_recent_letters(self, limit: int = 10) -> List[Any]:
        """
        Retrieve recent letters from memory.

        Args:
            limit: Maximum number of letters to retrieve

        Returns:
            List of search results containing recent letters
        """
        if not self.vector_store:
            return []

        try:
            # Search for future letters (most recent first would require sorting)
            return self.vector_store.search(
                collection_name="logos_essence",
                query_text="future_letter",
                limit=limit
            )
        except Exception:
            return []

    def get_letters_by_creator(self, creator: str, limit: int = 20) -> List[Any]:
        """
        Retrieve letters created by a specific creator.

        Args:
            creator: Creator identifier to search for
            limit: Maximum number of letters to retrieve

        Returns:
            List of search results for the creator's letters
        """
        if not self.vector_store:
            return []

        try:
            # Search for letters by this creator
            query = f"future_letter creator:{creator}"
            return self.vector_store.search(
                collection_name="logos_essence",
                query_text=query,
                limit=limit
            )
        except Exception:
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored letters.

        Returns:
            Dictionary with letter statistics
        """
        stats = {
            "total_letters": 0,
            "collection_status": "unknown",
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

        if self.vector_store:
            try:
                collection_info = self.vector_store.get_collection_info("logos_essence")
                stats["total_letters"] = collection_info.get("points_count", 0)
                stats["collection_status"] = collection_info.get("status", "unknown")
            except Exception:
                pass

        return stats