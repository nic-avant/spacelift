from temporalio import workflow
from temporalio.client import WorkflowClient
from temporalio.worker import Worker
from src.spacelift.spacelift import Spacelift

@workflow.defn
class StackExecutionWorkflow:
    @workflow.run
    async def run(self, stack_info: dict):
        # Workflow logic to manage stack execution
        print(f"Executing stack: {stack_info['stack_id']}")
        
        # Initialize Spacelift client
        spacelift_client = Spacelift(
            base_url="https://ORGNAME.app.spacelift.io/graphql",
            key_id="01HCJMP<API_KEY_ID ~26CHAR LONG>",
            key_secret="e355ae6fd5<API_KEY_SECRET ~64 CHAR LONG>"
        )
        
        # Trigger stack execution
        result = await spacelift_client.trigger_run(stack_info['stack_id'])
        print(f"Stack execution result: {result}")
        
        return "Stack execution completed"