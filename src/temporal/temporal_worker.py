import asyncio
import logging

from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

# Pass the activities through the sandbox
with workflow.unsafe.imports_passed_through():
    from temporal.activities.get_dependent_stacks import (
        get_dependent_stacks_activity,
    )
    from temporal.workflow.routing_workflow import (
        DependentStacksWorkflow,
    )


async def main():

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    logger.info("Connected to Temporal server")

    # Create and run the worker
    worker = Worker(
        client,
        task_queue="spacelift-task-queue",
        workflows=[
            DependentStacksWorkflow
        ],
        activities=[get_dependent_stacks_activity]
    )

    try:
        logger.info("Starting Temporal worker...")
        await worker.run()
    except Exception as e:
        logger.error(f"Error running worker: {e}")

if __name__ == "__main__":
    asyncio.run(main())
