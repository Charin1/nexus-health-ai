import asyncio
from acp_sdk.client import Client
from acp_sdk.models import Message, MessagePart

async def main():
    # Connect to your running server
    # client = Client(base_url="http://127.0.0.1:8000")

    # response = await client.run_sync(
    #     agent="health_agent",
    #     input="What are the symptoms of a common cold?")
    # print("Response:", response)

    # response = await client.run_sync(
    #     agent="doctor_agent",
    #     input="Find me doctors in CA")
    # print("Response:", response)

    client = Client(base_url="http://127.0.0.1:8001")
    response = await client.run_sync(
        agent="policy_agent",
        input="Is dental surgery covered under the Gold Hospital policy?")
    print("Response:", response)

asyncio.run(main())
