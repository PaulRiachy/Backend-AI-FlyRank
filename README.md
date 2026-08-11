# Task Management API

A lightweight RESTful API built with **Python**, **FastAPI**, and **PostgreSQL**, containerized with **Docker**. The project demonstrates REST API fundamentals, full CRUD operations, input validation, parameterized SQL queries, persistent database storage, SQL filtering, task statistics, timestamps, environment-based configuration, and containerized application deployment.

The project originally used in-memory storage, was migrated to SQLite, and was subsequently migrated to **PostgreSQL running in Docker** as part of the FlyRank Internship Backend Track.

---

## Features

* Full CRUD operations

  * Create tasks
  * Read tasks
  * Update tasks
  * Delete tasks
* PostgreSQL database storage
* PostgreSQL running in a dedicated Docker container
* FastAPI running in a dedicated Docker container
* Persistent database storage using a Docker volume
* Automatic database and table creation
* Automatic seeding of three example tasks on the first database initialization
* Parameterized SQL queries
* Task filtering using query parameters (`?done=true` / `?done=false`)
* Task search by title (`?search=keyword`)
* Task statistics endpoint
* Reset endpoint to restore the default task list
* `created_at` and `updated_at` timestamps
* Input validation
* Proper HTTP status code handling
* Automatic interactive API documentation through Swagger UI
* Environment-based configuration
* Secrets excluded from Git

---

# Tech Stack

* **Python 3.12**
* **FastAPI**
* **Uvicorn**
* **PostgreSQL**
* **psycopg**
* **python-dotenv**
* **Docker**
* **Docker Compose**

---

# Architecture

The application uses two Docker services:

```text
                    ┌──────────────────────┐
                    │       Client         │
                    │ Browser / PowerShell │
                    └──────────┬───────────┘
                               │
                               │ HTTP :8000
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI API       │
                    │      Container       │
                    │                      │
                    │  Uvicorn + FastAPI   │
                    └──────────┬───────────┘
                               │
                               │ PostgreSQL
                               │ :5432
                               ▼
                    ┌──────────────────────┐
                    │    PostgreSQL        │
                    │      Container       │
                    │                      │
                    │      tasks DB        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Docker Volume      │
                    │   Persistent Data    │
                    └──────────────────────┘
```

The API does **not** connect to PostgreSQL through `localhost` when running inside Docker.

Instead, Docker Compose provides an internal network and the API connects to PostgreSQL using the database service name.

For example:

```text
postgresql://postgres:password@db:5432/tasks
```

Here, `db` is the PostgreSQL Docker Compose service name.

---

# Project Structure

```text
.
├── main.py
├── database.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example
└── README.md
```

Environment files containing secrets are intentionally excluded from Git.

---

# Environment Variables

The application uses environment variables for database configuration.

A local `.env` file contains the actual configuration.

Example:

```env
DATABASE_URL=postgresql://postgres:dev@db:5432/tasks
```

The actual `.env` file should **never be committed to Git**.

A `.env.example` file can be committed instead:

```env
DATABASE_URL=postgresql://postgres:your_password@db:5432/tasks
```

This allows other developers to understand which environment variables are required without exposing actual credentials.

---

# Docker

The project uses Docker to separate the API and database into independent services.

## API Container

The API container contains:

* Python
* FastAPI
* Uvicorn
* psycopg
* Application source code

The API exposes port `8000`.

## PostgreSQL Container

The PostgreSQL container contains:

* PostgreSQL
* The `tasks` database
* The database tables and data

PostgreSQL uses port `5432` internally.

The database data is stored using a Docker volume so that database contents survive container recreation.

---

# Running the Application

## 1. Start Docker

Make sure Docker Desktop is running.

## 2. Build and Start the Services

From the project root:

```powershell
docker compose up --build
```

This starts:

```text
api-1
db-1
```

The PostgreSQL container initializes the database and the FastAPI container connects to it.

The API becomes available at:

```text
http://localhost:8000
```

---

## 3. Run in Detached Mode

To start the application in the background:

```powershell
docker compose up --build -d
```

Check the running containers:

```powershell
docker compose ps
```

You should see both services running.

---

