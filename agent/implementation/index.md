## Project Overview

This project involves setting up a system to manage Spacelift stack execution using FastAPI and Temporal. The implementation is divided into several phases, each introducing specific features and technologies.

### [Phase 1: Set Up FastAPI Webhook](./phase1.md)
**Features:**
- FastAPI application creation
- Endpoint `/webhook` to receive POST requests
- Payload processing and logging

**Technology:**
- FastAPI

### [Phase 2: Process Notification Payload](./phase2.md)
**Features:**
- Payload parsing
- Extraction of relevant information (e.g., stack ID, status)
- Logging of processed data

**Technology:**
- FastAPI

### [Phase 3: Set Up Temporal Server](./phase3.md)
**Features:**
- Local Temporal server setup using Docker
- Server accessibility and readiness for workflow definitions

**Technology:**
- Temporal
- Docker

### [Phase 4: Define Temporal Workflow](./phase4.md)
**Features:**
- Definition of a Temporal workflow for stack execution
- Workflow triggering with stack information payload
- Implementation of workflow logic

**Technology:**
- Temporal

### [Phase 5: Integrate FastAPI with Temporal](./phase5.md)
**Features:**
- Integration of FastAPI webhook with Temporal workflow
- Successful triggering of Temporal workflow with processed payload
- Integration testing and verification

**Technology:**
- FastAPI
- Temporal

### [Phase 6: Configure Spacelift Labels](./phase6.md)
**Features:**
- Creation of labels in Spacelift to trigger the webhook
- Configuration of webhook URL in Spacelift label settings
- Testing of labels to ensure correct triggering of the webhook

**Technology:**
- Spacelift

### [Phase 7: Test End-to-End Flow](./phase7.md)
**Features:**
- End-to-end testing with a test Spacelift stack change
- Verification of webhook processing and Temporal workflow triggering
- Successful management of stack execution by Temporal workflow
- Documentation of the entire flow

**Technology:**
- FastAPI
- Temporal
- Spacelift