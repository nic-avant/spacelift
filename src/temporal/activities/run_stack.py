from dataclasses import dataclass
from temporalio import activity

from src.spacelift.main import Spacelift


@dataclass
class RunStackInput:
    """Input for the run_stack activity."""
    stack_id: str


@activity.defn
async def run_stack(input: RunStackInput) -> dict:
    """
    Temporal activity to trigger a run on a Spacelift stack.
    
    Args:
        input: RunStackInput containing the stack_id to run
        
    Returns:
        dict: Information about the triggered run including id and branch
    """
    spacelift = Spacelift()
    result = spacelift.trigger_run(
        stack_id=input.stack_id,
        query_fields=["id", "branch", "state"]
    )
    return result