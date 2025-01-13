import asyncio
import logging
import os

from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

# Pass the activities through the sandbox
with workflow.unsafe.imports_passed_through():
    from temporal.activities.get_dependent_stacks import (
        get_dependent_stacks_activity,
    )
    from temporal.activities.run_stack import (
        run_stack,
    )
    from temporal.workflow.routing_workflow import (
        DependentStacksWorkflow,
        RunStackWorkflow
    )


async def main():

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Get Temporal connection URL from environment variable with default
    temporal_url = os.getenv("TEMPORAL_URL", "temporal:7233")

    # Connect to Temporal server
    client = await Client.connect(temporal_url)
    logger.info(f"Connected to Temporal server at {temporal_url}")

    # Create and run the worker
    worker = Worker(
        client,
        task_queue="spacelift-task-queue",
        workflows=[
            DependentStacksWorkflow,
            RunStackWorkflow
        ],
        activities=[get_dependent_stacks_activity, run_stack]
    )

    try:
        logger.info("Starting Temporal worker...")
        await worker.run()
    except Exception as e:
        logger.error(f"Error running worker: {e}")

if __name__ == "__main__":
    asyncio.run(main())
