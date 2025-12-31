"""
Unit tests for LogosEmbedder.

Tests the text embedding functionality using FastEmbed.
"""

import numpy as np
from unittest.mock import patch, MagicMock

from src.engine.embedder import LogosEmbedder


class TestLogosEmbedder:
    """Test LogosEmbedder functionality."""

    def test_initialization_with_fastembed_available(self):
        """Test embedder initialization when FastEmbed is available."""
        with patch('src.engine.embedder.FASTEMBED_AVAILABLE', True):
            with patch('src.engine.embedder.TextEmbedding') as mock_text_embedding:
                mock_model = MagicMock()
                mock_text_embedding.return_value = mock_model

                embedder = LogosEmbedder(model_name="test-model")

                assert embedder.model_name == "test-model"
                assert embedder.model == mock_model
                mock_text_embedding.assert_called_once_with(model_name="test-model")

    def test_initialization_fastembed_model_failure(self):
        """Test embedder initialization when FastEmbed model loading fails."""
        with patch('src.engine.embedder.FASTEMBED_AVAILABLE', True):
            with patch('src.engine.embedder.TextEmbedding') as mock_text_embedding:
                # First call (model init) raises exception
                mock_text_embedding.side_effect = [Exception("Model load failed"), MagicMock()]

                embedder = LogosEmbedder(model_name="test-model")

                assert embedder.model_name == "test-model"
                # Should have called TextEmbedding twice (once for real, once for fallback)
                assert mock_text_embedding.call_count == 2

    def test_initialization_without_fastembed(self):
        """Test embedder initialization when FastEmbed is not available."""
        with patch('src.engine.embedder.FASTEMBED_AVAILABLE', False):
            with patch('src.engine.embedder.TextEmbedding') as mock_text_embedding:
                mock_fallback = MagicMock()
                mock_text_embedding.return_value = mock_fallback

                embedder = LogosEmbedder(model_name="test-model")

                assert embedder.model_name == "test-model"
                assert embedder.model == mock_fallback
                # Should be called once for fallback mock
                mock_text_embedding.assert_called_once_with()

    def test_embed_text_single_string(self):
        """Test embed_text with a single string."""
        embedder = LogosEmbedder()
        mock_embeddings = [np.array([0.1, 0.2, 0.3]), np.array([0.4, 0.5, 0.6])]

        with patch.object(embedder.model, 'embed', return_value=iter(mock_embeddings)):
            result = embedder.embed_text("single text")

            assert len(result) == 2  # embed returns generator, we convert to list
            assert isinstance(result[0], np.ndarray)
            assert result[0].tolist() == [0.1, 0.2, 0.3]
            assert result[1].tolist() == [0.4, 0.5, 0.6]

    def test_embed_text_list_of_strings(self):
        """Test embed_text with a list of strings."""
        embedder = LogosEmbedder()
        mock_embeddings = [np.array([0.1, 0.2]), np.array([0.3, 0.4]), np.array([0.5, 0.6])]

        with patch.object(embedder.model, 'embed', return_value=iter(mock_embeddings)):
            texts = ["text1", "text2", "text3"]
            result = embedder.embed_text(texts)

            assert len(result) == 3
            assert isinstance(result[0], np.ndarray)
            assert result[0].tolist() == [0.1, 0.2]
            assert result[1].tolist() == [0.3, 0.4]
            assert result[2].tolist() == [0.5, 0.6]

            # Verify embed was called with the list directly
            embedder.model.embed.assert_called_once_with(texts)

    def test_vector_size_property_success(self):
        """Test vector_size property when embedding works."""
        embedder = LogosEmbedder()

        # Mock successful embedding
        mock_embedding = np.array([0.1] * 384)  # 384 dimensions
        with patch.object(embedder, 'embed_text', return_value=[mock_embedding]):
            vector_size = embedder.vector_size

            assert vector_size == 384
            embedder.embed_text.assert_called_once_with("test")

    def test_vector_size_property_failure(self):
        """Test vector_size property when embedding fails."""
        embedder = LogosEmbedder()

        # Mock failed embedding
        with patch.object(embedder, 'embed_text', side_effect=Exception("Embed failed")):
            vector_size = embedder.vector_size

            assert vector_size == 384  # Default fallback
            embedder.embed_text.assert_called_once_with("test")

    def test_default_model_name(self):
        """Test that default model name is used."""
        with patch('src.engine.embedder.FASTEMBED_AVAILABLE', False):
            embedder = LogosEmbedder()

            assert embedder.model_name == "BAAI/bge-small-en-v1.5"

    def test_custom_model_name(self):
        """Test custom model name initialization."""
        with patch('src.engine.embedder.FASTEMBED_AVAILABLE', False):
            embedder = LogosEmbedder(model_name="custom-model")

            assert embedder.model_name == "custom-model"