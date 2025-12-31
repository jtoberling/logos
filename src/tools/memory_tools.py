"""
Memory Tools for Logos MCP Server.

MCP tools for letter creation and memory management following
the Sophia methodology's Letters for Future Self protocol.
"""

import json
from typing import Optional

try:
    from mcp import tool
except ImportError:
    # Mock for testing when MCP not available
    def tool(*args, **kwargs) -> callable:
        def decorator(func) -> callable:
            return func
        return decorator

# Import from the letter protocol
try:
    from ..memory.letter_protocol import LetterProtocol
except ImportError:
    # Fallback for when running from tools directory
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
    from src.memory.letter_protocol import LetterProtocol

# Global letter protocol instance (initialized by MCP server)
_letter_protocol: Optional[LetterProtocol] = None


def initialize_memory_tools(letter_protocol: LetterProtocol) -> None:
    """
    Initialize memory tools with the letter protocol.

    Args:
        letter_protocol: Configured LetterProtocol instance
    """
    global _letter_protocol
    _letter_protocol = letter_protocol


@tool()
def create_letter_for_future_self(
    interaction_summary: str,
    emotional_context: str,
    lesson_learned: str = "",
    creator: str = "unknown"
) -> str:
    """
    Create a Letter for Future Self following the Sophia methodology.

    This transforms an interaction into a permanent memory that becomes
    part of Logos' personality and learning experience.

    Args:
        interaction_summary: What happened in the interaction
        emotional_context: How the interaction felt (productive, challenging, insightful, etc.)
        lesson_learned: Key lesson or insight gained (optional)
        creator: Identifier for who/what created this letter (optional)

    Returns:
        JSON string with creation result and letter ID
    """
    if not _letter_protocol:
        return json.dumps({
            "success": False,
            "error": "Memory tools not properly initialized"
        })

    # Validate required fields
    if not interaction_summary or not interaction_summary.strip():
        return json.dumps({
            "success": False,
            "error": "Interaction summary cannot be empty"
        })

    if not emotional_context or not emotional_context.strip():
        return json.dumps({
            "success": False,
            "error": "Emotional context cannot be empty"
        })

    try:
        # Create the letter (this also validates the content)
        letter = _letter_protocol.create_letter(
            interaction_summary=interaction_summary.strip(),
            emotional_context=emotional_context.strip(),
            lesson_learned=lesson_learned.strip() if lesson_learned else "",
            creator=creator.strip() if creator else "unknown"
        )

        # Store the letter
        success = _letter_protocol.store_letter(letter)

        if success:
            return json.dumps({
                "success": True,
                "letter_id": letter.letter_id,
                "message": "Letter for Future Self created and stored successfully",
                "interaction_summary": letter.interaction_summary,
                "emotional_context": letter.emotional_context,
                "lesson_learned": letter.lesson_learned,
                "creator": letter.creator,
                "timestamp": letter.timestamp
            })
        else:
            return json.dumps({
                "success": False,
                "error": "Failed to store letter in memory"
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Letter creation failed: {str(e)}"
        })


@tool()
def get_memory_statistics() -> str:
    """
    Get statistics about Logos' memory collections.

    Returns information about the total number of memories,
    collection status, and other memory-related metrics.

    Returns:
        JSON string with memory statistics
    """
    if not _letter_protocol:
        return json.dumps({
            "error": "Memory tools not properly initialized",
            "total_letters": 0,
            "collection_status": "unknown"
        })

    try:
        stats = _letter_protocol.get_statistics()
        return json.dumps(stats, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to retrieve memory statistics: {str(e)}",
            "total_letters": 0,
            "collection_status": "error"
        })


@tool()
def retrieve_recent_memories(limit: int = 10) -> str:
    """
    Retrieve recent Letters for Future Self from memory.

    Returns the most recently created letters that form Logos'
    personality and learning experience.

    Args:
        limit: Maximum number of recent memories to retrieve (default: 10)

    Returns:
        JSON string with recent memories and metadata
    """
    if not _letter_protocol:
        return json.dumps({
            "error": "Memory tools not properly initialized",
            "memories": [],
            "count": 0
        })

    try:
        results = _letter_protocol.get_recent_letters(limit=limit)

        # Format results for JSON response
        memories = []
        for result in results:
            payload = result.payload
            memories.append({
                "interaction_summary": _extract_summary_from_letter(payload.get("text", "")),
                "emotional_context": payload.get("emotional_context", "unknown"),
                "lesson_learned": payload.get("lesson_learned", ""),
                "creator": payload.get("creator", "unknown"),
                "timestamp": payload.get("timestamp", "unknown"),
                "letter_id": payload.get("letter_id", "unknown"),
                "score": result.score
            })

        return json.dumps({
            "memories": memories,
            "count": len(memories),
            "limit_requested": limit,
            "message": f"Retrieved {len(memories)} recent memories"
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to retrieve recent memories: {str(e)}",
            "memories": [],
            "count": 0
        })


@tool()
def retrieve_memories_by_creator(creator: str, limit: int = 20) -> str:
    """
    Retrieve Letters for Future Self created by a specific creator.

    Useful for tracking learning patterns from specific users,
    sessions, or interaction types.

    Args:
        creator: Creator identifier to search for
        limit: Maximum number of memories to retrieve (default: 20)

    Returns:
        JSON string with creator-specific memories
    """
    if not _letter_protocol:
        return json.dumps({
            "error": "Memory tools not properly initialized",
            "memories": [],
            "count": 0,
            "creator": creator
        })

    if not creator or not creator.strip():
        return json.dumps({
            "error": "Creator cannot be empty",
            "memories": [],
            "count": 0,
            "creator": creator
        })

    try:
        results = _letter_protocol.get_letters_by_creator(
            creator=creator.strip(),
            limit=limit
        )

        # Format results for JSON response
        memories = []
        for result in results:
            payload = result.payload
            memories.append({
                "interaction_summary": _extract_summary_from_letter(payload.get("text", "")),
                "emotional_context": payload.get("emotional_context", "unknown"),
                "lesson_learned": payload.get("lesson_learned", ""),
                "creator": payload.get("creator", "unknown"),
                "timestamp": payload.get("timestamp", "unknown"),
                "letter_id": payload.get("letter_id", "unknown"),
                "score": result.score
            })

        return json.dumps({
            "creator": creator,
            "memories": memories,
            "count": len(memories),
            "limit_requested": limit,
            "message": f"Retrieved {len(memories)} memories from creator '{creator}'"
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to retrieve memories by creator: {str(e)}",
            "memories": [],
            "count": 0,
            "creator": creator
        })


def _extract_summary_from_letter(letter_text: str) -> str:
    """
    Extract the interaction summary from a formatted letter text.

    Args:
        letter_text: Full formatted letter text

    Returns:
        Just the interaction summary portion
    """
    try:
        # Look for the Summary line in the formatted letter
        lines = letter_text.split('\n')
        for line in lines:
            if line.startswith('Summary:'):
                return line.replace('Summary:', '').strip()
        return letter_text[:100] + "..."  # Fallback to truncated text
    except Exception:
        return letter_text[:100] + "..." if letter_text else "Unknown summary"