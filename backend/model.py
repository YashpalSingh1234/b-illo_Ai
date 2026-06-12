# model.py
from peft import PeftModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

# Quantization setup (for GPU memory efficiency)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,   # can change to 8bit if 4bit fails
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16
)

# Base model + adapter path
BASE_MODEL = "NousResearch/Llama-2-7b-chat-hf"
ADAPTER_PATH = "/home/ravikant-sharma/Loara/Llama-2-7b-chat-finetune"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

# Load base model in 4bit
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="cuda:0",    # put on GPU
    torch_dtype="auto"
)

# Attach LoRA adapter
model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_PATH,
    device_map="cuda:0",
    torch_dtype="auto"
)

# Merge LoRA for inference
model = model.merge_and_unload()

# Build pipeline
pipe = pipeline(
    task="text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=500,
    # device=0  
)

import re
from collections import defaultdict

##checking variable #######################

sess_id = 0

# Simple in-memory memory store

SESSIONS = defaultdict(lambda: {"messages": [], "facts": {}})
MAX_TURNS = 18

def _trim_history(state):
    if len(state["messages"]) > 2 * MAX_TURNS:
        state["messages"] = state["messages"][-2 * MAX_TURNS:]

def _extract_and_update_facts(state, user_text: str):
    """
    Naive fact extraction. Keeps info but never forces response.
    """
    # detect name statements
    m = re.search(r"(?:mera?\s+(?:naam|name)\s+|my\s+name\s+is\s+)([A-Za-z][A-Za-z .'\-]{0,40})", user_text, re.IGNORECASE)
    if m:
        state["facts"]["name"] = m.group(1).strip().title()

def _build_system_prompt(state) -> str:
    lines = ["You are a helpful assistant."]
    lines.append("Always format your response in proper **Markdown** syntax.")
    if state["facts"]:
        lines.append("Here are some facts you know about the user:")
        for k, v in state["facts"].items():
            lines.append(f"- {k}: {v}")
        lines.append("Use these facts naturally in conversation if relevant.")
    else:
        lines.append("You don’t currently know personal facts about the user.")
    return "\n".join(lines)

def _to_chat_messages(state, user_text: str):
    sys = _build_system_prompt(state)
    chat = [{"role": "system", "content": sys}]
    chat.extend(state["messages"])
    chat.append({"role": "user", "content": user_text})
    return chat

def ai_model_response(query: str, session_id: str = "default") -> str:
    global SESSIONS
    state = SESSIONS[session_id]

    # Update facts
    _extract_and_update_facts(state, query)

    # Build chat prompt
    chat = _to_chat_messages(state, query)
    try:
        prompt = tokenizer.apply_chat_template(
            chat,
            tokenize=False,
            add_generation_prompt=True,
        )
    except Exception:
        # Fallback manual format
        sys = chat[0]["content"]
        prompt = f"<s>[INST] <<SYS>>\n{sys}\n<</SYS>>\n{chat[1]['content']} [/INST]"
        for msg in chat[2:-1]:
            if msg["role"] == "assistant":
                prompt += f" {msg['content']}"
            else:
                prompt += f"\n<s>[INST] {msg['content']} [/INST]"
        prompt += f"\n<s>[INST] {chat[-1]['content']} [/INST]"

    # Generate
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    out = pipe(
        prompt,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        max_new_tokens=256,
        return_full_text=False,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )[0]["generated_text"].strip()

    # Wrap output in Markdown code block
    out_markdown = f"{out}\n"

    # Save history
    state["messages"].append({"role": "user", "content": query})
    state["messages"].append({"role": "assistant", "content": out_markdown})
    _trim_history(state)

    return out_markdown


def main():
    
    while True:
        prmt = input("Enter your prompt: ")
        if prmt.lower() in ["exit", "quit"]:
            break
        print("Response:", ai_model_response(prmt), " ++ ", sess_id)

# Run the function
if __name__ == "__main__":
    main()