# Technology Stack

## Core Technologies
- **Language**: Python 3.10+
- **Dependency Management**: Poetry
- **API Interaction**: GraphQL (via `gql` library)
- **Workflow Management**: Temporal
- **Web Framework**: FastAPI
- **Webhook Handling**: FastAPI

## Key Libraries
- `gql`: GraphQL client for Spacelift API interactions
- `temporalio`: Workflow orchestration
- `fastapi`: Web framework for webhook endpoints
- `pydantic`: Data validation
- `requests`: HTTP client library

## Project Structure
- `src/spacelift/`: Main source code directory
  - `main.py`: Core Spacelift API client
  - `webhook/`: Webhook handling
  - `workflow/`: Temporal workflow implementations
  - `tests/`: Project test suite

## Development Tools
- Type Checking: mypy
- Testing: pytest
- Linting: flake8, black
- Environment Management: direnv, .env support

## Deployment Considerations
- Docker support via Dockerfile
- Environment configuration via .env and .envrc
- Supports local and containerized deployments