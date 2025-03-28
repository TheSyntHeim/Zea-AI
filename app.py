# ===================================================================================
# Project: Syntheim AI Companion
# File: app.py
# Description: Main application file that orchestrates the entire application
# Author: LALAN KUMAR
# Created: [15-03-2025]
# Updated: [24-03-2025]
# Version: 1.0.0
# License: [License Type, e.g., MIT]
# ===================================================================================
    
import os
import streamlit as st
from dotenv import load_dotenv
from interface import setup_interface, display_messages, display_document_list
from document_manager import process_document_file
from state_management import initialize_session_state, update_session_state
from agent import handle_user_query, process_query

# Load environment variables
load_dotenv()

# Initialize session state
initialize_session_state()

# Set up the interface
setup_interface()

# Display title and app description
st.title("ZERTHIA")
st.caption("Your AI Companion with Document Intelligence")

# Create main chat container
chat_container = st.container()

# Display message history
with chat_container:
    display_messages()
    
    # Show processing indicator only when processing
    if st.session_state.processing:
        with st.chat_message("ai"):
            st.write("Processing...")

# Display uploaded documents if any
if st.session_state.uploaded_files:
    display_document_list()

# Create a container for the upload button and chat input
input_container = st.container()

with input_container:
    # Create two columns for the chat input and upload button
    col1, col2 = st.columns([10, 2])
    
    with col2:
        # Simple upload button
        upload_button = st.button("📄 +", key="upload_button")
        if upload_button:
            st.session_state.show_uploader = not st.session_state.show_uploader
    
    with col1:
        # Chat input
        user_query = st.chat_input("Ask Zea...")

# Show the file uploader when toggled
if st.session_state.show_uploader:
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["pdf", "docx", "txt", "pptx", "ppt", "csv"],
        key="document_uploader"
    )
    
    # Process uploaded file
    if uploaded_file and (st.session_state.last_uploaded_file != uploaded_file.name):
        file_extension = uploaded_file.name.split('.')[-1].lower()
        with st.spinner(f"Processing {uploaded_file.name}..."):
            num_chunks, error = process_document_file(uploaded_file)
            
            if num_chunks > 0:
                # Update state
                update_session_state(uploaded_file.name, file_extension.upper(), num_chunks)
                
                # Rerun to update UI
                st.rerun()
            else:
                st.error(f"Failed to process document '{uploaded_file.name}': {error}")

# Handle user input
if user_query:
    # Add user message to chat history immediately
    st.session_state.message_log.append({"role": "user", "content": user_query})
    st.session_state.processing = True
    st.rerun()

# Continue processing if in processing state
if st.session_state.processing:
    # Process the query
    process_query()
    
    # Rerun to update the UI
    st.rerun()
    
    
    
