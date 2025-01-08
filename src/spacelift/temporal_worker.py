import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.activity import activity
from src.spacelift.workflow.spacelift_webhook_workflow import SpaceliftWebhookWorkflow
from src.spacelift.workflow.dummy_workflow import DummySpaceLiftWorkflow
from src.spacelift.workflow.dependent_stacks_workflow import DependentStacksWorkflow
from src.spacelift.main import Spacelift

@activity.defn
async def get_dependent_stacks_activity(stack_id: str) -> list[dict]:
    """
    Temporal activity to retrieve dependent stacks for a given stack_id.
    
    Args:
        stack_id (str): The ID of the stack to find dependencies for.
    
    Returns:
        list[dict]: A list of dependent stacks.
    """
    sl = Spacelift()
    stacks = sl.get_stacks(query_fields=["id", "labels", "attachedContexts { contextId }"])
    dependent_stacks = [
        stack for stack in stacks 
        if any(f"dependsOn:{stack_id}" in x for x in stack.get("labels", []))
    ]
    return dependent_stacks

async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Connect to Temporal server
    client = await Client.connect("temporal:7233")
    logger.info("Connected to Temporal server")

    # Create and run the worker
    worker = Worker(
        client,
        task_queue="spacelift-task-queue",
        workflows=[
            SpaceliftWebhookWorkflow, 
            DummySpaceLiftWorkflow,
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