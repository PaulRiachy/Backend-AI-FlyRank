from fastapi import FastAPI, HTTPException, status, Depends
from typing import Optional
from pydantic import BaseModel

from database import get_db, initialize_database, seed_database
from supabase_client import supabase
from auth import get_current_user


app = FastAPI()

initialize_database()
seed_database()

class AuthRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

def task_from_row(row):
    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
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
    with get_db() as db:
        with db.cursor() as cursor:

            query = """
                SELECT id, title, done
                FROM tasks
            """

            params = []
            conditions = []

            if done is not None:
                conditions.append("done = %s")
                params.append(done)

            if search:
                conditions.append("title ILIKE %s")
                params.append(f"%{search}%")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, params)

            rows = cursor.fetchall()

    return [task_from_row(row) for row in rows]


@app.get(
    "/tasks/{id}",
    summary="Get task",
    description="Get specific task by id"
)
async def get_task(id: int):
    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                """
                SELECT id, title, done
                FROM tasks
                WHERE id = %s
                """,
                (id,)
            )

            row = cursor.fetchone()

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

    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                RETURNING id, title, done
                """,
                (title.strip(), False)
            )

            row = cursor.fetchone()

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

    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                """
                SELECT id, title, done
                FROM tasks
                WHERE id = %s
                """,
                (id,)
            )

            existing_task = cursor.fetchone()

            if existing_task is None:
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

            cursor.execute(
                """
                UPDATE tasks
                SET title = %s,
                    done = %s
                WHERE id = %s
                RETURNING id, title, done
                """,
                (title, done, id)
            )

            updated_task = cursor.fetchone()

    return task_from_row(updated_task)


@app.delete(
    "/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Remove task from list"
)
async def delete_task(id: int):

    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute(
                "SELECT id FROM tasks WHERE id = %s",
                (id,)
            )

            existing_task = cursor.fetchone()

            if existing_task is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Task {id} not found"
                )

            cursor.execute(
                "DELETE FROM tasks WHERE id = %s",
                (id,)
            )

    return


@app.get(
    "/stats",
    summary="Task Statistics",
    description="Get statistics about all tasks."
)
async def get_stats():

    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute("SELECT COUNT(*) FROM tasks")
            total = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM tasks WHERE done = TRUE"
            )
            done = cursor.fetchone()[0]

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

    with get_db() as db:
        with db.cursor() as cursor:

            cursor.execute("DELETE FROM tasks")

            cursor.executemany(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                """,
                [
                    ("Homework", False),
                    ("Read a book", True),
                    ("Brainrot", True),
                ],
            )

            cursor.execute(
                """
                SELECT id, title, done
                FROM tasks
                """
            )

            rows = cursor.fetchall()

    return {
        "message": "Tasks have been reset.",
        "tasks": [task_from_row(row) for row in rows],
    }

#Supabase

@app.post("/auth/signup", status_code=201)
def signup(data: AuthRequest):
    if not data.email or not data.password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required",
        )

    response = supabase.auth.sign_up({
        "email": data.email,
        "password": data.password,
    })

    return response.user


@app.post("/auth/login")
def login(data: AuthRequest):
    if not data.email or not data.password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required",
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials",
        )

    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
    }


@app.get("/public/info")
async def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


@app.get("/protected/profile")
def profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }


@app.get("/protected/dashboard")
def dashboard(user=Depends(get_current_user)):
    return {
        "message": "Welcome to your dashboard",
        "user_id": user.id,
    }


@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(user=Depends(get_current_user)):
    supabase.auth.sign_out()

    return