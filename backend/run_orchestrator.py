import asyncio
from colorama import Fore, Style
from acp_sdk.client import Client
from langchain_ollama import OllamaLLM
from crewai import Agent, Task, Crew
from agent_tools.policy_tools import A2AAgentTool

# --- Configuration ---
SMOL_AGENT_SERVER_URL = "http://localhost:8000"
CREW_AGENT_SERVER_URL = "http://localhost:8001"

async def main():
    """
    This script runs a master CrewAI orchestrator agent for Nexus-Health-AI.
    It discovers all specialist agents and delegates a complex task to them.
    """
    print(f"{Fore.CYAN}--- Nexus-Health-AI Orchestrator ---{Style.RESET_ALL}")

    # 1. Configure the LLM for the Orchestrator Agent
    llm = OllamaLLM(model="ollama/llama3.1:8b-instruct-q4_K_M",
                    temperature=0.3)


    # 2. Use 'async with' to manage the entire lifecycle of the clients.
    # All code that uses the clients MUST be inside this block.
    print(f"\n{Fore.YELLOW}Connecting to agent servers...{Style.RESET_ALL}")
    try:
        async with Client(base_url=CREW_AGENT_SERVER_URL) as insurer_client, \
                   Client(base_url=SMOL_AGENT_SERVER_URL) as hospital_client:

            print(f"{Fore.GREEN}Connections successful.{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Discovering specialist agents and creating tools...{Style.RESET_ALL}")

            clients_and_urls = [
                (insurer_client, CREW_AGENT_SERVER_URL),
                (hospital_client, SMOL_AGENT_SERVER_URL)
            ]
            
            orchestrator_tools = []
            for client, url in clients_and_urls:
                async for agent_spec in client.agents():
                    print(f"  - Found agent: {agent_spec.name} on {url}")
                    agent_tool = A2AAgentTool(
                        name=agent_spec.name,
                        description=f"Use this tool for tasks related to: {agent_spec.description}. The input should be a clear and specific question for this agent.",
                        client=client,
                        agent_name=agent_spec.name
                    )
                    orchestrator_tools.append(agent_tool)

            if not orchestrator_tools:
                print(f"{Fore.RED}Error: No agents found. Make sure both agent servers are running.{Style.RESET_ALL}")
                return

            # 3. Initialize the Orchestrator Agent
            orchestrator_agent = Agent(
                role="Master Health Assistant",
                goal="Deconstruct a complex user query into sequential sub-tasks and delegate each sub-task to the appropriate specialist agent tool until the entire query is answered.",
                backstory="You are a highly intelligent project manager. You analyze user requests, identify the correct specialist agent for each part of the request, and use them in a logical order to build a complete answer.",
                llm=llm,
                tools=orchestrator_tools,
                verbose=True,
                max_execution_time=500,
                max_iter=8
            )

            # 4. Define the complex, multi-part user query
            user_query = "I think I have the flu, what are the symptoms? Also, find me a doctor in California, and tell me if my Gold Plan 2024 policy covers the consultation."

            print(f"\n{Fore.YELLOW}Sending complex query to orchestrator:{Style.RESET_ALL}")
            print(f"'{user_query}'")
            print("-" * 50)

            # 5. Define the orchestration task
            orchestration_task = Task(
                description=f"Fulfill the user's request: '{user_query}'. You must break this down into steps. First, address the health symptoms. Second, find a doctor. Third, check the policy coverage. Finally, combine all the gathered information into a single, comprehensive final answer.",
                expected_output="A complete, consolidated answer that addresses all parts of the user's original query.",
                agent=orchestrator_agent
            )

            # 6. Create and run the Crew
            crew = Crew(
                agents=[orchestrator_agent],
                tasks=[orchestration_task],
                verbose=True
            )
            
            final_result = await crew.kickoff_async()

            print("-" * 50)
            print(Fore.GREEN + Style.BRIGHT + "Orchestrator's Final Answer:" + Style.RESET_ALL)
            print(final_result)

    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
        print("Please ensure both the smol_agent_server (port 8000) and crew_agent_server (port 8001) are running.")

    # There is no need for a finally block or manual .close() calls.
    # The 'async with' statement handles closing the clients automatically when this block is exited.
    print(f"\n{Fore.GREEN}Orchestration complete. Client connections have been automatically closed.{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(main())