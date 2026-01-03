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
        logger.info(f"Connecting to Qdrant at {config.qdrant_host}:{config.qdrant_port}")

        # Test network connectivity to Qdrant
        import socket
        try:
            logger.info("Testing network connectivity to Qdrant...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10 second timeout
            result = sock.connect_ex((config.qdrant_host, config.qdrant_port))
            sock.close()

            if result != 0:
                logger.error(f"Cannot connect to Qdrant at {config.qdrant_host}:{config.qdrant_port} (connection refused)")
                logger.error("This usually means:")
                logger.error("  1) Qdrant service is not running")
                logger.error("  2) Network connectivity issues between services")
                logger.error("  3) Qdrant is still starting up (check health status)")
                raise ConnectionError(f"Qdrant service not reachable at {config.qdrant_host}:{config.qdrant_port}")
            else:
                logger.info("Network connectivity to Qdrant confirmed")
        except socket.gaierror as e:
            logger.error(f"DNS resolution failed for {config.qdrant_host}: {e}")
            logger.error("This usually means:")
            logger.error("  1) Services are not on the same Docker network")
            logger.error("  2) DNS resolution is not working")
            logger.error("  3) Hostname configuration issue")
            raise ConnectionError(f"Cannot resolve hostname {config.qdrant_host}: {e}")

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
    logger.info("Creating FastMCP server instance...")
    server = FastMCP(
        name="Logos",
        instructions="Digital personality and memory engine following Sophia methodology. Provides access to personality memories, project knowledge, and constitution.",
        version="0.1.0"
    )
    logger.info("FastMCP server instance created successfully")

    # Initialize tools with dependencies
    try:
        logger.info("Initializing MCP tools...")
        initialize_tools(vector_store, prompt_manager)
        initialize_file_tools(document_processor, vector_store)
        initialize_memory_tools(letter_protocol)
        logger.info("All MCP tools initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize tools: {e}")
        raise

    # Register tools from modules
    try:
        logger.info("Registering MCP tools with server...")

        # Import tool functions
        from .tools.query_tools import (
            query_logos,
            get_constitution,
            get_memory_context,
            get_collection_stats,
            get_version
        )

        from .tools.file_tools import (
            add_file,
            add_file_base64,
            list_files,
            delete_file,
            get_file_info,
            get_supported_formats,
            reindex_file
        )

        from .tools.memory_tools import (
            create_letter_for_future_self,
            get_memory_statistics,
            retrieve_recent_memories,
            retrieve_memories_by_creator
        )

        # Register query tools with the server using decorators
        server.tool()(query_logos)
        server.tool()(get_constitution)
        server.tool()(get_memory_context)
        server.tool()(get_collection_stats)
        server.tool()(get_version)

        # Register file management tools with the server using decorators
        server.tool()(add_file)
        server.tool()(add_file_base64)
        server.tool()(list_files)
        server.tool()(delete_file)
        server.tool()(get_file_info)
        server.tool()(get_supported_formats)
        server.tool()(reindex_file)

        # Register memory management tools with the server using decorators
        server.tool()(create_letter_for_future_self)
        server.tool()(get_memory_statistics)
        server.tool()(retrieve_recent_memories)
        server.tool()(retrieve_memories_by_creator)

        logger.info("Query tools registered: 5 (query_logos, get_constitution, get_memory_context, get_collection_stats, get_version)")
        logger.info("File management tools registered: 7 (add_file, add_file_base64, list_files, delete_file, get_file_info, get_supported_formats, reindex_file)")
        logger.info("Memory management tools registered: 4 (create_letter_for_future_self, get_memory_statistics, retrieve_recent_memories, retrieve_memories_by_creator)")
        logger.info("Total MCP tools registered: 16 tools across 3 categories")

    except Exception as e:
        logger.error(f"Failed to register tools: {e}")
        raise

    logger.info("Logos MCP server created successfully")
    return server


def main() -> None:
    """Main entry point for the Logos MCP server."""
    try:
        # Create server
        server = create_logos_server()

        # Start the server with HTTP transport for Docker deployment
        logger.info("Starting Logos MCP server...")
        config = get_config()

        logger.info(f"Server configuration: HTTP transport on {config.mcp_host}:{config.mcp_port}")
        logger.info("Initializing HTTP server with MCP protocol support...")

        # Start the server with HTTP transport for Docker deployment
        server.run(
            transport="http",
            host=config.mcp_host,
            port=config.mcp_port
        )

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()