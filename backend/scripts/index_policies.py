import os
import json
from crewai_tools import RagTool

# --- Configuration ---
POLICIES_DIR = "data/policies"
DB_DIR = "db"
MANIFEST_FILE = os.path.join(DB_DIR, "manifest.json")

# This config is only needed for the one-time indexing process.
# It tells the RagTool which embedding model to use.
RAG_CONFIG = {
    "embedding_model": {
        "provider": "huggingface",
        "config": {
            "model": "BAAI/bge-m3"
        }
    }
}

def index_policies():
    """
    Scans the policies directory, indexes each PDF into a separate persistent
    vector store, and creates a manifest file for the agents to use.
    """
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    manifest = {}
    
    print("Starting policy document indexing...")
    
    for filename in os.listdir(POLICIES_DIR):
        if filename.endswith(".pdf"):
            file_path = os.path.join(POLICIES_DIR, filename)
            # Use the filename without extension as the document ID
            document_id = os.path.splitext(filename)[0]
            persist_dir = os.path.join(DB_DIR, document_id)

            print(f"  - Indexing '{filename}' (ID: {document_id})...")
            
            # Create a new RAG tool for each document, pointing to a unique persistent directory
            rag_tool = RagTool(
                config=RAG_CONFIG,
                persist_dir=persist_dir
            )
            
            # Add and index the document. This will be saved to disk.
            rag_tool.add(file_path, data_type="pdf_file")

            # Create a human-readable name for the manifest
            human_readable_name = document_id.replace('-', ' ').replace('_', ' ').title()
            manifest[document_id] = f"The '{human_readable_name}' policy document."
            
            print(f"  - Successfully indexed '{filename}' to '{persist_dir}'")

    # Save the manifest file for the agents to use
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)
        
    print(f"\nIndexing complete. Manifest created at '{MANIFEST_FILE}'")
    print("Available Documents:")
    for doc_id, desc in manifest.items():
        print(f"  - ID: {doc_id}, Description: {desc}")

if __name__ == "__main__":
    index_policies()