from fastapi import FastAPI, HTTPException, status
from typing import Optional
import sqlite3


app = FastAPI()

DB_NAME = "tasks.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def initialize_database():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL
        )
    """)

    db.commit()
    db.close()

def seed_database():
    db = get_db()

    count = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    if count == 0:
        db.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Homework", False),
                ("Read a book", True),
                ("Brainrot", True),
            ],
        )

        db.commit()

    db.close()

initialize_database()
seed_database()

original_tasks = [
    {"id": 1, "title": "Homework", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Brainrot", "done": True},
]

tasks_list = [task.copy() for task in original_tasks]


@app.get("/", summary = "Root endpoint", description = "API info")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }


@app.get("/health", summary = "Health Check", description = "Check Status")
async def health():
    return {"status" : "ok"}


@app.get("/tasks", summary = "Get Tasks", description = "Get all tasks, optionally filtered by completion status or searched by title.")
async def get_all_tasks(
    done: Optional[bool] = None,
    search: Optional[str] = None
):
    db = get_db()

    query = "SELECT * FROM tasks"
    params = []
    conditions = []

    if done is not None:
        conditions.append("done = ?")
        params.append(done)

    if search:
        conditions.append("title LIKE ?")
        params.append(f"%{search}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    rows = db.execute(query, params).fetchall()
    db.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "done": bool(row[2]),
        }
        for row in rows
    ]


@app.get("/tasks/{id}", summary = "Get task", description = "Get specific task by id")
async def get_task(id: int):
    db = get_db()

    row = db.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (id,)
    ).fetchone()

    db.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
    }


@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary = "Add task", description = "Add task to the list")
async def add_task(task: dict):
    title = task.get("title")

    if not isinstance(title, str) or not title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required."
        )

    db = get_db()

    cursor = db.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (title.strip(), False)
    )

    task_id = cursor.lastrowid

    db.commit()

    row = db.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    db.close()

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
    }


@app.put("/tasks/{id}", summary = "Edit Task", description = "Edit a single available task in list")
async def edit_task(id: int, task_edited: dict):
    if not task_edited:
        raise HTTPException(
            status_code=400,
            detail="Request body cannot be empty"
        )

    if "title" in task_edited:
        title = task_edited["title"]

        if not isinstance(title, str) or not title.strip():
            raise HTTPException(
                status_code=400,
                detail="Title cannot be empty"
            )

    if "done" in task_edited:
        if not isinstance(task_edited["done"], bool):
            raise HTTPException(
                status_code=400,
                detail="Field 'done' must be a boolean"
            )

    db = get_db()

    existing_task = db.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (id,)
    ).fetchone()

    if existing_task is None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    title = (
        task_edited["title"].strip()
        if "title" in task_edited
        else existing_task[1]
    )

    done = (
        task_edited["done"]
        if "done" in task_edited
        else bool(existing_task[2])
    )

    db.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (title, done, id)
    )

    db.commit()

    updated_task = db.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (id,)
    ).fetchone()

    db.close()

    return {
        "id": updated_task[0],
        "title": updated_task[1],
        "done": bool(updated_task[2]),
    }


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary = "Delete task", description = "Remove task from list")
async def delete_task(id: int):
    db = get_db()

    existing_task = db.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (id,)
    ).fetchone()

    if existing_task is None:
        db.close()
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    db.execute(
        "DELETE FROM tasks WHERE id = ?",
        (id,)
    )

    db.commit()
    db.close()

    return


@app.get("/stats", summary = "Task Statistics", description = "Get statistics about all tasks.")
async def get_stats():
    total = len(tasks_list)
    done = sum(task["done"] for task in tasks_list)
    return {
        "total": total,
        "done": done,
        "open": total - done,
    }


@app.post(
    "/reset",summary = "Reset Tasks", description = "Restore the original sample tasks.")
async def reset_tasks():
    global tasks_list

    tasks_list = [task.copy() for task in original_tasks]

    return {
        "message": "Tasks have been reset.",
        "tasks": tasks_list,
    }