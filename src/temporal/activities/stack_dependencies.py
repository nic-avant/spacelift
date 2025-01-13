from dataclasses import dataclass

from spacelift.main import Spacelift
from temporalio import activity


@dataclass
class StackDependencyInput:
    """Input parameters for fetching dependent stacks."""
    stack_id: str


@activity.defn
async def fetch_dependent_stacks(
    input: StackDependencyInput,
) -> list[dict]:
    """
    Temporal activity to retrieve dependent stacks for a given stack_id.

    Args:
        input (StackDependencyInput): Contains the stack_id to find dependencies for.

    Returns:
        list[dict]: A list of dependent stacks, each containing stack information
                   including id, labels, and attached contexts.
    """
    sl = Spacelift()
    stacks = sl.get_stacks(
        query_fields=[
            "id",
            "labels",
            "attachedContexts { contextId }",
        ]
    )
    dependent_stacks = [
        stack
        for stack in stacks
        if any(
            f"dependsOn:{input.stack_id}"
            in x
            for x in stack.get(
                "labels", []
            )
        )
    ]
    return dependent_stacks