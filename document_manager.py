# ===================================================================================
# Project: Syntheim AI Companion
# File: document_manager.py
# Description: Handles document processing and retrieval
# Author: LALAN KUMAR
# Created: [20-03-2025]
# Updated: [24-03-2025]
# Version: 1.0.0
# License: [License Type, e.g., MIT]
# ===================================================================================

import os
import streamlit as st
from io import BytesIO
import pandas as pd
from langchain_community.document_loaders import (
    PDFPlumberLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    TextLoader,
    CSVLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_document_file(uploaded_file):
    """Process various document types and add to the vector store"""
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    # Create a temporary file-like object
    file_bytes = BytesIO(uploaded_file.getvalue())
    
    # Save to a temporary file that loaders can use
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(file_bytes.getvalue())
    
    try:
        # Select appropriate loader based on file extension
        if file_extension == 'pdf':
            loader = PDFPlumberLoader(temp_path)
        elif file_extension == 'docx':
            loader = UnstructuredWordDocumentLoader(temp_path)
        elif file_extension in ['pptx', 'ppt']:
            loader = UnstructuredPowerPointLoader(temp_path)
        elif file_extension == 'txt':
            loader = TextLoader(temp_path)
        elif file_extension == 'csv':
            loader = CSVLoader(temp_path)
        else:
            os.remove(temp_path)
            return 0, f"Unsupported file type: {file_extension}"
        
        raw_docs = loader.load()
        
        # Handle special case for CSV to include headers in metadata
        if file_extension == 'csv':
            # Read CSV headers for metadata
            df = pd.read_csv(temp_path)
            headers = list(df.columns)
            for doc in raw_docs:
                doc.metadata["headers"] = headers
        
        # Store the raw document content for direct access
        full_text = "\n\n".join([doc.page_content for doc in raw_docs])
        st.session_state.document_contents[uploaded_file.name] = full_text
        
        # Chunk documents
        text_processor = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )
        document_chunks = text_processor.split_documents(raw_docs)
        
        # Add metadata to track source document
        for chunk in document_chunks:
            if "source" not in chunk.metadata:
                chunk.metadata["source"] = uploaded_file.name
        
        # Add to vector store
        st.session_state.vector_store.add_documents(document_chunks)
        
        # Clean up the temporary file
        os.remove(temp_path)
        
        return len(document_chunks), None
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        error_msg = f"Error processing {file_extension.upper()} file: {str(e)}"
        return 0, error_msg

def query_documents(query: str) -> str:
    """Query the vector store for document information"""
    
    try:
        # Debug information
        doc_count = 0
        try:
            # This is a safer way to check document count that won't crash if structure changes
            if hasattr(st.session_state.vector_store, "_collection"):
                doc_count = st.session_state.vector_store._collection.count()
            else:
                # Alternative method if _collection doesn't exist
                doc_count = len(st.session_state.document_contents)
        except:
            doc_count = len(st.session_state.document_contents)
        
        # Check if there are documents in the vector store
        if doc_count == 0:
            return "No documents have been uploaded yet. Please upload a document first to enable document queries."
        
        # Find related documents
        try:
            relevant_docs = st.session_state.vector_store.similarity_search(query, k=4)
        except Exception as e:
            # Fallback to direct document search if vector search fails
            if len(st.session_state.document_contents) > 0:
                fallback_results = []
                for doc_name, content in st.session_state.document_contents.items():
                    fallback_results.append(f"Document: {doc_name}\nContent: {content[:1000]}...")
                
                context_text = "\n\n".join(fallback_results)
                
                # Log the issue but continue with fallback
                print(f"Vector search failed, using fallback: {str(e)}")
                
                return f"Vector search failed, using direct document content.\n\n{context_text}"
            else:
                return f"Error searching documents: {str(e)}"
        
        if not relevant_docs:
            # Fallback to direct document content search
            if len(st.session_state.document_contents) > 0:
                matching_docs = []
                for doc_name, content in st.session_state.document_contents.items():
                    # Simple keyword matching fallback
                    query_keywords = query.lower().split()
                    if any(keyword in content.lower() for keyword in query_keywords):
                        matching_docs.append(f"Document: {doc_name}\nContent: {content[:1000]}...")
                
                if matching_docs:
                    context_text = "\n\n".join(matching_docs)
                    return context_text
                else:
                    return "No relevant information found in the uploaded documents based on direct search."
            else:
                return "No relevant information found in the uploaded documents."
        
        # Create context from documents with source tracking
        doc_contexts = []
        for i, doc in enumerate(relevant_docs):
            source = doc.metadata.get("source", f"Document {i+1}")
            
            # Check if this is a CSV document with headers
            if "headers" in doc.metadata:
                headers_info = f"CSV Headers: {', '.join(doc.metadata['headers'])}\n"
                doc_contexts.append(f"Document: {source}\n{headers_info}Content: {doc.page_content}")
            else:
                doc_contexts.append(f"Document: {source}\nContent: {doc.page_content}")
        
        context_text = "\n\n".join(doc_contexts)
        
        return context_text
    except Exception as e:
        # Be more specific about the error and include debugging information
        error_message = f"Error querying documents: {str(e)}"
        print(error_message)  # For server logs
        
        # Include information about the document store state
        doc_info = "No document information available"
        if hasattr(st.session_state, "document_contents"):
            doc_names = list(st.session_state.document_contents.keys())
            doc_info = f"Available documents: {', '.join(doc_names) if doc_names else 'None'}"
        
        return f"{error_message}\n{doc_info}"


