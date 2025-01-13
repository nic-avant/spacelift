# Spacelift Temporal Workflows

This directory contains Temporal workflows for managing Spacelift stack dependencies and executions.

## Workflow Structure

### StackDependencyChainWorkflow

The main workflow that orchestrates the process of finding and executing dependent Spacelift stacks.

Flow:
1. Receives a stack ID as input
2. Fetches all stacks that depend on the input stack (using `fetch_dependent_stacks` activity)
3. For each dependent stack found, initiates a `StackExecutionWorkflow` as a child workflow
4. Collects and returns results from all stack executions

### StackExecutionWorkflow

A child workflow responsible for triggering runs on individual Spacelift stacks.

Flow:
1. Receives a stack ID as input
2. Triggers a run on the specified stack (using `trigger_stack_run` activity)
3. Returns the run information (id, branch, state)

## Activities

The workflows use two main activities:

- `fetch_dependent_stacks`: Queries Spacelift API to find stacks that depend on a given stack
- `trigger_stack_run`: Triggers a run on a specified Spacelift stack

## Retry Policies

Both workflows and activities use retry policies with:
- Initial retry interval: 1 second
- Maximum retry interval: 60 seconds
- Maximum attempts: 3

## Usage

To start the dependency chain workflow:

```python
await client.start_workflow(
    StackDependencyChainWorkflow.run,
    StackDependencyInput(stack_id="your-stack-id"),
    id="dependency-chain-your-stack-id",
    task_queue="spacelift-task-queue"
)
```

The workflow will automatically handle finding and executing all dependent stacks.