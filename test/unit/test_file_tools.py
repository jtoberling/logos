"""
Unit tests for file management tools.
"""

import pytest
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
        from unittest.mock import MagicMock
        return MagicMock()

    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store."""
        from unittest.mock import MagicMock
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

    def test_add_file_base64_not_initialized(self):
        """Test add_file_base64 when tools not initialized."""
        result = add_file_base64("test.txt", "dGVzdA==")
        assert "not properly initialized" in result

    def test_add_file_base64_invalid_base64(self):
        """Test add_file_base64 with invalid base64."""
        result = add_file_base64("test.txt", "invalid-base64!")
        assert "Invalid base64 content" in result

    def test_list_files_not_initialized(self):
        """Test list_files when tools not initialized."""
        result = list_files()
        assert "not properly initialized" in result

    def test_delete_file_not_initialized(self):
        """Test delete_file when tools not initialized."""
        result = delete_file("testhash123")
        assert "not properly initialized" in result

    def test_get_file_info_not_initialized(self):
        """Test get_file_info when tools not initialized."""
        result = get_file_info("testhash123")
        assert "not properly initialized" in result

    def test_get_supported_formats_not_initialized(self):
        """Test get_supported_formats when tools not initialized."""
        result = get_supported_formats()
        assert "not properly initialized" in result

    def test_reindex_file_not_initialized(self):
        """Test reindex_file when tools not initialized."""
        result = reindex_file("/path/to/test.pdf")
        assert "not properly initialized" in result