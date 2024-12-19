from fastapi import FastAPI, Request
from pydantic import BaseModel
from temporalio.client import Client
from src.spacelift.workflow.stack_execution_workflow import StackExecutionWorkflow

app = FastAPI()

class WebhookPayload(BaseModel):
    stack_id: str
    status: str

@app.post("/webhook")
async def webhook_endpoint(payload: WebhookPayload):
    print(f"Received webhook payload: {payload}")
    
    # Initialize Temporal client
    client = await Client.connect("localhost:7233")
    
    # Start the Temporal workflow with the payload
    result = await client.start_workflow(
        StackExecutionWorkflow.run,
        payload.dict(),
        task_queue="spacelift-task-queue",
    )
    
    print(f"Workflow started with result: {result}")
    
    return {"message": "Webhook processed and workflow triggered"}