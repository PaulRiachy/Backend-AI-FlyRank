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
            done BOOLEAN NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    db.commit()
    db.close()

def seed_database():
    db = get_db()

    count = db.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    if count == 0:
        db.executemany(
            """
            INSERT INTO tasks
            (title, done, created_at, updated_at)
            VALUES (?, ?, datetime('now'), datetime('now'))
            """,
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


def task_from_row(row):
    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
        "created_at": row[3],
        "updated_at": row[4],
    }


@app.get(
    "/",
    summary="Root endpoint",
    description="API info"
)
async def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get(
    "/health",
    summary="Health Check",
    description="Check Status"
)
async def health():
    return {"status": "ok"}


@app.get(
    "/tasks",
    summary="Get Tasks",
    description="Get all tasks, optionally filtered by completion status or searched by title."
)
async def get_all_tasks(
    done: Optional[bool] = None,
    search: Optional[str] = None
):
    db = get_db()

    query = """
        SELECT id, title, done, created_at, updated_at
        FROM tasks
    """

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

    return [task_from_row(row) for row in rows]


@app.get(
    "/tasks/{id}",
    summary="Get task",
    description="Get specific task by id"
)
async def get_task(id: int):
    db = get_db()

    row = db.execute(
        """
        SELECT id, title, done, created_at, updated_at
        FROM tasks
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    db.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    return task_from_row(row)


@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    summary="Add task",
    description="Add task to the list"
)
async def add_task(task: dict):
    title = task.get("title")

    if not isinstance(title, str) or not title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required."
        )

    db = get_db()

    cursor = db.execute(
        """
        INSERT INTO tasks
        (title, done, created_at, updated_at)
        VALUES (?, ?, datetime('now'), datetime('now'))
        """,
        (title.strip(), False)
    )

    task_id = cursor.lastrowid

    db.commit()

    row = db.execute(
        """
        SELECT id, title, done, created_at, updated_at
        FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    ).fetchone()

    db.close()

    return task_from_row(row)


@app.put(
    "/tasks/{id}",
    summary="Edit Task",
    description="Edit a single available task in list"
)
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
        """
        SELECT id, title, done, created_at, updated_at
        FROM tasks
        WHERE id = ?
        """,
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
        """
        UPDATE tasks
        SET title = ?,
            done = ?,
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (title, done, id)
    )

    db.commit()

    updated_task = db.execute(
        """
        SELECT id, title, done, created_at, updated_at
        FROM tasks
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    db.close()

    return task_from_row(updated_task)


@app.delete(
    "/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Remove task from list"
)
async def delete_task(id: int):
    db = get_db()

    existing_task = db.execute(
        "SELECT id FROM tasks WHERE id = ?",
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


@app.get(
    "/stats",
    summary="Task Statistics",
    description="Get statistics about all tasks."
)
async def get_stats():
    db = get_db()

    total = db.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    done = db.execute(
        "SELECT COUNT(*) FROM tasks WHERE done = 1"
    ).fetchone()[0]

    db.close()

    return {
        "total": total,
        "done": done,
        "open": total - done,
    }


@app.post(
    "/reset",
    summary="Reset Tasks",
    description="Restore the original sample tasks."
)
async def reset_tasks():
    db = get_db()

    db.execute("DELETE FROM tasks")

    db.executemany(
        """
        INSERT INTO tasks
        (title, done, created_at, updated_at)
        VALUES (?, ?, datetime('now'), datetime('now'))
        """,
        [
            ("Homework", False),
            ("Read a book", True),
            ("Brainrot", True),
        ],
    )

    db.commit()

    rows = db.execute(
        """
        SELECT id, title, done, created_at, updated_at
        FROM tasks
        """
    ).fetchall()

    db.close()

    return {
        "message": "Tasks have been reset.",
        "tasks": [task_from_row(row) for row in rows],
    }