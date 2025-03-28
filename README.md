# ZERTHIA: AI Assistant with Document Intelligence

ZERTHIA is an AI assistant with document intelligence capabilities, built using Streamlit, LangChain, and the Groq API. It provides a user-friendly chat interface for interacting with AI models and uploading documents for analysis.

## Features

- **Chat Interface**: Interact with the AI assistant through a natural language interface
- **Document Analysis**: Upload PDF documents for analysis and ask questions about their content
- **Web Search**: Retrieve up-to-date information from the web through the Tavily API
- **Emotional Intelligence**: The assistant can detect and respond to user emotions

## Project Structure

The application is structured into several modules:

- `app.py`: Main application file that orchestrates the entire application
- `agent.py`: Contains the AI agent logic, LLM integration, and search capabilities
- `document_manager.py`: Handles document processing and retrieval
- `interface.py`: Manages the user interface components
- `state_management.py`: Manages the Streamlit session state
- `requirements.txt`: Lists all required dependencies

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```
4. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Start the application
2. Upload documents using the "📄 +" button
3. Ask questions about the documents or any other topic
4. The AI will respond based on its knowledge, document content, or web search results

## Requirements

- Python 3.8+
- Groq API key for language model access
- Tavily API key for web search
- Ollama for local embeddings

## License

This project is licensed under the MIT License.