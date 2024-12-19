## Project Overview

This project involves setting up a system to manage Spacelift stack execution using FastAPI and Temporal. The implementation is divided into several phases, each introducing specific features and technologies.

### Phase 1: Set Up FastAPI Webhook
**Features:**
- [x] Create a FastAPI application.
- [x] Define an endpoint `/webhook` to receive POST requests.
- [x] Process the incoming payload and log the data.

**Technology:**
- FastAPI

### Phase 2: Process Notification Payload
**Features:**
- [x] Parse the payload received by the webhook.
- [x] Extract relevant information (e.g., stack ID, status) from the payload.
- [x] Log the processed data for verification.
- [x] Update the webhook endpoint to accept payload data through FastAPI Swagger docs.

**Technology:**
- FastAPI

### Phase 3: Set Up Temporal Server
**Features:**
- [x] Run a Temporal server locally using Docker.
- [x] Ensure the server is accessible and ready to accept workflow definitions.

**Technology:**
- Temporal
- Docker

### Phase 4: Define Temporal Workflow
**Features:**
- [x] Define a Temporal workflow to handle stack execution.
- [x] Trigger the workflow with a payload containing stack information.
- [x] Implement the workflow logic to manage stack execution.

**Technology:**
- Temporal

### Phase 5: Integrate FastAPI with Temporal
**Features:**
- [ ] Send the processed payload from the FastAPI webhook to the Temporal workflow.
- [ ] Trigger the Temporal workflow successfully with the payload.
- [ ] Test and verify the integration.

**Technology:**
- FastAPI
- Temporal

### Phase 6: Configure Spacelift Labels
**Features:**
- [ ] Create labels in Spacelift to trigger the webhook.
- [ ] Configure the webhook URL in the Spacelift label settings.
- [ ] Test the labels to ensure they trigger the webhook correctly.

**Technology:**
- Spacelift

### Phase 7: Test End-to-End Flow
**Features:**
- [ ] Trigger the webhook with a test Spacelift stack change.
- [ ] Process the payload and trigger the Temporal workflow.
- [ ] Manage the stack execution successfully with the Temporal workflow.
- [ ] Verify and document the entire flow.

**Technology:**
- FastAPI
- Temporal
- Spacelift