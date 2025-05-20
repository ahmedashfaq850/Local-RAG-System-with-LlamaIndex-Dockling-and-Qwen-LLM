import os
from typing import Dict, Any
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import PromptTemplate
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.docling import DoclingReader
from llama_index.core.node_parser import MarkdownNodeParser


class RAGEngine:
    """Main RAG engine class that handles document processing and querying."""

    def __init__(self):
        """Initialize the RAG engine with default settings."""
        self.llm = None
        self.embed_model = None
        self.query_engine = None
        self._initialize_models()

    def _initialize_models(self):
        """Initialize the LLM and embedding models."""
        # Initialize the LLM (Qwen 2.5 14B model)
        self.llm = Ollama(model="qwen2.5:14b", request_timeout=120.0)

        # Initialize the embedding model (BAAI/bge-large-en-v1.5)
        self.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-large-en-v1.5", trust_remote_code=True
        )

        # Set global settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

    def process_document(self, file_path: str) -> None:
        """
        Process a document and create the query engine.

        Args:
            file_path: Path to the document to process
        """
        # Load document using DoclingReader for Excel files
        reader = DoclingReader()
        loader = SimpleDirectoryReader(
            input_dir=os.path.dirname(file_path),
            file_extractor={".xlsx": reader},
        )
        docs = loader.load_data()

        # Create document index
        node_parser = MarkdownNodeParser()
        index = VectorStoreIndex.from_documents(
            documents=docs,
            transformations=[node_parser],
            show_progress=True,
        )

        # Create query engine with custom prompt
        self.query_engine = index.as_query_engine(streaming=True)
        self._setup_custom_prompt()

    def _setup_custom_prompt(self):
        """Set up the custom prompt template for the query engine."""
        qa_prompt_tmpl_str = (
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information above I want you to think step by step to answer the query in a highly precise and crisp manner focused on the final answer, incase case you don't know the answer say 'I don't know!'.\n"
            "Query: {query_str}\n"
            "/no_think"
            "Answer: "
        )
        qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

        self.query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
        )

    def query(self, query_text: str) -> Any:
        """
        Query the RAG system.

        Args:
            query_text: The query text to process

        Returns:
            The query response
        """
        if not self.query_engine:
            raise ValueError(
                "No document has been processed yet. Please process a document first."
            )

        return self.query_engine.query(query_text)
