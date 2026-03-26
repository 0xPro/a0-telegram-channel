import httpx
import asyncio
from dotenv import load_dotenv
import os

load_dotenv("/a0/usr/secrets.env")

AGENT_ZERO_URL = os.getenv("AGENT_ZERO_URL", "http://localhost:8000")
API_KEY = os.getenv("AGENT_ZERO_API_KEY")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", 1.5))

class ApiClient:
    def __init__(self):
        self.headers = {"Content-Type": "application/json", "X-API-KEY": API_KEY}

    async def api_message(self, message: str, context_id: str = None, attachments=None, project_name: str = None):
        payload = {"message": message, "lifetime_hours": 24}
        if context_id:
            payload["context_id"] = context_id
        if attachments:
            payload["attachments"] = attachments
        if project_name:
            payload["project_name"] = project_name  # Correct key per source code

        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    resp = await client.post(f"{AGENT_ZERO_URL}/api_message", json=payload, headers=self.headers, timeout=180)
                    if resp.is_success:
                        data = resp.json()
                        return data.get("response"), data.get("context_id")
                    await asyncio.sleep(2 ** attempt)
                except Exception:
                    await asyncio.sleep(2 ** attempt)
        raise Exception("Agent Zero unreachable after retries")

    async def api_log_get(self, context_id: str, length: int = 50):
        payload = {"context_id": context_id, "length": length}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{AGENT_ZERO_URL}/api_log_get", json=payload, headers=self.headers, timeout=30)
            if resp.is_success:
                return resp.json()
        return None

    async def api_reset_chat(self, context_id: str):
        payload = {"context_id": context_id}
        async with httpx.AsyncClient() as client:
            await client.post(f"{AGENT_ZERO_URL}/api_reset_chat", json=payload, headers=self.headers)

    async def api_terminate_chat(self, context_id: str):
        payload = {"context_id": context_id}
        async with httpx.AsyncClient() as client:
            await client.post(f"{AGENT_ZERO_URL}/api_terminate_chat", json=payload, headers=self.headers)