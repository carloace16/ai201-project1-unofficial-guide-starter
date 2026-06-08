import chromadb
from chromadb.utils import embedding_functions
from ingest import load_documents, chunk_document

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "anime_guide"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}
)

def build_database():
    """Takes chunks from ingest.py and saves them to ChromaDB."""
    if collection.count() > 0:
        print(f"Database already has {collection.count()} chunks. Ready to search!")
        return

    print("Loading and chunking documents...")
    docs = load_documents()
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc["text"], doc["filename"]))

    print(f"Translating {len(all_chunks)} chunks into vectors and saving...")
    
    collection.add(
        documents=[c["text"] for c in all_chunks],
        metadatas=[{"source": c["source"]} for c in all_chunks],
        ids=[c["chunk_id"] for c in all_chunks]
    )
    print("Database built successfully!")

def retrieve(query, top_k=3):
    """Searches the database for the closest matching chunks."""
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # ChromaDB wraps results in a list. We take because we only asked 1 question.
    docs = results["documents"] if results["documents"] else []
    metas = results["metadatas"] if results["metadatas"] else []
    dists = results["distances"] if results["distances"] else []

    formatted_results = []
    
    for i in range(len(docs)):
        # 1. Safely grab the text
        doc_text = docs[i]
        
        # 2. Safely grab the source
        meta_item = metas[i] if i < len(metas) else {}
        source = meta_item.get("source", "Unknown") if isinstance(meta_item, dict) else "Unknown"
        
        # 3. Safely grab the distance number
        dist_item = dists[i] if i < len(dists) else 0.0
        distance = dist_item if isinstance(dist_item, list) else float(dist_item)
        
        formatted_results.append({
            "text": doc_text,
            "source": source,
            "distance": distance
        })

    return formatted_results


# This block tests the database if we run the file directly
if __name__ == "__main__":
    build_database()

    print("\n--- Testing Search ---")
    test_question = "Should I skip the Skypiea arc in One Piece?"
    print(f"Question: {test_question}\n")

    results = retrieve(test_question)
    
    for i, res in enumerate(results):
        # We removed the :.4f formatting so Python won't crash even if it's a list!
        print(f"Result {i+1} | Source: {res['source']} | Distance: {res['distance']}")
        print(f"{res['text']}\n")