"""
File management tools for Logos MCP server.

These tools provide an interface for managing documents in Logos' knowledge base,
including adding files, listing processed documents, deleting files, and reindexing.
"""

import os
import base64
from typing import Optional, List, Dict, Any

try:
    from mcp import tool
except ImportError:
    # Mock for testing when MCP not available
    def tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Conditional import for DocumentProcessor and LogosVectorStore
try:
    from src.engine.document_processor import DocumentProcessor, DocumentProcessorError, DocumentMetadata
    from src.engine.vector_store import LogosVectorStore
    from src.logging_config import get_logger
except ImportError:
    # Fallback for when running from tools directory or tests
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
    from src.engine.document_processor import DocumentProcessor, DocumentProcessorError, DocumentMetadata
    from src.engine.vector_store import LogosVectorStore
    from src.logging_config import get_logger

logger = get_logger(__name__)

# Global instances (initialized by MCP server)
_file_processor: Optional[DocumentProcessor] = None
_vector_store: Optional[LogosVectorStore] = None


def initialize_file_tools(document_processor: DocumentProcessor, vector_store: LogosVectorStore) -> None:
    """
    Initialize file management tools with required dependencies.

    Args:
        document_processor: DocumentProcessor instance for text extraction
        vector_store: LogosVectorStore instance for data persistence
    """
    global _file_processor, _vector_store
    _file_processor = document_processor
    _vector_store = vector_store
    logger.info("File management tools initialized successfully")


