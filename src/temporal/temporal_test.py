from temporalio.client import Client
import asyncio

async def main():
    # Connect to the Temporal server
    client = await Client.connect("localhost:7233")

    # Get a list of all namespaces
    namespaces = await client.get_worker_task_reachability()

    print("Connected to Temporal server successfully!")
    print(f"Available namespaces: {', '.join(namespaces.keys())}")

if __name__ == "__main__":
    asyncio.run(main())