from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server
from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel, VisitWebpageTool, ToolCallingAgent, ToolCollection
from mcp import StdioServerParameters

# nest_asyncio has been removed as it conflicts with uvloop used by uvicorn.

server = Server()

# Configure the model to use the local LLM via the LiteLLM proxy
model = LiteLLMModel(
    model_id="ollama/llama3.1:8b-instruct-q4_K_M",
    api_base="http://localhost:11434",
    max_tokens=2048
)

# Configure the MCP parameters to run the doctor server
server_parameters = StdioServerParameters(
    command="uv",
    args=["run", "mcp_servers/doctor_server.py"],
    env=None,
)

HEALTH_AGENT_PROMPT_TEMPLATE = """
You are a helpful AI assistant that answers health questions.
Your task is to use the provided tools to find information and then provide a clear, final answer.

**CRITICAL INSTRUCTIONS:**
1.  All Python code you generate MUST be wrapped in `<code>...</code>` tags. Do NOT use triple backticks (```).
2.  When you have the final answer, you MUST call the `final_answer()` function.
3.  The `final_answer()` function takes a SINGLE STRING as its argument. Format your entire response, including lists or multiple points, into one comprehensive, human-readable string.

Example of a correct final answer:
<code>
final_answer("The symptoms of the flu include: fever, cough, sore throat, muscle aches, and fatigue.")
</code>

---

Now, fulfill the following user request:
{user_query}
"""

@server.agent()
async def health_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """
    This is a CodeAgent which supports the hospital to handle health based questions for patients.
    Current or prospective patients can use it to find answers about their health and hospital treatments.
    """
    agent = CodeAgent(tools=[DuckDuckGoSearchTool(), VisitWebpageTool()], model=model)
    prompt = input[0].parts[0].content
    full_prompt = HEALTH_AGENT_PROMPT_TEMPLATE.format(user_query=prompt)

    response = agent.run(full_prompt)
    yield Message(parts=[MessagePart(content=str(response))])

@server.agent()
async def doctor_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """This is a Doctor Agent which helps users find doctors near them."""
    with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
        agent = ToolCallingAgent(tools=[*tool_collection.tools], model=model)
        prompt = input[0].parts[0].content
        response = agent.run(prompt)
    yield Message(parts=[MessagePart(content=str(response))])

if __name__ == "__main__":
    server.run(port=8000)