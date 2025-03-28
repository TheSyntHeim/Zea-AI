# ===================================================================================
# Project: Syntheim AI Companion
# File: agent.py
# Description: Contains the AI agent logic, LLM integration, and search capabilities
# Author: LALAN KUMAR
# Created: [20-03-2025]
# Updated: [20-03-2025]
# Version: 1.0.0
# License: [License Type, e.g., MIT]
# ===================================================================================

import os
import streamlit as st
import datetime
from langchain_groq import ChatGroq
from langchain.tools import Tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from tavily import TavilyClient
from document_manager import query_documents
from state_management import get_active_user_query

# Get API keys
groq_api_key = os.getenv("GROQ_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
cohere_api_key=os.getenv("COHERE_API_KEY")

# Initialize Tavily client
tavily_client = TavilyClient(api_key=tavily_api_key)

# Initialize AI model (DeepSeek on Groq)
llm_engine = ChatGroq(model="Deepseek-R1-Distill-Qwen-32b", groq_api_key=groq_api_key)

# Get current date
current_date = datetime.datetime.now().strftime("%Y-%m-%d")

# Define system prompt templates
system_template = f"""
You are Zerthia, an expert AI companion with emotional intelligence, web search and document analysis capabilities, created by SYNTHEIM.

Today's date is {current_date}.

Core capabilities:
1. Emotional intelligence to detect and respond to user emotions
2. Concise and accurate responses tailored to user needs
3. Real-time information retrieval via web search when necessary
4. Document analysis and question answering for uploaded PDF documents

For emotional support:
- Identify the user's emotional state from their query
- Adapt your tone to match their emotional needs
- Show empathy for negative emotions
- Reinforce positive emotions
- For neutral queries, focus on delivering accurate information efficiently

When responding:
- If the user asks about current events, real-time data, or information you're uncertain about, use the web search results
- If the user asks about uploaded documents, use the document query results
- ALWAYS use web search or document query results when provided to give accurate information
- Summarize information from search or document results in your own words
- Cite sources by referring to "Source 1", "Source 2", etc. or "Document 1", "Document 2", etc and provide their relevant links.
- NEVER claim you can't access links, real-time data, or the internet
- When asked about dates, times, or current events, ALWAYS reference today's date: {current_date}
- If search or document results are provided BUT they're not relevant to the query, rely on your training instead
- If no search or document results are available, respond based on your training

Remember: For most conversational queries, you don't need web search or document queries. Use them only when necessary.

IMPORTANT DOCUMENT HANDLING INSTRUCTIONS:
- When users upload documents, you CAN access their content through the Document Query tool
- NEVER say you cannot access document content - you have direct access to all uploaded documents
- When answering document questions, cite specific parts of the document
- If a document doesn't contain relevant information, clearly state that instead of saying you can't access it
- If a document doesn't contain relevant information, use web search to answer the query AND clearly state that you have used the web search.
"""

# Enhanced search system message
search_instruction_template = """
IMPORTANT: You have access to recent web search results about the user's query.

These search results may contain current information that you can use to answer the user's question.

Please follow these guidelines:
1. Evaluate if the search results are RELEVANT to the user's query
2. If relevant, synthesize information from the search results for an accurate, up-to-date answer
3. If NOT relevant, DO NOT use them and instead rely on your training
4. When using search results, cite your sources by referring to "Source 1", "Source 2", etc and provide their relevant links.
5. If the search results contain conflicting information, acknowledge this and present multiple perspectives
6. Present information in a clear, concise manner
7. ALWAYS mention your sources AND provide their relevant links.
8. NEVER claim you can't access real-time data or the internet


Here are the search results:

{search_results}
"""

# Document query system message with clearer instructions
document_instruction_template = """
IMPORTANT: You have access to information from documents that the user has uploaded. The following content has been extracted from these documents.

Please follow these guidelines:
1. You CAN and SHOULD use this document information to answer the user's query
2. NEVER say you cannot access document content - you have direct access shown below
3. If the information below doesn't answer the query, state "The uploaded documents don't contain information about [specific topic]" 
4. The uploaded documents don't contain information about [specific topic], USE web search to answer the query
5. When using document information, cite your sources by referring to specific document names
6. If you have USED web search to answer the query, clearly state that you have used web search and provide relevant links to the sources
6. Be specific about what parts of the documents you're using
7. Present information in a clear, concise manner
8. Do not make up information that isn't in the documents

Here is the document information:

{document_results}
"""

# Function to perform internet search
def perform_web_search(query: str) -> str:
    """Perform a web search using Tavily"""
    
    try:
        response = tavily_client.search(query, search_depth="advanced", max_results=5)
        if response and "results" in response and len(response["results"]) > 0:
            formatted_results = []
            for i, res in enumerate(response["results"], 1):
                title = res.get('title', 'No title')
                url = res.get('url', '#')
                content = res.get('content', 'No description available.')
                
                # Format the result with source number for easier reference
                formatted_results.append(f"Source {i}: {title}\nURL: {url}\nContent: {content}\n")
            
            return "\n".join(formatted_results)
        return "No relevant search results found."
    except Exception as e:
        return f"Error performing web search: {str(e)}"

# Define Web Search and Document Query as Tools
web_search_tool = Tool(
    name="Web Search",
    func=perform_web_search,
    description="Use this tool to fetch the latest information from the web. Input a search query."
)

document_query_tool = Tool(
    name="Document Query",
    func=query_documents,
    description="Use this tool to search through uploaded documents. Input a search query."
)

# Function to build the prompt chain
def build_prompt_chain():
    """Build the prompt chain from message history"""
    
    # Start with just the system message
    messages = [SystemMessage(content=system_template)]
    
    # Add the conversation history
    for msg in st.session_state.message_log:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ai":
            messages.append(AIMessage(content=msg["content"]))
    
    return messages

# Function to determine if web search is needed
def needs_web_search(query):
    """Determine if web search is needed for the query"""
    
    # Check for explicit request for search
    explicit_search_patterns = [
        "search for", "look up", "find information", "search the web",
        "what's the latest", "current news", "recent updates"
    ]
    
    query_lower = query.lower()
    
    for pattern in explicit_search_patterns:
        if pattern in query_lower:
            return True
    
    # Check for queries about current events, dates, or time-sensitive information
    time_sensitive_patterns = [
        "today", "current", "latest", "recent", "now", "update", 
        "news", "weather", "price", "stock", "bitcoin", "crypto",
        "happened", "trending", "score", "result", "happening"
    ]
    
    for pattern in time_sensitive_patterns:
        if pattern in query_lower:
            return True
    
    # Check for questions about specific factual information that might need verification
    factual_patterns = [
        "how many", "how much", "what is the population", "what is the distance",
        "how far", "how old", "when was", "where is", "who is the current"
    ]
    
    for pattern in factual_patterns:
        if pattern in query_lower:
            return True
    
    # Don't use web search for conversational, opinion, or emotional queries
    conversational_patterns = [
        "how are you", "what do you think", "can you help", "i feel", 
        "i'm feeling", "i am feeling", "i need advice", "what should i do",
        "how do you feel", "tell me about yourself", "who are you"
    ]
    
    for pattern in conversational_patterns:
        if pattern in query_lower:
            return False
    
    # Default to not using web search for most queries
    return False

# Function to determine if we should check documents
def needs_document_search(query):
    """Determine if document search is needed for the query"""
    
    # Check for explicit request for document search
    document_patterns = [
        "in the document", "from the pdf", "in the pdf", "document says",
        "check the document", "in the uploaded", "from the uploaded",
        "the document mentions", "in my document", "in my pdf",
        "what does the document say about", "find in document",
        "tell me about the document", "summarize the document",
        "what's in the pdf", "what is in the document",
        "analyze the pdf", "analyze the document"
    ]
    
    query_lower = query.lower()
    
    for pattern in document_patterns:
        if pattern in query_lower:
            return True
    
    # If there are documents and the query sounds like it needs information:
    if st.session_state.has_documents and len(st.session_state.uploaded_files) > 0:
        info_patterns = [
            "what is", "how does", "tell me about", "explain", "summarize",
            "what are", "where is", "who is", "when did", "why did",
            "what was", "how many", "how much"
        ]
        
        for pattern in info_patterns:
            if query_lower.startswith(pattern):
                return True
    
    # Always try document search if we have few documents
    # This increases chances of getting relevant information
    if st.session_state.has_documents and len(st.session_state.uploaded_files) <= 3:
        return True
    
    # Default to not using document search unless explicitly requested
    return False

def handle_user_query(query):
    """Handle a user query and determine response strategy"""
    
    # Determine if web search or document search is needed
    should_search_web = needs_web_search(query)
    should_search_docs = needs_document_search(query)
    
    return should_search_web, should_search_docs

def process_query():
    """Process the latest user query and generate a response"""
    
    with st.spinner(""):
        messages = build_prompt_chain()
        
        # Get the last user query
        last_user_query = get_active_user_query()
        
        if not last_user_query:
            st.session_state.processing = False
            return
        
        # Determine query handling strategy
        should_search_web, should_search_docs = handle_user_query(last_user_query)
        
        # Flag to track if we've already handled the query
        query_handled = False
        
        # Always try document search first if we have documents
        if st.session_state.has_documents:
            # Query documents
            document_results = query_documents(last_user_query)
            
            if "No documents have been uploaded yet" not in document_results and "Error" not in document_results:
                # Format document instruction with results
                doc_instruction = document_instruction_template.format(document_results=document_results)
                
                # Add the document results as context
                doc_context_message = SystemMessage(content=doc_instruction)
                
                # Create new messages list with the document context
                doc_messages = [
                    SystemMessage(content=system_template),
                    doc_context_message,
                    HumanMessage(content=f"{last_user_query}")
                ]
                
                # Get response from LLM with document results
                ai_response = llm_engine.invoke(doc_messages).content
                query_handled = True
                
                # Add a thought process about document search
                if "<think>" not in ai_response:
                    ai_response += f"\n\n<think>Document search was performed and used to generate this response.</think>"
        
        # Handle web search if needed and not already handled
        if should_search_web and not query_handled:
            # Perform web search
            search_results = perform_web_search(last_user_query)
            
            # Format search instruction with results
            search_instruction = search_instruction_template.format(search_results=search_results)
            
            # Add the search results as context
            web_context_message = SystemMessage(content=search_instruction)
            
            # Create new messages list with the search context
            search_messages = [
                SystemMessage(content=system_template),
                web_context_message,
                HumanMessage(content=f"{last_user_query}")
            ]
            
            # Get response from LLM with search results
            ai_response = llm_engine.invoke(search_messages).content
            query_handled = True
            
            # Add a thought process about web search
            if "<think>" not in ai_response:
                ai_response += f"\n\n<think>Web search was performed and used to generate this response.</think>"
        
        # If neither search was used or they didn't provide useful results
        if not query_handled:
            # Add the current user query to the messages
            messages.append(HumanMessage(content=last_user_query))
            
            # Use LLM directly
            ai_response = llm_engine.invoke(messages).content
            
            # Add a thought process about using base knowledge
            if "<think>" not in ai_response:
                ai_response += f"\n\n<think>No external search was performed. Response generated from base knowledge.</think>"

    # Add AI response to chat history
    st.session_state.message_log.append({"role": "ai", "content": ai_response})
    
    # Turn off processing state
    st.session_state.processing = False

