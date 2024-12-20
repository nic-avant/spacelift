from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
import json
import logging

import os

class SpaceLiftRunContext:
    """
    Structured representation of a Spacelift run context
    Provides flexible parsing and access to key run information
    """
    def __init__(self, payload: dict):
        """
        Parse and extract key information from the Spacelift webhook payload
        
        Args:
            payload (dict): Full Spacelift webhook payload
        """
        self.raw_payload = payload
        
        # Extract core run information
        run_info = payload.get('run_updated', {}).get('run', {})
        stack_info = payload.get('run_updated', {}).get('stack', {})
        
        # Structured run details
        self.run_details = {
            'run_id': run_info.get('id'),
            'state': run_info.get('state', 'UNKNOWN'),
            'type': run_info.get('type', 'UNSPECIFIED'),
            'branch': run_info.get('branch', 'main'),
            'command': run_info.get('command', ''),
            
            # Commit information
            'commit': {
                'hash': run_info.get('commit', {}).get('hash'),
                'message': run_info.get('commit', {}).get('message'),
                'author': run_info.get('commit', {}).get('author')
            },
            
            # Stack details
            'stack': {
                'id': stack_info.get('id'),
                'name': stack_info.get('name'),
                'namespace': stack_info.get('namespace'),
                'repository': stack_info.get('repository')
            },
            
            # Changes detection
            'changes': [
                {
                    'action': change.get('action'),
                    'entity_type': change.get('entity', {}).get('entity_type'),
                    'entity_name': change.get('entity', {}).get('name')
                }
                for change in run_info.get('changes', [])
            ]
        }
    
    def get_trigger_command(self) -> str:
        """
        Generate a representative command for the run
        
        Returns:
            str: Simulated command to represent the run
        """
        if self.run_details['state'] == 'APPLYING':
            return f"terraform apply for stack {self.run_details['stack']['name']}"
        elif self.run_details['state'] == 'PLANNING':
            return f"terraform plan for stack {self.run_details['stack']['name']}"
        else:
            return f"Unhandled state: {self.run_details['state']}"

@workflow.defn
class SpaceliftWebhookWorkflow:
    """
    Temporal workflow for processing Spacelift webhook events
    Designed to be flexible and handle various run scenarios
    """

    @workflow.run
    async def run(self, webhook_payload: dict):
        """
        Process Spacelift webhook payload and manage workflow execution
        
        Args:
            webhook_payload (dict): Full Spacelift webhook payload
        """
        logger = workflow.logger
        logger.setLevel(logging.INFO)

        try:
            # Parse payload into structured context
            run_context = SpaceLiftRunContext(webhook_payload)
            
            logger.info(f"Processing Spacelift run: {run_context.run_details['run_id']}")
            logger.info(f"Run State: {run_context.run_details['state']}")
            
            # Simulate stack execution based on run state
            if run_context.run_details['state'] in ['APPLYING', 'PLANNING']:
                # Commented out actual API call
                # result = await workflow.execute_activity(
                #     spacelift_client.trigger_run, 
                #     run_context.run_details['stack']['id']
                # )
                
                # Simulated command execution
                simulated_command = run_context.get_trigger_command()
                logger.info(f"SIMULATED COMMAND: {simulated_command}")
                
                # Additional processing based on changes
                for change in run_context.run_details['changes']:
                    logger.info(f"Change detected: {change}")
            
            else:
                logger.warning(f"Unhandled run state: {run_context.run_details['state']}")
            
            return {
                "status": "processed",
                "run_id": run_context.run_details['run_id'],
                "state": run_context.run_details['state']
            }
        
        except Exception as e:
            logger.error(f"Workflow processing error: {str(e)}")
            raise