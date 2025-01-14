# Spacelift Client and Workflow Manager

This project provides a simple client library for working with the [spacelift.io](https://spacelift.io) API, along with an automated dependency management system for Spacelift stacks. It enables automatic triggering of dependent stacks when their dependencies complete execution.

## Core Problem Solved

This project solves the challenge of managing dependencies between Spacelift stacks by:
1. Allowing stacks to declare dependencies using labels (e.g., `dependsOn:stack-id`)
2. Automatically detecting when a stack finishes execution via webhooks
3. Finding and triggering runs for all dependent stacks using Temporal workflows
4. Providing reliable execution with retries and error handling

## Project Design

For detailed design specifications, please refer to our design documentation:

- [Deliverables](agent/design/deliverables.md)
- [Project Overview](agent/design/overview.md)
- [Technology Stack](agent/design/tech-stack.md)

## Essential features:

### Spacelift Client
- Read operations for Spaces, Contexts, Stacks, and Blueprints
- Create operations for Spaces, Contexts, and Stacks (from Blueprints)
- Delete operations for Spaces, Contexts, and Stacks
- Trigger a run for a Stack
- Support for custom GraphQL queries via `_execute` method
- Environment variable configuration support
- JWT authentication handling

### Mock Client for Testing
- `MockSpacelift` class that mimics the real client's behavior
- In-memory storage of spaces, stacks, and contexts
- Perfect for unit testing without actual API calls
- Implements most read/write operations

### Webhook and Workflow Management
- FastAPI webhook to receive and validate Spacelift notifications
- Pydantic models for robust payload validation
- Temporal workflow integration for managing stack execution
- Automatic workflow triggering based on webhook events
- UUID-based workflow tracking
- Comprehensive error handling and logging

## Install
```bash
pip install spacelift
```

## Usage

### Spacelift Client
```python
from spacelift import Spacelift

def main():
    sl = Spacelift(
        base_url="https://ORGNAME.app.spacelift.io/graphql",
        key_id="01HCJMP<API_KEY_ID ~26CHAR LONG>",
        key_secret="e355ae6fd5<API_KEY_SECRET ~64 CHAR LONG>"
    )
    result = sl.get_stacks()
    print(result)

    result = sl.get_stacks(query_fields=["id", "name", "branch", "namespace", "repository", "state"])
    print(result)

if __name__ == "__main__":
    main()
```
```shell
$ python main.py
[{'id': 'demo-stack', 'space': 'legacy'}]
[{'id': 'demo-stack', 'name': 'Demo stack', 'branch': 'showcase', 'namespace': 'spacelift-io', 'repository': 'onboarding', 'state': 'FINISHED'}]
$ 
```

#### Relevant Methods
```python
from spacelift import Spacelift
sl = Spacelift()
sl.get_stacks()
sl.get_stack_by_id(stack_id)
sl.get_spaces()
sl.get_space_by_id(space_id)
sl.get_contexts()
sl.get_context_by_id(context_id)
sl.get_blueprints()
sl.get_blueprint_by_id(blueprint_id)

sl.create_stack_from_blueprint(blueprint_id, inputs=[{'id': 'bp_var1', 'value': 'bp_var1_value'}])

sl.trigger_run(stack_id)
```

### Webhook and Workflow Management
The webhook and workflow management system provides automated handling of Spacelift events:

#### Webhook Features
- FastAPI-based webhook server with robust error handling
- Pydantic models for payload validation and type safety
- Automatic extraction of critical information:
  - Run ID and Stack ID
  - State changes and timestamps
  - Branch and commit information
  - Space ID and stack metadata
- Seamless integration with Temporal workflows
- Detailed logging for debugging and monitoring

#### Temporal Workflow Integration
- Automatic workflow triggering on webhook events
- UUID-based workflow tracking
- Configurable task queue ("spacelift-task-queue")
- Development environment with:
  - Temporal server (gRPC on port 7233)
  - Web UI monitoring (http://localhost:8088)
  - PostgreSQL persistence (port 5433)
- Support for complex workflow patterns
- Error handling and retry logic

#### Running the stack

`docker compose up --build -d` will bring up all the containers for temporal and the fastapi app

The webhook is at `http://0.0.0.0:8000/webhook`. You can send POST requests to `http://0.0.0.0:8000/webhook` with Spacelift payload data.

Access the Temporal Web UI at http://localhost:8088

The Temporal server will be available at:
- gRPC: `localhost:7233` (for worker/client connections)
- Web UI: `localhost:8088` (for monitoring workflows)
- PostgreSQL: `localhost:5433` (if direct database access is needed)

#### Webhook Payload Structure
The webhook now processes and logs the following information from the Spacelift payload:
- Run ID
- Stack ID
- State
- Branch
- Commit SHA
- Timestamp
- Additional information (space ID, stack name, run type)

(Detailed usage instructions for the Temporal workflow will be added as it is implemented)

## Environment Variables
The `Spacelift` object can also infer its parameters from the following environment variables:

```bash
SPACELIFT_BASE_URL="https://ORGNAME.app.spacelift.io/graphql"
SPACELIFT_KEY_ID="01HCJMP<API_KEY_ID ~26CHAR LONG>"
SPACELIFT_KEY_SECRET="e355ae6fd5<API_KEY_SECRET ~64 CHAR LONG>"
```

## API Keys
Currently, this depends on the API Key workflow [here](https://docs.spacelift.io/integrations/api#spacelift-api-key-token).
The Current Spacelift.io documentation doesn't clearly specify this, but the API Key ID is the 26 character code that 
appears after the name in the web UI.  It does not appear at all in the downloaded `.config` file.  

The required Secret value is the first code (64 characters long) that appears in the downloaded `.config` file.

## Raw GraphQL
The `Spacelift` object also has a `_execute` method that accepts a raw GraphQL query object.  This can be created by 
sending a valid GraphQL query string to `gql.gql()` from the [gql package](https://pypi.org/project/gql/).  This is 
necessary for more advanced queries.

## Mocked Version
There's also a mocked version `MockedSpacelift` that can be used for testing.  It offers mocked versions of all the 
CRUD methods without any real API calls.

## Development

### Publishing
```bash
poetry build
poetry publish
```

### Setting up the development environment
1. Clone the repository
2. Install dependencies: `poetry install`
3. Set up pre-commit hooks: `pre-commit install`

### Running tests
```bash
poetry run pytest
```
