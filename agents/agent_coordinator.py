# agents/agent_coordinator.py

import os
from typing import List, Dict, Any
from mcp.message_protocol import MCPMessage
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_response_agent import LLMResponseAgent

class AgentCoordinator:
    """
    The AgentCoordinator orchestrates the flow of messages and tasks
    between the IngestionAgent, RetrievalAgent, and LLMResponseAgent.
    It acts as the central hub for the agentic RAG system.
    """
    def __init__(self, documents_dir: str = 'documents'):
        self.ingestion_agent = IngestionAgent()
        self.retrieval_agent = RetrievalAgent()
        self.llm_response_agent = LLMResponseAgent()
        self.documents_dir = documents_dir
        os.makedirs(self.documents_dir, exist_ok=True) # Ensure documents directory exists

        # In-memory storage for processed chunks
        self.all_indexed_chunks: List[Dict[str, Any]] = []

    def handle_document_upload(self, file_path: str) -> Dict[str, Any]:
        """
        Handles the document upload process, sending the file to the IngestionAgent
        and then indexing the resulting chunks with the RetrievalAgent.
        """
        print(f"Coordinator: Handling document upload for {file_path}")

        # 1. Send to IngestionAgent
        # MCP Message (simulated): UI -> Coordinator (implicit upload action)
        # Coordinator -> IngestionAgent
        ingestion_request_payload = {"file_path": file_path}
        ingestion_message = MCPMessage(
            sender="Coordinator",
            receiver="IngestionAgent",
            type="INGEST_DOCUMENT_REQUEST",
            payload=ingestion_request_payload
        )
        print(f"Coordinator sending: {ingestion_message}")
        
        # IngestionAgent processes the document
        chunks = self.ingestion_agent.process_document(file_path)

        # MCP Message (simulated): IngestionAgent -> Coordinator
        ingestion_response_payload = {"chunks": chunks, "file_path": file_path}
        ingestion_response_message = MCPMessage(
            sender="IngestionAgent",
            receiver="Coordinator",
            type="INGEST_DOCUMENT_RESPONSE",
            payload=ingestion_response_payload
        )
        print(f"Coordinator received: {ingestion_response_message}")

        if not chunks:
            return {"status": "error", "message": f"Failed to process or extract text from {os.path.basename(file_path)}."}

        # 2. Send chunks to RetrievalAgent for indexing
        # Coordinator -> RetrievalAgent
        retrieval_indexing_request_payload = {"chunks": chunks}
        retrieval_indexing_message = MCPMessage(
            sender="Coordinator",
            receiver="RetrievalAgent",
            type="INDEX_CHUNKS_REQUEST",
            payload=retrieval_indexing_request_payload
        )
        print(f"Coordinator sending: {retrieval_indexing_message}")

        self.retrieval_agent.index_documents(chunks)
        self.all_indexed_chunks.extend(chunks) # Keep track of all chunks for potential future use or debugging

        # MCP Message (simulated): RetrievalAgent -> Coordinator
        retrieval_indexing_response_payload = {"status": "indexed", "num_chunks": len(chunks)}
        retrieval_indexing_response_message = MCPMessage(
            sender="RetrievalAgent",
            receiver="Coordinator",
            type="INDEX_CHUNKS_RESPONSE",
            payload=retrieval_indexing_response_payload
        )
        print(f"Coordinator received: {retrieval_indexing_response_message}")

        return {"status": "success", "message": f"Document '{os.path.basename(file_path)}' processed and indexed. {len(chunks)} chunks added."}

    def handle_chat_query(self, query: str) -> Dict[str, Any]:
        """
        Handles a user chat query, orchestrating retrieval and LLM response generation.
        """
        print(f"Coordinator: Handling chat query: '{query}'")

        # 1. Send query to RetrievalAgent
        # Coordinator -> RetrievalAgent
        retrieval_query_request_payload = {"query": query}
        retrieval_query_message = MCPMessage(
            sender="Coordinator",
            receiver="RetrievalAgent",
            type="RETRIEVE_CONTEXT_REQUEST",
            payload=retrieval_query_request_payload
        )
        print(f"Coordinator sending: {retrieval_query_message}")

        retrieved_chunks = self.retrieval_agent.retrieve_relevant_chunks(query)

        # MCP Message (simulated): RetrievalAgent -> Coordinator
        retrieval_query_response_payload = {"retrieved_context": retrieved_chunks, "query": query}
        retrieval_query_response_message = MCPMessage(
            sender="RetrievalAgent",
            receiver="Coordinator",
            type="RETRIEVE_CONTEXT_RESPONSE",
            payload=retrieval_query_response_payload
        )
        print(f"Coordinator received: {retrieval_query_response_message}")

        # 2. Send query and retrieved context to LLMResponseAgent
        # Coordinator -> LLMResponseAgent
        llm_request_payload = {"query": query, "retrieved_context": retrieved_chunks}
        llm_request_message = MCPMessage(
            sender="Coordinator",
            receiver="LLMResponseAgent",
            type="GENERATE_RESPONSE_REQUEST",
            payload=llm_request_payload
        )
        print(f"Coordinator sending: {llm_request_message}")

        llm_response = self.llm_response_agent.generate_response(query, retrieved_chunks)

        # MCP Message (simulated): LLMResponseAgent -> Coordinator
        llm_response_message_payload = {"answer": llm_response['answer'], "source_context": llm_response['source_context']}
        llm_response_message = MCPMessage(
            sender="LLMResponseAgent",
            receiver="Coordinator",
            type="GENERATE_RESPONSE_RESPONSE",
            payload=llm_response_message_payload
        )
        print(f"Coordinator received: {llm_response_message}")

        return llm_response

    def clear_all_data(self):
        """Clears all indexed documents and agent states."""
        self.retrieval_agent.clear_index()
        self.all_indexed_chunks = []
        # Optionally, clear uploaded files from the documents directory
        for filename in os.listdir(self.documents_dir):
            file_path = os.path.join(self.documents_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        print("All indexed data and uploaded documents cleared.")

# Example usage (for testing)
if __name__ == "__main__":
    # Ensure a 'documents' directory exists for testing
    if not os.path.exists("../documents"):
        os.makedirs("../documents")

    # Create a dummy test file
    with open("../documents/sample_report.txt", "w") as f:
        f.write("This is a sample report about Q1 performance. Revenue increased by 10% and customer satisfaction improved. " * 10)
        f.write("Key Performance Indicators (KPIs) for this quarter included sales volume, customer retention, and average transaction value. " * 10)

    coordinator = AgentCoordinator(documents_dir="../documents")

    # Test document upload and indexing
    upload_result = coordinator.handle_document_upload("../documents/sample_report.txt")
    print(f"\nUpload Result: {upload_result}")

    # Test chat query
    chat_response = coordinator.handle_chat_query("What were the KPIs for Q1?")
    print(f"\nChat Response:")
    print(f"Answer: {chat_response['answer']}")
    print(f"Sources: {chat_response['source_context']}")

    chat_response_2 = coordinator.handle_chat_query("Tell me about revenue.")
    print(f"\nChat Response 2:")
    print(f"Answer: {chat_response_2['answer']}")
    print(f"Sources: {chat_response_2['source_context']}")

    # Test query with no relevant context (after clearing or if no docs uploaded)
    coordinator.clear_all_data()
    print("\nCleared all data. Testing query again.")
    chat_response_no_docs = coordinator.handle_chat_query("What is the weather like?")
    print(f"\nChat Response (No Docs):")
    print(f"Answer: {chat_response_no_docs['answer']}")
    print(f"Sources: {chat_response_no_docs['source_context']}")

    # Clean up dummy file
    if os.path.exists("../documents/sample_report.txt"):
        os.remove("../documents/sample_report.txt")