## 4. View Logs

To view both API and database logs:

```powershell
docker compose logs
```

To follow the logs:

```powershell
docker compose logs -f
```

To view only the API:

```powershell
docker compose logs api
```

To view only PostgreSQL:

```powershell
docker compose logs db
```

---

## 5. Stop the Application

```powershell
docker compose down
```

Stopping the containers does not remove the database volume, so PostgreSQL data remains persistent.

---

# PostgreSQL Database

The application uses PostgreSQL instead of SQLite.

The database is named:

```text
tasks
```

The PostgreSQL server runs inside the `db` Docker container.

The API connects to it through Docker's internal network.

The connection is configured through:

```text
DATABASE_URL
```

Example:

```text
postgresql://postgres:dev@db:5432/tasks
```

The important distinction is:

```text
Inside Docker:
db:5432
```

rather than:

```text
localhost:5432
```

because `localhost` inside the API container refers to the API container itself, not the PostgreSQL container.

---

# Database Persistence

PostgreSQL data is stored using a Docker volume.

This means:

1. The PostgreSQL container can be stopped.
2. The PostgreSQL container can be recreated.
3. The database data remains available.

The volume is managed by Docker rather than being stored inside the API container.

This separates application lifecycle from database storage.

---

# Database Schema

The application uses a `tasks` table.

| Column  | Type    | Description                         |
| ------- | ------- | ----------------------------------- |
| `id`    | SERIAL  | Automatically generated primary key |
| `title` | TEXT    | Task title                          |
| `done`  | BOOLEAN | Completion status                   |

The table is created automatically when the application starts.

The SQL used by the application is conceptually:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL
);
```

---

# Database Initialization

When the API starts, it initializes the database.

The application:

1. Connects to PostgreSQL.
2. Creates the `tasks` table if it does not already exist.
3. Checks whether the table contains any tasks.
4. Inserts the default sample tasks if the table is empty.

The initial tasks are:

```text
Homework
Read a book
Brainrot
```

This prevents the application from requiring manual database setup before it can run.

---

# Database Configuration

Database access is handled in `database.py`.

The application loads environment variables using `python-dotenv`.

The database connection is created using `psycopg`.

Conceptually:

```python
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    return psycopg.connect(DATABASE_URL)
```

The application does not hard-code database credentials in the source code.

---

# API Documentation

FastAPI automatically generates interactive API documentation.

| Documentation | URL                         |
| ------------- | --------------------------- |
| Swagger UI    | http://localhost:8000/docs  |
| ReDoc         | http://localhost:8000/redoc |

Swagger UI can be used to test the API directly from the browser.

---

# API Endpoints

| Method     | Endpoint      | Description               | Success Status     |
| ---------- | ------------- | ------------------------- | ------------------ |
| **GET**    | `/`           | API information           | **200 OK**         |
| **GET**    | `/health`     | Health check              | **200 OK**         |
| **GET**    | `/tasks`      | Retrieve all tasks        | **200 OK**         |
| **GET**    | `/tasks/{id}` | Retrieve a task by ID     | **200 OK**         |
| **POST**   | `/tasks`      | Create a new task         | **201 Created**    |
| **PUT**    | `/tasks/{id}` | Update an existing task   | **200 OK**         |
| **DELETE** | `/tasks/{id}` | Delete a task             | **204 No Content** |
| **GET**    | `/stats`      | Retrieve task statistics  | **200 OK**         |
| **POST**   | `/reset`      | Restore the default tasks | **200 OK**         |

---

# Query Parameters

The `GET /tasks` endpoint supports optional query parameters.

| Parameter | Example                        | Description              |
| --------- | ------------------------------ | ------------------------ |
| `done`    | `/tasks?done=true`             | Returns completed tasks  |
| `done`    | `/tasks?done=false`            | Returns incomplete tasks |
| `search`  | `/tasks?search=book`           | Searches task titles     |
| Combined  | `/tasks?done=true&search=book` | Applies both filters     |

## Filter by Status

```text
GET /tasks?done=true
```

Returns only completed tasks.

## Search by Title

```text
GET /tasks?search=book
```

Returns tasks whose titles contain the search term.

The search uses SQL's `LIKE` operator and a parameterized query.

---

# Statistics

The API provides:

```text
GET /stats
```

Example response:

```json
{
    "total": 5,
    "done": 2,
    "open": 3
}
```

The statistics are calculated directly using SQL aggregation rather than loading every task into Python.

---

# Reset Tasks

The API provides:

```text
POST /reset
```

This deletes the current tasks and recreates:

```text
Homework
Read a book
Brainrot
```

The endpoint is useful for restoring a known state while testing the API.

---

# Error Responses

The API returns appropriate HTTP status codes for invalid requests.

| Status Code         | Description                                |
| ------------------- | ------------------------------------------ |
| **400 Bad Request** | Invalid request body or validation failure |
| **404 Not Found**   | Requested task does not exist              |

Example:

```json
{
    "detail": "Task 999 not found"
}
```

---

# Example Requests

The following examples use PowerShell.

## Get All Tasks

```powershell
(Invoke-WebRequest `
    -Method GET `
    -Uri "http://localhost:8000/tasks").Content
