# Project Architecture Overview: Python Jogja Member API

## 1. Core Technologies

* **Web Framework:** FastAPI (Python)
* **ORM/Database:** SQLModel (built on SQLAlchemy and Pydantic)
* **Database:** SQLite (for development/demo), PostgreSQL (for production - agent should be aware of this for schema generation, though we'll use SQLite for this demo)
* **Dependency Management:** pip/venv
* **Testing:** Pytest

## 2. Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application, API endpoints
│   ├── models.py           # SQLModel definitions (e.g., Member)
│   ├── database.py         # Database engine, session management
│   └── crud.py             # CRUD operations (optional, for larger apps)
├── tests/
│   ├── __init__.py
│   └── test_members.py     # Unit and integration tests
├── scripts/                # Utility scripts (e.g., initial data, migrations)
│   └── initial_data.py
├── .env                    # Environment variables
├── README.md
└── ARCHITECTURE.md         # This file
```

## 3. Design Principles

* **API-First:** Design endpoints clearly and consistently.
* **Separation of Concerns:** Keep API routes, data models, and database logic distinct.
* **Dependency Injection:** Utilize FastAPI's dependency injection for database sessions and other services.
* **Type Hinting:** Strictly use Python type hints for clarity and static analysis.
* **Asynchronous Operations:** Prefer `async/await` for database operations where applicable.

## 4. Database Migrations

* **Tool:** Alembic (for production, though not strictly required for this simple demo with SQLite).
* **Principle:** Schema changes should be managed via migrations.

## 5. Error Handling

* Use FastAPI's `HTTPException` for standard API errors.
* Implement custom exception handlers for specific business logic errors.

