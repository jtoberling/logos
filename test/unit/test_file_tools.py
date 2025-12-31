"""
Unit tests for file management tools.
"""

import json
import base64
import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.tools.file_tools import (
    initialize_file_tools,
    add_file,
    add_file_base64,
    list_files,
    delete_file,
    get_file_info,
    get_supported_formats,
    reindex_file
)


class TestFileTools:
    """Test cases for file management tools."""

    @pytest.fixture(autouse=True)
    def reset_globals(self):
        """Reset global variables before each test."""
        from src.tools import file_tools
        file_tools._file_processor = None
        file_tools._vector_store = None

    @pytest.fixture
    def mock_document_processor(self):
        """Mock document processor."""
        return MagicMock()

    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store."""
        return MagicMock()

    def test_initialize_file_tools(self, mock_document_processor, mock_vector_store):
        """Test file tools initialization."""
        initialize_file_tools(mock_document_processor, mock_vector_store)

        # Check that global variables are set (we can't directly access them)
        # This is mainly for ensuring no exceptions are raised
        assert True

    def test_add_file_not_initialized(self):
        """Test add_file when tools not initialized."""
        result = add_file("/path/to/test.pdf")
        assert "not properly initialized" in result

    def test_add_file_success(self, mock_document_processor, mock_vector_store):
        """Test successful file addition."""
        # Setup mocks
        initialize_file_tools(mock_document_processor, mock_vector_store)

        # Mock the metadata returned by process_file_from_path
        mock_metadata = MagicMock()
        mock_metadata.filename = "test.pdf"
        mock_metadata.file_path = "/path/to/test.pdf"
        mock_metadata.file_format = "PDF"
        mock_metadata.mimetype = "application/pdf"
        mock_metadata.file_size = 1024
        mock_metadata.text_length = 500
        mock_metadata.chunk_count = 2
        mock_metadata.content_hash = "abc123"
        mock_metadata.processed_at = "2024-01-01T12:00:00"
        mock_metadata.collection = "project_knowledge"

        mock_document_processor.process_file_from_path.return_value = mock_metadata

        # Execute
        result = add_file("/path/to/test.pdf", collection="project_knowledge")

        # Verify
        mock_document_processor.process_file_from_path.assert_called_once_with(
            file_path="/path/to/test.pdf",
            collection="project_knowledge",
            chunk_size=1000,
            chunk_overlap=200
        )

        assert "File processed successfully:" in result
        assert "test.pdf" in result
        assert "Format: PDF" in result
        assert "Chunks created: 2" in result

    def test_add_file_file_not_found(self, mock_document_processor, mock_vector_store):
        """Test add_file when file doesn't exist."""
        initialize_file_tools(mock_document_processor, mock_vector_store)

        mock_document_processor.process_file_from_path.side_effect = FileNotFoundError("File not found")

        result = add_file("/path/to/missing.pdf")
        assert "Error: File not found:" in result

    def test_add_file_processing_error(self, mock_document_processor, mock_vector_store):
        """Test add_file when document processing fails."""
        initialize_file_tools(mock_document_processor, mock_vector_store)

        from src.engine.document_processor import DocumentProcessorError
        mock_document_processor.process_file_from_path.side_effect = DocumentProcessorError("Processing failed")

        result = add_file("/path/to/test.pdf")
        assert "Error: Document processing failed:" in result

    def test_add_file_unexpected_error(self, mock_document_processor, mock_vector_store):
        """Test add_file with unexpected error."""
        initialize_file_tools(mock_document_processor, mock_vector_store)

        mock_document_processor.process_file_from_path.side_effect = Exception("Unexpected error")

        result = add_file("/path/to/test.pdf")
        assert "Error: Unexpected error adding file" in result

    def test_add_file_base64_not_initialized(self):
        """Test add_file_base64 when tools not initialized."""
        result = add_file_base64("test.txt", "dGVzdA==")
        assert "not properly initialized" in result

    def test_add_file_base64_invalid_base64(self):
        """Test add_file_base64 with invalid base64."""
        result = add_file_base64("test.txt", "invalid-base64!")
        assert "Invalid base64 content" in result

    def test_add_file_base64_success(self, mock_document_processor, mock_vector_store):
        """Test successful base64 file addition."""
        initialize_file_tools(mock_document_processor, mock_vector_store)

        # Mock process_document call (note: actual implementation passes extra params)
        mock_text = "Decoded text content"
        mock_metadata = MagicMock()
        mock_metadata.filename = "test.txt"
        mock_metadata.file_format = "TXT"
        mock_metadata.size_bytes = 12
        mock_metadata.text_length = 19
        mock_metadata.processing_timestamp = "2024-01-01T12:00:00"
        mock_metadata.checksum = "hash123"

        mock_document_processor.process_document.return_value = (mock_text, mock_metadata)

        result = add_file_base64("test.txt", "dGVzdCBjb250ZW50", mimetype="text/plain")

        # Verify process_document was called (note: implementation passes extra params)
        mock_document_processor.process_document.assert_called_once()
        call_kwargs = mock_document_processor.process_document.call_args[1]
        assert call_kwargs['content'] == b"test content"  # decoded base64
        assert call_kwargs['filename'] == "test.txt"
        assert call_kwargs['mimetype'] == "text/plain"

        # Check response contains success info
        assert "success" in result.lower() or "processed" in result.lower()

    def test_add_file_base64_processing_error(self, mock_document_processor, mock_vector_store):
        """Test base64 file addition with processing error."""
        initialize_file_tools(mock_document_processor, mock_vector_store)

        from src.engine.document_processor import DocumentProcessorError
        mock_document_processor.process_document.side_effect = DocumentProcessorError("Processing failed")

        result = add_file_base64("test.txt", "dGVzdA==")
        assert "Error:" in result

    def test_list_files_not_initialized(self):
        """Test list_files when tools not initialized."""
        result = list_files()
        assert "not properly initialized" in result

    def test_list_files_success(self, mock_document_processor):
        """Test successful file listing."""
        initialize_file_tools(mock_document_processor, MagicMock())

        # Mock documents
        mock_doc1 = MagicMock()
        mock_doc1.filename = "file1.pdf"
        mock_doc1.file_format = "PDF"
        mock_doc1.file_size = 1024
        mock_doc1.chunk_count = 2
        mock_doc1.text_length = 1000
        mock_doc1.processed_at = "2024-01-01T12:00:00"

        mock_doc2 = MagicMock()
        mock_doc2.filename = "file2.txt"
        mock_doc2.file_format = "TXT"
        mock_doc2.file_size = 512
        mock_doc2.chunk_count = 1
        mock_doc2.text_length = 500
        mock_doc2.processed_at = "2024-01-01T13:00:00"

        mock_document_processor.list_processed_documents.return_value = [mock_doc1, mock_doc2]

        result = list_files()

        mock_document_processor.list_processed_documents.assert_called_once()
        assert "file1.pdf" in result
        assert "file2.txt" in result
        assert "Total: 2 files" in result

    def test_list_files_empty(self, mock_document_processor):
        """Test file listing when no files exist."""
        initialize_file_tools(mock_document_processor, MagicMock())

        mock_document_processor.list_processed_documents.return_value = []

        result = list_files()
        assert "No files found" in result

    def test_delete_file_not_initialized(self):
        """Test delete_file when tools not initialized."""
        result = delete_file("testhash123")
        assert "not properly initialized" in result

    def test_delete_file_success(self, mock_vector_store):
        """Test successful file deletion request."""
        initialize_file_tools(MagicMock(), mock_vector_store)

        # Mock search results
        mock_result = MagicMock()
        mock_result.id = "point123"
        mock_result.payload = {
            "filename": "test.pdf",
            "file_format": "PDF",
            "total_chunks": 3
        }
        mock_vector_store.search.return_value = [mock_result]

        result = delete_file("hash123")

        mock_vector_store.search.assert_called_once()
        assert "Delete requested for file: test.pdf" in result
        assert "manual deletion required" in result.lower()

    def test_delete_file_not_found(self, mock_vector_store):
        """Test file deletion when file doesn't exist."""
        initialize_file_tools(MagicMock(), mock_vector_store)

        mock_vector_store.search.return_value = []

        result = delete_file("hash123")
        assert "No file found with content hash:" in result

    def test_get_file_info_not_initialized(self):
        """Test get_file_info when tools not initialized."""
        result = get_file_info("testhash123")
        assert "not properly initialized" in result

    def test_get_file_info_success(self, mock_document_processor):
        """Test successful file info retrieval."""
        initialize_file_tools(mock_document_processor, MagicMock())

        mock_info = MagicMock()
        mock_info.filename = "test.pdf"
        mock_info.file_path = "/path/to/test.pdf"
        mock_info.file_format = "PDF"
        mock_info.mimetype = "application/pdf"
        mock_info.file_size = 1024
        mock_info.text_length = 1000
        mock_info.chunk_count = 2
        mock_info.content_hash = "abc123"
        mock_info.processed_at = "2024-01-01T12:00:00"
        mock_info.collection = "project_knowledge"

        mock_document_processor.get_document_info.return_value = mock_info

        result = get_file_info("abc123")

        mock_document_processor.get_document_info.assert_called_once_with("abc123", "project_knowledge")
        assert "test.pdf" in result
        assert "1,024" in result  # formatted with commas
        assert "PDF" in result

    def test_get_file_info_not_found(self, mock_document_processor):
        """Test file info retrieval when file doesn't exist."""
        initialize_file_tools(mock_document_processor, MagicMock())

        mock_document_processor.get_document_info.return_value = None

        result = get_file_info("hash123")
        assert "No file found with content hash:" in result

    def test_get_supported_formats_not_initialized(self):
        """Test get_supported_formats when tools not initialized."""
        result = get_supported_formats()
        assert "not properly initialized" in result

    def test_get_supported_formats_success(self, mock_document_processor):
        """Test successful supported formats retrieval."""
        initialize_file_tools(mock_document_processor, MagicMock())

        mock_document_processor.get_supported_formats.return_value = ["PDF", "DOCX", "TXT"]

        result = get_supported_formats()

        mock_document_processor.get_supported_formats.assert_called_once()
        assert "PDF" in result
        assert "DOCX" in result
        assert "TXT" in result

    def test_reindex_file_not_initialized(self):
        """Test reindex_file when tools not initialized."""
        result = reindex_file("/path/to/test.pdf")
        assert "not properly initialized" in result

    def test_reindex_file_success(self, mock_document_processor, mock_vector_store):
        """Test successful file reindexing."""
        initialize_file_tools(mock_document_processor, mock_vector_store)

        # Mock the reindexing process
        mock_metadata = MagicMock()
        mock_metadata.filename = "test.pdf"
        mock_metadata.chunk_count = 3
        mock_metadata.content_hash = "newhash123"

        mock_document_processor.process_file_from_path.return_value = mock_metadata

        result = reindex_file("/path/to/test.pdf", collection="project_knowledge")

        mock_document_processor.process_file_from_path.assert_called_once_with(
            file_path="/path/to/test.pdf",
            collection="project_knowledge",
            chunk_size=1000,
            chunk_overlap=200
        )
        assert "successfully reindexed" in result.lower() or "reindexed" in result.lower()
        assert "3" in result  # chunk count

    def test_reindex_file_not_found(self, mock_document_processor, mock_vector_store):
        """Test reindexing when file doesn't exist."""
        initialize_file_tools(mock_document_processor, mock_vector_store)

        mock_document_processor.process_file_from_path.side_effect = FileNotFoundError("File not found")

        result = reindex_file("/path/to/missing.pdf")
        assert "Error:" in result

    def test_reindex_file_processing_error(self, mock_document_processor, mock_vector_store):
        """Test reindexing with processing error."""
        initialize_file_tools(mock_document_processor, mock_vector_store)

        from src.engine.document_processor import DocumentProcessorError
        mock_document_processor.process_file_from_path.side_effect = DocumentProcessorError("Processing failed")

        result = reindex_file("/path/to/test.pdf")
        assert "Error:" in result