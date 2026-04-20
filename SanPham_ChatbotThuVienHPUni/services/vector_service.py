import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config import CHUNKS_FILE, FAISS_INDEX, VECTOR_DIR
from services.pdf_service import batch_process_pdfs, split_into_chunks

# Initialize sentence transformer model
print("🔄 Loading sentence transformer model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("✅ Model loaded successfully")

# BUILD VECTOR STORE FROM PDFS
def build_vector_store_from_pdfs():
    """
    Process all PDFs and build FAISS index
    Returns:
        Number of chunks processed
    """
    print("🔄 Building vector store from PDFs...")
    
    # Process all PDFs
    pdf_results = batch_process_pdfs()
    
    # Collect all chunks
    all_chunks = []
    chunk_metadata = []  # Store which PDF each chunk came from
    
    for result in pdf_results:
        if result["success"]:
            for chunk in result["chunks"]:
                all_chunks.append(chunk)
                chunk_metadata.append({
                    "filename": result["filename"],
                    "metadata": result["metadata"]
                })
    
    if not all_chunks:
        print("⚠️ No chunks to process")
        return 0
    
    # Save chunks
    os.makedirs(VECTOR_DIR, exist_ok=True)
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump({
            "chunks": all_chunks,
            "metadata": chunk_metadata
        }, f)
    
    # Create embeddings
    print(f"🔄 Creating embeddings for {len(all_chunks)} chunks...")
    embeddings = model.encode(all_chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")
    
    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save index
    faiss.write_index(index, FAISS_INDEX)
    
    print(f"✅ Vector store built with {len(all_chunks)} chunks")
    return len(all_chunks)

# BUILD VECTOR STORE FROM TEXTS
def build_vector_store_from_texts(texts, metadata=None):
    """
    Build FAISS index from list of texts
    Args:
        texts: List of text chunks
        metadata: Optional metadata for each chunk
    Returns:
        Number of chunks processed
    """
    if not texts:
        return 0
    
    if metadata is None:
        metadata = [{} for _ in texts]
    
    # Save chunks and metadata
    os.makedirs(VECTOR_DIR, exist_ok=True)
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump({
            "chunks": texts,
            "metadata": metadata
        }, f)
    
    # Create embeddings
    print(f"🔄 Creating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")
    
    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save index
    faiss.write_index(index, FAISS_INDEX)
    
    return len(texts)

# SEARCH VECTOR STORE
def search_vector_store(query, top_k=5):
    """
    Search for similar chunks in vector store
    Args:
        query: Search query
        top_k: Number of results to return
    Returns:
        List of (chunk, score, metadata) tuples
    """
    if not os.path.exists(FAISS_INDEX) or not os.path.exists(CHUNKS_FILE):
        print("⚠️ Vector store not found")
        return []
    
    try:
        # Load index
        index = faiss.read_index(FAISS_INDEX)
        
        # Load chunks and metadata
        with open(CHUNKS_FILE, "rb") as f:
            data = pickle.load(f)
            chunks = data["chunks"]
            metadata = data.get("metadata", [{} for _ in chunks])
        
        # Create query embedding
        query_vec = model.encode([query]).astype("float32")
        
        # Search
        distances, indices = index.search(query_vec, min(top_k, len(chunks)))
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(chunks):
                score = 1.0 / (1.0 + distances[0][i])  # Convert distance to similarity score
                results.append({
                    "chunk": chunks[idx],
                    "score": float(score),
                    "metadata": metadata[idx] if idx < len(metadata) else {}
                })
        
        return results
        
    except Exception as e:
        print(f"❌ Error searching vector store: {e}")
        return []

# ADD TEXTS TO EXISTING STORE
def add_to_vector_store(new_texts, new_metadata=None):
    """
    Add new texts to existing vector store
    Args:
        new_texts: List of new text chunks
        new_metadata: Optional metadata for new chunks
    Returns:
        Total number of chunks after addition
    """
    if not os.path.exists(CHUNKS_FILE):
        # No existing store, create new
        return build_vector_store_from_texts(new_texts, new_metadata)
    
    # Load existing data
    with open(CHUNKS_FILE, "rb") as f:
        data = pickle.load(f)
        existing_chunks = data["chunks"]
        existing_metadata = data.get("metadata", [{} for _ in existing_chunks])
    
    if new_metadata is None:
        new_metadata = [{} for _ in new_texts]
    
    # Combine
    all_chunks = existing_chunks + new_texts
    all_metadata = existing_metadata + new_metadata
    
    # Rebuild index (simplest approach)
    return build_vector_store_from_texts(all_chunks, all_metadata)

# GET VECTOR STORE INFO
def get_vector_store_info():
    """
    Get information about the vector store
    Returns:
        Dictionary with store info
    """
    if not os.path.exists(FAISS_INDEX) or not os.path.exists(CHUNKS_FILE):
        return {
            "exists": False,
            "num_chunks": 0,
            "dimension": 0
        }
    
    try:
        index = faiss.read_index(FAISS_INDEX)
        
        with open(CHUNKS_FILE, "rb") as f:
            data = pickle.load(f)
            chunks = data["chunks"]
        
        return {
            "exists": True,
            "num_chunks": len(chunks),
            "dimension": index.d,
            "index_size": os.path.getsize(FAISS_INDEX),
            "chunks_file_size": os.path.getsize(CHUNKS_FILE)
        }
        
    except Exception as e:
        return {
            "exists": False,
            "error": str(e),
            "num_chunks": 0
        }

# SEMANTIC SEARCH
def semantic_search(query, threshold=0.5, top_k=10):
    """
    Perform semantic search with relevance threshold
    Args:
        query: Search query
        threshold: Minimum similarity score (0-1)
        top_k: Maximum number of results
    Returns:
        List of relevant chunks
    """
    results = search_vector_store(query, top_k=top_k)
    
    # Filter by threshold
    filtered = [r for r in results if r["score"] >= threshold]
    
    return filtered

# DELETE VECTOR STORE
def delete_vector_store():
    """
    Delete vector store files
    Returns:
        Boolean indicating success
    """
    try:
        if os.path.exists(FAISS_INDEX):
            os.remove(FAISS_INDEX)
        if os.path.exists(CHUNKS_FILE):
            os.remove(CHUNKS_FILE)
        return True
    except Exception as e:
        print(f"❌ Error deleting vector store: {e}")
        return False


if __name__ == "__main__":
    # Test vector service
    print("🔍 Vector Service Test")
    print("=" * 50)
    
    # Get store info
    info = get_vector_store_info()
    print(f"Vector store exists: {info.get('exists', False)}")
    
    if info.get('exists', False):
        print(f"Number of chunks: {info['num_chunks']}")
        print(f"Dimension: {info['dimension']}")
        
        # Test search
        test_query = "Python programming"
        print(f"\n🔍 Testing search for: '{test_query}'")
        
        results = search_vector_store(test_query, top_k=3)
        for i, r in enumerate(results):
            print(f"\nResult {i+1} (score: {r['score']:.3f}):")
            print(f"  {r['chunk'][:200]}...")
            if r['metadata']:
                print(f"  Source: {r['metadata'].get('filename', 'Unknown')}")