from typing import Any, Dict, List, Optional, Tuple

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from config import (
    ADAPTER_PATH,
    BASE_MODEL,
    MAX_NEW_TOKENS,
    MIN_SCORE,
    TEMPERATURE,
    TOP_K,
)
from index import EmbeddingManager, VectorStore, build_index, get_embedding_manager, get_vectorstore
from prompts import rag_prompt, summary_prompt


class RAGRetriever:
    """Handle query-based retrieval from the vector store."""

    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingManager):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K,
        score_threshold: float = MIN_SCORE,
    ) -> List[Dict[str, Any]]:
        print(f"Retrieving documents for query: '{query}'")
        print(f"Top k: {top_k}, Score threshold: {score_threshold}")

        query_embedding = self.embedding_manager.generate_embeddings([query])[0]

        try:
            results = self.vector_store.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
            retrieved_docs: List[Dict[str, Any]] = []

            if not results.get("documents") or not results["documents"][0]:
                print("No documents retrieved.")
                return retrieved_docs

            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            ids = results["ids"][0]
            distances = results["distances"][0]

            for i, (doc_id, document, metadata, distance) in enumerate(
                zip(ids, documents, metadatas, distances)
            ):
                similarity_score = 1 - distance
                if similarity_score >= score_threshold:
                    retrieved_docs.append(
                        {
                            "id": doc_id,
                            "content": document,
                            "metadata": metadata,
                            "similarity_score": similarity_score,
                            "distance": distance,
                            "rank": i + 1,
                        }
                    )

            print(f"Retrieved {len(retrieved_docs)} documents (after filtering)")
            return retrieved_docs
        except Exception as exc:
            print(f"Error during retrieval: {exc}")
            return []


_retriever: Optional[RAGRetriever] = None
_pipeline: Optional["AdvancedRAGPipeline"] = None
_llm: Optional[Tuple[Any, Any]] = None


def get_retriever() -> RAGRetriever:
    global _retriever

    if _retriever is None:
        build_index()
        _retriever = RAGRetriever(get_vectorstore(), get_embedding_manager())

    return _retriever


def get_llm() -> Tuple[Any, Any]:
    global _llm

    if _llm is not None:
        return _llm

    print(f"Loading tokenizer: {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )

    print(f"Loading base model: {BASE_MODEL}")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype="auto",
    )

    print(f"Loading LoRA adapter: {ADAPTER_PATH}")
    model = PeftModel.from_pretrained(
        base_model,
        ADAPTER_PATH,
        device_map="auto",
        torch_dtype="auto",
    )
    model = model.merge_and_unload()

    _llm = (tokenizer, model)
    return _llm


def local_llm(prompt: str, max_new_tokens: int = MAX_NEW_TOKENS, temperature: float = TEMPERATURE) -> str:
    tokenizer, model = get_llm()
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=temperature > 0,
        pad_token_id=tokenizer.eos_token_id,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


class AdvancedRAGPipeline:
    def __init__(self, retriever: RAGRetriever):
        self.retriever = retriever
        self.history: List[Dict[str, Any]] = []

    def query(
        self,
        question: str,
        top_k: int = TOP_K,
        min_score: float = MIN_SCORE,
        summarize: bool = False,
    ) -> Dict[str, Any]:
        results = self.retriever.retrieve(question, top_k=top_k, score_threshold=min_score)

        if not results:
            answer = "No relevant context found."
            sources: List[Dict[str, Any]] = []
        else:
            context = "\n\n".join(doc["content"] for doc in results)
            sources = [
                {
                    "source": doc["metadata"].get("source_file", doc["metadata"].get("source", "unknown")),
                    "page": doc["metadata"].get("page", "unknown"),
                    "score": doc["similarity_score"],
                    "preview": doc["content"][:120] + "...",
                }
                for doc in results
            ]
            answer = local_llm(rag_prompt(context, question))

        citations = [
            f"[{i + 1}] {src['source']} (page {src['page']})"
            for i, src in enumerate(sources)
        ]
        answer_with_citations = (
            answer + "\n\nCitations:\n" + "\n".join(citations)
            if citations
            else answer
        )

        summary = local_llm(summary_prompt(answer)) if summarize and answer else None

        self.history.append(
            {
                "question": question,
                "answer": answer,
                "sources": sources,
                "summary": summary,
            }
        )
        self.history = self.history[-20:]

        return {
            "question": question,
            "answer": answer_with_citations,
            "sources": sources,
            "summary": summary,
            "history": self.history,
        }


def get_pipeline() -> AdvancedRAGPipeline:
    global _pipeline

    if _pipeline is None:
        _pipeline = AdvancedRAGPipeline(get_retriever())

    return _pipeline


def ai_model_response(query: str) -> str:
    return get_pipeline().query(query)["answer"]
