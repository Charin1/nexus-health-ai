from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server
from crewai import Crew, Task, Agent
from langchain_ollama import OllamaLLM

# Import the function that creates our list of tools
from agent_tools.policy_tools import load_policy_rag_tools

server = Server()

# Configure the local LLM for the CrewAI agent
local_llm = OllamaLLM(model="ollama/llama3.1:8b-instruct-q4_K_M")

# --- Load all RAG tools at startup ---
all_policy_tools = load_policy_rag_tools()

@server.agent()
async def policy_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """
    A single-agent crew that selects the correct policy document tool from its
    toolbelt and uses it to answer the user's query.
    """
    user_query = input[0].parts[0].content

    # --- SIMPLIFIED AGENT DEFINITION ---
    # We create one agent and give it all the tools it might need.
    specialist_agent = Agent(
        role="Insurance Policy Specialist",
        goal="Analyze the user's query to select the single most appropriate policy document tool from your toolbelt. Then, use that specific tool to answer the user's question accurately based on the document's content.",
        backstory="You are a meticulous insurance expert with access to multiple, specific policy document tools. Your primary skill is choosing the correct document tool before answering a question.",
        llm=local_llm,
        tools=all_policy_tools,  # <-- Give the agent the list of all RAG tools
        verbose=True
    )

    # --- SIMPLIFIED TASK DEFINITION ---
    # One task for the one agent.
    querying_task = Task(
        description=f"Answer the user's query: '{user_query}'. You must first determine which policy document is relevant by looking at your available tools, and then use the single most appropriate tool to find the answer.",
        expected_output="A detailed and accurate answer to the user's question, based on the information found in the correct policy document.",
        agent=specialist_agent
    )

    # --- SIMPLIFIED CREW ---
    crew = Crew(
        agents=[specialist_agent],
        tasks=[querying_task],
        verbose=True
    )

    task_output = await crew.kickoff_async()
    yield Message(parts=[MessagePart(content=str(task_output))])


if __name__ == "__main__":
    server.run(port=8001)