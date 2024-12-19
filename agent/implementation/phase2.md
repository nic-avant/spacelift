### Phase 2: Process Notification Payload

<TASKS prepend>

- [x] Parse the payload received by the webhook.
- [x] Extract relevant information (e.g., stack ID, status) from the payload.
- [x] Log the processed data for verification.
- [x] Update the webhook endpoint to accept payload data through FastAPI Swagger docs.

</TASKS prepend>

Additional improvements made:
- Updated the `SpaceliftPayload` model to better reflect the structure of the incoming payload.
- Created additional models for nested structures (CommitInfo, RunInfo, StackInfo, SpaceInfo).
- Modified the `parse_payload` function to extract more detailed information.
- Updated the webhook response to include a comprehensive set of processed data.
- Added a new `WebhookPayload` model to match the structure of the incoming JSON payload.
- Modified the `/webhook` endpoint to accept a `WebhookPayload` instead of a `Request` object.

Next steps:
- Test the webhook endpoint using the FastAPI Swagger docs to ensure it can receive and process payload data correctly.
- Implement Temporal workflow triggering (to be done in later phases).
- Add unit tests for the webhook and payload processing.
- Consider adding more detailed validation for the incoming payload.

Additional improvements made:
- Enhanced the SpaceliftPayload model to include more fields (branch, commit_sha, timestamp, additional_info).
- Created a separate parse_payload function for better organization and reusability.
- Improved error handling and logging.
- Included processed data in the webhook response for easier debugging and verification.

Next steps:
- Implement Temporal workflow triggering (to be done in later phases).
- Add unit tests for the webhook and payload processing.
- Consider adding more detailed validation for the incoming payload.