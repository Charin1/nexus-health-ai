from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server
from crewai import Crew, Task, Agent
from crewai_tools import RagTool
from langchain_ollama import OllamaLLM

server = Server()

# This part is correct, as langchain-ollama also connects directly.
local_llm = OllamaLLM(model="ollama/llama3.1:8b-instruct-q4_K_M")

# --- CORRECTED SECTION ---
# The RAG tool's LLM config must also use the real Ollama model name.
rag_config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.1:8b-instruct-q4_K_M",  # <-- CORRECTED: Use the real Ollama model name
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
# --- END CORRECTED SECTION ---

rag_tool = RagTool(
    config=rag_config,
    chunk_size=1200,
    chunk_overlap=200,
)
rag_tool.add("data/gold-hospital-and-premium-extras.pdf", data_type="pdf_file")


@server.agent()
async def policy_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """
    This is an agent for questions around policy coverage. It uses a RAG pattern
    to find answers based on policy documentation. Use it to help answer questions
    on coverage and waiting periods.
    """
    insurance_agent = Agent(
        role="Senior Insurance Coverage Assistant",
        goal="Determine whether something is covered or not based on the provided policy documents",
        backstory="You are an expert insurance agent designed to assist with coverage queries. You ONLY use the information available in the provided documents to answer questions.",
        verbose=True,
        allow_delegation=False,
        llm=local_llm,
        tools=[rag_tool],
        max_retry_limit=3
    )

    task1 = Task(
         description=input[0].parts[0].content,
         expected_output="A comprehensive response to the user's question, citing information directly from the policy documents.",
         agent=insurance_agent
    )
    crew = Crew(agents=[insurance_agent], tasks=[task1], verbose=True)

    task_output = await crew.kickoff_async()
    yield Message(parts=[MessagePart(content=str(task_output))])


if __name__ == "__main__":
    server.run(port=8001)