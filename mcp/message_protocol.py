# mcp/message_protocol.py

import json
from typing import Dict, Any, Optional
import uuid

class MCPMessage:
    """
    Represents a Model Context Protocol (MCP) message for inter-agent communication.
    """
    def __init__(self, sender: str, receiver: str, type: str, payload: Dict[str, Any], trace_id: Optional[str] = None):
        self.sender = sender
        self.receiver = receiver
        self.type = type
        self.payload = payload
        self.trace_id = trace_id if trace_id else str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Converts the MCP message to a dictionary."""
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.type,
            "trace_id": self.trace_id,
            "payload": self.payload
        }

    def to_json(self) -> str:
        """Converts the MCP message to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """Creates an MCPMessage instance from a dictionary."""
        return cls(
            sender=data["sender"],
            receiver=data["receiver"],
            type=data["type"],
            payload=data["payload"],
            trace_id=data.get("trace_id")
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'MCPMessage':
        """Creates an MCPMessage instance from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self):
        return f"MCPMessage(sender={self.sender}, receiver={self.receiver}, type={self.type}, trace_id={self.trace_id}, payload={self.payload})"

# Example usage (for testing/demonstration)
if __name__ == "__main__":
    # Create a sample message
    sample_payload = {
        "top_chunks": ["chunk 1 content", "chunk 2 content"],
        "query": "What is the capital of France?"
    }
    msg = MCPMessage(
        sender="RetrievalAgent",
        receiver="LLMResponseAgent",
        type="CONTEXT_RESPONSE",
        payload=sample_payload
    )

    print("MCP Message Dictionary:")
    print(msg.to_dict())
    print("\nMCP Message JSON:")
    print(msg.to_json())

    # Reconstruct from JSON
    reconstructed_msg = MCPMessage.from_json(msg.to_json())
    print("\nReconstructed MCP Message:")
    print(reconstructed_msg)
    print(reconstructed_msg.payload)
