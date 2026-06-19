import os
import uuid
from typing import Any, List

import chromadb
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from sentence_transformers import SentenceTransformer

from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    PDF_DIR,
    VECTOR_DB_PATH,
)


def chunk_documents(documents, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    """
    Split documents into smaller chunks for better RAG performance.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(split_docs)} chunks")

    if split_docs:
        print("\nExample chunk:")
        print(f"Content: {split_docs[0].page_content[:200]}...")
        print(f"Metadata: {split_docs[0].metadata}")

    return split_docs


def create_chunks():
    dir_loader = DirectoryLoader(
        PDF_DIR,
        glob="**/*.pdf",
        loader_cls=PyMuPDFLoader,
        show_progress=False,
    )
    pdf_document = dir_loader.load()
    return chunk_documents(pdf_document)


class EmbeddingManager:
    """Handles document embedding generation using SentenceTransformer."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(
                "Model loaded successfully. "
                f"Embedding dimension: {self.model.get_sentence_embedding_dimension()}"
            )
        except Exception as exc:
            print(f"Error loading model {self.model_name}: {exc}")
            raise

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        if not self.model:
            raise ValueError("Model not loaded.")

        print(f"Generating embeddings for {len(texts)} texts.")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"Generated embedding with shape: {embeddings.shape}")
        return embeddings


_embedding_manager = None


def get_embedding_manager():
    global _embedding_manager

    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager()

    return _embedding_manager


class VectorStore:
    """Manages document embeddings in a ChromaDB vector store."""

    def __init__(
        self,
        collection_name: str = COLLECTION_NAME,
        persist_directory: str = VECTOR_DB_PATH,
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_store()

    def _initialize_store(self):
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "PDF document embeddings for RAG"},
            )
            print(f"Vector store initialized. Collection: {self.collection_name}")
            print(f"Existing documents in collection: {self.collection.count()}")
        except Exception as exc:
            print(f"Error initializing vector store: {exc}")
            raise

    def add_documents(self, documents: List[Any], embeddings: np.ndarray):
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")

        print(f"Adding {len(documents)} documents to vector store...")

        ids = []
        metadatas = []
        documents_text = []
        embeddings_list = []

        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)

            metadata = dict(doc.metadata)
            metadata["doc_index"] = i
            metadata["content_length"] = len(doc.page_content)
            if "page" in metadata and isinstance(metadata["page"], int):
                metadata["page"] = metadata["page"] + 1
            metadatas.append(metadata)

            documents_text.append(doc.page_content)
            embeddings_list.append(embedding.tolist())

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_text,
            )
            print(f"Successfully added {len(documents)} documents to vector store.")
            print(f"Total documents in collection: {self.collection.count()}")
        except Exception as exc:
            print(f"Error adding documents to vector store: {exc}")
            raise


_vectorstore = None
_vectorstore_initialized = False


def get_vectorstore():
    global _vectorstore

    if _vectorstore is None:
        _vectorstore = VectorStore()

    return _vectorstore


def initialize_vectorstore():
    global _vectorstore_initialized

    if _vectorstore_initialized:
        return get_vectorstore()

    print("Initializing Chroma...")
    print(f"VECTOR_DB_PATH: {VECTOR_DB_PATH}")
    print(f"COLLECTION_NAME: {COLLECTION_NAME}")
    print(f"PDF_DIR: {PDF_DIR}")
    print(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")
    print(f"CHUNK_SIZE: {CHUNK_SIZE}")
    print(f"CHUNK_OVERLAP: {CHUNK_OVERLAP}")

    vector_db_exists = os.path.exists(VECTOR_DB_PATH)
    vectorstore = get_vectorstore()

    if vector_db_exists and vectorstore.collection.count() > 0:
        print("Using existing vectorstore")
        print("Vector store initialized")
        _vectorstore_initialized = True
        return vectorstore

    print("No vectorstore found")
    print("Creating vectorstore...")
    print("Loading PDFs...")
    chunks = create_chunks()

    if not chunks:
        print("No PDF chunks found. Vectorstore is empty.")
        print("Vector store initialized")
        _vectorstore_initialized = True
        return vectorstore

    print("Creating embeddings...")
    text = [doc.page_content for doc in chunks]
    embeddings = get_embedding_manager().generate_embeddings(text)

    print("Persisting database...")
    vectorstore.add_documents(chunks, embeddings)
    print("Vectorstore created")
    print("Vector store initialized")
    _vectorstore_initialized = True
    return vectorstore


def build_index():
    return initialize_vectorstore()
