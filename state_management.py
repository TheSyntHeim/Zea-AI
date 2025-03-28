# ===================================================================================
# Project: Syntheim AI Companion
# File: state_management.py
# Description:  Manages the Streamlit session state
# Author: LALAN KUMAR
# Created: [20-03-2025]
# Updated: [24-03-2025]
# Version: 1.0.0
# License: [License Type, e.g., MIT]
# ===================================================================================

import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

# Get the huggingface API Key
os.environ["HUGGINGFACE_API_KEY"]=os.getenv("HUGGINGFACE_API_KEY")
os.environ["COHERE_API_KEY"]=os.getenv("COHERE_API_KEY")

def initialize_session_state():
    """Initialize all session state variables"""
    
    # Initialize embedding model
    try:
        EMBEDDING_MODEL = CohereEmbeddings(model="embed-english-v3.0") 
    except Exception:
        EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Initialize vector store
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = InMemoryVectorStore(embedding=EMBEDDING_MODEL)

    # Initialize document contents
    if "document_contents" not in st.session_state:
        st.session_state.document_contents = {}

    # Initialize message log
    if "message_log" not in st.session_state:
        st.session_state.message_log = [
            {"role": "ai", "content": "Hi, I’m Zea – your AI Companion from Zerthia, where empathy meets intelligence. I’m here to help you explore, understand, and take action. You can chat with me or upload your documents (PDF, DOCX, TXT, PPTX, CSV) for smart, meaningful insights. Let’s decode data, inspire impact, and change the world, together. For more, visit www.syntheim.com"}
        ]

    # Initialize processing state
    if "processing" not in st.session_state:
        st.session_state.processing = False

    # Initialize document flag
    if "has_documents" not in st.session_state:
        st.session_state.has_documents = False

    # Initialize uploaded files list
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    # Initialize last uploaded file
    if "last_uploaded_file" not in st.session_state:
        st.session_state.last_uploaded_file = None

    # Initialize file uploader visibility
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False

def update_session_state(file_name, file_type, num_chunks):
    """Update session state after document upload"""
    
    # Update document state
    st.session_state.has_documents = True
    if file_name not in st.session_state.uploaded_files:
        st.session_state.uploaded_files.append(file_name)
    
    # Add system message about the upload
    upload_message = f"📄 {file_type} document '{file_name}' successfully uploaded and processed ({num_chunks} chunks). You can now ask questions about this document."
    st.session_state.message_log.append({"role": "ai", "content": upload_message})
    
    # Update last uploaded file to prevent duplicate messages
    st.session_state.last_uploaded_file = file_name
    
    # Hide the uploader after successful upload
    st.session_state.show_uploader = False

def get_active_user_query():
    """Get the last user query from message log"""
    
    if st.session_state.message_log and st.session_state.message_log[-1]["role"] == "user":
        return st.session_state.message_log[-1]["content"]
    return None
