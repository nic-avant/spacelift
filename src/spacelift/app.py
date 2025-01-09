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
        
        try:
            # Convert to NotificationPolicy object
            payload = NotificationPolicy(**raw_payload)
            
            # Log using the to_dict method
            logger.info(f"Received webhook payload: {json.dumps(payload.to_dict(), indent=2)}")
        except Exception as e:
            logger.error(f"Error parsing payload: {str(e)}")
            logger.error(f"Raw payload: {json.dumps(raw_payload, indent=2)}")
            raise HTTPException(status_code=400, detail=f"Invalid payload format: {str(e)}")

        # Generate a unique uuid for the workflow
        wf_id = str(uuid.uuid4())
        
        try:
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
        except Exception as e:
            logger.error(f"Error with Temporal workflow: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")
        
        return {
            "message": "Webhook processed and workflow triggered", 
            "workflow_id": result.id,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))