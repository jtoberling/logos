"""
Query tools for Logos MCP server.

These tools provide pure memory engine functionality - they return context
and constitution data without any LLM integration. The client handles LLM calls.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

try:
    from mcp import tool
except ImportError:
    # Mock for testing when MCP not available
    def tool(*args, **kwargs) -> callable:
        def decorator(func) -> callable:
            return func
        return decorator

from ..logging_config import get_logger

logger = get_logger(__name__)

# These will be imported when the MCP server initializes
# from ..config import get_config
# from ..engine.vector_store import LogosVectorStore
# from ..personality.prompt_manager import LogosPromptManager

# Global instances (set during MCP server initialization)
_vector_store = None
_prompt_manager = None

# Version information
try:
    import src as logos
except ImportError:
    # Fallback for testing
    class MockLogos:
        __version__ = "1.0.0"
        __author__ = "Janos Toberling"
        __description__ = "Digital memory engine and personality framework"
        __url__ = "https://github.com/janos/logos"
    logos = MockLogos()


def initialize_tools(vector_store, prompt_manager) -> None:
    """Initialize tools with required dependencies."""
    global _vector_store, _prompt_manager
    _vector_store = vector_store
    _prompt_manager = prompt_manager

    logger.info("Query tools initialized with vector store and prompt manager")
    logger.info("Available query tools: query_logos, get_constitution, get_memory_context, get_collection_stats, get_version")


@tool()
def query_logos(question: str, limit: int = 5) -> str:
    """
    Query Logos for relevant context and constitution.

    This is the main query interface that returns all relevant information
    for answering a question, including constitution, personality memories,
    and project knowledge. The client handles the actual LLM call.

    Args:
        question: The question to query for
        limit: Maximum results per collection (default: 5)

    Returns:
        JSON string containing:
        - constitution: Logos' personality constitution
        - personality_memories: Relevant memories from logos_essence
        - project_knowledge: Relevant knowledge from project_knowledge
        - metadata: Query metadata
    """
    logger.info(f"MCP API: query_logos called with question='{question}' (limit={limit})")

    if not _vector_store or not _prompt_manager:
        logger.warning("MCP API: query_logos failed - server not properly initialized")
        return json.dumps({
            "error": "Logos MCP server not properly initialized",
            "constitution": "",
            "personality_memories": [],
            "project_knowledge": [],
            "metadata": {}
        })

    try:
        logger.info(f"Searching logos_essence collection for: {question}")
        # Search both collections
        essence_results = _vector_store.search("logos_essence", question, limit=min(limit, 3))

        logger.info(f"Searching project_knowledge collection for: {question}")
        project_results = _vector_store.search("project_knowledge", question, limit=limit)

        # Build response
        total_results = len(essence_results) + len(project_results)
        logger.info(f"Found {len(essence_results)} personality memories and {len(project_results)} project knowledge results")

        response = {
            "constitution": _prompt_manager.get_constitution(),
            "personality_memories": [
                {
                    "text": result.payload.get("text", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"},
                    "score": result.score
                }
                for result in essence_results
            ],
            "project_knowledge": [
                {
                    "text": result.payload.get("text", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"},
                    "score": result.score
                }
                for result in project_results
            ],
            "metadata": {
                "query": question,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "personality_results_count": len(essence_results),
                "project_results_count": len(project_results),
                "total_results": total_results
            }
        }

        logger.info(f"MCP API: query_logos completed - returned {total_results} total results")
        return json.dumps(response, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"MCP API: query_logos failed - {str(e)}")
        return json.dumps({
            "error": f"Query failed: {str(e)}",
            "constitution": _prompt_manager.get_constitution() if _prompt_manager else "",
            "personality_memories": [],
            "project_knowledge": [],
            "metadata": {"query": question, "error": str(e)}
        })


@tool()
def get_constitution() -> str:
    """
    Get Logos' personality constitution.

    Returns:
        The complete constitution text that defines Logos' personality,
        rules, and behavioral guidelines.
    """
    logger.info("MCP API: get_constitution called")

    if not _prompt_manager:
        logger.warning("MCP API: get_constitution failed - prompt manager not available")
        return "Error: Logos constitution not available"

    try:
        constitution = _prompt_manager.get_constitution()
        logger.info(f"MCP API: get_constitution completed - returned {len(constitution)} characters")
        return constitution
    except Exception as e:
        logger.error(f"MCP API: get_constitution failed - {str(e)}")
        return f"Error retrieving constitution: {str(e)}"


@tool()
def get_memory_context(question: str, collection: str = "both", limit: int = 5) -> str:
    """
    Get relevant memory context for a question.

    Args:
        question: Question to search for
        collection: Which collection to search ("essence", "project", or "both")
        limit: Maximum results to return

    Returns:
        JSON string with relevant memories and metadata
    """
    logger.info(f"MCP API: get_memory_context called with question='{question}' (collection={collection}, limit={limit})")

    if not _vector_store:
        logger.warning("MCP API: get_memory_context failed - vector store not available")
        return json.dumps({
            "error": "Vector store not available",
            "memories": [],
            "metadata": {}
        })

    try:
        results = []

        if collection in ["essence", "both"]:
            logger.info(f"Searching logos_essence collection for: {question}")
            essence_results = _vector_store.search("logos_essence", question, limit=limit if collection == "essence" else limit//2)
            results.extend([{
                "collection": "logos_essence",
                "text": result.payload.get("text", ""),
                "metadata": {k: v for k, v in result.payload.items() if k != "text"},
                "score": result.score
            } for result in essence_results])
            logger.info(f"Found {len(essence_results)} results in logos_essence")

        if collection in ["project", "both"]:
            logger.info(f"Searching project_knowledge collection for: {question}")
            project_results = _vector_store.search("project_knowledge", question, limit=limit if collection == "project" else limit//2)
            results.extend([{
                "collection": "project_knowledge",
                "text": result.payload.get("text", ""),
                "metadata": {k: v for k, v in result.payload.items() if k != "text"},
                "score": result.score
            } for result in project_results])
            logger.info(f"Found {len(project_results)} results in project_knowledge")

        # Sort by score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)
        logger.info(f"MCP API: get_memory_context completed - returned {len(results)} total memories")

        return json.dumps({
            "memories": results,
            "metadata": {
                "query": question,
                "collection": collection,
                "limit": limit,
                "results_count": len(results),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"MCP API: get_memory_context failed - {str(e)}")
        return json.dumps({
            "error": f"Memory search failed: {str(e)}",
            "memories": [],
            "metadata": {"query": question, "error": str(e)}
        })


@tool()
def get_collection_stats() -> str:
    """
    Get statistics about the memory collections.

    Returns:
        JSON string with collection statistics
    """
    logger.info("MCP API: get_collection_stats called")

    if not _vector_store:
        logger.warning("MCP API: get_collection_stats failed - vector store not available")
        return json.dumps({
            "error": "Vector store not available",
            "collections": {}
        })

    try:
        # This would need to be implemented in the vector store
        # For now, return basic info
        stats = {
            "collections": {
                "logos_essence": {"description": "Personality memories and letters"},
                "project_knowledge": {"description": "Project and technical knowledge"},
                "canon": {"description": "Manifesto and constitution storage"}
            },
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

        logger.info(f"MCP API: get_collection_stats completed - returned stats for {len(stats['collections'])} collections")
        return json.dumps(stats, indent=2)

    except Exception as e:
        logger.error(f"MCP API: get_collection_stats failed - {str(e)}")
        return json.dumps({
            "error": f"Failed to get collection stats: {str(e)}",
            "collections": {}
        })


@tool()
def get_version() -> str:
    """
    Get Logos version and system information.

    Returns:
        JSON string with version information including version number,
        author, description, and system details.
    """
    logger.info("MCP API: get_version called")

    try:
        version_info = {
            "version": logos.__version__,
            "author": logos.__author__,
            "description": logos.__description__,
            "url": logos.__url__,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": {
                "name": "Logos",
                "type": "Digital Memory Engine",
                "architecture": "MCP Server + Document Processing"
            }
        }

        logger.info(f"MCP API: get_version completed - returned version {logos.__version__}")
        return json.dumps(version_info, indent=2)

    except Exception as e:
        logger.error(f"MCP API: get_version failed - {str(e)}")
        return json.dumps({
            "error": f"Failed to get version information: {str(e)}",
            "version": "unknown"
        })