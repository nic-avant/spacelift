from temporalio.client import Client
from temporalio.worker import Worker
from src.spacelift.workflow.stack_execution_workflow import StackExecutionWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="spacelift-task-queue",
        workflows=[StackExecutionWorkflow],
    )
    await worker.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())