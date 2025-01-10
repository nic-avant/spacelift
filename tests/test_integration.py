import asyncio

from httpx import AsyncClient


async def main():
    async with AsyncClient() as client:
        payload = {
            "stack_id": "demo-stack",
            "status": "RUNNING"
        }
        response = await client.post("http://localhost:8000/webhook", json=payload)
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    asyncio.run(main())
