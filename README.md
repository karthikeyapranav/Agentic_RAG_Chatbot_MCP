### Agentic RAG Chatbot for Multi-Format Document QA
Empowering LLMs with Your Data, Agent-Style!
Welcome to the Agentic RAG Chatbot, a powerful application designed to answer your questions using information from your own diverse documents. This project leverages a modular, agent-based architecture and a custom communication protocol (MCP) to provide accurate and contextually relevant responses.

### Features
Multi-Format Document Support: Upload and process documents in various formats:

* PDF

* PPTX

* CSV

* DOCX

* TXT / Markdown

Agentic Architecture: A clear separation of concerns with dedicated agents for:

Ingestion: Parsing and preprocessing documents.

Retrieval: Creating embeddings and performing semantic search.

LLM Response: Forming prompts and generating answers.

Model Context Protocol (MCP): Structured, standardized communication between agents for robust data flow.

Vector Store & Embeddings: Utilizes sentence-transformers for embeddings and FAISS for efficient similarity search.

Interactive Chatbot UI:

User-friendly interface for document uploads.

Supports multi-turn conversations.

Displays responses with source context (which document the information came from).

Ability to clear all uploaded data.

### How It Works (High-Level Flow)
Document Upload: You upload documents (PDFs, DOCX, etc.) through the UI.

Ingestion Agent: This agent reads, extracts text, and breaks your documents into smaller, manageable "chunks."

Retrieval Agent: These chunks are then converted into numerical representations (embeddings) and stored in a vector database (FAISS).

User Query: You ask a question in the chat.

Retrieval Agent (again): The agent takes your question, converts it into an embedding, and searches the vector database to find the most relevant chunks from your uploaded documents.

LLM Response Agent: Your question, along with the retrieved relevant chunks, is sent to a powerful Large Language Model (LLM).

Answer Generation: The LLM synthesizes the information from the retrieved chunks to generate a coherent and accurate answer, which is then displayed in the chat, along with its sources.

All these steps are orchestrated by an AgentCoordinator using structured messages defined by the Model Context Protocol (MCP).

### Key Improvement: Enhanced LLM Integration
Initially, the chatbot used a simulated LLM response to demonstrate the RAG flow. However, to provide truly intelligent and coherent answers, we have upgraded the LLMResponseAgent to integrate with a real Large Language Model from Hugging Face!

Specifically, we are now using the google/flan-t5-small model. This model is a powerful, pre-trained text-to-text transformer that excels at following instructions and generating high-quality text.

Why this is important:

Superior Answer Quality: Instead of just echoing retrieved text, the LLM can now understand, synthesize, and generate human-like answers based on the context provided by your documents.

Grounded Responses: By explicitly instructing the LLM to use only the retrieved information (via prompt engineering), we ensure that answers are factual and directly supported by your uploaded documents, minimizing "hallucinations."

Flexibility: While google/flan-t5-small is used, the architecture allows for easy swapping with other Hugging Face models or even proprietary LLMs (e.g., Gemini, OpenAI GPT) by simply updating the LLMResponseAgent.

### Setup Instructions
Follow these steps to get the chatbot up and running on your local machine.

Prerequisites
Python 3.8+

pip (Python package installer)

Installation
Clone the Repository:

git clone https://github.com/your-username/Agentic_RAG_Chatbot_using_MCP.git
cd Agentic_RAG_Chatbot_using_MCP

(Replace your-username with your actual GitHub username)

Create a Virtual Environment (Recommended):

python -m venv venv

On Windows:

.\venv\Scripts\activate

On macOS/Linux:

source venv/bin/activate

Install Dependencies:

pip install -r requirements.txt

Note: The first time you run this, torch and sentence-transformers (which downloads the embedding model) and transformers (which downloads google/flan-t5-small) might take some time and consume significant disk space. Be patient!

If you face issues with faiss-cpu on Windows, consider installing a pre-built wheel or using WSL/Linux.

Directory Structure
Agentic_RAG_Chatbot_using_MCP/
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── agents/                    # Agent implementations
│   ├── __init__.py
│   ├── agent_coordinator.py
│   ├── ingestion_agent.py
│   ├── retrieval_agent.py
│   ├── llm_response_agent.py
├── mcp/                       # Model Context Protocol definitions
│   ├── __init__.py
│   ├── message_protocol.py
├── documents/                 # Uploaded documents are stored here
├── static/                    # Frontend assets (CSS, JS)
│   ├── style.css
│   └── script.js
└── templates/                 # HTML templates
    └── index.html

