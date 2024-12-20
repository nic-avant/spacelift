# Technology Stack

## Core Technologies
- **Language**: Python 3.9+
- **Package Management**: Poetry
- **Type Checking**: Mypy

## API and Networking
- **API Client**: GraphQL (via `gql` package)
- **Web Framework**: FastAPI
- **HTTP Client**: `httpx` or `requests`

## Workflow Orchestration
- **Workflow Engine**: Temporal
- **Temporal Server**: Local development with Docker
- **Persistence Layer**: PostgreSQL

## Development and Testing
- **Testing Framework**: pytest
- **Mocking**: Built-in mocked client
- **Pre-commit Hooks**: Code quality and formatting
- **Linting**: 
  - flake8
  - black
  - isort

## Deployment and Infrastructure
- **Containerization**: Docker
- **Dependency Management**: Poetry
- **CI/CD**: (To be determined)

## External Integrations
- **Primary Integration**: Spacelift.io
- **Workflow Monitoring**: Temporal Web UI

## Environment Management
- **Virtual Environments**: Poetry
- **Environment Variables**: python-dotenv
- **Configuration**: YAML-based dynamic configuration

## Monitoring and Logging
- **Logging**: Python's built-in logging
- **Workflow Tracking**: Temporal Web UI