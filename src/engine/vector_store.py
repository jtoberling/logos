"""
Logos Vector Store - Consolidated Qdrant interface for memory operations.

This module provides a unified interface for vector database operations,
supporting both personality memories (logos_essence) and project knowledge
(project_knowledge), plus the canon collection for core documents.
"""

import uuid
from typing import List, Dict, Optional, Any
from ..logging_config import get_logger

logger = get_logger(__name__)

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    # Mock classes for testing when qdrant is not available
    class QdrantClient:
        pass
    class models:
        class VectorParams:
            pass
        class Distance:
            COSINE = "Cosine"
        class PointStruct:
            pass
        class Filter:
            pass

from .embedder import LogosEmbedder


class LogosVectorStore:
    """
    Consolidated interface for the Qdrant vector database.

    Handles collection management, data ingestion, and semantic search
    for both personality memories and project knowledge.
    """

    # Required collections
    COLLECTIONS = {
        "logos_essence": "Personality memories and letters for future self",
        "project_knowledge": "Project and technical knowledge",
        "canon": "Core documents and constitution"
    }

    def __init__(self, host: str = "qdrant", port: int = 6333, embedder: Optional[LogosEmbedder] = None) -> None:
        """
        Initialize the vector store connection.

        Args:
            host: Qdrant host (default: "qdrant" for Docker)
            port: Qdrant port (default: 6333)
            embedder: LogosEmbedder instance (created if None)
        """
        self.client = QdrantClient(host=host, port=port)
        self.embedder = embedder or LogosEmbedder()

        # Ensure all required collections exist
        self._ensure_collections()

    def _ensure_collections(self) -> None:
        """
        Ensure all required collections exist in the database.

        Creates collections if they don't exist with proper configuration.
        """
        existing_collections = self.client.get_collections().collections
        existing_names = {c.name for c in existing_collections}

        for collection_name in self.COLLECTIONS.keys():
            if collection_name not in existing_names:
                logger.info(f"Creating collection '{collection_name}'...")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=self.embedder.vector_size,
                        distance=models.Distance.COSINE
                    )
                )

    def upsert(self, collection_name: str, texts: List[str],
               metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Embed texts and upload them to the vector store with metadata.

        Args:
            collection_name: Target collection name
            texts: List of text strings to embed and store
            metadatas: Optional list of metadata dictionaries (one per text)
        """
        if not texts:
            return  # Nothing to do

        # Embed all texts
        vectors = self.embedder.embed_text(texts)

        # Prepare points for upload
        points = []
        for i, (text, vector) in enumerate(zip(texts, vectors)):
            # Generate unique ID
            point_id = str(uuid.uuid4())

            # Prepare payload
            payload = {"text": text}
            if metadatas and i < len(metadatas):
                payload.update(metadatas[i])

            points.append(models.PointStruct(
                id=point_id,
                vector=vector.tolist(),
                payload=payload
            ))

        # Upload to Qdrant
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )

    def search(self, collection_name: str, query_text: str, limit: int = 3) -> List[Any]:
        """
        Perform semantic search on a collection.

        Args:
            collection_name: Collection to search in
            query_text: Text to search for
            limit: Maximum number of results (default: 3)

        Returns:
            List of search results with scores and payloads
        """
        # Embed query
        query_vector = self.embedder.embed_text(query_text)[0]

        # Search in Qdrant
        return self.client.search(
            collection_name=collection_name,
            query_vector=query_vector.tolist(),
            limit=limit,
            with_payload=True
        )

    def delete_points(self, collection_name: str, point_ids: List[str]) -> None:
        """
        Delete points from a collection.

        Args:
            collection_name: Collection name
            point_ids: List of point IDs to delete
        """
        self.client.delete(
            collection_name=collection_name,
            points=point_ids
        )

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about a collection.

        Args:
            collection_name: Collection name

        Returns:
            Dictionary with collection information
        """
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": "exists"
            }
        except Exception as e:
            return {
                "name": collection_name,
                "status": "error",
                "error": str(e)
            }

    def list_collections(self) -> List[str]:
        """
        List all collections in the database.

        Returns:
            List of collection names
        """
        collections = self.client.get_collections().collections
        return [c.name for c in collections]

    def clear_collection(self, collection_name: str) -> None:
        """
        Clear all points from a collection (keep collection structure).

        Args:
            collection_name: Collection to clear
        """
        # Delete all points by using a filter that matches everything
        self.client.delete(
            collection_name=collection_name,
            points=models.Filter()  # Empty filter matches all points
        )