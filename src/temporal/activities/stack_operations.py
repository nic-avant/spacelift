from dataclasses import dataclass
from temporalio import activity

from spacelift.main import Spacelift


@dataclass
class StackExecutionInput:
    """Input parameters for triggering a stack run."""
    stack_id: str


@activity.defn
async def trigger_stack_run(input: StackExecutionInput) -> dict:
    """
    Temporal activity to trigger a run on a Spacelift stack.
    
    Args:
        input (StackExecutionInput): Contains the stack_id to trigger a run for.
        
    Returns:
        dict: Information about the triggered run including id, branch, and state.
    """
    spacelift = Spacelift()
    result = spacelift.trigger_run(
        stack_id=input.stack_id,
        query_fields=["id", "branch", "state"]
    )
    return result