"""
GitHub Actions REST API integration service.
Provides live workflow monitoring, job status synchronization, and secure token management.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import httpx


class GitHubService:
    """Interacts securely with GitHub REST API for Actions monitoring and workflow dispatch."""

    BASE_URL = "https://api.github.com"

    @classmethod
    def _headers(cls, token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Intelligent-API-Automation-Platform"
        }
        if token and token.strip():
            headers["Authorization"] = f"Bearer {token.strip()}"
        return headers

    @classmethod
    async def verify_connection(cls, owner: str, repo: str, token: Optional[str] = None) -> Tuple[bool, str]:
        """Verify repository existence and token access."""
        url = f"{cls.BASE_URL}/repos/{owner}/{repo}"
        async with httpx.AsyncClient(timeout=6.0) as client:
            try:
                resp = await client.get(url, headers=cls._headers(token))
                if resp.status_code == 200:
                    data = resp.json()
                    return True, f"Connected to {data.get('full_name')} ({data.get('default_branch', 'main')})"
                elif resp.status_code == 404:
                    return False, "Repository not found or private (provide token for private repos)."
                elif resp.status_code == 401:
                    return False, "GitHub Authentication failed. Invalid access token."
                else:
                    return False, f"GitHub API error HTTP {resp.status_code}: {resp.text[:150]}"
            except Exception as exc:
                return False, f"Network error connecting to GitHub: {str(exc)}"

    @classmethod
    async def get_workflow_runs(
        cls,
        owner: str,
        repo: str,
        token: Optional[str] = None,
        branch: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch real workflow runs from GitHub Actions."""
        url = f"{cls.BASE_URL}/repos/{owner}/{repo}/actions/runs"
        params = {"per_page": limit}
        if branch:
            params["branch"] = branch

        async with httpx.AsyncClient(timeout=8.0) as client:
            try:
                resp = await client.get(url, headers=cls._headers(token), params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    runs = []
                    for r in data.get("workflow_runs", []):
                        runs.append({
                            "id": r.get("id"),
                            "name": r.get("name"),
                            "event": r.get("event"),
                            "status": r.get("status"),  # queued, in_progress, completed
                            "conclusion": r.get("conclusion"),  # success, failure, neutral, cancelled
                            "branch": r.get("head_branch"),
                            "commit_sha": (r.get("head_sha") or "")[:7],
                            "commit_message": r.get("head_commit", {}).get("message", "").split("\n")[0] if r.get("head_commit") else "",
                            "created_at": r.get("created_at"),
                            "updated_at": r.get("updated_at"),
                            "html_url": r.get("html_url"),
                            "run_number": r.get("run_number")
                        })
                    return runs
                else:
                    return []
            except Exception:
                return []

    @classmethod
    async def trigger_workflow(
        cls,
        owner: str,
        repo: str,
        workflow_id: str,
        branch: str,
        token: str
    ) -> Tuple[bool, str]:
        """Dispatches a manual workflow run on GitHub Actions."""
        if not token:
            return False, "GitHub Personal Access Token is required to trigger workflows."

        url = f"{cls.BASE_URL}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
        payload = {"ref": branch}

        async with httpx.AsyncClient(timeout=8.0) as client:
            try:
                resp = await client.post(url, headers=cls._headers(token), json=payload)
                if resp.status_code in (204, 201):
                    return True, f"Workflow '{workflow_id}' triggered successfully on branch '{branch}'."
                elif resp.status_code == 404:
                    return False, f"Workflow '{workflow_id}' not found in repository."
                else:
                    return False, f"Failed to dispatch workflow: HTTP {resp.status_code} {resp.text[:150]}"
            except Exception as exc:
                return False, f"Error dispatching workflow: {str(exc)}"
