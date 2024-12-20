import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from src.spacelift.workflow.spacelift_webhook_workflow import SpaceliftWebhookWorkflow

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
        workflows=[SpaceliftWebhookWorkflow],
        activities=[]  # Add any activities if needed
    )

    try:
        logger.info("Starting Temporal worker...")
        await worker.run()
    except Exception as e:
        logger.error(f"Error running worker: {e}")

if __name__ == "__main__":
    asyncio.run(main())