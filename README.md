# Task Management API

A lightweight RESTful API built with **Python** and **FastAPI** for managing tasks in memory. This project demonstrates REST API fundamentals, including full CRUD operations, input validation, proper HTTP status codes, query parameter filtering, and automatically generated API documentation with Swagger UI.

---

## Features

- Full CRUD operations (Create, Read, Update, Delete)
- In-memory task storage (no database required)
- Task filtering using query parameters (`?done=true` / `?done=false`)
- Task search by title (`?search=keyword`)
- Task statistics endpoint
- Reset endpoint to restore the default task list
- Strict input validation
  - Rejects empty request bodies
  - Rejects invalid data types
  - Rejects whitespace-only task titles
- Proper HTTP status code handling
- Automatic interactive API documentation via Swagger UI
- Clean, lightweight FastAPI implementation

---

## Tech Stack

- **Python 3.9+**
- **FastAPI**
- **Uvicorn**

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PaulRiachy/Backend-AI-FlyRank.git
cd Backend-AI-FlyRank
```

### 2. Create a Virtual Environment

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install fastapi uvicorn
```

### 4. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

---

## API Documentation

FastAPI automatically generates interactive API documentation.

| Documentation | URL |
|--------------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## API Endpoints

| Method | Endpoint | Description | Success Status |
|:------:|----------|-------------|:--------------:|
| **GET** | `/` | API information and available routes | **200 OK** |
| **GET** | `/health` | Health check | **200 OK** |
| **GET** | `/tasks` | Retrieve all tasks (supports filtering and search) | **200 OK** |
| **GET** | `/tasks/{id}` | Retrieve a task by ID | **200 OK** |
| **POST** | `/tasks` | Create a new task | **201 Created** |
| **PUT** | `/tasks/{id}` | Update an existing task | **200 OK** |
| **DELETE** | `/tasks/{id}` | Delete a task | **204 No Content** |
| **GET** | `/stats` | Retrieve task statistics | **200 OK** |
| **POST** | `/reset` | Restore the default sample tasks | **200 OK** |

---

## Query Parameters

The `GET /tasks` endpoint supports optional query parameters.

| Parameter | Example | Description |
|-----------|---------|-------------|
| `done` | `/tasks?done=true` | Returns only completed or incomplete tasks |
| `search` | `/tasks?search=book` | Returns tasks whose title contains the search term |
| Combined | `/tasks?done=true&search=book` | Applies both filters together |

---

## Error Responses

The API returns appropriate HTTP status codes for invalid requests.

| Status Code | Description |
|-------------|-------------|
| **400 Bad Request** | Invalid request body or validation failed |
| **404 Not Found** | Requested task does not exist |

---

## Example Requests

### Get All Tasks

```powershell
(Invoke-WebRequest -Method GET -Uri "http://localhost:8000/tasks").Content
```

### Get a Task

```powershell
(Invoke-WebRequest -Method GET -Uri "http://localhost:8000/tasks/1").Content
```

### Create a Task

```powershell
(Invoke-WebRequest `
-Method POST `
-Uri "http://localhost:8000/tasks" `
-Headers @{"Content-Type"="application/json"} `
-Body '{"title":"Complete Stage 6"}').Content
```

### Update a Task

```powershell
(Invoke-WebRequest `
-Method PUT `
-Uri "http://localhost:8000/tasks/1" `
-Headers @{"Content-Type"="application/json"} `
-Body '{"title":"Updated Title","done":true}').Content
```

### Delete a Task

```powershell
(Invoke-WebRequest `
-Method DELETE `
-Uri "http://localhost:8000/tasks/1").StatusCode
```

### Filter Completed Tasks

```powershell
(Invoke-WebRequest -Method GET -Uri "http://localhost:8000/tasks?done=true").Content
```

### Search Tasks

```powershell
(Invoke-WebRequest -Method GET -Uri "http://localhost:8000/tasks?search=book").Content
```

### Task Statistics

```powershell
(Invoke-WebRequest -Method GET -Uri "http://localhost:8000/stats").Content
```

### Reset Tasks

```powershell
(Invoke-WebRequest -Method POST -Uri "http://localhost:8000/reset").Content
```

---

## Sample Response

Example response from creating a task:

```text
HTTP/1.1 201 Created
content-type: application/json

{
    "id": 4,
    "title": "Complete Stage 6",
    "done": false
}
```

---

## Swagger UI

Interactive API documentation is available at:

```
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

## Project Structure

```text
.
├── main.py
├── README.md
├── .gitignore
└── images/
    └── swagger-ui.png
```

---

## Validation Rules

The API validates incoming requests before processing them.

- Task title is required.
- Task title cannot be empty.
- Task title cannot contain only whitespace.
- Invalid request formats are rejected.
- Requests for non-existent tasks return `404 Not Found`.

---

## In-Memory Storage

Tasks are stored entirely in memory. Any changes made while the server is running are lost when the application is restarted. Restarting the server restores the original sample tasks, demonstrating why persistent databases are commonly used in production applications.

---

## Learning Objectives

This project demonstrates:

- RESTful API design
- FastAPI fundamentals
- CRUD endpoint implementation
- HTTP methods and status codes
- Input validation
- Query parameters for filtering and searching
- Interactive API documentation with Swagger UI
- Basic API testing using PowerShell and Swagger UI

---

## License

This project is intended for educational purposes and may be freely modified or extended.