import os
from groq import Groq
from dotenv import load_dotenv

# Load your API key from the .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

_client = Groq(api_key=GROQ_API_KEY)

def generate_response(query, retrieved_chunks):
    if not retrieved_chunks:
        return "I don't have enough information on that."

    # 1. Mash all the retrieved text together so the AI can read it
    context_text = ""
    for chunk in retrieved_chunks:
        # We wrap it in string format just in case ChromaDB hands us a weird array
        context_text += f"{str(chunk['text'])}\n\n"

    # 2. The Strict System Prompt (Grounding)
    system_prompt = (
        "You are an expert Anime and Manga Guide. "
        "Answer the user's question using ONLY the provided text below. "
        "If the answer is not in the text, say 'I don't have enough information on that.' "
        "Do not use outside knowledge or guess."
    )

    # 3. Combine the context and the question
    user_message = f"Here is the context:\n{context_text}\n\nQuestion: {query}"

    # 4. Call the Groq AI
    response = _client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content