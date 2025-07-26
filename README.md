# Python Jogja Member API

A FastAPI-based REST API for managing Python Jogjakarta Community members. This API provides endpoints to create, read, update, and delete member information with proper validation and error handling.

## 🚀 Features

- **RESTful API** with FastAPI framework
- **Member Management** - Create, read, update, delete operations
- **Data Validation** - Comprehensive input validation and business logic
- **Unique Constraints** - Email and phone number uniqueness enforcement
- **Error Handling** - Proper HTTP status codes and error messages
- **API Documentation** - Automatic OpenAPI/Swagger documentation
- **Database** - SQLite for development, PostgreSQL-ready for production
- **Testing** - Comprehensive unit test suite
- **Type Safety** - Full Python type hints throughout

## 🏗️ Architecture

- **FastAPI** - Modern, fast web framework for Python APIs
- **SQLModel** - SQL databases using Python type hints (built on SQLAlchemy + Pydantic)
- **SQLite** - Default database for development (easily switchable to PostgreSQL)
- **Pydantic** - Data validation using Python type annotations
- **unittest** - Testing framework with in-memory database isolation

## 📋 Requirements

- Python 3.8+
- pip (Python package manager)

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd pyjo-lightning
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# On macOS/Linux:
source env/bin/activate
# On Windows:
env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

The API uses environment variables for configuration. Default values are provided for development:

- `DATABASE_URL`: Database connection string (default: `sqlite:///./pyjo_members.db`)
- `API_TITLE`: API title (default: `Python Jogja Member API`)
- `API_VERSION`: API version (default: `1.0.0`)
- `ENVIRONMENT`: Environment mode (default: `development`)

For production, create a `.env` file or set environment variables:

```bash
# .env file (optional)
DATABASE_URL=sqlite:///./pyjo_members.db
API_TITLE=Python Jogja Member API
API_VERSION=1.0.0
ENVIRONMENT=development
```

### 5. Initialize Database

The database tables are created automatically when you first run the application. Optionally, you can populate it with sample data:

```bash
# Create sample data
python scripts/initial_data.py

# Or clear existing data and create fresh sample data
python scripts/initial_data.py --clear
```

## 🚀 Running the Application

### Development Server

```bash
# Run with uvicorn (recommended for development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Production Server

```bash
# Run without reload for production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

### Base URLs

- **Development**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

### Endpoints

#### **POST /members/** - Create New Member

Create a new member in the Python Jogja community.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890"  // Optional
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `409 Conflict` - Email or phone already exists
- `500 Internal Server Error` - Server error

#### **GET /members/** - List All Members

Retrieve all members with optional pagination.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 100, max: 100)

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890"
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "phone": null
  }
]
```

#### **GET /members/{member_id}** - Get Member by ID

Retrieve a specific member by their ID.

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890"
}
```

**Error Responses:**
- `404 Not Found` - Member not found

#### **PUT /members/{member_id}** - Update Member

Update an existing member's information (partial updates supported).

**Request Body (all fields optional):**
```json
{
  "name": "John Smith",
  "email": "john.smith@example.com",
  "phone": "+0987654321"
}
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john.smith@example.com",
  "phone": "+0987654321"
}
```

#### **DELETE /members/{member_id}** - Delete Member

Delete a member from the database.

**Success Response:** `204 No Content`

**Error Responses:**
- `404 Not Found` - Member not found

### Data Validation Rules

#### Name
- Required field
- Minimum 2 characters
- Maximum 100 characters
- Only letters, spaces, hyphens, apostrophes, and dots allowed

#### Email
- Required field
- Must be valid email format (RFC 5322 compliant)
- Maximum 254 characters
- Automatically converted to lowercase
- Must be unique across all members

#### Phone
- Optional field
- Maximum 20 characters
- Must contain only digits and common formatting characters (+, -, (), ., spaces)
- Minimum 8 digits, maximum 15 digits (ITU-T E.164 standard)
- Must be unique if provided

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_members

