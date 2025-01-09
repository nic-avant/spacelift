from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
from typing import List, Dict

with workflow.unsafe.imports_passed_through():
    from temporal.activities.get_dependent_stacks import get_dependent_stacks_activity, InputParams
    from temporal.activities.dummy_activity import dummy_activity

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
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            maximum_attempts=3,
            non_retryable_error_types=[]
        )

        # Execute the get_dependent_stacks activity
        dependent_stacks = await workflow.execute_activity(
            get_dependent_stacks_activity,
            InputParams(stack_id=stack_id),
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(seconds=30)
        )
        # dependent_stacks = await workflow.execute_activity(
        #     dummy_activity,
        #     retry_policy=retry_policy,
        #     start_to_close_timeout=timedelta(seconds=30)
        # )

        # Optional: Add additional processing logic for dependent stacks
        workflow.logger.info(f"Found {len(dependent_stacks)} dependent stacks for stack {stack_id}")

        # You can add further workflow logic here, such as:
        # - Triggering subsequent workflows for each dependent stack
        # - Performing additional checks or actions
        
        return dependent_stacks