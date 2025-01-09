# Spacelift Webhook Workflow Documentation

## Overview
The `SpaceliftWebhookWorkflow` is a Temporal workflow designed to handle webhook events from Spacelift, providing a robust and extensible mechanism for processing stack execution events.

## Workflow Lifecycle

### Event Types
The workflow supports three primary event types:
1. `triggered`: When a stack run is initiated
2. `completed`: When a stack run successfully completes
3. `failed`: When a stack run encounters an error

### Workflow Execution Flow
1. **Payload Validation**
   - Checks for required `stack_id`
   - Validates webhook payload structure

2. **Event Processing**
   - Initializes Spacelift client
   - Determines event type
   - Executes appropriate action based on event type

3. **Error Handling**
   - Implements retry policies for run triggering
   - Provides comprehensive logging
   - Supports signal methods for custom post-run actions

## Key Components

### Main Workflow Method: `run()`
- Receives webhook payload
- Logs incoming events
- Manages workflow logic based on event type
- Returns processed event details

### Signal Methods
- `handle_completed_run()`: Custom actions for successful runs
- `handle_failed_run()`: Error handling and notification logic

## Retry and Error Handling
- Uses Temporal's `RetryPolicy` for run triggering
- Configurable retry attempts (default: 3)
- Exponential backoff for retry intervals

## Configuration Considerations
- Spacelift client configuration (base URL, API keys) should be securely managed
- Logging levels can be adjusted as needed
- Signal methods can be extended for custom post-run actions

## Example Workflow Scenarios

### Successful Stack Run
1. Webhook receives `triggered` event
2. Spacelift client initiates stack run
3. Run completes successfully
4. `handle_completed_run()` is called
5. Workflow logs and returns success status

### Failed Stack Run
1. Webhook receives `failed` event
2. Workflow logs error details
3. `handle_failed_run()` is triggered
4. Potential notifications or error tracking initiated

## Extensibility
The workflow is designed to be easily extended:
- Add more event types
- Implement custom notification mechanisms
- Integrate with external monitoring or alerting systems

## Best Practices
- Keep API credentials secure
- Implement comprehensive logging
- Design signal methods to be idempotent
- Handle potential exceptions gracefully