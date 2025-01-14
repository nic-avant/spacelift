# Temporal Workflow Documentation

## Introduction to Temporal

[Temporal](https://temporal.io) is an open-source, distributed, and scalable workflow orchestration platform that enables developers to build and operate reliable applications at scale.

## Project Temporal Integration

This project uses Temporal to automate the execution of dependent Spacelift stacks. When a stack finishes running, the system automatically identifies and triggers runs for any stacks that depend on it. Dependencies are declared using Spacelift stack labels in the format `dependsOn:stack-id`.

### Flow Overview
1. A stack completes execution
2. Webhook receives notification
3. Temporal workflow is triggered
4. System queries Spacelift for stacks with matching dependency labels
5. Child workflows are spawned to trigger runs for dependent stacks
6. Retries and error handling ensure reliable execution

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
   - Primary workflow triggered by webhook notifications
   - Discovers dependent stacks by querying Spacelift API for stacks with matching `dependsOn:stack-id` labels
   - Implements retry policy with exponential backoff (1-60 seconds, max 3 attempts)
   - Spawns child `StackExecutionWorkflow` for each dependent stack
   - Returns results from all triggered stack runs

2. **Stack Execution Workflow**
   - Located in `src/temporal/workflows/stack_dependency_chain.py`
   - Child workflow responsible for triggering individual stack runs
   - Uses Spacelift API to initiate stack execution
   - Implements same retry policy as parent workflow
   - Returns run information including ID, branch, and state

### Activities

1. **Stack Dependencies Activity**
   - Located in `src/temporal/activities/stack_dependencies.py`
   - Uses Spacelift API to query all stacks with their labels and attached contexts
   - Filters stacks based on dependency labels (format: `dependsOn:stack-id`)
   - Returns list of dependent stacks with their metadata
   - Input: `StackDependencyInput` with stack_id to find dependencies for
   - Output: List of stack objects containing ID, labels, and context information

2. **Stack Operations Activity**
   - Located in `src/temporal/activities/stack_operations.py`
   - Interfaces with Spacelift API to trigger stack runs
   - Input: `StackExecutionInput` containing stack_id to trigger
   - Output: Run details including ID, branch, and state
   - Handles API errors and provides meaningful error messages

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

1. Stack Dependencies
   - Use clear, consistent naming for dependency labels (`dependsOn:stack-id`)
   - Document dependencies in stack configurations
   - Avoid circular dependencies between stacks
   - Consider dependency chain length when designing stack relationships

2. Workflow Design
   - Keep workflows deterministic and idempotent
   - Handle API rate limits in activities
   - Use appropriate timeouts for API operations
   - Implement comprehensive error handling with retries
   - Log key events and state transitions

3. Security
   - Secure Spacelift API credentials using environment variables
   - Validate webhook payloads
   - Monitor workflow access patterns
   - Implement appropriate access controls

4. Monitoring
   - Track dependency chain execution times
   - Monitor for failed or stuck workflows
   - Set up alerts for workflow failures
   - Keep audit logs of triggered stack runs

## Monitoring and Observability

- Temporal provides built-in visibility into workflow executions
- Use Temporal Web UI for tracking workflow status
- Implement detailed logging in workflows and activities

## Extending the Workflow

The dependency management system can be extended in several ways:

1. Enhanced Dependency Rules
   - Add support for conditional dependencies (e.g., only trigger on successful runs)
   - Implement dependency priority levels to control execution order
   - Support dependency groups or tags for batch processing
   - Add dependency validation rules to prevent circular dependencies

2. Advanced Workflow Features
   - Add workflow cancellation support for stopping dependency chains
   - Implement stack run status monitoring with timeout handling
   - Add support for manual approval steps in critical paths
   - Create dependency visualization tools for stack relationships

3. Integration Enhancements
   - Add support for other CI/CD platforms beyond Spacelift
   - Implement notification systems (Slack, Email, etc.) for run status
   - Create audit/reporting tools for dependency chain analysis
   - Add metrics collection for performance analytics

4. Custom Controls
   - Add rate limiting for stack runs to prevent system overload
   - Implement maintenance windows for controlled execution
   - Create blackout periods to prevent runs during sensitive times
   - Add stack-specific retry policies based on failure patterns

## References

- [Temporal Documentation](https://docs.temporal.io/)
- [Temporal Python SDK](https://github.com/temporalio/sdk-python)