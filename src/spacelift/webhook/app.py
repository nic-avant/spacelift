from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from typing import Optional, Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class CommitInfo(BaseModel):
    author: str
    branch: str
    hash: str
    message: str
    url: str

class RunInfo(BaseModel):
    id: str
    state: str
    type: str
    created_at: int
    updated_at: int

class StackInfo(BaseModel):
    id: str
    name: str
    namespace: str
    labels: List[str]

class SpaceInfo(BaseModel):
    id: str
    name: str

class SpaceliftPayload(BaseModel):
    account_name: str
    run: RunInfo
    stack: StackInfo
    space: SpaceInfo
    commit: CommitInfo
    changes: List[Dict[str, Any]]

class WebhookPayload(BaseModel):
    account: Dict[str, Any]
    run_updated: Dict[str, Any]

def parse_payload(payload: Dict[str, Any]) -> SpaceliftPayload:
    return SpaceliftPayload(
        account_name=payload.get("account", {}).get("name"),
        run=RunInfo(
            id=payload.get("run_updated", {}).get("run", {}).get("id"),
            state=payload.get("run_updated", {}).get("run", {}).get("state"),
            type=payload.get("run_updated", {}).get("run", {}).get("type"),
            created_at=payload.get("run_updated", {}).get("run", {}).get("created_at"),
            updated_at=payload.get("run_updated", {}).get("run", {}).get("updated_at")
        ),
        stack=StackInfo(
            id=payload.get("run_updated", {}).get("stack", {}).get("id"),
            name=payload.get("run_updated", {}).get("stack", {}).get("name"),
            namespace=payload.get("run_updated", {}).get("stack", {}).get("namespace"),
            labels=payload.get("run_updated", {}).get("stack", {}).get("labels", [])
        ),
        space=SpaceInfo(
            id=payload.get("run_updated", {}).get("stack", {}).get("space", {}).get("id"),
            name=payload.get("run_updated", {}).get("stack", {}).get("space", {}).get("name")
        ),
        commit=CommitInfo(
            author=payload.get("run_updated", {}).get("run", {}).get("commit", {}).get("author"),
            branch=payload.get("run_updated", {}).get("run", {}).get("commit", {}).get("branch"),
            hash=payload.get("run_updated", {}).get("run", {}).get("commit", {}).get("hash"),
            message=payload.get("run_updated", {}).get("run", {}).get("commit", {}).get("message"),
            url=payload.get("run_updated", {}).get("run", {}).get("commit", {}).get("url")
        ),
        changes=payload.get("run_updated", {}).get("run", {}).get("changes", [])
    )

@app.post("/webhook")
async def webhook(payload: WebhookPayload):
    try:
        logger.info(f"Received webhook payload: {payload.dict()}")

        # Parse and extract relevant information
        processed_payload = parse_payload(payload.dict())

        # Log the processed data
        logger.info(f"Processed payload: {processed_payload.dict()}")

        # TODO: Trigger Temporal workflow with processed payload

        return {
            "status": "success",
            "message": "Webhook received and processed",
            "processed_data": {
                "account_name": processed_payload.account_name,
                "run_id": processed_payload.run.id,
                "run_state": processed_payload.run.state,
                "stack_id": processed_payload.stack.id,
                "stack_name": processed_payload.stack.name,
                "space_id": processed_payload.space.id,
                "space_name": processed_payload.space.name,
                "commit_hash": processed_payload.commit.hash,
                "commit_branch": processed_payload.commit.branch,
                "changes_count": len(processed_payload.changes)
            }
        }
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)