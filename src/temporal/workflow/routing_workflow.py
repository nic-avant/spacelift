from datetime import timedelta
from typing import Dict, List

from temporalio import workflow
from temporalio.common import (
    RetryPolicy,
)

with workflow.unsafe.imports_passed_through():
    from temporal.activities.get_dependent_stacks import (
        InputParams,
        get_dependent_stacks_activity,
    )
    from temporal.activities.run_stack import (
        RunStackInput,
        run_stack,
    )


@workflow.defn
class DependentStacksWorkflow:
    @workflow.run
    async def run(
        self, input: InputParams
    ) -> List[Dict]:
        """
        Workflow to retrieve and process dependent stacks for a given stack.
        For each dependent stack found, it kicks off a RunStackWorkflow.

        Args:
            input (InputParams): Object with `stack_id` attribute: The ID of the stack to find dependencies for.

        Returns:
            List[Dict]: Results from running each dependent stack, containing run information like id and branch.
        """
        # Retry policy for the activity
        retry_policy = RetryPolicy(
            initial_interval=timedelta(
                seconds=1
            ),
            maximum_interval=timedelta(
                seconds=60
            ),
            maximum_attempts=3,
            non_retryable_error_types=[],
        )

        # Execute the get_dependent_stacks activity
        dependent_stacks = await workflow.execute_activity(
            get_dependent_stacks_activity,
            InputParams(
                stack_id=input.stack_id
            ),
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(
                seconds=30
            ),
        )

        workflow.logger.info(
            f"Found {len(dependent_stacks)} dependent stacks for stack {input.stack_id}"
        )

        # Start a RunStackWorkflow for each dependent stack
        run_results = []
        for stack in dependent_stacks:
            stack_id = stack["id"]
            workflow.logger.info(f"Starting RunStackWorkflow for stack {stack_id}")
            
            result = await workflow.start_child_workflow(
                RunStackWorkflow,
                RunStackInput(stack_id=stack_id),
                id=f"run-stack-{stack_id}",
                retry_policy=retry_policy,
            )
            run_results.append(result)
            workflow.logger.info(f"Successfully started run for stack {stack_id}")

        return run_results


@workflow.defn
class RunStackWorkflow:
    @workflow.run
    async def run(self, input: RunStackInput) -> Dict:
        """
        Workflow to execute a Spacelift stack.

        Args:
            input (RunStackInput): Object with stack_id attribute to identify which stack to run.

        Returns:
            Dict: Information about the triggered run including id, branch, and state.
        """
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            maximum_attempts=3,
            non_retryable_error_types=[],
        )

        # Execute the run_stack activity
        result = await workflow.execute_activity(
            run_stack,
            input,
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(seconds=30),
        )

        workflow.logger.info(
            f"Successfully triggered run for stack {input.stack_id}: {result}"
        )

        return result
