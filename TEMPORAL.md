# Temporal Workflow Documentation

## Introduction to Temporal

[Temporal](https://temporal.io) is an open-source, distributed, and scalable workflow orchestration platform that enables developers to build and operate reliable applications at scale.

## Project Temporal Integration

This project uses Temporal for robust workflow management, specifically for handling Spacelift webhook events and stack execution workflows.

### Key Temporal Concepts

#### Workflows
- Workflows are the core abstraction in Temporal
- Represent a set of actions that can be executed reliably and consistently
- In this project, workflows manage Spacelift stack run lifecycles

#### Activities
- Discrete units of work performed within a workflow
- Represent individual tasks like triggering a stack run, logging events, or handling notifications

#### Signal Methods
- Allow external communication with running workflows
- Enable dynamic interaction and state modification during workflow execution

### Workflow Types in This Project

1. **Stack Dependency Chain Workflow**
   - Located in `src/temporal/workflows/stack_dependency_chain.py`
   - Manages the discovery and execution of dependent Spacelift stacks
   - Implemented in the `StackDependencyChainWorkflow` class
   - Spawns `StackExecutionWorkflow` for each dependent stack

2. **Stack Execution Workflow**
   - Located in `src/temporal/workflows/stack_dependency_chain.py`
   - Handles individual stack run execution
   - Implemented in the `StackExecutionWorkflow` class

### Activities

1. **Stack Dependencies Activity**
   - Located in `src/temporal/activities/stack_dependencies.py`
   - Retrieves dependent stacks information
   - Implemented in the `fetch_dependent_stacks` function

2. **Stack Operations Activity**
   - Located in `src/temporal/activities/stack_operations.py`
   - Handles stack run operations
   - Implemented in the `trigger_stack_run` function

### Temporal Worker

The Temporal worker is implemented in `src/temporal/worker.py`. It:
- Registers both workflows and activities
- Connects to the Temporal server using the configured TEMPORAL_URL
- Processes tasks on the "spacelift-task-queue" task queue

## Configuration and Setup

### Dependencies
- `temporalio` Python library for Python SDK integration
- Temporal server running and accessible

### Environment Configuration
- `TEMPORAL_URL`: Temporal server endpoint (defaults to "temporal:7233")
- Task queue configured as "spacelift-task-queue"

### Testing Connection
The project includes a test script (`src/temporal/temporal_test.py`) that:
- Verifies connection to the Temporal server
- Lists available namespaces
- Provides basic logging of connection status

## Best Practices

1. Design workflows to be deterministic
2. Keep activities idempotent
3. Use appropriate error handling and retry mechanisms
4. Implement comprehensive logging
5. Secure sensitive information like API credentials

## Monitoring and Observability

- Temporal provides built-in visibility into workflow executions
- Use Temporal Web UI for tracking workflow status
- Implement detailed logging in workflows and activities

## Extending the Workflow

The current implementation can be extended by:
- Adding new event types
- Implementing custom signal methods
- Integrating with additional external systems
- Enhancing error handling and notification mechanisms

## References

- [Temporal Documentation](https://docs.temporal.io/)
- [Temporal Python SDK](https://github.com/temporalio/sdk-python)