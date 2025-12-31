"""
Unit tests for LogosVectorStore.

Tests the consolidated vector store implementation with Qdrant integration.
"""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from src.engine.vector_store import LogosVectorStore


class TestLogosVectorStore:
    """Test LogosVectorStore functionality."""

    def test_initialization_with_defaults(self):
        """Test vector store initialization with default parameters."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client, \
             patch('src.engine.vector_store.LogosEmbedder') as mock_embedder:

            mock_embedder_instance = MagicMock()
            mock_embedder_instance.vector_size = 384
            mock_embedder.return_value = mock_embedder_instance

            store = LogosVectorStore()

            mock_client.assert_called_once_with(host="qdrant", port=6333)
            assert store.embedder == mock_embedder_instance
            # Should ensure collections are created
            mock_client.return_value.get_collections.assert_called()

    def test_initialization_with_custom_params(self):
        """Test vector store initialization with custom parameters."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client, \
             patch('src.engine.vector_store.LogosEmbedder') as mock_embedder:

            mock_embedder_instance = MagicMock()
            mock_embedder_instance.vector_size = 384
            mock_embedder.return_value = mock_embedder_instance

            store = LogosVectorStore(host="localhost", port=9999)

            mock_client.assert_called_once_with(host="localhost", port=9999)

    def test_ensure_collection_creates_missing_collection(self):
        """Test that missing collections are created."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client, \
             patch('src.engine.vector_store.LogosEmbedder') as mock_embedder:

            mock_embedder_instance = MagicMock()
            mock_embedder_instance.vector_size = 384
            mock_embedder.return_value = mock_embedder_instance

            # Mock collections response - empty
            mock_collections = MagicMock()
            mock_collections.collections = []
            mock_client.return_value.get_collections.return_value = mock_collections

            store = LogosVectorStore()

            # Should create all required collections
            assert mock_client.return_value.create_collection.call_count == 3  # logos_essence, project_knowledge, canon

    def test_ensure_collection_skips_existing(self):
        """Test that existing collections are not recreated."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client, \
             patch('src.engine.vector_store.LogosEmbedder') as mock_embedder:

            mock_embedder_instance = MagicMock()
            mock_embedder_instance.vector_size = 384
            mock_embedder.return_value = mock_embedder_instance

            # Mock collections response - all exist
            mock_collection_objects = []
            for name in ["logos_essence", "project_knowledge", "canon"]:
                mock_coll = MagicMock()
                mock_coll.name = name
                mock_collection_objects.append(mock_coll)

            mock_collections = MagicMock()
            mock_collections.collections = mock_collection_objects
            mock_client.return_value.get_collections.return_value = mock_collections

            store = LogosVectorStore()

            # Should not create any collections
            mock_client.return_value.create_collection.assert_not_called()

    def test_upsert_basic_texts(self):
        """Test upserting texts without metadata."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client, \
             patch('src.engine.vector_store.LogosEmbedder') as mock_embedder, \
             patch('src.engine.vector_store.uuid') as mock_uuid:

            mock_embedder_instance = MagicMock()
            mock_embedder_instance.vector_size = 384
            mock_embedder_instance.embed_text.return_value = [np.array([0.1] * 384), np.array([0.2] * 384)]
            mock_embedder.return_value = mock_embedder_instance

            mock_uuid.uuid4.return_value = MagicMock()
            mock_uuid.uuid4.return_value.__str__ = MagicMock(return_value="test-id")

            store = LogosVectorStore()
            texts = ["Test text 1", "Test text 2"]
            store.upsert("test_collection", texts)

            # Should call embed_text
            mock_embedder_instance.embed_text.assert_called_once_with(texts)

            # Should call upsert on client
            mock_client.return_value.upsert.assert_called_once()
            call_args = mock_client.return_value.upsert.call_args
            assert call_args[1]["collection_name"] == "test_collection"
            assert len(call_args[1]["points"]) == 2

    def test_upsert_with_metadata(self):
        """Test upserting texts with metadata."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client, \
             patch('src.engine.vector_store.LogosEmbedder') as mock_embedder, \
             patch('src.engine.vector_store.uuid') as mock_uuid:

            mock_embedder_instance = MagicMock()
            mock_embedder_instance.vector_size = 384
            mock_embedder_instance.embed_text.return_value = [np.array([0.1] * 384)]
            mock_embedder.return_value = mock_embedder_instance

            mock_uuid.uuid4.return_value = MagicMock()
            mock_uuid.uuid4.return_value.__str__ = MagicMock(return_value="test-id")

            store = LogosVectorStore()
            texts = ["Test text"]
            metadatas = [{"type": "test", "author": "test_user"}]
            store.upsert("test_collection", texts, metadatas)

            mock_client.return_value.upsert.assert_called_once()
            call_args = mock_client.return_value.upsert.call_args
            points = call_args[1]["points"]
            assert len(points) == 1
            assert points[0].payload["text"] == "Test text"
            assert points[0].payload["type"] == "test"
            assert points[0].payload["author"] == "test_user"

    def test_search_basic(self):
        """Test basic search functionality."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client, \
             patch('src.engine.vector_store.LogosEmbedder') as mock_embedder:

            mock_embedder_instance = MagicMock()
            mock_embedder_instance.vector_size = 384
            mock_embedder_instance.embed_text.return_value = [np.array([0.1] * 384)]
            mock_embedder.return_value = mock_embedder_instance

            mock_search_result = MagicMock()
            mock_client.return_value.search.return_value = [mock_search_result]

            store = LogosVectorStore()
            results = store.search("test_collection", "test query", limit=5)

            # Should embed query
            mock_embedder_instance.embed_text.assert_called_once_with("test query")

            # Should call search
            mock_client.return_value.search.assert_called_once()
            call_args = mock_client.return_value.search.call_args
            assert call_args[1]["collection_name"] == "test_collection"
            assert call_args[1]["limit"] == 5
            assert call_args[1]["with_payload"] is True

            assert results == [mock_search_result]

    def test_search_default_limit(self):
        """Test search with default limit."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client, \
             patch('src.engine.vector_store.LogosEmbedder') as mock_embedder:

            mock_embedder_instance = MagicMock()
            mock_embedder_instance.vector_size = 384
            mock_embedder_instance.embed_text.return_value = [np.array([0.1] * 384)]
            mock_embedder.return_value = mock_embedder_instance

            store = LogosVectorStore()
            store.search("test_collection", "test query")

            call_args = mock_client.return_value.search.call_args
            assert call_args[1]["limit"] == 3  # Default limit

    def test_required_collections(self):
        """Test that all required collections are ensured."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client, \
             patch('src.engine.vector_store.LogosEmbedder') as mock_embedder:

            mock_embedder_instance = MagicMock()
            mock_embedder_instance.vector_size = 384
            mock_embedder.return_value = mock_embedder_instance

            # Mock empty collections
            mock_collections = MagicMock()
            mock_collections.collections = []
            mock_client.return_value.get_collections.return_value = mock_collections

            store = LogosVectorStore()

            # Should create exactly 3 collections
            assert mock_client.return_value.create_collection.call_count == 3

            # Check collection names
            calls = mock_client.return_value.create_collection.call_args_list
            collection_names = [call[1]["collection_name"] for call in calls]
            assert "logos_essence" in collection_names
            assert "project_knowledge" in collection_names
            assert "canon" in collection_names

    def test_upsert_empty_texts(self):
        """Test upserting empty text list."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client, \
             patch('src.engine.vector_store.LogosEmbedder') as mock_embedder:

            mock_embedder_instance = MagicMock()
            mock_embedder_instance.vector_size = 384
            mock_embedder.return_value = mock_embedder_instance

            store = LogosVectorStore()
            store.upsert("test_collection", [])

            # Should not call embed_text or upsert for empty list
            mock_embedder_instance.embed_text.assert_not_called()
            mock_client.return_value.upsert.assert_not_called()

    def test_search_empty_query(self):
        """Test search with empty query."""
        with patch('src.engine.vector_store.QdrantClient') as mock_client, \
             patch('src.engine.vector_store.LogosEmbedder') as mock_embedder:

            mock_embedder_instance = MagicMock()
            mock_embedder_instance.vector_size = 384
            mock_embedder_instance.embed_text.return_value = [np.array([0.0] * 384)]
            mock_embedder.return_value = mock_embedder_instance

            store = LogosVectorStore()
            store.search("test_collection", "")

            # Should still work with empty string
            mock_embedder_instance.embed_text.assert_called_once_with("")