from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from temporalio.client import Client
from src.spacelift.workflow.spacelift_webhook_workflow import SpaceliftWebhookWorkflow
from src.spacelift.workflow.dummy_workflow import DummySpaceLiftWorkflow

import json
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

class WebhookPayload(BaseModel):
    """
    Flexible payload model to accept various Spacelift webhook structures
    """
    payload: Dict[str, Any] = Field(..., description="Full Spacelift webhook payload")

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
        
        # Initialize Temporal client
        logger.info("Attempting to connect to Temporal server")
        client = await Client.connect("temporal:7233")
        logger.info("Successfully connected to Temporal server")
        
        # Start the Temporal workflow with the full payload
        workflow_id = f"spacelift-webhook-{payload.get('run_updated', {}).get('run', {}).get('id', 'unknown')}"
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
            "workflow_id": result.id
        }
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))