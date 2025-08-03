import ollama

def generate_response_stream(context: str, query: str):
    prompt = f"""
You are an AI assistant answering questions based ONLY on the given project document below.

--- PROJECT CONTEXT START ---
{context}
--- PROJECT CONTEXT END ---

Now answer the following user question using the above context only. If the answer is not found in the context, say "I couldn't find that in the project document."

User Question: {query}
Answer:
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in response:
        if 'message' in chunk and 'content' in chunk['message']:
            yield chunk['message']['content']
