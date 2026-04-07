import logging
from base64 import b64encode

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class JiraService:
    """Best-effort Jira integration. Methods log and swallow exceptions."""

    def __init__(self) -> None:
        self.base_url = settings.JIRA_BASE_URL.rstrip("/")
        self.email = settings.JIRA_EMAIL
        self.api_token = settings.JIRA_API_TOKEN

    @property
    def _headers(self) -> dict[str, str]:
        creds = b64encode(f"{self.email}:{self.api_token}".encode()).decode()
        return {
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @property
    def _configured(self) -> bool:
        return bool(self.email and self.api_token)

    async def get_issue(self, key: str) -> dict | None:
        if not self._configured:
            return None
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.base_url}/rest/api/3/issue/{key}",
                    headers=self._headers,
                    timeout=10.0,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception:
            logger.exception("Failed to get Jira issue %s", key)
            return None

    async def create_issue(
        self, summary: str, description: str, project_key: str = "PRED"
    ) -> dict | None:
        if not self._configured:
            return None
        try:
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"type": "text", "text": description}],
                            }
                        ],
                    },
                    "issuetype": {"name": "Task"},
                }
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/rest/api/3/issue",
                    headers=self._headers,
                    json=payload,
                    timeout=10.0,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception:
            logger.exception("Failed to create Jira issue")
            return None

    async def add_comment(self, key: str, comment: str) -> dict | None:
        if not self._configured:
            return None
        try:
            payload = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": comment}],
                        }
                    ],
                }
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/rest/api/3/issue/{key}/comment",
                    headers=self._headers,
                    json=payload,
                    timeout=10.0,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception:
            logger.exception("Failed to add comment to Jira issue %s", key)
            return None

    async def transition_issue(self, key: str, transition_id: str) -> bool:
        if not self._configured:
            return False
        try:
            payload = {"transition": {"id": transition_id}}
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/rest/api/3/issue/{key}/transitions",
                    headers=self._headers,
                    json=payload,
                    timeout=10.0,
                )
                resp.raise_for_status()
                return True
        except Exception:
            logger.exception("Failed to transition Jira issue %s", key)
            return False


jira_service = JiraService()
