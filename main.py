from fastapi import FastAPI, HTTPException, status

app = FastAPI()

tasks_list = [
    {"id": 1, "title": "Homework", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Brainrot", "done": True},
]


@app.get("/")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }


@app.get("/health")
async def health():
    return {"status" : "ok"}


@app.get("/tasks")
async def get_all_tasks():
    return tasks_list


@app.get("/tasks/{id}")
async def get_task(id: int):
    for task in tasks_list:
        if task["id"] == id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {id} not found")


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def add_task(task: dict):
    title = task.get("title")
    if not title or not title.strip():
        raise HTTPException(
            status_code=400, detail="Title is required."
        )

    new_id = max((t["id"] for t in tasks_list), default=0) + 1

    new_task = {"id": new_id, "title": title.strip(), "done": False}

    tasks_list.append(new_task)
    return new_task
