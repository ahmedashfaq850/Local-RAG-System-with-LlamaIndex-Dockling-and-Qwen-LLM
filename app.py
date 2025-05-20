import streamlit as st
import uuid
import gc
from typing import Dict, Any

from rag.core import RAGEngine
from rag.utils import save_uploaded_file, display_excel

# Page config
st.set_page_config(
    page_title="Excel RAG Chat",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        padding: 2rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
    }
    .chat-message.assistant {
        background-color: #475063;
    }
    .chat-message .content {
        display: flex;
        margin-top: 0.5rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 0.5rem;
        height: 3rem;
        font-size: 1rem;
        font-weight: 600;
    }
    .stTextInput input {
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    .upload-section {
        background-color: #1e1e1e;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #2e7d32;
        color: white;
        margin: 1rem 0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache: Dict[str, Any] = {}
    st.session_state.messages = []

session_id = st.session_state.id


def reset_chat():
    """Reset the chat history and clear memory."""
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()


# Sidebar
with st.sidebar:
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='font-size: 1.5rem; margin-bottom: 0.5rem;'>📊 Excel RAG Chat</h1>
            <p style='color: #666; font-size: 0.9rem;'>Chat with your Excel files using AI</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📁 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose your Excel file",
        type=["xlsx", "xls"],
        help="Upload an Excel file to start chatting",
    )

    if uploaded_file:
        try:
            with st.spinner("Processing your document..."):
                # Save uploaded file
                temp_dir, file_path = save_uploaded_file(uploaded_file)

                file_key = f"{session_id}-{uploaded_file.name}"

                # Process document if not in cache
                if file_key not in st.session_state.file_cache:
                    rag_engine = RAGEngine()
                    rag_engine.process_document(file_path)
                    st.session_state.file_cache[file_key] = rag_engine
                else:
                    rag_engine = st.session_state.file_cache[file_key]

                st.markdown(
                    """
                    <div class='success-message'>
                        <h3 style='margin: 0;'>✨ Ready to Chat!</h3>
                        <p style='margin: 0.5rem 0 0 0;'>Your document has been processed successfully.</p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                # Display Excel preview
                st.markdown("### 📋 Document Preview")
                df = display_excel(uploaded_file)
                if df is not None:
                    st.dataframe(df, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()

# Main content
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>Excel RAG Chat</h1>
        <p style='color: #666; font-size: 1.1rem;'>Powered by Qwen 2.5 14B & Dockling 🐥</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Single centered Clear Chat button
st.markdown(
    """
    <div style='display: flex; justify-content: center; margin-bottom: 2rem;'>
        <form action="#" method="post">
            <button type="submit" name="clear_chat" style="background: none; border: 2px solid #444; border-radius: 0.5rem; padding: 1rem 2.5rem; font-size: 1.2rem; font-weight: 600; color: white; cursor: pointer; display: flex; align-items: center; gap: 0.5rem;">
                🗑️ Clear Chat
            </button>
        </form>
    </div>
""",
    unsafe_allow_html=True,
)
if st.session_state.get("clear_chat_clicked", False):
    reset_chat()
    st.session_state["clear_chat_clicked"] = False
    st.rerun()
if "clear_chat" in st.query_params:
    st.session_state["clear_chat_clicked"] = True

# Custom chat rendering
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f"""
                <div style='display: flex; justify-content: flex-end; margin-bottom: 1rem;'>
                    <div style='background: #2b313e; color: white; padding: 1rem 1.5rem; border-radius: 1.5rem 1.5rem 0 1.5rem; max-width: 70%; box-shadow: 0 2px 8px #0002;'>
                        <span style='font-size: 1.1rem;'>{message['content']}</span>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div style='display: flex; justify-content: flex-start; margin-bottom: 1rem;'>
                    <div style='background: #475063; color: white; padding: 1rem 1.5rem; border-radius: 1.5rem 1.5rem 1.5rem 0; max-width: 70%; box-shadow: 0 2px 8px #0002;'>
                        <span style='font-size: 1.1rem;'>{message['content']}</span>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

# Chat input
st.markdown("<br>", unsafe_allow_html=True)
if prompt := st.chat_input("Ask a question about your Excel data..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show user message on right
    st.markdown(
        f"""
        <div style='display: flex; justify-content: flex-end; margin-bottom: 1rem;'>
            <div style='background: #2b313e; color: white; padding: 1rem 1.5rem; border-radius: 1.5rem 1.5rem 0 1.5rem; max-width: 70%; box-shadow: 0 2px 8px #0002;'>
                <span style='font-size: 1.1rem;'>{prompt}</span>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Get RAG engine from cache
    if not st.session_state.file_cache:
        st.error("Please upload a document first!")
        st.stop()

    rag_engine = next(iter(st.session_state.file_cache.values()))

    # Display assistant response
    with st.spinner("Thinking..."):
        full_response = ""
        streaming_response = rag_engine.query(prompt)
        for chunk in streaming_response.response_gen:
            if "<think>" in chunk or "</think>" in chunk:
                continue
            full_response += chunk
        st.markdown(
            f"""
            <div style='display: flex; justify-content: flex-start; margin-bottom: 1rem;'>
                <div style='background: #475063; color: white; padding: 1rem 1.5rem; border-radius: 1.5rem 1.5rem 1.5rem 0; max-width: 70%; box-shadow: 0 2px 8px #0002;'>
                    <span style='font-size: 1.1rem;'>{full_response}</span>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
