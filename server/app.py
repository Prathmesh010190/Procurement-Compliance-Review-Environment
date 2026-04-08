from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from models import ProcurementAction
from server.environment import ProcurementComplianceEnvironment

app = FastAPI(title="Procurement Compliance Review Environment")

env = ProcurementComplianceEnvironment()


class ResetRequest(BaseModel):
    seed: Optional[int] = None
    episode_id: Optional[str] = None
    task_id: Optional[str] = None


@app.get("/")
def root():
    return {
        "name": "Procurement Compliance Review Environment",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    """Return all available task IDs — used by validators to discover tasks."""
    return {
        "task_ids": env.get_task_ids(),
        "total": len(env.get_task_ids()),
    }


@app.post("/reset")
def reset(request: ResetRequest = None):
    try:
        obs = env.reset(
            seed=request.seed if request else None,
            episode_id=request.episode_id if request else None,
            task_id=request.task_id if request else None,
        )
        return obs.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
def step(action: ProcurementAction):
    try:
        obs = env.step(action)
        return obs.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def state():
    try:
        return env.state().model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def main():
    import uvicorn
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=7860,
        reload=False,
    )


if __name__ == "__main__":
    main()