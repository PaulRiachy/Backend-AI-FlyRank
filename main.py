from fastapi import FastAPI, HTTPException, status

app = FastAPI()

tasks_list = [
    {"id": 1, "title": "Homework", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Brainrot", "done": True},
]


@app.get("/", summary = "Root endpoint", description = "API info")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }


@app.get("/health", summary = "Health Check", description = "Check Status")
async def health():
    return {"status" : "ok"}


@app.get("/tasks", summary = "Get Tasks", description = "Get all available tasks")
async def get_all_tasks():
    return tasks_list


@app.get("/tasks/{id}", summary = "Get task", description = "Get specific task by id")
async def get_task(id: int):
    for task in tasks_list:
        if task["id"] == id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {id} not found")


@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary = "Add task", description = "Add task to the list")
async def add_task(task: dict):
    title = task.get("title")
    if not title or not title.strip() or not isinstance(title, str):
        raise HTTPException(status_code=400, detail="Title is required.")

    new_id = max((t["id"] for t in tasks_list), default=0) + 1

    new_task = {"id": new_id, "title": title.strip(), "done": False}

    tasks_list.append(new_task)
    return new_task

@app.put("/tasks/{id}", summary = "Edit Task", description = "Edit a single available task in list")
async def edit_task(id: int, task_edited: dict):
    if not task_edited:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    if "title" in task_edited:
        title = task_edited["title"]
        if not isinstance(title, str) or not title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")

    if "done" in task_edited:
        if not isinstance(task_edited["done"], bool):
            raise HTTPException(status_code=400, detail="Field 'done' must be a boolean")
        
    for task in tasks_list:
        if task["id"] == id:
            if "title" in task_edited:
                task["title"] = task_edited["title"].strip()
            if "done" in task_edited:
                task["done"] = task_edited["done"]
            return task

    raise HTTPException(status_code=404, detail=f"Task {id} not found")


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary = "Delete task", description = "Remove task from list")
async def delete_task(id: int):
    for index, task in enumerate(tasks_list):
        if task["id"] == id:
            tasks_list.pop(index)
            return

    raise HTTPException(status_code=404, detail=f"Task {id} not found")