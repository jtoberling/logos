"""
Additional unit tests for LogosVectorStore missing coverage.

Tests the uncovered lines in vector_store.py.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.engine.vector_store import LogosVectorStore


class TestLogosVectorStoreMissingCoverage:
    """Test missing coverage in LogosVectorStore."""

    def test_delete_points(self):
        """Test delete_points method."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            with patch('src.engine.vector_store.LogosEmbedder'):
                store = LogosVectorStore()

                point_ids = ["point1", "point2", "point3"]
                store.delete_points("test_collection", point_ids)

                mock_client.delete.assert_called_once_with(
                    collection_name="test_collection",
                    points=point_ids
                )

    def test_get_collection_info_success(self):
        """Test get_collection_info method success case."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            with patch('src.engine.vector_store.LogosEmbedder'):
                store = LogosVectorStore()

                # Mock successful collection info
                mock_info = MagicMock()
                mock_info.vectors_count = 100
                mock_info.points_count = 150
                mock_client.get_collection.return_value = mock_info

                result = store.get_collection_info("test_collection")

                expected = {
                    "name": "test_collection",
                    "vectors_count": 100,
                    "points_count": 150,
                    "status": "exists"
                }
                assert result == expected
                mock_client.get_collection.assert_called_once_with("test_collection")

    def test_get_collection_info_error(self):
        """Test get_collection_info method error case."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            with patch('src.engine.vector_store.LogosEmbedder'):
                store = LogosVectorStore()

                # Mock exception
                mock_client.get_collection.side_effect = Exception("Collection not found")

                result = store.get_collection_info("test_collection")

                expected = {
                    "name": "test_collection",
                    "status": "error",
                    "error": "Collection not found"
                }
                assert result == expected

    def test_list_collections(self):
        """Test list_collections method."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            with patch('src.engine.vector_store.LogosEmbedder'):
                # Mock collections response for both initialization and test
                mock_collections_response = MagicMock()
                mock_collections_response.collections = []  # Empty for initialization
                mock_client.get_collections.return_value = mock_collections_response

                store = LogosVectorStore()

                # Now set up mock for the actual test
                mock_collection1 = MagicMock()
                mock_collection1.name = "logos_essence"
                mock_collection2 = MagicMock()
                mock_collection2.name = "project_knowledge"
                mock_collections_response.collections = [mock_collection1, mock_collection2]

                result = store.list_collections()

                assert result == ["logos_essence", "project_knowledge"]
                # get_collections is called twice: once during init, once during test
                assert mock_client.get_collections.call_count == 2

    def test_clear_collection(self):
        """Test clear_collection method."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            with patch('src.engine.vector_store.LogosEmbedder'):
                store = LogosVectorStore()

                store.clear_collection("test_collection")

                # Should delete with empty filter (matches all points)
                mock_client.delete.assert_called_once()
                call_args = mock_client.delete.call_args
                assert call_args[1]["collection_name"] == "test_collection"
                assert "points" in call_args[1]