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

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        """
        Initialize the embedder.

        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name

        if FASTEMBED_AVAILABLE:
            try:
                # Ensure cache directory exists and has proper permissions
                import os
                cache_dir = os.environ.get('FASTEMBED_CACHE_DIR', '/app/cache/fastembed')
                try:
                    os.makedirs(cache_dir, exist_ok=True)

                    # Ensure we can write to the cache directory
                    test_file = os.path.join(cache_dir, '.test_write')
                    try:
                        with open(test_file, 'w') as f:
                            f.write('test')
                        os.remove(test_file)
                        logger.info(f"Using FastEmbed cache directory: {cache_dir}")
                    except (OSError, PermissionError) as e:
                        logger.warning(f"Cannot write to cache directory {cache_dir}: {e}")
                        logger.warning("Model caching may not work properly")
                except (OSError, PermissionError) as e:
                    logger.warning(f"Cannot create cache directory {cache_dir}: {e}")
                    logger.warning("Model caching may not work properly")

                logger.info(f"Initializing embedding model {model_name}...")
                logger.info("Note: First startup may take several minutes to download the model (~100MB)")
                logger.info("Subsequent startups will be much faster using the cached model")

                # Time the model loading for better user feedback
                import time
                start_time = time.time()

                self.model = TextEmbedding(model_name=model_name)

                load_time = time.time() - start_time
                if load_time > 10:  # Log timing for operations that took more than 10 seconds
                    logger.info(".1f")
                else:
                    logger.info(f"Model {model_name} loaded successfully from cache.")

            except Exception as e:
                logger.error(f"Failed to initialize embedding model {model_name}")
                logger.error(f"Error details: {e}")
                logger.warning("Falling back to mock embeddings for basic functionality")
                logger.warning("Troubleshooting steps:")
                logger.warning("  1) Check network connectivity for model download")
                logger.warning("  2) Verify cache directory permissions: " + cache_dir)
                logger.warning("  3) Ensure sufficient disk space (~200MB free)")
                logger.warning("  4) Check Docker volume mount: logos_model_cache -> /app/cache")
                logger.info("Continuing with mock embeddings - limited functionality available")
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
            Vector dimension (384 for all-MiniLM-L6-v2)
        """
        # Try to get actual vector size, fallback to known size
        try:
            dummy_vector = self.embed_text("test")
            return len(dummy_vector[0])
        except Exception:
            # Default size for all-MiniLM-L6-v2
            return 384