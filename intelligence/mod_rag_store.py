import chromadb
from sentence_transformers import SentenceTransformer
import os

class RAGStore:
    def __init__(self, persist_dir="./knowledge_db"):
        print("[RAG] Initializing Offline Knowledge Base...")
        
        # 1. Embedding Model (Converts text to numbers)
        # 'all-MiniLM-L6-v2' is tiny (80MB) and fast on CPU
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 2. Vector Database (Stores the numbers)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name="farm_manuals")
        
        # Check if empty, and load seed data if needed
        if self.collection.count() == 0:
            self._seed_knowledge()

    def _seed_knowledge(self):
        """
        Loads initial offline data. In a real app, this would ingest PDFs.
        Here we inject dummy manuals for the demo.
        """
        print("[RAG] Database empty. Seeding with default manuals...")
        
        documents = [
            "To fix a slipping fan belt on a tractor, loosen the alternator bolt, push the alternator to tighten the belt, and retighten the bolt.",
            "PM-Kisan scheme provides 6000 rupees per year to eligible farmers in three installments.",
            "Wheat leaf rust appears as small, round, orange blisters on the leaves. Treat with fungicides immediately.",
            "Tomato early blight causes dark concentric rings on older leaves. Improve air circulation to prevent it."
        ]
        
        metadatas = [
            {"source": "Tractor Repair Guide v1"},
            {"source": "Govt Scheme Handbook 2025"},
            {"source": "Crop Disease Manual"},
            {"source": "Crop Disease Manual"}
        ]
        
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Embed and Add to DB
        embeddings = self.encoder.encode(documents).tolist()
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"[RAG] Ingested {len(documents)} documents.")

    def retrieve(self, query, n_results=1):
        """
        Semantic Search: Finds the most relevant manual entry.
        """
        query_emb = self.encoder.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_emb,
            n_results=n_results
        )
        
        if not results['documents'][0]:
            return "No relevant manual found."
            
        # Return the text content of the best match
        best_doc = results['documents'][0][0]
        source = results['metadatas'][0][0]['source']
        return f"{best_doc} (Source: {source})"

# --- Test Block ---
if __name__ == "__main__":
    kb = RAGStore()
    
    # Test: Semantic Search (Notice I don't use exact keywords)
    user_query = "How do I tighten the belt on my machine?" 
    print(f"\nUser: {user_query}")
    print(f"Retrieved: {kb.retrieve(user_query)}")
    
    user_query_2 = "What is the symptom of wheat rust?"
    print(f"\nUser: {user_query_2}")
    print(f"Retrieved: {kb.retrieve(user_query_2)}")