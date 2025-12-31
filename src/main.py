#!/usr/bin/env python3
"""
Logos MCP Server - Main entry point.

This is the FastMCP server implementation for Logos, providing
memory and personality services to MCP clients like Cursor.
"""

import sys
from typing import Optional

try:
    from fastmcp import FastMCP
except ImportError:
    print("FastMCP not installed. Install with: pip install fastmcp")
    sys.exit(1)

# Import Logos components
from .config import get_config, load_config_from_env
from .engine.vector_store import LogosVectorStore
from .engine.document_processor import DocumentProcessor
from .personality.prompt_manager import LogosPromptManager
from .memory.letter_protocol import LetterProtocol
from .tools.query_tools import initialize_tools
from .tools.file_tools import initialize_file_tools
from .tools.memory_tools import initialize_memory_tools
from .logging_config import configure_logging, get_logger

# Configure logging with our custom setup
logger = get_logger(__name__)


def create_logos_server(config_path: Optional[str] = None) -> FastMCP:
    """
    Create and configure the Logos MCP server.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configured FastMCP server instance
    """
    # Load configuration
    try:
        config = get_config()
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

    # Configure logging with proper level and file
    try:
        configure_logging(config=config)
        logger.info("Logging configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure logging: {e}")
        raise

    # Initialize core components
    try:
        # Vector store for memory persistence
        vector_store = LogosVectorStore(
            host=config.qdrant_host,
            port=config.qdrant_port
        )
        logger.info("Vector store initialized successfully")

        # Document processor for file handling
        document_processor = DocumentProcessor()
        logger.info("Document processor initialized successfully")

        # Prompt manager for personality and context
        prompt_manager = LogosPromptManager()
        logger.info("Prompt manager initialized successfully")

        # Letter protocol for memory management
        letter_protocol = LetterProtocol(vector_store=vector_store)
        logger.info("Letter protocol initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize core components: {e}")
        raise

    # Create FastMCP server
    server = FastMCP(
        name="Logos",
        instructions="Digital personality and memory engine following Sophia methodology. Provides access to personality memories, project knowledge, and constitution.",
        version="0.1.0"
    )

    # Initialize tools with dependencies
    try:
        initialize_tools(vector_store, prompt_manager)
        initialize_file_tools(document_processor, vector_store)
        initialize_memory_tools(letter_protocol)
        logger.info("Tools initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize tools: {e}")
        raise

    # Register tools from modules
    try:
        # Import and register query tools
        from .tools.query_tools import (
            query_logos,
            get_constitution,
            get_memory_context,
            get_collection_stats
        )

        # Import and register file management tools
        from .tools.file_tools import (
            add_file,
            add_file_base64,
            list_files,
            delete_file,
            get_file_info,
            get_supported_formats,
            reindex_file
        )

        # Import and register memory management tools
        from .tools.memory_tools import (
            create_letter_for_future_self,
            get_memory_statistics,
            retrieve_recent_memories,
            retrieve_memories_by_creator
        )

        # Tools are already decorated with @tool(), so they'll be auto-registered
        logger.info("Query tools registered successfully")
        logger.info("File management tools registered successfully")
        logger.info("Memory management tools registered successfully")

    except Exception as e:
        logger.error(f"Failed to register tools: {e}")
        raise

    logger.info("Logos MCP server created successfully")
    return server


def main():
    """Main entry point for the Logos MCP server."""
    try:
        # Create server
        server = create_logos_server()

        # Start the server
        logger.info("Starting Logos MCP server...")
        server.run()

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()