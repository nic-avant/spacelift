import json
import logging
import os
import uuid

from app.models.notification_policy import (
    NotificationPolicy,
)
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)
from temporal.activities.stack_dependencies import (
    StackDependencyInput,
)
from temporal.workflows.stack_dependency_chain import (
    StackDependencyChainWorkflow,
)
from temporalio.client import Client

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/health")
async def health_check():
    """
    Health check endpoint that returns 200 OK when the service is healthy
    """
    return {"status": "healthy"}



@app.post("/webhook")
async def webhook_endpoint(
    request: Request,
):
    """
    Flexible webhook endpoint to process Spacelift events

    Supports parsing of complex webhook payloads
    """
    try:
        # Parse raw JSON payload
        raw_payload = (
            await request.json()
        )

        try:
            # Convert to NotificationPolicy object - Pydantic handles validation
            payload = NotificationPolicy.parse_obj(
                raw_payload
            )

            # Log using Pydantic's json() method
            logger.info(
                f"Received webhook payload: {payload.json(indent=2)}"
            )
        except Exception as e:
            logger.error(
                f"Error parsing payload: {str(e)}"
            )
            logger.error(
                f"Raw payload: {json.dumps(raw_payload, indent=2)}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payload format: {str(e)}",
            )

        if payload.run_updated.state != "FINISHED":
            logger.info(
                f"Skipping webhook payload with state: {payload.run_updated.state}"
            )
            return {
                "message": "Webhook processed and skipped",
            }
        stack_id = (
            payload.run_updated.stack.id
        )

        # Generate a unique uuid for the workflow
        wf_id = str(uuid.uuid4())

        try:
            # Initialize Temporal client using environment variable
            logger.info(
                "Attempting to connect to Temporal server"
            )
            temporal_url = os.getenv("TEMPORAL_URL", "temporal:7233")

            client = (
                await Client.connect(
                    temporal_url
                )
            )
            logger.info(
                f"Successfully connected to Temporal server at {temporal_url}"
            )

            # Start the Temporal workflow with the full payload
            logger.info(
                f"Starting workflow with ID: {wf_id}"
            )
            result = await client.start_workflow(
                StackDependencyChainWorkflow.run,
                StackDependencyInput(stack_id=stack_id),
                id=wf_id,
                task_queue="spacelift-task-queue",
            )

            logger.info(
                f"Workflow started successfully with ID: {result.id}"
            )
        except Exception as e:
            logger.error(
                f"Error with Temporal workflow: {str(e)}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Workflow error: {str(e)}",
            )

        return {
            "message": "Webhook processed and workflow triggered",
            "workflow_id": result.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
