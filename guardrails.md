# Project Guardrails: Python Jogja Member API

---

## 1. Coding Standards & Style

* **PEP 8 Compliance**: All Python code must strictly follow [PEP 8](https://www.python.org/dev/peps/pep-0008/).
* **Black Formatting**: Use [Black](https://github.com/psf/black) for automatic code formatting.
* **Isort**: Use [isort](https://pycqa.github.io/isort/) for import sorting.
* **Docstrings**: All functions, classes, and modules must have clear docstrings (Google style preferred).
* **Type Hinting**: Mandatory for all function arguments, return values, and class attributes.
* **Naming Conventions**:
    * Variables: `snake_case`
    * Functions: `snake_case`
    * Classes: `PascalCase`
    * Constants: `UPPER_SNAKE_CASE`

---

## 2. Security Considerations

* **Input Validation**: All API inputs must be thoroughly validated (FastAPI/Pydantic models handle much of this).
* **No Raw SQL**: Absolutely no raw SQL queries. Use SQLModel's ORM capabilities exclusively.
* **Sensitive Data**: Do not log sensitive user information (passwords, full PII).
* **Error Messages**: Generic error messages for production environments; avoid exposing internal details.
* **Dependency Security**: Keep dependencies updated to avoid known vulnerabilities.

---

## 3. Performance & Scalability

* **Database Queries**: Optimize database queries. Avoid N+1 issues.
* **Asynchronous Operations**: Use `async`/`await` for I/O bound operations (like database calls).
* **No Blocking Operations**: Ensure no long-running synchronous tasks block the event loop.

---

## 4. Error Handling

* **FastAPI HTTPException**: Use `raise HTTPException(status_code=..., detail=...)` for API errors.
* **Specific Exceptions**: Define custom exceptions for business logic errors where appropriate.
* **Logging**: Implement structured logging for debugging and monitoring.

---

## 5. Code Readability & Maintainability

* **Modularity**: Break down complex logic into smaller, testable functions/modules.
* **Comments**: Use comments to explain complex logic, but prefer self-documenting code.
* **DRY Principle**: Avoid code duplication.

---

## 6. Validation Architecture

### Problem: SQLModel + Pydantic Validator Conflicts

When using SQLModel with complex Pydantic validators, you may encounter SQLAlchemy mapping issues like:
```
sqlalchemy.exc.ArgumentError: Mapper could not assemble any primary key columns
```

### Solution: Business Logic Layer Validation

**Recommended Approach:**
* **Keep models simple** - Use basic SQLModel classes without complex validators
* **Validate in CRUD layer** - Implement validation functions in the business logic layer
* **Custom exceptions** - Create specific exception types for business rule violations

**Example Implementation:**
```python
# models.py - Simple, clean models
class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="Member's full name")
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = Field(default=None, unique=True, index=True)

# crud.py - Validation in business logic
def validate_email(email: str) -> str:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip().lower()):
        raise ValueError("Invalid email format")
    return email.strip().lower()

def create_member(session: Session, member_data: MemberCreate) -> Member:
    # Validate input data
    name = validate_name(member_data.name)
    email = validate_email(member_data.email)
    phone = validate_phone(member_data.phone)
    
    # Check business rules (uniqueness)
    # Create member with validated data
```

**Benefits:**
* **Cleaner separation** - Models focus on data structure, CRUD handles validation
* **Better testability** - Can unit test validation logic independently
* **More control** - Full control over error messages and validation flow
* **Avoids framework conflicts** - No SQLModel/Pydantic version compatibility issues

