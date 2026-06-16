
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from config import MIN_SCORE, TOP_K
from index import initialize_vectorstore
from rag import get_llm, get_pipeline, get_retriever

app = FastAPI()

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class Query(BaseModel):
    query: str
    top_k: int | None = None
    min_score: float | None = None


@app.on_event("startup")
def startup():
    print("Starting RAG pipeline...")
    initialize_vectorstore()
    get_pipeline()
    print("Loading model...")
    get_llm()
    print("Application ready")

# GET route (test purpose)
@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running!"}

# POST route (main AI query)
@app.post("/query")
def query_model(q: Query):
    print("query:", q.query)
    pipeline = get_pipeline()
    result = pipeline.query(
        q.query,
        top_k=q.top_k if q.top_k is not None else TOP_K,
        min_score=q.min_score if q.min_score is not None else MIN_SCORE,
    )
    print("answer:", result["answer"])
    print("sources:", result["sources"])
    return result


@app.get("/retriever/status")
def retriever_status():
    return get_retriever().status()


@app.post("/retriever/test")
def test_retriever(q: Query):
    retriever = get_retriever()
    docs = retriever.retrieve(
        q.query,
        top_k=q.top_k if q.top_k is not None else TOP_K,
        score_threshold=q.min_score if q.min_score is not None else MIN_SCORE,
    )
    return {
        "query": q.query,
        "retriever": retriever.status(),
        "sources": [
            {
                "rank": doc["rank"],
                "score": doc["semantic_score"],
                "distance": doc["distance"],
                "source": doc["metadata"].get("source_file", doc["metadata"].get("source", "unknown")),
                "page": doc["metadata"].get("page", "unknown"),
                "preview": doc["content"][:200],
            }
            for doc in docs
        ],
    }
