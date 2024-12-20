import json
import asyncio
from temporalio.client import Client
from src.spacelift.workflow.spacelift_webhook_workflow import SpaceliftWebhookWorkflow

async def test_webhook_workflow():
    """
    Test the Spacelift webhook workflow with an example payload
    """
    # Load the example payload
    with open('notification-policy.example.global-dev-delhi-airflow02-env-var.json', 'r') as f:
        example_payload = json.load(f)
    
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Start the workflow
    result = await client.start_workflow(
        SpaceliftWebhookWorkflow.run,
        example_payload,
        id=f"test-spacelift-webhook-{example_payload.get('run_updated', {}).get('run', {}).get('id', 'unknown')}",
        task_queue="spacelift-task-queue"
    )
    
    print(f"Workflow started with ID: {result.id}")
    
    # Wait for the workflow to complete
    workflow_result = await result.result()
    
    print("Workflow Result:", workflow_result)

def run_test():
    """
    Synchronous wrapper to run the async test
    """
    asyncio.run(test_webhook_workflow())

if __name__ == "__main__":
    run_test()