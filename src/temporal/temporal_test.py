import os
from temporalio.client import Client
import asyncio

async def main():
    # Get Temporal connection URL from environment variable with default
    temporal_url = os.getenv("TEMPORAL_URL", "temporal:7233")

    # Connect to the Temporal server
    client = await Client.connect(temporal_url)

    # Get a list of all namespaces
    namespaces = await client.get_worker_task_reachability()

    print("Connected to Temporal server successfully!")
    print(f"Connected to: {temporal_url}")
    print(f"Available namespaces: {', '.join(namespaces.keys())}")

if __name__ == "__main__":
    asyncio.run(main())