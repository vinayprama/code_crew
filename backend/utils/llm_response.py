
import ollama

def generate_response_stream(context: str, query: str):
    prompt = f"""You are a helpful assistant. Use the context to answer the user's query.

    Context: {context}

    Query: {query}

    Answer:"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in response:
        if 'message' in chunk and 'content' in chunk['message']:
            yield chunk['message']['content']

