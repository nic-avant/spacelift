from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from temporalio.client import Client
from src.spacelift.workflow.spacelift_webhook_workflow import SpaceliftWebhookWorkflow
from src.spacelift.workflow.dummy_workflow import DummySpaceLiftWorkflow
import json
import logging
from src.spacelift.main import Spacelift

app = FastAPI()
logger = logging.getLogger(__name__)

class WebhookPayload(BaseModel):
    """
    Flexible payload model to accept various Spacelift webhook structures
    """
    payload: Dict[str, Any] = Field(..., description="Full Spacelift webhook payload")

async def get_dependent_stacks(stack_id: str) -> list[dict]:
    sl = Spacelift()
    stacks = sl.get_stacks(query_fields=["id", "labels", "attachedContexts { contextId }"])
    #dependent_stacks = [stack for stack in stacks if stack.get("labels") and "dependsOn" in stack["labels"] and stack["labels"]["dependsOn"] == stack_id]
    dependent_stacks = [stack for stack in stacks if any(f"dependsOn:{stack_id}" in x for x in stack.get("labels", []))]
    return dependent_stacks

@app.post("/webhook")
async def webhook_endpoint(request: Request):
    """
    Flexible webhook endpoint to process Spacelift events
    
    Supports parsing of complex webhook payloads
    """
    try:
        # Parse raw JSON payload
        payload = await request.json()
        logger.info(f"Received webhook payload: {json.dumps(payload, indent=2)}")

        # Extract stack id from payload
        stack_id = payload.get('run_updated', {}).get('stack', {}).get('id', 'unknown')
        
        # Get dependent stacks
        dependent_stacks = await get_dependent_stacks(stack_id)
        logger.info(f"Dependent stacks: {dependent_stacks}")

        # Initialize Temporal client
        logger.info("Attempting to connect to Temporal server")
        client = await Client.connect("temporal:7233")
        logger.info("Successfully connected to Temporal server")
        
        # Start the Temporal workflow with the full payload
        workflow_id = f"spacelift-webhook-{stack_id}"
        logger.info(f"Starting workflow with ID: {workflow_id}")
        result = await client.start_workflow(
            SpaceliftWebhookWorkflow.run,
            payload,
            id=workflow_id,
            task_queue="spacelift-task-queue",
        )
        
        logger.info(f"Workflow started successfully with ID: {result.id}")
        
        return {
            "message": "Webhook processed and workflow triggered", 
            "workflow_id": result.id,
            "dependent_stacks": dependent_stacks
        }
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))