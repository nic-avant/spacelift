# Spacelift FastAPI Application

A FastAPI wrapper around the Spacelift Python client that provides RESTful endpoints for interacting with the Spacelift GraphQL API.

## Features

- **Stack Management**
  - List and filter stacks by labels and state
  - Get stack details
  - Trigger stack runs
  - Delete stacks
  - Create stacks from blueprints

- **Space Management**
  - List all spaces
  - Get space details
  - Create new spaces
  - Delete spaces

- **Context Management**
  - List all contexts
  - Get context details
  - Create new contexts with environment variables
  - Delete contexts

- **Blueprint Management**
  - List all blueprints
  - Get blueprint details with input specifications

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables in a `.env` file:
```bash
SPACELIFT_BASE_URL="https://your-org.app.spacelift.io/graphql"
SPACELIFT_KEY_ID="your-key-id"
SPACELIFT_KEY_SECRET="your-key-secret"
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## API Endpoints

### Stacks

- `GET /stacks` - List all stacks
  - Query params:
    - `label` (optional): Filter stacks by label
    - `state` (optional): Filter stacks by state (e.g., FINISHED, UNCONFIRMED, STOPPED)

- `GET /stacks/state/{state}` - Get all stacks with a specific state
  - Common states:
    - `FINISHED`: Stack run completed successfully
    - `UNCONFIRMED`: Stack is waiting for confirmation
    - `STOPPED`: Stack run was stopped
    - `FAILED`: Stack run failed

- `GET /stacks/{stack_id}` - Get stack details

- `POST /stacks/{stack_id}/run` - Trigger a stack run

- `DELETE /stacks/{stack_id}` - Delete a stack

- `POST /stacks/blueprint` - Create a stack from blueprint
  ```json
  {
    "blueprint_id": "string",
    "inputs": [
      {
        "id": "string",
        "value": "string"
      }
    ]
  }
  ```

### Spaces

- `GET /spaces` - List all spaces

- `GET /spaces/{space_id}` - Get space details

- `POST /spaces` - Create a new space
  ```json
  {
    "name": "string",
    "parent_space_id": "string",
    "description": "string",
    "labels": ["string"],
    "inherit_entities": true
  }
  ```

- `DELETE /spaces/{space_id}` - Delete a space

### Contexts

- `GET /contexts` - List all contexts

- `GET /contexts/{context_id}` - Get context details

- `POST /contexts` - Create a new context
  ```json
  {
    "name": "string",
    "space_id": "string",
    "description": "string",
    "labels": ["string"],
    "envvars": [
      {
        "id": "string",
        "value": "string",
        "type": "ENVIRONMENT_VARIABLE",
        "writeOnly": false
      }
    ]
  }
  ```

- `DELETE /contexts/{context_id}` - Delete a context

### Blueprints

- `GET /blueprints` - List all blueprints

- `GET /blueprints/{blueprint_id}` - Get blueprint details

## Error Handling

The API uses standard HTTP status codes:
- `200`: Success
- `404`: Resource not found
- `500`: Server error

Errors are returned in the following format:
```json
{
  "detail": "Error message"
}
```

## Security

The application uses environment variables for authentication with Spacelift. Make sure to:
1. Never commit your `.env` file
2. Use appropriate security measures when deploying the application
3. Consider implementing additional authentication for the FastAPI endpoints in production

## Development

The application is built using:
- FastAPI for the web framework
- Pydantic for data validation
- Python-dotenv for environment variable management
- Spacelift Python client for interacting with Spacelift's GraphQL API
