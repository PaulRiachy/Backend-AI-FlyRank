# Task Management API

A lightweight RESTful API built with **Python**, **FastAPI**, and **SQLite** for managing tasks. This project demonstrates REST API fundamentals, full CRUD operations, input validation, parameterized SQL queries, database persistence, SQL filtering, task statistics, timestamps, and automatically generated API documentation with Swagger UI.

The project originally used in-memory storage and was migrated to SQLite as part of the FlyRank Internship Backend Track Week 3 Assignment A2.

---

## Features

* Full CRUD operations (Create, Read, Update, Delete)
* SQLite database storage
* Persistent task data that survives server restarts
* Automatic database and table creation
* Automatic seeding of three example tasks on the first run
* Parameterized SQL queries for database safety
* Task filtering using query parameters (`?done=true` / `?done=false`)
* Task search by title (`?search=keyword`)
* Task statistics endpoint
* Reset endpoint to restore the default task list
* Task creation and update timestamps
* Automatic `created_at` timestamp for every task
* Automatic `updated_at` timestamp when a task is modified
* Strict input validation

  * Rejects empty request bodies
  * Rejects invalid data types
  * Rejects whitespace-only task titles
* Proper HTTP status code handling
* Automatic interactive API documentation via Swagger UI
* SQL database exploration using DB Browser for SQLite

---

## Tech Stack

* **Python 3.9+**
* **FastAPI**
* **Uvicorn**
* **SQLite**
* **Python `sqlite3`**

