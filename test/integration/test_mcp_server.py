"""
Integration tests for Logos MCP server.

Tests the full MCP server functionality with mocked dependencies.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.main import create_logos_server


class TestMCPIntegration:
    """Integration tests for MCP server functionality."""

    @patch('src.main.LogosVectorStore')
    @patch('src.main.LogosPromptManager')
    @patch('src.main.get_config')
    def test_server_creation_with_mocked_dependencies(self, mock_get_config, mock_prompt_manager, mock_vector_store):
        """Test that MCP server can be created with all mocked dependencies."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.qdrant_host = "localhost"
        mock_config.qdrant_port = 6333
        mock_get_config.return_value = mock_config

        mock_vector_store_instance = MagicMock()
        mock_vector_store.return_value = mock_vector_store_instance

        mock_prompt_manager_instance = MagicMock()
        mock_prompt_manager.return_value = mock_prompt_manager_instance

        # Create server
        server = create_logos_server()

        # Verify components were initialized
        mock_vector_store.assert_called_once_with(host="localhost", port=6333)
        mock_prompt_manager.assert_called_once()

        # Verify tools were initialized
        # This would need to be checked differently since initialize_tools modifies globals
        assert server is not None

    @patch('src.main.LogosVectorStore')
    @patch('src.main.LogosPromptManager')
    @patch('src.main.get_config')
    def test_server_creation_failure_handling(self, mock_get_config, mock_prompt_manager, mock_vector_store):
        """Test that server creation handles failures gracefully."""
        # Setup config mock with proper string values
        mock_config = MagicMock()
        mock_config.qdrant_host = "localhost"
        mock_config.qdrant_port = 6333
        mock_get_config.return_value = mock_config

        # Make vector store fail
        mock_vector_store.side_effect = Exception("Qdrant connection failed")

        # Test that exception is raised
        with pytest.raises(Exception, match="Qdrant connection failed"):
            create_logos_server()

    @patch('src.main.LogosVectorStore')
    @patch('src.main.LogosPromptManager')
    @patch('src.main.get_config')
    @patch('src.main.initialize_tools')
    def test_tools_initialization(self, mock_initialize_tools, mock_get_config, mock_prompt_manager, mock_vector_store):
        """Test that tools are properly initialized with dependencies."""
        # Setup mocks with proper string values
        mock_config = MagicMock()
        mock_config.qdrant_host = "localhost"
        mock_config.qdrant_port = 6333
        mock_get_config.return_value = mock_config

        mock_vector_store_instance = MagicMock()
        mock_vector_store.return_value = mock_vector_store_instance

        mock_prompt_manager_instance = MagicMock()
        mock_prompt_manager.return_value = mock_prompt_manager_instance

        # Create server
        server = create_logos_server()

        # Verify tools initialization was called
        mock_initialize_tools.assert_called_once_with(
            mock_vector_store_instance,
            mock_prompt_manager_instance
        )

    @patch('src.main.LogosVectorStore')
    @patch('src.main.LogosPromptManager')
    @patch('src.main.get_config')
    def test_config_validation_in_server_creation(self, mock_get_config, mock_prompt_manager, mock_vector_store):
        """Test that configuration validation occurs during server creation."""
        # Setup mocks with proper string values
        mock_config = MagicMock()
        mock_config.qdrant_host = "localhost"
        mock_config.qdrant_port = 6333
        mock_get_config.return_value = mock_config

        mock_vector_store_instance = MagicMock()
        mock_vector_store.return_value = mock_vector_store_instance

        mock_prompt_manager_instance = MagicMock()
        mock_prompt_manager.return_value = mock_prompt_manager_instance

        # Create server
        server = create_logos_server()

        # Verify get_config was called
        mock_get_config.assert_called_once()

        # Verify components received config values
        mock_vector_store.assert_called_once_with(
            host=mock_config.qdrant_host,
            port=mock_config.qdrant_port
        )