from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Task Tracker API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def main_html_template():
    return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>VectorShift</title>
        </head>
        <body>
            <h1>🚀 FastAPI is Running,..</h1>
            <p style ="color:blue; font-weight:bold">Status: <span style="color: green; font-weight: bold;">OK</span></p>
        </body>
        </html>
        """

@app.get("/", response_class=HTMLResponse)
def read_root():
    return main_html_template()

class CreateTask(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None

class UpdateTask(BaseModel):
    status: str

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


tasks: List[Task] = []
task_id_counter = 1

VALID_STATUSES = {"pending", "in_progress", "completed"}



@app.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: CreateTask):
    global task_id_counter
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    now = datetime.utcnow()
    task = Task(
        id=task_id_counter,
        title=payload.title,
        description=payload.description,
        status="pending",
        created_at=now,
        updated_at=now,
    )
    tasks.append(task)
    task_id_counter += 1
    return task


@app.get("/tasks", response_model=List[Task])
def list_tasks(status: Optional[str] = Query(None)):
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status filter")

    if status:
        return [task for task in tasks if task.status == status]

    return tasks


@app.put("/tasks/{task_id}", response_model=Task)
def update_task_status(task_id: int, payload: UpdateTask):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status value")

    for task in tasks:
        if task.id == task_id:
            task.status = payload.status
            task.updated_at = datetime.utcnow()
            return task

    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    global tasks

    for index, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(index)
            return

    raise HTTPException(status_code=404, detail="Task not found")

