import requests
from typing import Any, Dict, Optional


class ProcurementComplianceEnv:
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url.rstrip("/")

    def reset(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {}
        if task_id:
            payload["task_id"] = task_id
        response = requests.post(f"{self.base_url}/reset", json=payload)
        response.raise_for_status()
        return response.json()

    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/step", json=action)
        response.raise_for_status()
        return response.json()

    def state(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/state")
        response.raise_for_status()
        return response.json()