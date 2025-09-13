# Nexus-Health-AI Backend


![status](https://img.shields.io/badge/status-in_development-yellow)

⚠️ This project is under active development and is **not production-ready**.

Welcome to the backend of Nexus-Health-AI, a multi-agent AI system designed to serve as a comprehensive, private, and locally-run healthcare assistant.

This system leverages multiple specialized AI agents to handle a variety of tasks, from answering general health questions to performing detailed analysis of insurance policy documents.

## Core Features

*   **Multi-Agent Specialization:** Utilizes different agent frameworks (`smolagents` and `crewai`) to assign specialized agents to specific tasks for optimal performance.
*   **Local-First AI:** Ensures data privacy and eliminates API costs by running entirely on local models using **Ollama**.
*   **Advanced RAG Capabilities:** The Policy Agent uses Retrieval-Augmented Generation to provide accurate answers from specific documents, such as insurance policies.
*   **Modular and Scalable:** Built with a clear separation of concerns, using modern protocols like ACP and MCP for communication between agents and tools.
*   **Tool-Enabled Agents:** Agents can use external tools, such as a real-time web search or a custom doctor database, to enhance their capabilities.

## Architecture Overview

The backend is composed of several independent services that work together:

1.  **Local Models Server (Ollama):** This is the core service that runs the local LLM (`llama3:8b`) and the embedding model (`BAAI/bge-m3`). It must be running for any of the AI agents to function.
2.  **ACP Agent Servers (The Agents):** These are the main entry points for user interaction, running on the Agent-Communication-Protocol (ACP) protocol.
    *   **Smol Agent Server (Port 8000):** Hosts the generalist agents (`health_agent`, `doctor_agent`). It connects directly to the Ollama server.
    *   **CrewAI Agent Server (Port 8001):** Hosts the specialist `policy_agent` for document analysis. It also connects directly to the Ollama server.
3.  **MCP Tool Server (The Tool):**
    *   **Doctor Server:** This is a lightweight microservice running on the Model-Context-Protocol (MCP). It exposes a `list_doctors` function that the `doctor_agent` can call to retrieve data. It is started automatically by the Smol Agent Server.

## Tech Stack

This project integrates a modern stack of AI and backend technologies:

| Category | Technology | Role |
| :--- | :--- | :--- |
| **Language & Frameworks** | Python 3.11+ | Core programming language. |
| | FastAPI | Underpins the `acp-sdk` server for high-performance API endpoints. |
| **AI Agent Frameworks** | **CrewAI** | Used for the specialized `policy_agent` to orchestrate tasks requiring a thought-action reasoning loop. |
| | **Smol Agents** | Used for the more straightforward `health_agent` and `doctor_agent` that rely on direct tool execution. |
| **Communication Protocols**| **ACP (Agent-Communication-Protocol)** | The primary, modern protocol for exposing agents as services. |
| | **MCP (Model-Context-Protocol)**| Used for inter-service communication, allowing agents to discover and use external tools like the doctor database. |
| **AI Models & Infra** | **Ollama** | The engine for serving and running local LLMs and embedding models. |
| | **`llama3:8b`** | The specific local Large Language Model used for reasoning and generation. |
| | **`BAAI/bge-m3`** | The high-performance embedding model used by the RAG tool for document analysis. |
| **Core Libraries** | **`langchain-ollama`** | The dedicated, modern library for connecting LangChain-based frameworks (like CrewAI) to Ollama. |
| | **`litellm`** | Used internally by `smolagents` to provide a unified interface for connecting to hundreds of LLMs, including Ollama. |
| | **`uvicorn`** | A lightning-fast ASGI server used to run the agent applications. |
| **Dependency Management**| **`uv`** | An extremely fast Python package installer and resolver, used for managing all project dependencies. |

## Further Learning & Resources

The ACP protocol used in this project. To understand the foundational concepts of agent-to-agent communication, this course from DeepLearning.AI is an excellent resource:

*   **[Building Applications with Agent-to-Agent Communication](https://learn.deeplearning.ai/courses/acp-agent-communication-protocol/)**

## Setup and Installation

Follow these steps to get the backend up and running.

#### Prerequisites

*   Python 3.11+
*   `git` for cloning the repository.
*   `uv` (pip installer). If you don't have it, install it with: `pip install uv`

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd nexus-health-ai/backend```

### Step 2: Set Up the Environment

Create a virtual environment and install all the required dependencies using `uv`.

```bash
# Create a virtual environment in the .venv folder
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install all dependencies from requirements.txt
uv pip install -r requirements.txt
```

### Step 3: Set Up Local Models with Ollama

Follow the instructions in `local_models/README.md` or run the commands below. You must have the Ollama application running on your machine.

```bash
# Pull the Llama 3 8B Instruct model
ollama pull llama3:8b

# Pull the BGE-M3 embedding model
ollama pull bge-m3
```

## Running the Application

You will need **two separate terminals** to run the two main agent servers. Make sure you have activated the virtual environment (`source .venv/bin/activate`) in both terminals.

#### Terminal 1: Start the Smol Agent Server

This server runs the general health and doctor-finding agents on port 8000.

```bash
uv run a2a_servers/smol_agent_server.py
```

#### Terminal 2: Start the CrewAI Agent Server

This server runs the specialized insurance policy agent on port 8001.

```bash
uv run a2a_servers/crew_agent_server.py
```

Your backend is now fully operational and ready to receive requests.

## How to Interact with the Agents (API Examples)

Use a client script to send requests to your running agents.

```bash
python client.py
```

#### 1. Test the Health Agent (Port 8000)

Asks a general health question that requires web search.


#### 2. Test the Doctor Agent (Port 8000)

Asks to find doctors, which will trigger the MCP tool.


#### 3. Test the Policy Agent (Port 8001)

Asks a specific question about the PDF document.

## Status
This project is still in its early stages. Expect breaking changes.