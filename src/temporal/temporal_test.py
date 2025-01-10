import asyncio
import logging
import os

from temporalio.client import Client


logger = logging.getLogger(__name__)


async def main():
    # Get Temporal connection URL from environment variable with default
    temporal_url = os.getenv("TEMPORAL_URL", "temporal:7233")

    # Connect to the Temporal server
    client = await Client.connect(temporal_url)

    # Get a list of all namespaces
    namespaces = await client.get_worker_task_reachability()

    logger.info("Connected to Temporal server successfully!")
    logger.info(f"Connected to: {temporal_url}")
    logger.info(f"Available namespaces: {', '.join(namespaces.keys())}")

if __name__ == "__main__":
    # Set up basic logging configuration
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