### How to Run
Activate your virtual environment (if you haven't already):

On Windows: .\venv\Scripts\activate

On macOS/Linux: source venv/bin/activate

Start the Flask application:

python app.py

You should see output indicating the Flask server is running, usually at http://127.0.0.1:5000/.

Open in Browser:
Navigate to http://127.0.0.1:5000/ in your web browser.

### How to Use the Chatbot
Upload Documents:

On the left sidebar, click "Choose Files" under "Upload Documents."

Select one or more PDF, PPTX, CSV, DOCX, TXT, or Markdown files.

The upload-status will show "Uploading and processing..." and a loading spinner will appear.

Once complete, a success message will appear. For large files, this might take a moment.

Ask Questions:

In the chat area on the right, type your question in the input field at the bottom.

Click the "Send" button or press Enter.

A loading spinner will appear while the agents process your query.

View Responses:

The chatbot's answer will appear in the chat.

If the answer is based on your documents, you will see "Sources:" listed below the answer, indicating which files were used.

Clear All Data:

To remove all uploaded documents and indexed data from the system, click the "Clear All Data" button on the left sidebar. This action requires confirmation.

### Challenges Faced & Improvements
Challenges Faced
Large File Uploads & Processing Time:

Challenge: Handling large PDF or DOCX files can be slow, both in terms of file upload (network transfer) and the subsequent parsing and embedding generation. This led to "Network error during upload" initially if the client-side timeout was shorter than the server's processing time.

Solution: Increased Flask's MAX_CONTENT_LENGTH to 200MB and implemented client-side fetch timeouts with AbortController to provide better user feedback for long-running operations. Optimizing document parsing for very large files remains an area for further refinement.

Initial LLM Response Quality (Simulated):

Challenge: The initial prototype used a simulated LLM, which merely echoed parts of the retrieved documents. This didn't demonstrate true generative AI capabilities.

Solution: Integrated google/flan-t5-small from Hugging Face's transformers library. This required adding transformers and torch to requirements.txt and updating the LLMResponseAgent to use the pipeline for text generation. This significantly improved the quality and coherence of the generated answers.

Dependency Management & Environment Setup:

Challenge: Ensuring all Python dependencies (especially torch and faiss-cpu which can have platform-specific quirks) are correctly installed and compatible.

Solution: Provided clear requirements.txt and emphasized virtual environment usage.

Future Scope & Improvements
Persistent Storage:

Currently, all indexed data (FAISS index and document chunks) are in-memory and lost upon server restart.

Improvement: Implement persistent storage for the vector database (e.g., saving FAISS index to disk, or using a dedicated vector database like ChromaDB, Pinecone, Weaviate) and document metadata (e.g., in a simple SQLite database or cloud-based solution).

True Multi-Turn Conversational Memory:

The current system displays chat history but doesn't explicitly pass it to the LLM for contextual understanding of follow-up questions (e.g., "What about Q2?" after "What KPIs were tracked in Q1?").

Improvement: Implement a mechanism to store and pass relevant chat history to the LLMResponseAgent's prompt, potentially with a "query rephrasing" sub-agent to make follow-up questions self-contained.

Advanced RAG Techniques:

Improvement: Explore techniques like re-ranking retrieved documents, hybrid search (keyword + semantic), or recursive retrieval to improve the quality of context provided to the LLM.

User Authentication & Multi-User Support:

Improvement: Add user login/registration and isolate document uploads and chat histories per user.

Asynchronous Processing:

Improvement: For very large documents or high concurrency, switch to asynchronous processing (e.g., using Celery with a message queue) for document ingestion to prevent blocking the main Flask thread.

Enhanced UI/UX:

Improvement: Add progress bars for document processing, a list of currently uploaded documents, and more sophisticated chat UI features.

Containerization (Docker Compose):

Improvement: Provide a Dockerfile and docker-compose.yml for easier deployment and environment consistency.

* Deliverables Checklist
* GitHub Repository:

Well-organized code

Clear README.md with setup instructions (this file!)

### Architecture Presentation (PDF or PPTX):

To be created separately and uploaded to this repo.

Slide deck (3–6 slides) including:

Agent-based architecture with MCP integration

System flow diagram (with message passing)

Tech stack used

### UI screenshots of working app

Challenges Faced

(Optional) future scope / improvements

### Short 5-minute video:

1 min: App demo

2 min: System architecture & flow explanation

2 min: Code walkthrough

(Optional to show face)

### Contributing
Feel free to fork this repository, open issues, or submit pull requests.

### License
This project is open-source and available under the MIT License. (You'll need to create a LICENSE file if you don't have one)