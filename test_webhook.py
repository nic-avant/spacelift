import json
import requests
from rich.console import Console

def test_webhook():
    console = Console()
    
    # Read the webhook payload
    with open('webhook-payload.example', 'r') as f:
        payload = json.load(f)

    # Print a summary of the payload
    stack_id = payload['stack']['id']
    run_id = payload['run']['id']
    run_state = payload['state']
    console.print(f"Sending webhook for stack: [bold magenta]{stack_id}[/bold magenta]")
    console.print(f"Run ID: [bold blue]{run_id}[/bold blue] is in state: [bold green]{run_state}[/bold green]")
    
    # Send POST request to webhook endpoint
    response = requests.post(
        'http://127.0.0.1:8000/webhook',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    # Display the response in a nice format
    console.print(f"Status Code: {response.status_code}", style="bold cyan")
    console.print("Response:", response.json())

# Run the test
if __name__ == "__main__":
    test_webhook()