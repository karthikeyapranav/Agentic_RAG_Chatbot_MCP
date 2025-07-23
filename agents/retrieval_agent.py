# agents/retrieval_agent.py

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Any, Optional

class RetrievalAgent:
    """
    The RetrievalAgent handles embedding generation and semantic retrieval
    using a FAISS vector store.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        # Load a pre-trained sentence transformer model for embeddings
        # This model is good for general purpose sentence embeddings and is relatively small.
        self.model = SentenceTransformer(model_name)
        self.vector_store: Optional[faiss.IndexFlatL2] = None
        self.documents_metadata: List[Dict[str, Any]] = [] # Stores chunk content and metadata

    def _generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generates embeddings for a list of texts."""
        print(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        print("Embeddings generated.")
        return embeddings

    def index_documents(self, chunks: List[Dict[str, Any]]):
        """
        Indexes a list of document chunks into the FAISS vector store.
        Each chunk should be a dictionary with at least a 'content' key.
        """
        if not chunks:
            print("No chunks to index.")
            return

        # Extract content for embedding
        texts_to_embed = [chunk['content'] for chunk in chunks]
        embeddings = self._generate_embeddings(texts_to_embed)

        # Initialize FAISS index if not already done
        if self.vector_store is None:
            dimension = embeddings.shape[1]
            # Using IndexFlatL2 for simple Euclidean distance search
            self.vector_store = faiss.IndexFlatL2(dimension)
            print(f"Initialized FAISS index with dimension: {dimension}")

        # Add embeddings to the FAISS index
        self.vector_store.add(embeddings)
        print(f"Added {len(embeddings)} embeddings to FAISS index.")

        # Store the original chunks (or their metadata) corresponding to the embeddings
        # The index in self.documents_metadata will correspond to the index in FAISS
        self.documents_metadata.extend(chunks)
        print(f"Stored metadata for {len(chunks)} chunks. Total indexed chunks: {len(self.documents_metadata)}")

    def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves the top_k most relevant chunks based on the query.
        """
        if self.vector_store is None or self.vector_store.ntotal == 0:
            print("Vector store is empty. No documents indexed yet.")
            return []

        # Generate embedding for the query
        query_embedding = self._generate_embeddings([query])
        # Reshape for FAISS search (FAISS expects 2D array for queries)
        query_embedding = np.array([query_embedding[0]])

        # Perform similarity search
        # D: distances, I: indices of the nearest neighbors
        distances, indices = self.vector_store.search(query_embedding, top_k)

        relevant_chunks = []
        for i, idx in enumerate(indices[0]):
            if idx != -1: # Ensure the index is valid
                chunk = self.documents_metadata[idx]
                # You can add the distance to the chunk if needed for debugging/ranking
                # chunk['distance'] = distances[0][i]
                relevant_chunks.append(chunk)
        print(f"Retrieved {len(relevant_chunks)} relevant chunks for query: '{query}'")
        return relevant_chunks

    def clear_index(self):
        """Clears the current FAISS index and stored metadata."""
        self.vector_store = None
        self.documents_metadata = []
        print("FAISS index and document metadata cleared.")


# Example usage (for testing)
if __name__ == "__main__":
    retrieval_agent = RetrievalAgent()

    # Create some dummy chunks (as if from IngestionAgent)
    dummy_chunks = [
        {"content": "The quick brown fox jumps over the lazy dog.", "source": "doc1.txt"},
        {"content": "Artificial intelligence is rapidly advancing.", "source": "doc2.pdf"},
        {"content": "Machine learning is a subset of AI.", "source": "doc2.pdf"},
        {"content": "Dogs are often called man's best friend.", "source": "doc1.txt"},
        {"content": "Deep learning models require large datasets.", "source": "doc2.pdf"},
        {"content": "Cats are independent pets.", "source": "doc3.txt"},
    ]

    # Index the dummy chunks
    retrieval_agent.index_documents(dummy_chunks)

    # Test retrieval
    query1 = "What is AI?"
    retrieved_1 = retrieval_agent.retrieve_relevant_chunks(query1, top_k=2)
    print(f"\nQuery: '{query1}'")
    for i, chunk in enumerate(retrieved_1):
        print(f"  Chunk {i+1} (Source: {chunk['source']}): {chunk['content']}")

    query2 = "Tell me about animals."
    retrieved_2 = retrieval_agent.retrieve_relevant_chunks(query2, top_k=2)
    print(f"\nQuery: '{query2}'")
    for i, chunk in enumerate(retrieved_2):
        print(f"  Chunk {i+1} (Source: {chunk['source']}): {chunk['content']}")

    # Clear index and re-index
    retrieval_agent.clear_index()
    print("\nIndex cleared.")
    retrieval_agent.index_documents([
        {"content": "New document content about space exploration.", "source": "space.txt"},
        {"content": "The first moon landing was in 1969.", "source": "history.pdf"}
    ])
    query3 = "When was the moon landing?"
    retrieved_3 = retrieval_agent.retrieve_relevant_chunks(query3, top_k=1)
    print(f"\nQuery: '{query3}'")
    for i, chunk in enumerate(retrieved_3):
        print(f"  Chunk {i+1} (Source: {chunk['source']}): {chunk['content']}")
