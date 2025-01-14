import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from temporalio.client import Client

from app.app import app
from app.models.notification_policy import NotificationPolicy, RunUpdated, Run, Stack, Space, Commit, CreatorSession, RuntimeConfig, Urls, Timing

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def valid_webhook_payload():
    return {
        "account": {"id": "test-account"},
        "run_updated": {
            "state": "FINISHED",
            "username": "test-user",
            "note": "Test run completed",
            "run": {
                "branch": "main",
                "commit": {
                    "author": "test-author",
                    "branch": "main",
                    "created_at": 1234567890,
                    "hash": "abcdef123456",
                    "message": "Test commit",
                    "url": "https://github.com/test/repo/commit/abcdef123456"
                },
                "created_at": 1234567890,
                "creator_session": {
                    "admin": False,
                    "creator_ip": "127.0.0.1",
                    "login": "test-user",
                    "name": "Test User",
                    "teams": [],
                    "machine": False
                },
                "id": "run-123",
                "runtime_config": {
                    "runner_image": "spacelift/runner:latest",
                    "terraform_version": "1.0.0"
                },
                "state": "FINISHED",
                "type": "TRACKED",
                "updated_at": 1234567890
            },
            "stack": {
                "branch": "main",
                "id": "stack-123",
                "name": "test-stack",
                "repository": "test/repo",
                "space": {
                    "id": "space-123",
                    "labels": [],
                    "name": "test-space"
                },
                "state": "FINISHED",
                "tracked_commit": {
                    "author": "test-author",
                    "branch": "main",
                    "created_at": 1234567890,
                    "hash": "abcdef123456",
                    "message": "Test commit",
                    "url": "https://github.com/test/repo/commit/abcdef123456"
                }
            },
            "timing": [
                {
                    "duration": 60,
                    "state": "FINISHED"
                }
            ],
            "urls": {
                "run": "https://spacelift.io/test/stack/run/123"
            }
        },
        "webhook_endpoints": []
    }

@pytest.mark.asyncio
async def test_webhook_valid_payload(test_client, valid_webhook_payload):
    """Test webhook endpoint with valid payload and FINISHED state"""
    mock_client = AsyncMock(spec=Client)
    mock_workflow = AsyncMock()
    mock_workflow.id = "test-workflow-id"
    mock_client.start_workflow.return_value = mock_workflow

    with patch("temporalio.client.Client.connect", return_value=mock_client):
        response = test_client.post("/webhook", json=valid_webhook_payload)
        assert response.status_code == 200
        assert response.json() == {
            "message": "Webhook processed and workflow triggered",
            "workflow_id": "test-workflow-id"
        }

@pytest.mark.asyncio
async def test_webhook_non_finished_state(test_client, valid_webhook_payload):
    """Test webhook endpoint with non-FINISHED state"""
    valid_webhook_payload["run_updated"]["state"] = "RUNNING"
    response = test_client.post("/webhook", json=valid_webhook_payload)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Webhook processed and skipped"
    }

@pytest.mark.asyncio
async def test_webhook_invalid_payload(test_client):
    """Test webhook endpoint with invalid payload"""
    invalid_payload = {"invalid": "data"}
    response = test_client.post("/webhook", json=invalid_payload)
    assert response.status_code == 400
    assert "Invalid payload format" in response.json()["detail"]

@pytest.mark.asyncio
@patch("temporalio.client.Client.connect", side_effect=Exception("Temporal connection error"))
async def test_webhook_temporal_error(mock_connect, test_client, valid_webhook_payload):
    """Test webhook endpoint with Temporal connection error"""
    response = test_client.post("/webhook", json=valid_webhook_payload)
    assert response.status_code == 500
    assert "Workflow error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_webhook_general_error(test_client):
    """Test webhook endpoint with general error"""
    response = test_client.post("/webhook", json=None)
    assert response.status_code == 500
    assert response.json()["detail"] is not None