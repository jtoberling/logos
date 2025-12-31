"""
Logos Embedder - Text embedding interface using FastEmbed.

This module provides text embedding functionality for the vector store.
"""

import numpy as np
from typing import List, Union
from ..logging_config import get_logger

logger = get_logger(__name__)

try:
    from fastembed import TextEmbedding
    FASTEMBED_AVAILABLE = True
except ImportError:
    FASTEMBED_AVAILABLE = False
    # Mock for testing
    class TextEmbedding:
        def __init__(self, model_name=None) -> None:
            pass
        def embed(self, texts) -> list:
            # Return mock embeddings
            return [np.random.rand(384).astype(np.float32) for _ in texts]


class LogosEmbedder:
    """
    Text embedding interface for Logos.

    Uses FastEmbed for local text vectorization.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        """
        Initialize the embedder.

        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name

        if FASTEMBED_AVAILABLE:
            try:
                self.model = TextEmbedding(model_name=model_name)
                logger.info(f"Model {model_name} loaded successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize model {model_name}. Error: {e}")
                # Fallback to mock
                self.model = TextEmbedding()
        else:
            # Use mock for testing
            self.model = TextEmbedding()
            logger.info("Using mock embeddings (FastEmbed not available).")

    def embed_text(self, text: Union[str, List[str]]) -> List[np.ndarray]:
        """
        Embed text(s) into vectors.

        Args:
            text: Single text string or list of text strings

        Returns:
            List of numpy arrays containing embeddings
        """
        if isinstance(text, str):
            text = [text]

        # Use the embedding model
        embeddings_generator = self.model.embed(text)
        return list(embeddings_generator)

    @property
    def vector_size(self) -> int:
        """
        Get the dimension of the embedding vectors.

        Returns:
            Vector dimension (384 for bge-small-en-v1.5)
        """
        # Try to get actual vector size, fallback to known size
        try:
            dummy_vector = self.embed_text("test")
            return len(dummy_vector[0])
        except Exception:
            # Default size for bge-small-en-v1.5
            return 384