# Run with verbose output
python -m unittest discover tests -v
```

### Test Coverage

```bash
# Install coverage if not already installed
pip install coverage

# Run tests with coverage
coverage run -m unittest discover tests

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

### Test Structure

The test suite includes:
- **Validation Tests** - Input validation and data normalization
- **CRUD Tests** - Database operations and business logic
- **Business Logic Tests** - Edge cases and complex scenarios
- **Error Handling Tests** - Exception handling and error responses

Each test uses a fresh in-memory SQLite database for complete isolation.

## 📁 Project Structure

```
pyjo-lightning/
├── app/                     # Main application package
│   ├── __init__.py
│   ├── main.py             # FastAPI application and endpoints
│   ├── models.py           # SQLModel data models
│   ├── database.py         # Database configuration and session management
│   ├── crud.py             # Database operations (Create, Read, Update, Delete)
│   ├── validation.py       # Business logic validation functions
│   └── exceptions.py       # Custom exception classes
├── tests/                  # Test suite
│   ├── __init__.py
│   └── test_members.py     # Unit tests for member operations
├── scripts/                # Utility scripts
│   └── initial_data.py     # Sample data population script
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── architecture.md        # Technical architecture documentation
├── guardrails.md          # Development guidelines and best practices
├── requirements.md        # Feature requirements and specifications
└── testing.md            # Testing strategy and guidelines
```

## 🔒 Security Considerations

- **Input Validation** - All inputs are validated at multiple levels
- **No Raw SQL** - Uses SQLModel/SQLAlchemy ORM exclusively
- **Generic Error Messages** - Production-safe error messages that don't expose internals
- **Type Safety** - Comprehensive type hints prevent common errors
- **Database Constraints** - Uniqueness enforced at database level

## 🚦 API Usage Examples

### Using curl

```bash
# Create a new member
curl -X POST "http://localhost:8000/members/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Andi Pratama",
    "email": "andi.pratama@python-jogja.org",
    "phone": "+62812345678"
  }'

# Get all members
curl "http://localhost:8000/members/"

# Get specific member
curl "http://localhost:8000/members/1"

# Update member
curl -X PUT "http://localhost:8000/members/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Andi Pratama Wijaya"
  }'

# Delete member
curl -X DELETE "http://localhost:8000/members/1"
```

### Using Python requests

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Create a new member
new_member = {
    "name": "Siti Nurhaliza",
    "email": "siti.nurhaliza@python-jogja.org",
    "phone": "+62812345679"
}
response = requests.post(f"{BASE_URL}/members/", json=new_member)
print(response.json())

# Get all members
response = requests.get(f"{BASE_URL}/members/")
members = response.json()
print(f"Total members: {len(members)}")

# Get specific member
member_id = 1
response = requests.get(f"{BASE_URL}/members/{member_id}")
if response.status_code == 200:
    member = response.json()
    print(f"Member: {member['name']} ({member['email']})")
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Use a different port
   uvicorn app.main:app --reload --port 8001
   ```

2. **Database locked (SQLite)**
   ```bash
   # Stop all running instances and try again
   # Or delete the database file and restart
   rm pyjo_members.db
   ```

3. **Import errors**
   ```bash
   # Make sure you're in the project root directory
   # And virtual environment is activated
   pwd  # Should show pyjo-lightning directory
   which python  # Should show virtual environment path
   ```

4. **Tests failing**
   ```bash
   # Make sure all dependencies are installed
   pip install -r requirements.txt
   
   # Run tests with verbose output for debugging
   python -m unittest discover tests -v
   ```

## 🤝 Contributing

1. Follow the coding standards defined in `guardrails.md`
2. Write tests for any new functionality
3. Ensure all tests pass before submitting changes
4. Use proper type hints throughout
5. Follow PEP 8 style guidelines

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Python Jogjakarta Community** - For the inspiration and requirements
- **FastAPI** - For the excellent web framework
- **SQLModel** - For the innovative ORM approach
- **Pydantic** - For robust data validation

---

**Happy coding!** 🐍✨ 