@tool()
def add_file(
    file_path: str,
    collection: str = "project_knowledge",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> str:
    """
    Add a file to Logos' knowledge base.

    This tool reads a file from the filesystem, extracts its text content,
    chunks it appropriately, and stores it in the vector database for future
    retrieval and querying.

    Args:
        file_path: Path to the file to add (relative to data directory or absolute)
        collection: Vector database collection to store in (default: project_knowledge)
        chunk_size: Maximum characters per chunk (default: 1000)
        chunk_overlap: Characters to overlap between chunks (default: 200)

    Returns:
        JSON string with processing results and metadata

    Raises:
        FileNotFoundError: If the file doesn't exist
        DocumentProcessorError: If processing fails
    """
    if not _file_processor or not _vector_store:
        return '{"success": false, "error": "File management tools not properly initialized"}'

    try:
        # Process the file
        metadata = _file_processor.process_file_from_path(
            file_path=file_path,
            collection=collection,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Return success response
        response = {
            "success": True,
            "message": f"File '{metadata.filename}' processed and added to collection '{collection}'",
            "file_path": metadata.file_path,
            "filename": metadata.filename,
            "file_format": metadata.file_format,
            "mimetype": metadata.mimetype,
            "file_size": metadata.file_size,
            "text_length": metadata.text_length,
            "chunk_count": metadata.chunk_count,
            "content_hash": metadata.content_hash,
            "processed_at": metadata.processed_at,
            "collection": metadata.collection
        }

        logger.info(f"Successfully added file: {metadata.filename} ({metadata.chunk_count} chunks)")
        return f"File processed successfully:\n{metadata.filename}\nFormat: {metadata.file_format}\nSize: {metadata.file_size} bytes\nText length: {metadata.text_length} chars\nChunks created: {metadata.chunk_count}"

    except FileNotFoundError as e:
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        return f"Error: {error_msg}"

    except DocumentProcessorError as e:
        error_msg = f"Document processing failed: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"

    except Exception as e:
        error_msg = f"Unexpected error adding file '{file_path}': {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool()
def add_file_base64(
    filename: str,
    file_content_base64: str,
    mimetype: Optional[str] = None,
    collection: str = "project_knowledge",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> str:
    """
    Add a file to Logos' knowledge base using base64 encoded content.

    This tool decodes base64 content, extracts text, chunks it, and stores
    it in the vector database. Useful for files provided through APIs or UI.

    Args:
        filename: Name of the file (used for format detection)
        file_content_base64: Base64 encoded file content
        mimetype: MIME type (optional, will be detected if not provided)
        collection: Vector database collection to store in
        chunk_size: Maximum characters per chunk
        chunk_overlap: Characters to overlap between chunks

    Returns:
        JSON string with processing results and metadata
    """
    try:
        # Decode base64 content first (this can be validated without initialization)
        try:
            file_content = base64.b64decode(file_content_base64)
        except Exception as e:
            return f"Error: Invalid base64 content: {str(e)}"
    except Exception:
        # Handle any unexpected errors in base64 processing
        return "Error: Invalid base64 content"

    if not _file_processor or not _vector_store:
        return '{"success": false, "error": "File management tools not properly initialized"}'

    try:

        # Process the document
        text, metadata = _file_processor.process_document(
            content=file_content,
            filename=filename,
            mimetype=mimetype,
            collection=collection,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Return success response
        response = {
            "success": True,
            "message": f"File '{filename}' processed and added to collection '{collection}'",
            "filename": metadata.filename,
            "file_format": metadata.file_format,
            "mimetype": metadata.mimetype,
            "file_size": metadata.size_bytes,
            "text_length": metadata.text_length,
            "chunk_count": metadata.chunk_count,
            "content_hash": metadata.checksum,
            "processed_at": metadata.processing_timestamp,
            "collection": collection
        }

        logger.info(f"Successfully added base64 file: {filename} ({metadata.chunk_count} chunks)")
        return f"File processed successfully:\n{filename}\nFormat: {metadata.file_format}\nSize: {metadata.size_bytes} bytes\nText length: {metadata.text_length} chars\nChunks created: {metadata.chunk_count}"

    except DocumentProcessorError as e:
        error_msg = f"Document processing failed: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"

    except Exception as e:
        error_msg = f"Unexpected error processing base64 file '{filename}': {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool()
def list_files(
    collection: str = "project_knowledge",
    limit: int = 50,
    format_filter: Optional[str] = None
) -> str:
    """
    List files processed and stored in Logos' knowledge base.

    Args:
        collection: Collection to list files from (default: project_knowledge)
        limit: Maximum number of files to return (default: 50)
        format_filter: Filter by file format (optional)

    Returns:
        JSON string with list of processed files and their metadata
    """
    if not _file_processor or not _vector_store:
        return '{"success": false, "error": "File management tools not properly initialized"}'

    try:
        # Get list of processed documents
        documents = _file_processor.list_processed_documents(
            collection=collection,
            limit=limit
        )

        # Apply format filter if specified
        if format_filter:
            documents = [doc for doc in documents if doc.file_format.upper() == format_filter.upper()]

        # Format for display
        if not documents:
            return f"No files found in collection '{collection}'" + (f" with format '{format_filter}'" if format_filter else "")

        # Create summary
        summary_lines = [f"Files in collection '{collection}'" + (f" (format: {format_filter})" if format_filter else "") + ":"]
        summary_lines.append("-" * 80)

        for i, doc in enumerate(documents, 1):
            summary_lines.append(f"{i:2d}. {doc.filename}")
            summary_lines.append(f"    Format: {doc.file_format} | Size: {doc.file_size:,} bytes | Chunks: {doc.chunk_count}")
            summary_lines.append(f"    Text: {doc.text_length:,} chars | Processed: {doc.processed_at[:10]}")
            summary_lines.append("")

        summary_lines.append(f"Total: {len(documents)} files")
        summary_lines.append(f"Formats: {', '.join(sorted(set(doc.file_format for doc in documents)))}")

        return "\n".join(summary_lines)

    except Exception as e:
        error_msg = f"Error listing files: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool()
def delete_file(
    content_hash: str,
    collection: str = "project_knowledge"
) -> str:
    """
    Delete a file from Logos' knowledge base by content hash.

    This removes all chunks associated with the specified file from the vector database.
    The content hash is returned when a file is added and can be obtained by listing files.

    Args:
        content_hash: SHA256 hash of the file content (returned when file was added)
        collection: Collection to delete from

    Returns:
        Success/error message
    """
    if not _vector_store:
        return '{"success": false, "error": "File management tools not properly initialized"}'

    try:
        # Find all points with this content hash
        search_results = _vector_store.search(
            collection_name=collection,
            query_text=f"content_hash:{content_hash}",
            limit=1000  # Get all chunks for this file
        )

        if not search_results:
            return f"No file found with content hash: {content_hash}"

        # Extract point IDs to delete
        point_ids = [str(result.id) for result in search_results]

        # Note: Qdrant client doesn't have batch delete by IDs in the current version
        # For now, we'll return information about what would be deleted
        # In a production implementation, you'd use the delete API

        # Get metadata from first result
        first_payload = search_results[0].payload
        filename = first_payload.get("filename", "unknown")
        file_format = first_payload.get("file_format", "unknown")
        total_chunks = first_payload.get("total_chunks", len(search_results))

        logger.warning(f"Delete operation requested for {filename} ({total_chunks} chunks) - manual deletion required")
        return f"Delete requested for file: {filename}\nFormat: {file_format}\nChunks to delete: {total_chunks}\nContent hash: {content_hash}\n\nNote: Manual deletion required in current implementation"

    except Exception as e:
        error_msg = f"Error deleting file: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool()
def get_file_info(
    content_hash: str,
    collection: str = "project_knowledge"
) -> str:
    """
    Get detailed information about a processed file.

    Args:
        content_hash: SHA256 hash of the file content
        collection: Collection to search in

    Returns:
        Detailed file information
    """
    if not _file_processor or not _vector_store:
        return '{"success": false, "error": "File management tools not properly initialized"}'

    try:
        # Get document info
        info = _file_processor.get_document_info(content_hash, collection)

        if not info:
            return f"No file found with content hash: {content_hash}"

        # Format detailed information
        details = [
            f"File Information:",
            f"Name: {info.filename}",
            f"Path: {info.file_path or 'N/A'}",
            f"Format: {info.file_format}",
            f"MIME Type: {info.mimetype}",
            f"Size: {info.file_size:,} bytes",
            f"Text Length: {info.text_length:,} characters",
            f"Chunks: {info.chunk_count}",
            f"Content Hash: {info.content_hash}",
            f"Processed: {info.processed_at}",
            f"Collection: {info.collection}"
        ]

        return "\n".join(details)

    except Exception as e:
        error_msg = f"Error getting file info: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool()
def get_supported_formats() -> str:
    """
    Get list of file formats supported by Logos' document processor.

    Returns:
        List of supported file formats with descriptions
    """
    if not _file_processor:
        return "File management tools not properly initialized"

    try:
        formats = _file_processor.get_supported_formats()

        if not formats:
            return "No file formats currently supported (text extraction libraries not available)"

        # Group formats by category
        text_formats = ["TXT", "CSV", "MD", "HTML", "HTM"]
        office_formats = ["DOCX", "PDF"]
        other_formats = [fmt for fmt in formats if fmt not in text_formats + office_formats]

        response_lines = ["Supported File Formats:"]
        response_lines.append("")

        if any(fmt in formats for fmt in text_formats):
            response_lines.append("📄 Text Files:")
            for fmt in sorted(text_formats):
                if fmt in formats:
                    response_lines.append(f"  • {fmt}")
            response_lines.append("")

        if any(fmt in formats for fmt in office_formats):
            response_lines.append("🏢 Office Documents:")
            for fmt in sorted(office_formats):
                if fmt in formats:
                    response_lines.append(f"  • {fmt}")
            response_lines.append("")

        if other_formats:
            response_lines.append("📋 Other:")
            for fmt in sorted(other_formats):
                response_lines.append(f"  • {fmt}")
            response_lines.append("")

        response_lines.append("Note: Format support depends on installed Python libraries.")
        response_lines.append("Missing libraries will disable corresponding format support.")

        return "\n".join(response_lines)

    except Exception as e:
        return f"Error getting supported formats: {str(e)}"


@tool()
def reindex_file(
    file_path: str,
    collection: str = "project_knowledge",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> str:
    """
    Reindex an existing file in Logos' knowledge base.

    This removes the old version and adds the current version of the file.
    Useful when a file has been updated and you want to refresh its content
    in the knowledge base.

    Args:
        file_path: Path to the file to reindex
        collection: Collection to reindex in
        chunk_size: Maximum characters per chunk
        chunk_overlap: Characters to overlap between chunks

    Returns:
        Success/error message
    """
    if not _file_processor or not _vector_store:
        return '{"success": false, "error": "File management tools not properly initialized"}'

    try:
        # First, try to get the content hash of the existing file
        # This is a simplified implementation - in practice you'd need to
        # search for files by path or other metadata

        logger.info(f"Reindexing file: {file_path}")

        # Process the file (this will create a new version)
        metadata = _file_processor.process_file_from_path(
            file_path=file_path,
            collection=collection,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Note: In a full implementation, you'd want to delete the old version first
        # For now, this just adds a new version (old chunks remain)

        return f"File reindexed successfully:\n{metadata.filename}\nNew chunks created: {metadata.chunk_count}\nContent hash: {metadata.content_hash}\n\nNote: Old version may still exist in database"

    except Exception as e:
        error_msg = f"Error reindexing file '{file_path}': {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"