import os
import json
from crewai_tools import RagTool

# --- Configuration ---
DB_DIR = "db"
MANIFEST_FILE = os.path.join(DB_DIR, "manifest.json")

RAG_CONFIG = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.1:8b-instruct-q4_K_M",
            "base_url": "http://localhost:11434"
        }
    },
    "embedding_model": {
        "provider": "huggingface",
        "config": {
            "model": "BAAI/bge-m3"
        }
    }
}

def load_policy_rag_tools():
    """
    Loads the manifest and creates a list of uniquely named RagTool instances,
    one for each indexed policy document.
    """
    if not os.path.exists(MANIFEST_FILE):
        print(f"FATAL ERROR: Manifest file not found at {MANIFEST_FILE}. Please run the indexing script.")
        return []

    with open(MANIFEST_FILE, 'r') as f:
        manifest = json.load(f)

    tools = []
    for doc_id, description in manifest.items():
        persist_dir = os.path.join(DB_DIR, doc_id)
        
        # Sanitize the doc_id to create a valid tool name
        tool_name = doc_id.replace('-', '_').replace(' ', '_') + "_query_tool"
        
        tool = RagTool(
            config=RAG_CONFIG,
            persist_dir=persist_dir,
            name=tool_name,
            description=f"Use this tool to answer questions specifically about the '{description}'"
        )
        tools.append(tool)
        
    print(f"Loaded {len(tools)} policy RAG tools.")
    return tools