# Technology Stack

## Core Technologies
- **Language**: Python 3.10+
- **Infrastructure Management**: Spacelift.io
- **Workflow Management**: Temporal
- **Web Framework**: FastAPI
- **Dependency Management**: Poetry

## Key Libraries and Integrations
- **Infrastructure Management**
  - Spacelift GraphQL API (via `gql`)
  - Infrastructure state tracking
  - Stack dependency resolution

- **Change Management**
  - `temporalio`: Infrastructure change workflow orchestration
  - `fastapi`: Change event webhooks
  - `pydantic`: Data validation

- **Development Tools**
  - `pytest`: Testing infrastructure
  - `mypy`: Type checking
  - `flake8`, `black`: Code quality
  - `direnv`: Environment management

## Project Structure
- `src/spacelift/`: Infrastructure client and models
  - `main.py`: Spacelift API client wrapper
  - `app.py`: FastAPI application
  - `models/`: Data schemas
  - `mock_spacelift.py`: Test infrastructure mocks

- `src/temporal/`: Change workflow management
  - `activities/`: Infrastructure operations
    - `stack_dependencies.py`: Dependency resolution
    - `stack_operations.py`: Stack execution operations
  - `workflows/`: Change orchestration
    - `stack_dependency_chain.py`: Dependency chain execution
  - `worker.py`: Worker process
  - `temporal_test.py`: Workflow testing

- `tests/`: Test suite

## Development Environment
- Local Temporal server via Docker
- PostgreSQL for workflow state
- Web UI for workflow monitoring
- Environment configuration via .env

## Deployment Architecture
- Docker containerization
- Environment-specific configurations
- Scalable worker processes
- Persistent workflow state