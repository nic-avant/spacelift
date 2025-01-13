from datetime import timedelta
from typing import Dict, List

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from temporal.activities.stack_dependencies import (
        StackDependencyInput,
        fetch_dependent_stacks,
    )
    from temporal.activities.stack_operations import (
        StackExecutionInput,
        trigger_stack_run,
    )


@workflow.defn
class StackDependencyChainWorkflow:
    @workflow.run
    async def run(
        self, input: StackDependencyInput
    ) -> List[Dict]:
        """
        Workflow to retrieve and process dependent stacks for a given stack.
        For each dependent stack found, it kicks off a StackExecutionWorkflow.

        Args:
            input (StackDependencyInput): Contains the stack_id to find dependencies for.

        Returns:
            List[Dict]: Results from running each dependent stack, containing run information
                       like id, branch, and state.
        """
        # Retry policy for activities and child workflows
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            maximum_attempts=3,
            non_retryable_error_types=[],
        )

        # Execute the fetch_dependent_stacks activity
        dependent_stacks = await workflow.execute_activity(
            fetch_dependent_stacks,
            StackDependencyInput(stack_id=input.stack_id),
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(seconds=30),
        )

        workflow.logger.info(
            f"Found {len(dependent_stacks)} dependent stacks for stack {input.stack_id}"
        )

        # Start a StackExecutionWorkflow for each dependent stack
        run_results = []
        for stack in dependent_stacks:
            stack_id = stack["id"]
            workflow.logger.info(f"Starting StackExecutionWorkflow for stack {stack_id}")
            
            # Start the child workflow and await its completion
            handle = await workflow.start_child_workflow(
                StackExecutionWorkflow,
                StackExecutionInput(stack_id=stack_id),
                id=f"run-stack-{stack_id}",
                retry_policy=retry_policy,
            )
            # Await the actual result from the child workflow
            result = await handle
            run_results.append(result)
            workflow.logger.info(f"Successfully started run for stack {stack_id}")

        return run_results


@workflow.defn
class StackExecutionWorkflow:
    @workflow.run
    async def run(self, input: StackExecutionInput) -> Dict:
        """
        Workflow to execute a Spacelift stack.

        Args:
            input (StackExecutionInput): Contains the stack_id to trigger a run for.

        Returns:
            Dict: Information about the triggered run including id, branch, and state.
        """
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            maximum_attempts=3,
            non_retryable_error_types=[],
        )

        # Execute the trigger_stack_run activity
        result = await workflow.execute_activity(
            trigger_stack_run,
            input,
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(seconds=30),
        )

        workflow.logger.info(
            f"Successfully triggered run for stack {input.stack_id}: {result}"
        )

        return result