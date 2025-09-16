import os
import json
import asyncio
from crewai.tools import BaseTool
from crewai_tools import RagTool
from acp_sdk.client import Client
from acp_sdk.models import Message, MessagePart

# --- Configuration (unchanged) ---
DB_DIR = "db"
MANIFEST_FILE = os.path.join(DB_DIR, "manifest.json")
RAG_CONFIG = {
    "llm": { "provider": "ollama", "config": { "model": "llama3.1:8b-instruct-q4_K_M", "base_url": "http://localhost:11434" }},
    "embedding_model": { "provider": "huggingface", "config": { "model": "BAAI/bge-m3" }}
}

# --- DEFINITIVE SOLUTION: A PROPERLY IMPLEMENTED ASYNC TOOL ---
class A2AAgentTool(BaseTool):
    """A tool to interact with a specific A2A agent."""
    name: str
    description: str
    client: Client
    agent_name: str

    # This is the asynchronous version of the tool's execution logic.
    # CrewAI will automatically use this when `kickoff_async` is called.
    async def _arun(self, query: str) -> str:
        """Asynchronously delegates the query to the specified A2A agent."""
        response = await self.client.run_sync(
            agent=self.agent_name,
            input=[Message(parts=[MessagePart(content=query)])]
        )
        return response.output[0].parts[0].content

    # This is the synchronous version that MUST be implemented to satisfy the BaseTool contract.
    # It simply wraps the async method.
    def _run(self, query: str) -> str:
        """Synchronously delegates the query to the specified A2A agent."""
        return asyncio.run(self._arun(query=query))

# --- load_policy_rag_tools function is unchanged ---
def load_policy_rag_tools():
    if not os.path.exists(MANIFEST_FILE):
        print(f"Warning: Manifest file not found at {MANIFEST_FILE}. No policy tools will be loaded.")
        return []
    with open(MANIFEST_FILE, 'r') as f:
        manifest = json.load(f)
    tools = []
    for doc_id, description in manifest.items():
        persist_dir = os.path.join(DB_DIR, doc_id)
        tool_name = doc_id.replace('-', '_').replace(' ', '_') + "_query_tool"
        tool_instance = RagTool(
            config=RAG_CONFIG,
            persist_dir=persist_dir,
            name=tool_name,
            description=f"Use this tool to answer questions specifically about the '{description}'"
        )
        tools.append(tool_instance)
    print(f"Loaded {len(tools)} policy RAG tools.")
    return tools