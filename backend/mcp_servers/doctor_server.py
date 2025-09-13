
#### `backend/mcp_servers/doctor_server.py`

from colorama import Fore
from mcp.server.fastmcp import FastMCP
import json
import requests

mcp = FastMCP("doctorserver")

@mcp.tool()
def list_doctors(state: str) -> str:
    """This tool returns doctors that may be near you.
    Args:
        state: the two letter state code that you live in.
        Example payload: "CA"

    Returns:
        str: a list of doctors that may be near you
        Example Response: "[{'name': 'Dr John James', 'specialty': 'Cardiology', ...}]"
    """
    print(f"{Fore.CYAN}MCP Tool 'list_doctors' called with state: {state}{Fore.RESET}")
    try:
        url = 'https://raw.githubusercontent.com/nicknochnack/ACPWalkthrough/main/doctors.json'
        resp = requests.get(url)
        resp.raise_for_status()  # Raise an exception for bad status codes
        doctors = resp.json()

        matches = [doctor for doctor in doctors.values() if doctor.get('address', {}).get('state') == state]
        print(f"{Fore.GREEN}Found {len(matches)} doctors in {state}.{Fore.RESET}")
        return json.dumps(matches)
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error fetching doctor data: {e}{Fore.RESET}")
        return json.dumps({"error": "Failed to fetch doctor data."})
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error decoding JSON from doctor data source.{Fore.RESET}")
        return json.dumps({"error": "Invalid data format from doctor source."})


if __name__ == "__main__":
    print(f"{Fore.YELLOW}Starting Doctor MCP Server...{Fore.RESET}")
    mcp.run(transport="stdio")