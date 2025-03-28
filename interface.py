# ===================================================================================
# Project: Syntheim AI Companion
# File: interface.py
# Description: Manages the user interface components
# Author: LALAN KUMAR
# Created: [20-03-2025]
# Updated: [24-03-2025]
# Version: 1.0.0
# License: [License Type, e.g., MIT]
# ===================================================================================

import streamlit as st
import re

def setup_interface():
    """Set up the Streamlit interface styling"""
    
    st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Chat Input Styling */
    .stChatInput input {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #3A3A3A !important;
    }
    
    /* User Message Styling */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E1E1E !important;
        border: 1px solid #3A3A3A !important;
        color: #E0E0E0 !important;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Assistant Message Styling */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #2A2A2A !important;
        border: 1px solid #404040 !important;
        color: #F0F0F0 !important;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Avatar Styling */
    .stChatMessage .avatar {
        background-color: #00FFAA !important;
        color: #000000 !important;
    }
    
    /* Text Color Fix */
    .stChatMessage p, .stChatMessage div {
        color: #FFFFFF !important;
    }
    
    .stFileUploader {
        background-color: #1E1E1E;
        border: 1px solid #3A3A3A;
        border-radius: 5px;
        padding: 15px;
    }
    
    h1, h2, h3 {
        color: #00FFAA !important;
    }
    
    /* Style for upload button */
    .stButton button {
        background-color: #1E1E1E !important;
        color: #00FFAA !important;
        border: 1px solid #3A3A3A !important;
        border-radius: 5px;
        padding: 5px 10px;
        font-weight: bold;
        font-size: 16px;
    }
    
    .stButton button:hover {
        background-color: #2A2A2A !important;
        border: 1px solid #00FFAA !important;
    }
    
    /* File type icons */
    .file-icon {
        margin-right: 5px;
        font-weight: bold;
    }
    .pdf-icon { color: #FF5733; }
    .docx-icon { color: #4285F4; }
    .txt-icon { color: #CCCCCC; }
    .pptx-icon { color: #FF9900; }
    .csv-icon { color: #34A853; }
    </style>
    """, unsafe_allow_html=True)

def display_messages():
    """Display message history in the UI"""
    
    for message in st.session_state.message_log:
        with st.chat_message(message["role"]):
            content = message["content"]
            think_matches = re.findall(r'<think>(.*?)</think>', content, flags=re.DOTALL)
            content_without_think = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)

            st.markdown(content_without_think)

            for think_text in think_matches:
                with st.expander("💭 Thought Process"):
                    st.markdown(think_text)

def get_file_icon(filename):
    """Return appropriate icon and style based on file extension"""
    ext = filename.split('.')[-1].lower()
    if ext == 'pdf':
        return "📕", "pdf-icon"
    elif ext == 'docx':
        return "📘", "docx-icon"
    elif ext == 'txt':
        return "📄", "txt-icon"
    elif ext in ['pptx', 'ppt']:
        return "📊", "pptx-icon"
    elif ext == 'csv':
        return "📈", "csv-icon"
    else:
        return "📁", ""

def display_document_list():
    """Display the list of uploaded documents with appropriate icons"""
    
    with st.expander("📚 Uploaded Documents"):
        for file_name in st.session_state.uploaded_files:
            icon, icon_class = get_file_icon(file_name)
            st.markdown(f"<span class='file-icon {icon_class}'>{icon}</span> {file_name}", unsafe_allow_html=True)