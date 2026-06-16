# Phi-3-mini Migration Report

Date: 2026-06-16

## Summary

The project has been shifted from Llama-2 references to `microsoft/Phi-3-mini-4k-instruct`.
The old Llama LoRA adapter is disabled by default because it is not compatible with the Phi-3-mini base model.

## Changes Made

- Updated `backend/config.py` to use `microsoft/Phi-3-mini-4k-instruct`.
- Disabled the old Llama adapter path by setting `ADAPTER_PATH = ""`.
- Updated `backend/rag.py` to:
  - cache the model under a Phi-specific folder name,
  - skip adapters unless they match the configured base model,
  - support CPU loading without 4-bit quantization,
  - use the tokenizer chat template for Phi-3-mini prompts,
  - decode only newly generated tokens.
- Replaced duplicated eager model-loading code in `backend/model.py` and `backend/testmodel.py` with wrappers around the main RAG runtime.
- Updated `train.ipynb` model and prompt examples to Phi-3-mini format.
- Added missing backend dependencies to `requirement.txt`.
- Fixed the React hook lint warning in `ui/src/App.tsx` by memoizing the active chat messages.

## Verification

- `rg -n "Llama|llama|LLaMA|NousResearch/Llama|Llama-2|llama2|\[INST\]" .`
  - Result: no matches.
- `python3 -m py_compile backend/*.py`
  - Result: passed.
- `npm run lint` in `ui`
  - Result: passed.
- `npm run build` in `ui`
  - Result: passed.

## Notes

- `npm install` was required because `ui/node_modules` was incomplete.
- `npm install` reported 12 dependency audit findings: 1 low, 5 moderate, 6 high.
- A real model download/runtime smoke test was not run, because it would require downloading the Phi-3-mini weights and enough local compute to load them.
