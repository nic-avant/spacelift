from temporalio import workflow
from datetime import timedelta
import logging
import json

@workflow.defn
class DummySpaceLiftWorkflow:
    """
    A dummy Temporal workflow for demonstrating basic workflow execution
    """

    @workflow.run
    async def run(self, payload: dict):
        """
        Simple dummy workflow that simulates processing 
        
        Args:
            payload (dict): Incoming payload from webhook or trigger
        """
        logger = workflow.logger
        logger.setLevel(logging.INFO)

        try:
            # Log the received payload
            logger.info(f"Received payload: {json.dumps(payload, indent=2)}")

            # Simulate some workflow steps
            await workflow.wait_condition(lambda: True, timeout=timedelta(seconds=5))
            logger.info("Workflow started successfully")

            # Simulate some processing
            workflow_stages = [
                "Initializing workflow",
                "Validating payload",
                "Processing data",
                "Generating report"
            ]

            for stage in workflow_stages:
                logger.info(f"Current stage: {stage}")
                # Simulate some work
                await workflow.sleep(timedelta(seconds=1))

            # Return a dummy result
            return {
                "status": "completed",
                "message": "Dummy workflow executed successfully",
                "payload_received": payload
            }

        except Exception as e:
            logger.error(f"Workflow processing error: {str(e)}")
            raise