from dataclasses import dataclass
from temporalio import activity
from spacelift.main import Spacelift

@dataclass
class InputParams:
    stack_id: str

@activity.defn
async def get_dependent_stacks_activity(input: InputParams) -> list[dict]:
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
        if any(f"dependsOn:{input.stack_id}" in x for x in stack.get("labels", []))
    ]
    return dependent_stacks
