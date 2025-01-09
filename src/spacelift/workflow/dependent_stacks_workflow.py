from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
import asyncio
from typing import List, Dict
from dataclasses import dataclass
from temporalio import activity
from spacelift.main import Spacelift

@activity.defn
async def get_dependent_stacks_activity(stack_id: str) -> list[dict]:
    """
    Temporal activity to retrieve dependent stacks for a given stack_id.
    
    Args:
        stack_id (str): The ID of the stack to find dependencies for.
    
    Returns:
        list[dict]: A list of dependent stacks.
    """
    sl = Spacelift()
    stacks = sl.get_stacks(query_fields=["id", "labels", "attachedContexts { contextId }"])
    dependent_stacks = [
        stack for stack in stacks 
        if any(f"dependsOn:{stack_id}" in x for x in stack.get("labels", []))
    ]
    return dependent_stacks
@dataclass
class InputParams:
    stack_id: str

@workflow.defn
class DependentStacksWorkflow:
    @workflow.run
    async def run(self, stack_id: str) -> List[Dict]:
        """
        Workflow to retrieve and process dependent stacks for a given stack.
        
        Args:
            stack_id (str): The ID of the stack to find dependencies for.
        
        Returns:
            List[Dict]: A list of dependent stacks that can be processed.
        """
        # Retry policy for the activity
        # retry_policy = RetryPolicy(
        #     initial_interval=timedelta(seconds=1),
        #     maximum_interval=timedelta(seconds=60),
        #     maximum_attempts=3,
        #     non_retryable_error_types=[]
        # )

        # Execute the get_dependent_stacks activity
        dependent_stacks = await workflow.execute_activity(
            get_dependent_stacks_activity,
            InputParams(stack_id=stack_id),
            #retry_policy=retry_policy,
            start_to_close_timeout=timedelta(seconds=30)
        )

        # Optional: Add additional processing logic for dependent stacks
        workflow.logger.info(f"Found {len(dependent_stacks)} dependent stacks for stack {stack_id}")

        # You can add further workflow logic here, such as:
        # - Triggering subsequent workflows for each dependent stack
        # - Performing additional checks or actions
        
        return dependent_stacks