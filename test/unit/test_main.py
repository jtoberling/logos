"""
Unit tests for main.py - Logos MCP Server entry point.

Tests the server initialization, configuration, and error handling.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock, call

from src.main import create_logos_server, main

def test_main_module_imports():
    """Test that main module can be imported successfully."""
    # This exercises the import block in main.py including the FastMCP import error handling
    import src.main  # This should succeed in our environment

    # Verify the module has the expected functions
    assert hasattr(src.main, 'create_logos_server')
    assert hasattr(src.main, 'main')
    assert callable(src.main.create_logos_server)
    assert callable(src.main.main)


class TestMain:
    """Test main.py functionality."""



    @patch('src.main.get_config')
    def test_create_logos_server_config_failure(self, mock_get_config):
        """Test server creation when configuration fails."""
        mock_get_config.side_effect = Exception("Config error")

        with pytest.raises(Exception, match="Config error"):
            create_logos_server()

    @patch('src.main.configure_logging')
    @patch('src.main.get_config')
    @patch('src.main.LogosVectorStore')
    def test_create_logos_server_vector_store_failure(self, mock_vector_store, mock_get_config, mock_configure_logging):
        """Test server creation when vector store initialization fails."""
        mock_config = MagicMock()
        mock_get_config.return_value = mock_config
        mock_vector_store.side_effect = Exception("Vector store error")

        with pytest.raises(Exception, match="Vector store error"):
            create_logos_server()



    @patch('src.main.FastMCP')
    @patch('src.main.get_config')
    @patch('src.main.LogosVectorStore')
    @patch('src.main.LogosPromptManager')
    @patch('src.main.initialize_tools')
    def test_create_logos_server_tools_import_failure(self, mock_init_tools, mock_prompt_manager,
                                                       mock_vector_store, mock_get_config, mock_fastmcp):
        """Test server creation when tool imports fail."""
        # Setup successful initialization
        mock_config = MagicMock()
        mock_get_config.return_value = mock_config
        mock_vector_store.return_value = MagicMock()
        mock_prompt_manager.return_value = MagicMock()
        mock_fastmcp.return_value = MagicMock()
        mock_init_tools.return_value = None

        # Mock import failure
        with patch.dict('sys.modules', {'src.tools.query_tools': None}):
            with pytest.raises(Exception):
                # This should fail when trying to import query_tools
                create_logos_server()

    @patch('src.main.create_logos_server')
    @patch('src.main.logger')
    def test_main_success(self, mock_logger, mock_create_server):
        """Test successful main function execution."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server

        # Mock server.run() to avoid infinite loop
        with patch.object(mock_server, 'run', side_effect=KeyboardInterrupt()):
            main()

        mock_create_server.assert_called_once()
        mock_logger.info.assert_any_call("Starting Logos MCP server...")
        mock_logger.info.assert_any_call("Server shutdown requested by user")

    @patch('src.main.create_logos_server')
    @patch('src.main.logger')
    @patch('sys.exit')
    def test_main_server_creation_failure(self, mock_exit, mock_logger, mock_create_server):
        """Test main function when server creation fails."""
        mock_create_server.side_effect = Exception("Server creation failed")

        main()

        mock_create_server.assert_called_once()
        mock_logger.error.assert_called_once()
        mock_exit.assert_called_once_with(1)

    @patch('src.main.create_logos_server')
    @patch('src.main.logger')
    @patch('sys.exit')
    def test_main_server_run_failure(self, mock_exit, mock_logger, mock_create_server):
        """Test main function when server.run() fails."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server
        mock_server.run.side_effect = Exception("Server run failed")

        main()

        mock_create_server.assert_called_once()
        mock_server.run.assert_called_once()
        mock_logger.error.assert_called_once()
        mock_exit.assert_called_once_with(1)

    @patch('src.main.create_logos_server')
    @patch('src.main.logger')
    def test_main_keyboard_interrupt(self, mock_logger, mock_create_server):
        """Test main function with KeyboardInterrupt."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server
        mock_server.run.side_effect = KeyboardInterrupt()

        main()

        mock_create_server.assert_called_once()
        mock_logger.info.assert_any_call("Starting Logos MCP server...")
        mock_logger.info.assert_any_call("Server shutdown requested by user")
