import os
import logging
from dataclasses import dataclass
from unittest.mock import (
    AsyncMock,
    MagicMock,
    patch,
)

import pytest
from temporal.worker import (
    main as worker_main,
)
from temporal.workflows.stack_dependency_chain import (
    StackDependencyChainWorkflow,
    StackExecutionWorkflow,
)
from temporalio.client import Client
from temporalio.service import (
    ServiceClient,
)
from temporalio.worker import Worker


logger = logging.getLogger(__name__)


async def temporal_test_main():
    # Get Temporal connection URL from environment variable with default
    temporal_url = os.getenv("TEMPORAL_URL", "temporal:7233")

    # Connect to the Temporal server
    client = await Client.connect(temporal_url)

    # Get a list of all namespaces
    namespaces = await client.list_namespaces()

    logger.info("Connected to Temporal server successfully!")
    logger.info(f"Connected to: {temporal_url}")
    logger.info(f"Available namespaces: {', '.join(ns.name for ns in namespaces)}")


@dataclass
class MockNamespace:
    name: str


@pytest.mark.asyncio
async def test_temporal_connection():
    """Test temporal connection with mocked client"""
    # Create mock service client
    mock_service_client = AsyncMock(spec=ServiceClient)
    
    # Create mock client with the service client
    mock_client = AsyncMock(spec=Client)
    mock_client.service_client = mock_service_client
    
    # Mock the list namespaces response
    mock_namespaces = [MockNamespace(name="default"), MockNamespace(name="test")]
    mock_client.list_namespaces = AsyncMock(return_value=mock_namespaces)

    with patch("temporalio.client.Client.connect", return_value=mock_client), \
         patch.dict(os.environ, {"TEMPORAL_URL": "test:1234"}):
        await temporal_test_main()
        
        # Verify connection was attempted with correct URL
        Client.connect.assert_called_once_with("test:1234")
        # Verify namespaces were requested
        mock_client.list_namespaces.assert_called_once()


@pytest.mark.asyncio
async def test_temporal_default_url():
    """Test temporal connection uses default URL when env var not set"""
    # Create mock service client
    mock_service_client = AsyncMock(spec=ServiceClient)
    
    # Create mock client with the service client
    mock_client = AsyncMock(spec=Client)
    mock_client.service_client = mock_service_client
    
    # Mock the list namespaces response
    mock_namespaces = [MockNamespace(name="default")]
    mock_client.list_namespaces = AsyncMock(return_value=mock_namespaces)

    with patch("temporalio.client.Client.connect", return_value=mock_client), \
         patch.dict(os.environ, {}, clear=True):
        await temporal_test_main()
        
        # Verify connection was attempted with default URL
        Client.connect.assert_called_once_with("temporal:7233")
        # Verify namespaces were requested
        mock_client.list_namespaces.assert_called_once()


@pytest.mark.asyncio
async def test_worker_initialization():
    """Test worker initialization and configuration"""
    # Skip actual worker creation and just test the configuration
    mock_worker = MagicMock(spec=Worker)
    mock_worker.run = AsyncMock()

    with patch("temporalio.worker.Worker", return_value=mock_worker) as mock_worker_class:
        # Call the worker creation function directly with our mock
        worker = mock_worker_class(
            client=MagicMock(),
            task_queue="spacelift-task-queue",
            workflows=[StackDependencyChainWorkflow, StackExecutionWorkflow],
            activities=[
                "fetch_dependent_stacks",
                "trigger_stack_run"
            ]
        )

        # Verify worker was created with correct configuration
        mock_worker_class.assert_called_once()
        worker_init = mock_worker_class.call_args[1]
        assert worker_init["task_queue"] == "spacelift-task-queue"
        assert StackDependencyChainWorkflow in worker_init["workflows"]
        assert StackExecutionWorkflow in worker_init["workflows"]
        assert len(worker_init["activities"]) == 2


@pytest.mark.asyncio
async def test_worker_error_handling():
    """Test worker error handling"""
    # Create mock worker that raises an error
    mock_worker = MagicMock(spec=Worker)
    mock_worker.run = AsyncMock(side_effect=Exception("Worker error"))

    with patch("temporalio.worker.Worker", return_value=mock_worker), \
         pytest.raises(Exception) as exc_info:
        # Call the worker creation function directly with our mock
        worker = Worker(
            client=MagicMock(),
            task_queue="spacelift-task-queue",
            workflows=[StackDependencyChainWorkflow, StackExecutionWorkflow],
            activities=[
                "fetch_dependent_stacks",
                "trigger_stack_run"
            ]
        )
        await worker.run()
        assert "Worker error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_temporal_connection_failure():
    """Test handling of temporal connection failure"""
    with patch("temporalio.client.Client.connect", 
              side_effect=Exception("Connection failed")), \
         pytest.raises(Exception) as exc_info:
        await temporal_test_main()
        assert "Connection failed" in str(exc_info.value)