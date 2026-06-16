# prompts.py


def rag_prompt(
    context,
    question
):

    return f"""
Answer only using
the provided context.

If answer is not found
inside context then say:

'I could not find this
inside the uploaded
documents.'

Context:
{context}

Question:
{question}

Answer:
"""


def summary_prompt(
    answer
):

    return f"""
Summarize
the following answer
in 2 sentences.

Answer:

{answer}
"""


def fallback_prompt(question):
    return f"""
Answer the user's question using your general knowledge.
Do not claim that the answer came from the uploaded documents.

Question:
{question}

Answer:
"""