SQLite is provided through Python's standard library, so no additional database server or SQLite package is required.

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/PaulRiachy/Backend-AI-FlyRank.git
cd Backend-AI-FlyRank
```

## 2. Create a Virtual Environment

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```bash
pip install fastapi uvicorn
```

## 4. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

The SQLite database is created automatically when the application starts.

---

# SQLite Database

## Why SQLite?

SQLite was chosen because it is lightweight and requires almost no setup.

The database:

* Is stored in a single file
* Does not require a separate database server
* Requires no separate SQLite installation
* Is included with Python through the `sqlite3` module
* Provides persistent storage
* Makes it easy to inspect the database using DB Browser for SQLite

The database file is:

```text
tasks.db
```

It is created automatically by the application if it does not already exist.

The `tasks` table is also created automatically if it does not exist.

---

## Database Schema

The application uses a single `tasks` table.

| Column       | Type    | Description                                       |
| ------------ | ------- | ------------------------------------------------- |
| `id`         | INTEGER | Primary key, automatically assigned by SQLite     |
| `title`      | TEXT    | Task title                                        |
| `done`       | BOOLEAN | Completion status, stored by SQLite as `0` or `1` |
| `created_at` | TEXT    | Date and time when the task was created           |
| `updated_at` | TEXT    | Date and time when the task was last updated      |

The database is initialized automatically when the application starts.

Three example tasks are inserted only when the table is empty, preventing duplicate seed data when the server is restarted.

---

## Database Persistence

Unlike the original in-memory implementation, tasks are now stored in `tasks.db`.

This means data survives application restarts.

For example:

1. Create a new task.
2. Stop the FastAPI server.
3. Start the server again.
4. Run `GET /tasks`.
5. The previously created task is still present.

The database file acts as the persistent source of truth for the API.

---

# Timestamps

Each task contains two timestamps:

* `created_at` — records when the task was created.
* `updated_at` — records when the task was last modified.

When a task is created, both timestamps are set automatically.

When a task is updated using `PUT /tasks/{id}`, the `created_at` value remains unchanged while `updated_at` is refreshed.

Example:

```json
{
    "id": 4,
    "title": "Complete Assignment",
    "done": false,
    "created_at": "2026-08-08 13:20:15",
    "updated_at": "2026-08-08 13:20:15"
}
```

After updating the task, the `created_at` timestamp remains the same while `updated_at` changes.

Adding timestamps required changing the shape of the database table and updating the SQL used for inserts, updates, and reads. It demonstrated how adding even a small piece of information requires the database schema and application code to stay synchronized, which is why structured database migrations become important as applications grow.

---

# API Documentation

FastAPI automatically generates interactive API documentation.

| Documentation | URL                         |
| ------------- | --------------------------- |
| Swagger UI    | http://localhost:8000/docs  |
| ReDoc         | http://localhost:8000/redoc |

Swagger UI can be used to test all API endpoints directly from the browser.

---

# API Endpoints

|   Method   | Endpoint      | Description                          |   Success Status   |
| :--------: | ------------- | ------------------------------------ | :----------------: |
|   **GET**  | `/`           | API information and available routes |     **200 OK**     |
|   **GET**  | `/health`     | Health check                         |     **200 OK**     |
|   **GET**  | `/tasks`      | Retrieve all tasks                   |     **200 OK**     |
|   **GET**  | `/tasks/{id}` | Retrieve a task by ID                |     **200 OK**     |
|  **POST**  | `/tasks`      | Create a new task                    |   **201 Created**  |
|   **PUT**  | `/tasks/{id}` | Update an existing task              |     **200 OK**     |
| **DELETE** | `/tasks/{id}` | Delete a task                        | **204 No Content** |
|   **GET**  | `/stats`      | Retrieve task statistics             |     **200 OK**     |
|  **POST**  | `/reset`      | Restore the default sample tasks     |     **200 OK**     |

The five core CRUD endpoints maintain the same behavior as Assignment 1. The primary change is that task data is now stored in SQLite instead of Python memory.

---

# Query Parameters

The `GET /tasks` endpoint supports optional query parameters.

| Parameter | Example                        | Description              |
| --------- | ------------------------------ | ------------------------ |
| `done`    | `/tasks?done=true`             | Returns completed tasks  |
| `done`    | `/tasks?done=false`            | Returns incomplete tasks |
| `search`  | `/tasks?search=book`           | Searches task titles     |
| Combined  | `/tasks?done=true&search=book` | Applies both filters     |

### Filter by Status

```text
GET /tasks?done=true
```

Returns only completed tasks.

### Search by Title

```text
GET /tasks?search=book
```

Returns tasks whose titles contain the search term.

The search functionality uses SQL's `LIKE` operator and a parameterized query:

```sql
SELECT * FROM tasks WHERE title LIKE ?
```

The search value is supplied separately as a parameter rather than being directly inserted into the SQL statement.

---

# Statistics

The API provides a statistics endpoint:

```text
GET /stats
```

The statistics are calculated directly using SQL queries.

Example response:

```json
{
    "total": 5,
    "done": 2,
    "open": 3
}
```

The endpoint uses SQL `COUNT(*)` rather than loading every task into Python and counting them manually.

---

# Reset Tasks

The API provides a reset endpoint:

```text
POST /reset
```

This deletes the current tasks and recreates the three default sample tasks:

```text
Homework
Read a book
Brainrot
```

The reset operation uses parameterized SQL for inserting the replacement tasks.

The reset endpoint is useful for restoring a known starting state while testing the API.

---

# Error Responses

The API returns appropriate HTTP status codes for invalid requests.

| Status Code         | Description                               |
| ------------------- | ----------------------------------------- |
| **400 Bad Request** | Invalid request body or validation failed |
| **404 Not Found**   | Requested task does not exist             |

Example:

```json
{
    "detail": "Task 999 not found"
}
```

---

# Example Requests

## Get All Tasks

```powershell
(Invoke-WebRequest -Method GET -Uri "http://localhost:8000/tasks").Content
```

## Get a Task

```powershell
(Invoke-WebRequest -Method GET -Uri "http://localhost:8000/tasks/1").Content
```

## Create a Task

```powershell
(Invoke-WebRequest `
-Method POST `
-Uri "http://localhost:8000/tasks" `
-Headers @{"Content-Type"="application/json"} `
-Body '{"title":"Complete Stage 5"}').Content
```

## Update a Task

```powershell
(Invoke-WebRequest `
-Method PUT `
-Uri "http://localhost:8000/tasks/1" `
-Headers @{"Content-Type"="application/json"} `
-Body '{"title":"Updated Title","done":true}').Content
```

## Delete a Task

```powershell
(Invoke-WebRequest `
-Method DELETE `
-Uri "http://localhost:8000/tasks/1").StatusCode
```

## Filter Completed Tasks

```powershell
(Invoke-WebRequest -Method GET -Uri "http://localhost:8000/tasks?done=true").Content
```

## Search Tasks

```powershell
(Invoke-WebRequest -Method GET -Uri "http://localhost:8000/tasks?search=book").Content
```

## Task Statistics

```powershell
(Invoke-WebRequest -Method GET -Uri "http://localhost:8000/stats").Content
```

## Reset Tasks

```powershell
(Invoke-WebRequest -Method POST -Uri "http://localhost:8000/reset").Content
```

---

# SQL Queries

The database can be opened directly using **DB Browser for SQLite**.

Some example queries used during Stage 4 were:

## Get All Tasks

```sql
SELECT * FROM tasks;
```

## Get Completed Tasks

```sql
SELECT * FROM tasks WHERE done = 1;
```

## Count All Tasks

```sql
SELECT COUNT(*) FROM tasks;
```

## Mark All Tasks as Completed

```sql
UPDATE tasks SET done = 1;
```

## Delete Completed Tasks

```sql
DELETE FROM tasks WHERE done = 1;
```

### Stage 4 Example

One of the queries used during Stage 4 was:

```sql
SELECT * FROM tasks WHERE done = 1;
```

This query returns only the tasks whose `done` value is `1`, meaning they are completed.

Changes made directly in DB Browser are immediately reflected when querying the API because both the API and DB Browser use the same `tasks.db` file.

---

# Parameterized Queries

The application uses parameterized SQL queries instead of directly inserting user input into SQL strings.

For example:

```sql
SELECT * FROM tasks WHERE id = ?
```

The task ID is supplied separately as a parameter.

This approach prevents user input from being directly concatenated into SQL statements and helps protect the database from SQL injection.

Parameterized queries are used for database operations including:

* Selecting tasks by ID
* Searching tasks
* Inserting tasks
* Updating tasks
* Deleting tasks

---

# Database Seeding

When the application starts, it:

1. Opens `tasks.db`.
2. Creates the `tasks` table if it does not already exist.
3. Checks whether the table contains any rows.
4. Inserts the three sample tasks only if the table is empty.

The seed data is:

```text
Homework
Read a book
Brainrot
```

Each seeded task also receives `created_at` and `updated_at` timestamps.

Restarting the application does not create duplicate copies of these tasks.

---

# Swagger UI

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```