```

## Get a Task

```powershell
(Invoke-WebRequest `
    -Method GET `
    -Uri "http://localhost:8000/tasks/1").Content
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
(Invoke-WebRequest `
    -Method GET `
    -Uri "http://localhost:8000/tasks?done=true").Content
```

## Search Tasks

```powershell
(Invoke-WebRequest `
    -Method GET `
    -Uri "http://localhost:8000/tasks?search=book").Content
```

## Task Statistics

```powershell
(Invoke-WebRequest `
    -Method GET `
    -Uri "http://localhost:8000/stats").Content
```

## Reset Tasks

```powershell
(Invoke-WebRequest `
    -Method POST `
    -Uri "http://localhost:8000/reset").Content
```

---

# Parameterized Queries

The application uses parameterized SQL queries instead of directly concatenating user input into SQL statements.

For example:

```sql
SELECT id, title, done
FROM tasks
WHERE id = %s
```

The value is supplied separately:

```python
cursor.execute(query, (id,))
```

This prevents user-controlled values from being directly inserted into SQL statements and protects the database against SQL injection.

Parameterized queries are used for operations including:

* Selecting tasks by ID
* Searching tasks
* Inserting tasks
* Updating tasks
* Deleting tasks

---

# Validation Rules

The API validates incoming requests before processing them.

* Task title is required.
* Task title cannot be empty.
* Task title cannot contain only whitespace.
* Empty update request bodies are rejected.
* The `done` field must be a boolean when provided.
* Requests for non-existent tasks return `404 Not Found`.

---

# Security and Secrets

Sensitive configuration is stored in environment variables rather than committed to the repository.

The `.gitignore` file excludes:

```gitignore
.env
.env.local
```

This prevents database credentials and other environment-specific secrets from accidentally being pushed to GitHub.

A safe `.env.example` file can be committed to document the required configuration without containing real credentials.

---

# Docker Ignore

Files that are unnecessary inside the Docker build context should be excluded using `.dockerignore`.

Typical exclusions include:

```text
.venv/
venv/
__pycache__/
*.pyc
.git/
.env
```

This keeps the Docker build context smaller and prevents local virtual environments and secrets from being copied into the image.

---

# Containerized Development

The application can now be run without requiring PostgreSQL to be installed directly on the host machine.

Docker provides:

```text
FastAPI
    ↓
API container
    ↓
PostgreSQL container
```

This makes the development environment more reproducible because the application and its database run using defined container configurations.

The host machine only needs Docker and the project source code.

---

# Local PostgreSQL vs Docker PostgreSQL

During development, PostgreSQL may also exist as a locally installed Windows service.

However, the project is configured to use the **Docker PostgreSQL container** when started through Docker Compose.

Therefore, the application architecture does not depend on the PostgreSQL installation on the host machine.

The Docker Compose database service provides the PostgreSQL instance used by the containerized API.

---

# Persistence Demonstration

The database persistence can be demonstrated with the following process:

1. Start the application:

```powershell
docker compose up --build
```

2. Create a task using `POST /tasks`.

3. Verify the task using:

```text
GET /tasks
```

4. Stop the services:

```powershell
docker compose down
```

5. Start them again:

```powershell
docker compose up
```

6. Run:

```text
GET /tasks
```

7. Confirm that the previously created task is still present.

This demonstrates that PostgreSQL data is persisted independently of the API container.

---

# Git Ignore

The project excludes local and sensitive files from Git.

Important entries include:

```gitignore
# Python
__pycache__/
*.py[cod]

