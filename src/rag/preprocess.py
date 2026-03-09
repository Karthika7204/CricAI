import os
import json
import faiss
import pickle
import argparse
import numpy as np
from pathlib import Path
from embedding import EmbeddingEngine
from chunker import get_chunks_with_tags

def run_preprocessing(match_id, data_dir="d:/CricAI/data"):
    """
    V5 Preprocessing Pipeline:
    - Loads optimized JSON
    - Generates tagged narrative chunks
    - PERSISTS: index.faiss, chunks.pkl, metadata.pkl
    """
    match_folder = Path(data_dir) / "processed" / "t20" / "matches" / match_id
    summary_path = match_folder / "structured_summary.json"
    
    if not summary_path.exists():
        print(f"Error: {summary_path} not found.")
        return

    # 1. Load Data
    with open(summary_path, 'r') as f:
        data = json.load(f)

    # 2. Extract Fast-Track Metadata (for rule-based router)
    # This metadata will be used by the router for instant answers
    fast_meta = {
        "winner": data['Match_Result'].get('winner'),
        "score": data['Match_Result'].get('summary'),
        "margin": data['Match_Result'].get('margin'),
        "margin_type": data['Match_Result'].get('margin_type'),
        "venue": data['match_context'].get('venue'),
        "date": data['match_context'].get('date'),
        "captains": data['match_context'].get('Teams', {}),
        "teams": list(data['match_context'].get('Teams', {}).keys()),
        "all_players": list(set([imp['player'] for imp in data.get('Detailed_Impact_Analysis', [])]))
    }

    # 3. Generate Tagged Narrative Chunks
    chunks_with_tags = get_chunks_with_tags(data)
    embeddings_list = []
    
    engine = EmbeddingEngine()
    
    for item in chunks_with_tags:
        vec = engine.encode(item['text'])
        embeddings_list.append(vec)
    
    embeddings_np = np.vstack(embeddings_list).astype('float32')

    # 4. Build FAISS Index
    dim = engine.get_dimension()
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings_np)

    # 5. Persist
    faiss.write_index(index, str(match_folder / "index.faiss"))
    
    with open(match_folder / "chunks.pkl", 'wb') as f:
        pickle.dump(chunks_with_tags, f)
        
    with open(match_folder / "metadata.pkl", 'wb') as f:
        pickle.dump(fast_meta, f)

    print(f"✅ V5 Indexing Complete for Match {match_id}")
    print(f"   Chunks: {len(chunks_with_tags)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match_id", required=True)
    args = parser.parse_args()
    
    run_preprocessing(args.match_id)
