import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
from peft import PeftModel
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from config import (
    ADAPTER_PATH,
    BASE_MODEL,
    MAX_NEW_TOKENS,
    MODEL_CACHE_DIR,
    
    MIN_SCORE,
    TEMPERATURE,
    TOP_K,
    USE_LOCAL_MODEL_CACHE,
)
from index import EmbeddingManager, VectorStore, initialize_vectorstore, get_embedding_manager
from prompts import fallback_prompt, rag_prompt, summary_prompt


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


def _adapter_matches_base_model(adapter_path: str, base_model: str) -> bool:
    if not adapter_path:
        return False

    adapter_config_path = Path(adapter_path) / "adapter_config.json"

    if not adapter_config_path.exists():
        return False

    with adapter_config_path.open("r", encoding="utf-8") as config_file:
        adapter_config = json.load(config_file)

    adapter_base_model = adapter_config.get("base_model_name_or_path")
    return adapter_base_model == base_model


def _local_model_path() -> Path:
    safe_model_name = BASE_MODEL.replace("/", "--")
    return Path(MODEL_CACHE_DIR) / safe_model_name


def _get_model_dtype():
    return torch.float16 if torch.cuda.is_available() else torch.float32


def _load_phi3_config(model_path: str):
    config = AutoConfig.from_pretrained(model_path, trust_remote_code=False)
    rope_scaling = getattr(config, "rope_scaling", None)

    if isinstance(rope_scaling, dict) and "type" not in rope_scaling:
        rope_type = rope_scaling.get("rope_type", "default")
        config.rope_scaling = {**rope_scaling, "type": rope_type}

    config._attn_implementation = "eager"
    return config


def get_retriever() -> RAGRetriever:
    global _retriever

    if _retriever is None:
        _retriever = RAGRetriever(initialize_vectorstore(), get_embedding_manager())

    return _retriever


def get_llm() -> Tuple[Any, Any]:
    global _llm

    if _llm is not None:
        return _llm

    use_adapter = _adapter_matches_base_model(ADAPTER_PATH, BASE_MODEL)
    local_model_path = _local_model_path()
    local_model_exists = (
        USE_LOCAL_MODEL_CACHE
        and local_model_path.exists()
        and (local_model_path / "config.json").exists()
    )

    if local_model_exists:
        base_model_path = str(local_model_path)
        print("Loading model from local cache...")
        tokenizer = AutoTokenizer.from_pretrained(
            base_model_path,
            local_files_only=True,
            trust_remote_code=False,
        )
    else:
        base_model_path = BASE_MODEL
        if USE_LOCAL_MODEL_CACHE:
            print("Model not found in project cache.")
        print("Loading model from Hugging Face cache/hub...")
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_kwargs: Dict[str, Any] = {
        "attn_implementation": "eager",
        "config": _load_phi3_config(base_model_path),
        "dtype": _get_model_dtype(),
        "trust_remote_code": False,
    }
    if torch.cuda.is_available():
        model_kwargs.update(
            {
                "quantization_config": BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_compute_dtype=torch.float16,
                ),
                "device_map": "auto",
            }
        )
    else:
        print("CUDA is not available. Loading model on CPU without 4-bit quantization.")

    if local_model_exists:
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            **model_kwargs,
            local_files_only=True,
        )
    else:
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            **model_kwargs,
        )
        if USE_LOCAL_MODEL_CACHE:
            local_model_path.mkdir(parents=True, exist_ok=True)
            tokenizer.save_pretrained(local_model_path)
            base_model.save_pretrained(local_model_path)
            print("Model saved locally.")

    if use_adapter:
        print(f"Loading LoRA adapter from local files: {ADAPTER_PATH}")
        model = PeftModel.from_pretrained(
            base_model,
            ADAPTER_PATH,
            device_map="auto" if torch.cuda.is_available() else None,
            dtype="auto",
            local_files_only=True,
        )
        model = model.merge_and_unload()
    else:
        if ADAPTER_PATH:
            print(
                f"Skipping LoRA adapter because it was not trained for {BASE_MODEL}: "
                f"{ADAPTER_PATH}"
            )
        else:
            print("No LoRA adapter configured. Using the Phi-3-mini base model.")
        print(
            f"Loaded base model: {BASE_MODEL}"
        )
        model = base_model

    _llm = (tokenizer, model)
    return _llm


def local_llm(prompt: str, max_new_tokens: int = MAX_NEW_TOKENS, temperature: float = TEMPERATURE) -> str:
    tokenizer, model = get_llm()
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    try:
        formatted_prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )
    except Exception:
        formatted_prompt = prompt

    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=temperature > 0,
        pad_token_id=tokenizer.eos_token_id,
    )
    generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
    return tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()


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
            answer = local_llm(fallback_prompt(question))
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
            "answer": answer,
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
