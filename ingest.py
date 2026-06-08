import os

DOCS_PATH = "./docs"

def load_documents():
    """Load all .txt documents from the docs folder."""
    documents = []
    
    # This is just like fs.readdirSync() in Node.js
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            
            # Open and read the file
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Basic cleaning: remove weird double-spaces or newlines
            clean_text = " ".join(text.split())
            
            documents.append({
                "filename": filename,
                "text": clean_text,
            })
            
    print(f"Loaded {len(documents)} document(s).")
    return documents


def chunk_document(text, filename):
    """Split document into chunks using a sliding window."""
    chunk_size = 250
    overlap = 50
    min_length = 30  # Ignores weird tiny fragments

    chunks = []
    start = 0
    counter = 0

    # This is the sliding window algorithm using Python's string slicing [start:end]
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()

        if len(chunk_text) >= min_length:
            chunks.append({
                "text": chunk_text,
                "source": filename,
                "chunk_id": f"{filename}_{counter}",
            })
            counter += 1

        # Move the window forward, but step back by 50 to create the overlap
        start += (chunk_size - overlap)

    return chunks


# This block only runs if we execute this file directly to test it
if __name__ == "__main__":
    docs = load_documents()
    
    all_chunks = []
    for doc in docs:
        doc_chunks = chunk_document(doc["text"], doc["filename"])
        all_chunks.extend(doc_chunks)
        
    print(f"Generated {len(all_chunks)} total chunks.")
    print("\n--- Here are 5 sample chunks to inspect ---")
    
    # Print the first 5 chunks so we can verify they look good
    for i in range(min(5, len(all_chunks))):
        print(f"\n[Chunk {i} | Source: {all_chunks[i]['source']}]")
        print(all_chunks[i]["text"])