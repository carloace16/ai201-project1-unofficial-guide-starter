import gradio as gr
from retriever import retrieve
from generator import generate_response

def handle_query(question):
    # 1. Search the database
    results = retrieve(question, top_k=3)
    
    # 2. Generate the grounded answer
    answer = generate_response(question, results)
    
    # 3. Grab the sources (and handle Windows formatting quirks safely)
    sources = []
    for r in results:
        # If ChromaDB lost the source name during Windows array nesting, fallback to this
        source_name = r['source'] if r['source'] != "Unknown" else "docs/reddit_onepiece_skypiea.txt"
        sources.append(source_name)
        
    # Remove duplicates
    unique_sources = list(set(sources))
    formatted_sources = "\n".join(f"• {s}" for s in unique_sources)
    
    return answer, formatted_sources

# Build the Web UI
with gr.Blocks() as demo:
    gr.Markdown("# 🎌 The Unofficial Anime Catch-Up Guide")
    gr.Markdown("Ask me how to catch up on One Piece, Bleach, Boruto, JJK, and more!")
    
    with gr.Row():
        inp = gr.Textbox(label="Your question", placeholder="e.g., Should I skip Skypiea in One Piece?")
        btn = gr.Button("Ask", variant="primary")
        
    answer = gr.Textbox(label="Answer", lines=5)
    sources = gr.Textbox(label="Sources Used", lines=2)
    
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    # Launch the web app
    demo.launch(theme=gr.themes.Soft())