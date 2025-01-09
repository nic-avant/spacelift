from fastapi import FastAPI, Request, HTTPException
from temporalio.client import Client
from spacelift.workflow.routing_workflow import DependentStacksWorkflow
import json
import logging
import uuid
from spacelift.models.notification_policy import NotificationPolicy

app = FastAPI()
logger = logging.getLogger(__name__)

@app.post("/webhook")
async def webhook_endpoint(request: Request):
    """
    Flexible webhook endpoint to process Spacelift events
    
    Supports parsing of complex webhook payloads
    """
    try:
        # Parse raw JSON payload
        raw_payload = await request.json()
        payload = NotificationPolicy(**raw_payload)
        logger.info(f"Received webhook payload: {json.dumps(payload, indent=2)}")

        # Extract stack id from payload
        # stack_id = payload.get('run_updated', {}).get('stack', {}).get('id', 'unknown')
        # Generate a unique uuid for the workflow
        wf_id = str(uuid.uuid4())
        # Initialize Temporal client
        logger.info("Attempting to connect to Temporal server")
        client = await Client.connect("temporal:7233")
        logger.info("Successfully connected to Temporal server")
        
        # Start the Temporal workflow with the full payload
        logger.info(f"Starting workflow with ID: {wf_id}")
        result = await client.start_workflow(
            DependentStacksWorkflow.run,
            id=wf_id,
            task_queue="spacelift-task-queue",
        )
        
        logger.info(f"Workflow started successfully with ID: {result.id}")
        
        return {
            "message": "Webhook processed and workflow triggered", 
            "workflow_id": result.id,
        }
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))