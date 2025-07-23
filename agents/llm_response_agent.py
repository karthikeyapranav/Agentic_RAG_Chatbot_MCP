# # agents/llm_response_agent.py

# from typing import List, Dict, Any

# class LLMResponseAgent:
#     """
#     The LLMResponseAgent is responsible for forming the final LLM query
#     using the retrieved context and generating the answer.
#     """
#     def __init__(self):
#         # In a real application, you would initialize your LLM client here
#         # e.g., self.llm_client = OpenAI() or self.llm_client = GoogleGenerativeAI()
#         pass

#     def _format_prompt(self, query: str, retrieved_context: List[Dict[str, Any]]) -> str:
#         """
#         Formats the prompt for the LLM, including the user's query
#         and the retrieved context.
#         """
#         context_str = "\n".join([f"Source: {c['source']}\nContent: {c['content']}" for c in retrieved_context])

#         prompt = f"""
# You are a helpful AI assistant. Use the following retrieved information to answer the user's question.
# If the answer cannot be found in the provided information, respond with "I don't have enough information to answer that."

# Retrieved Information:
# ---
# {context_str}
# ---

# User Query: {query}

# Answer:
# """
#         return prompt

#     def generate_response(self, query: str, retrieved_context: List[Dict[str, Any]]) -> Dict[str, Any]:
#         """
#         Generates a response using the LLM based on the query and retrieved context.
#         In this prototype, it simulates an LLM call.
#         """
#         if not retrieved_context:
#             return {
#                 "answer": "I don't have enough information to answer that based on the uploaded documents. Please upload relevant documents.",
#                 "source_context": []
#             }

#         prompt = self._format_prompt(query, retrieved_context)
#         print(f"\n--- LLM Prompt (simulated) ---\n{prompt}\n--- End Prompt ---")

#         # --- SIMULATED LLM CALL ---
#         # In a real application, you would call your LLM API here.
#         # Example:
#         # response = self.llm_client.chat.completions.create(
#         #     model="gpt-3.5-turbo",
#         #     messages=[{"role": "user", "content": prompt}]
#         # )
#         # generated_text = response.choices[0].message.content
#         # --- END SIMULATED LLM CALL ---

#         # For demonstration, we'll generate a simple response based on context availability
#         # and extract sources.
#         simulated_answer = f"Based on the documents, here's what I found regarding '{query}':\n\n"
#         sources = []
#         for i, chunk in enumerate(retrieved_context):
#             simulated_answer += f"- From '{chunk['source']}': \"{chunk['content'][:100]}...\"\n"
#             sources.append(f"{chunk['source']} (Chunk {i+1})")

#         simulated_answer += "\n\n(This is a simulated LLM response. In a real application, an actual LLM would generate a more coherent answer.)"

#         return {
#             "answer": simulated_answer,
#             "source_context": list(set(sources)) # Unique sources
#         }

# # Example usage (for testing)
# if __name__ == "__main__":
#     llm_agent = LLMResponseAgent()

#     # Dummy retrieved context
#     dummy_context = [
#         {"content": "The annual sales review showed a 15% increase in Q1 revenue due to new product launches.", "source": "sales_review.pdf"},
#         {"content": "Key Performance Indicators (KPIs) for Q1 included revenue growth, customer acquisition cost, and net promoter score.", "source": "metrics.csv"},
#         {"content": "The marketing team focused on digital campaigns in the first quarter, leading to higher engagement.", "source": "marketing_report.docx"}
#     ]

#     query = "What KPIs were tracked in Q1?"
#     response = llm_agent.generate_response(query, dummy_context)

#     print("\n--- LLM Response ---")
#     print(f"Answer: {response['answer']}")
#     print(f"Sources: {response['source_context']}")

#     query_no_context = "What is the meaning of life?"
#     response_no_context = llm_agent.generate_response(query_no_context, [])
#     print(f"\n--- LLM Response (No Context) ---")
#     print(f"Answer: {response_no_context['answer']}")
#     print(f"Sources: {response_no_context['source_context']}")

# agents/llm_response_agent.py

from typing import List, Dict, Any
from transformers import pipeline # Import the pipeline function

class LLMResponseAgent:
    """
    The LLMResponseAgent is responsible for forming the final LLM query
    using the retrieved context and generating the answer.
    """
    def __init__(self):
        # Initialize the Hugging Face pipeline for text generation
        # Using "google/flan-t5-small" model
        print("Initializing Hugging Face LLM pipeline (google/flan-t5-small)... This may take a moment.")
        self.text_generator = pipeline("text2text-generation", model="google/flan-t5-small")
        print("Hugging Face LLM pipeline initialized.")

    def _format_prompt(self, query: str, retrieved_context: List[Dict[str, Any]]) -> str:
        """
        Formats the prompt for the LLM, including the user's query
        and the retrieved context.
        """
        context_str = "\n".join([f"Source: {c['source']}\nContent: {c['content']}" for c in retrieved_context])

        prompt = f"""
You are a helpful AI assistant. Use the following retrieved information to answer the user's question.
If the answer cannot be found in the provided information, respond with "I don't have enough information to answer that."

Retrieved Information:
---
{context_str}
---

User Query: {query}

Answer:
"""
        return prompt

    def generate_response(self, query: str, retrieved_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a response using the LLM based on the query and retrieved context.
        """
        if not retrieved_context:
            return {
                "answer": "I don't have enough information to answer that based on the uploaded documents. Please upload relevant documents.",
                "source_context": []
            }

        prompt = self._format_prompt(query, retrieved_context)
        print(f"\n--- LLM Prompt ---\n{prompt}\n--- End Prompt ---")

        try:
            # --- ACTUAL LLM CALL using Hugging Face pipeline ---
            # The pipeline returns a list of dictionaries, e.g., [{'generated_text': '...'}]
            llm_output = self.text_generator(prompt, max_length=200, num_return_sequences=1)
            generated_text = llm_output[0]['generated_text']
            # --- END ACTUAL LLM CALL ---

            sources = []
            # Extract unique sources from the retrieved context
            for chunk in retrieved_context:
                if chunk['source'] not in sources:
                    sources.append(chunk['source'])

            return {
                "answer": generated_text,
                "source_context": sources
            }
        except Exception as e:
            print(f"Error during LLM generation: {e}")
            return {
                "answer": f"An error occurred while generating the response: {str(e)}. Please try again.",
                "source_context": []
            }

# Example usage (for testing)
if __name__ == "__main__":
    llm_agent = LLMResponseAgent()

    # Dummy retrieved context
    dummy_context = [
        {"content": "The annual sales review showed a 15% increase in Q1 revenue due to new product launches.", "source": "sales_review.pdf"},
        {"content": "Key Performance Indicators (KPIs) for Q1 included revenue growth, customer acquisition cost, and net promoter score.", "source": "metrics.csv"},
        {"content": "The marketing team focused on digital campaigns in the first quarter, leading to higher engagement.", "source": "marketing_report.docx"}
    ]

    query = "What KPIs were tracked in Q1?"
    response = llm_agent.generate_response(query, dummy_context)

    print("\n--- LLM Response ---")
    print(f"Answer: {response['answer']}")
    print(f"Sources: {response['source_context']}")

    query_no_context = "What is the meaning of life?"
    response_no_context = llm_agent.generate_response(query_no_context, [])
    print(f"\n--- LLM Response (No Context) ---")
    print(f"Answer: {response_no_context['answer']}")
    print(f"Sources: {response_no_context['source_context']}")
