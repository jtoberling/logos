import numpy as np
from typing import List, Union
from fastembed import TextEmbedding

class LogosEmbedder:
    """
    The neural heart of Logos. 
    Responsible for transforming raw text into the vector-space of Reason.
    """
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initializes the local embedding model.
        Default model is BGE-Small, which offers an excellent balance 
        between speed and semantic accuracy.
        """
        try:
            # This will download the model on first run (~100MB)
            self.model = TextEmbedding(model_name=model_name)
            print(f"LogosEmbedder: Model {model_name} loaded successfully.")
        except Exception as e:
            print(f"LogosEmbedder: Failed to initialize model. Error: {e}")
            raise

    def embed_text(self, text: Union[str, List[str]]) -> List[np.ndarray]:
        """
        Converts text into vectors (embeddings).
        Returns a list of numpy arrays.
        """
        if isinstance(text, str):
            text = [text]
            
        # FastEmbed returns a generator for memory efficiency
        embeddings_generator = self.model.embed(text)
        return list(embeddings_generator)

    @property
    def vector_size(self) -> int:
        """
        Returns the dimension of the vectors. 
        Crucial for Qdrant collection initialization.
        For bge-small-en-v1.5, this is 384.
        """
        # Quick hack to get the dimension if not hardcoded
        dummy_vector = self.embed_text("Logos")
        return len(dummy_vector[0])

# Example usage for testing
if __name__ == "__main__":
    embedder = LogosEmbedder()
    vector = embedder.embed_text("Reason over Mimicry")
    print(f"Vector generated. Dimensions: {len(vector[0])}")
    