"""Small manual smoke-test entrypoint for the configured local model."""

from rag import ai_model_response, get_llm


def main():
    get_llm()
    while True:
        prompt = input("Enter your prompt: ")
        if prompt.lower() in ["exit", "quit"]:
            break
        print("Response:", ai_model_response(prompt))


if __name__ == "__main__":
    main()