# Virtual environments
.venv/
venv/
ENV/
env/

# Environment variables / secrets
.env
.env.local

# Docker
.docker/

# IDE settings
.vscode/
```

The PostgreSQL database itself is not stored as a local database file in the repository. Its data is managed through Docker's PostgreSQL volume.

---

# Assignment Progress

## Stage 0 — Initial Task API

* Created the FastAPI application.
* Implemented the original CRUD endpoints.
* Added task validation.
* Added filtering and search functionality.
* Added statistics and reset functionality.

## Stage 1 — Database Migration

* Migrated the API from in-memory storage to database-backed storage.
* Added database initialization.
* Added database seeding.
* Updated CRUD operations to use SQL queries.

## Stage 2 — PostgreSQL Migration

* Replaced SQLite with PostgreSQL.
* Added `psycopg`.
* Added PostgreSQL connection configuration.
* Moved database configuration into environment variables.
* Updated SQL syntax from SQLite to PostgreSQL.
* Verified the API can connect to PostgreSQL.

## Stage 3 — Dockerization

* Created a Docker image for the FastAPI API.
* Created a PostgreSQL Docker container.
* Connected the API container to the PostgreSQL container.
* Configured the API to communicate with PostgreSQL through the Docker network.
* Added Docker volume persistence for PostgreSQL.

## Stage 4 — Containerized Application Testing

* Started both API and PostgreSQL services with Docker Compose.
* Verified PostgreSQL initializes successfully.
* Verified the API connects to the database container.
* Tested API endpoints through `localhost:8000`.
* Verified task creation and persistence.

## Stage 5 — Project Documentation and Publishing

* Updated project documentation to reflect PostgreSQL.
* Documented the Docker architecture.
* Documented environment variables and secret handling.
* Added `.env` to `.gitignore`.
* Added Docker-related configuration documentation.
* Prepared the repository for publication.

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
* PostgreSQL
* Database persistence
* Parameterized queries
* Database seeding
* SQL filtering using `WHERE`
* Text searching using `LIKE`
* SQL aggregation using `COUNT(*)`
* Database timestamps
* Environment variable configuration
* Docker containerization
* Docker Compose
* API-to-database container networking
* Docker volumes
* Interactive API documentation with Swagger UI
* API testing using PowerShell

---

# Final Architecture

The final application consists of:

```text
┌─────────────────────────────────────────────┐
│                  Host Machine               │
│                                             │
│   ┌─────────────────────────────────────┐   │
│   │         Docker Compose              │   │
│   │                                     │   │
│   │   ┌──────────────┐                  │   │
│   │   │ API          │                  │   │
│   │   │ FastAPI      │                  │   │
│   │   │ Uvicorn      │                  │   │
│   │   └──────┬───────┘                  │   │
│   │          │                          │   │
│   │          │ Docker network           │   │
│   │          ▼                          │   │
│   │   ┌──────────────┐                  │   │
│   │   │ PostgreSQL   │                  │   │
│   │   │ Database     │                  │   │
│   │   └──────┬───────┘                  │   │
│   │          │                          │   │
│   │          ▼                          │   │
│   │   ┌──────────────┐                  │   │
│   │   │ Docker       │                  │   │
│   │   │ Volume       │                  │   │
│   │   └──────────────┘                  │   │
│   │                                     │   │
│   └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘

                 ▲
                 │
                 │ http://localhost:8000
                 │
              Client
```

The important separation is:

```text
API code → API container
Database → PostgreSQL container
Database data → Docker volume
Secrets → .env
```

This provides a reproducible containerized development environment while keeping application code, database infrastructure, persistent data, and secrets properly separated.

---

# License

This project is intended for educational purposes and may be freely modified or extended.
