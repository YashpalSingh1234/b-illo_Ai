from pathlib import Path

# Paths are resolved from the project root so commands work from any directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ===== MODEL =====
BASE_MODEL = "NousResearch/Llama-2-7b-chat-hf"
ADAPTER_PATH = str(PROJECT_ROOT / "Llama-2-7b-chat-finetune")

# ===== VECTOR DB =====
COLLECTION_NAME = "pdf_document"
VECTOR_DB_PATH = str(PROJECT_ROOT / "data" / "vector_store")
PDF_DIR = str(PROJECT_ROOT / "data" / "pdf")

# ===== EMBEDDING =====
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# ===== CHUNK SETTINGS =====
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ===== RETRIEVAL =====
TOP_K = 5
MIN_SCORE = 0.2

# ===== GENERATION =====
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.3