Add a screenshot of the Swagger UI below after running the application.

```text
images/
└── swagger-ui.png
```

Then include:

```markdown
![Swagger UI](images/swagger-ui.png)
```

---

# DB Browser for SQLite

The `tasks.db` database can be opened using DB Browser for SQLite.

The database should show the `tasks` table, its columns, and its stored rows.

Add a screenshot of the database below:

```text
images/
└── database.png
```

Then include:

```markdown
![SQLite Database](images/database.png)
```

The database screenshot demonstrates that the API data is actually persisted in SQLite.

---

# Project Structure

```text
.
├── main.py
├── README.md
├── .gitignore
└── images/
    ├── swagger-ui.png
    └── database.png
```

`tasks.db` is generated automatically and is excluded from Git so that each clone can create its own fresh database.

SQLite journal and temporary files are also excluded from Git.

---

# Git Ignore

The following SQLite files should not be committed:

```gitignore
# SQLite database files
tasks.db
tasks.db-journal
tasks.db-wal
tasks.db-shm
```

The database itself is intentionally not required in the repository because the application creates it automatically.

A fresh clone can therefore start with:

```bash
uvicorn main:app --reload
```

and the database, table, and initial seed data will be created automatically.

---

# Validation Rules

The API validates incoming requests before processing them.

* Task title is required.
* Task title cannot be empty.
* Task title cannot contain only whitespace.
* Invalid request formats are rejected.
* Empty update request bodies are rejected.
* The `done` field must be a boolean when provided.
* Requests for non-existent tasks return `404 Not Found`.

---

# Learning Objectives

This project demonstrates:

* RESTful API design
* FastAPI fundamentals
* CRUD endpoint implementation
* HTTP methods and status codes
* Input validation
* Query parameters
* SQL queries
* SQLite database storage
* Database persistence
* Parameterized queries
* Database seeding
* SQL filtering using `WHERE`
* Text searching using `LIKE`
* SQL aggregation using `COUNT(*)`
* Database timestamps
* SQL operations using DB Browser for SQLite
* Interactive API documentation with Swagger UI
* API testing using PowerShell

---

# Assignment Progress

This project was completed as part of the FlyRank Internship Backend Track Week 3 Assignment A2.

## Stage 0 — Create SQLite Database

* Created `tasks.db`
* Created the `tasks` table automatically
* Added `id`, `title`, and `done` columns
* Added three seed tasks
* Ensured seed data is only inserted when the table is empty

## Stage 1 — Database Read Endpoints

* Updated `GET /tasks` to read from SQLite
* Updated `GET /tasks/{id}` to query SQLite
* Used parameterized queries
* Preserved `404 Not Found` behavior

## Stage 2 — Insert Into Database

* Updated `POST /tasks`
* Tasks are inserted into SQLite
* SQLite generates task IDs
* Created tasks persist after server restarts

## Stage 3 — Update and Delete

* Updated `PUT /tasks/{id}` to use SQL `UPDATE`
* Updated `DELETE /tasks/{id}` to use SQL `DELETE`
* Preserved the original API status codes and validation behavior

## Stage 4 — Explore SQLite

* Opened `tasks.db` using DB Browser for SQLite
* Executed SQL queries manually
* Verified that database changes are reflected through the API

## Stage 5 — Publish Database Project

* Updated project documentation
* Added SQLite setup and persistence documentation
* Added database screenshots
* Added SQLite files to `.gitignore`
* Prepared the project to run from a clean clone

## Additional Extras

The project was extended beyond the required CRUD implementation with:

* SQL-based task searching using `LIKE`
* SQL-based task filtering using `WHERE`
* Task statistics using `COUNT(*)`
* Task reset functionality
* `created_at` and `updated_at` timestamps

---

# Persistence Demonstration

The migration from in-memory storage to SQLite can be demonstrated using the following process:

1. Start the application.
2. Create a new task using `POST /tasks`.
3. Confirm the task appears using `GET /tasks`.
4. Stop the server.
5. Start the server again.
6. Run `GET /tasks`.
7. Confirm the created task is still present.
8. Open `tasks.db` using DB Browser for SQLite.
9. Confirm the same task exists in the database.

This demonstrates that the API is using persistent database storage rather than an in-memory Python list.

---

# License

This project is intended for educational purposes and may be freely modified or extended.
