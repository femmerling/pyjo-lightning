"""
FastAPI application for Python Jogja Member API.

This is the main application module that defines the FastAPI app,
API endpoints, and exception handlers.

Following architecture.md principles:
- API-first design with clear endpoints
- Dependency injection for database sessions
- Proper error handling with HTTP status codes
"""

from typing import List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.database import get_session, create_db_and_tables
from app.models import Member, MemberCreate, MemberResponse, MemberUpdate
from app import crud
from app.exceptions import (
    MemberAPIException,
    MemberAlreadyExistsError,
    MemberNotFoundError,
    InvalidMemberDataError,
    DatabaseOperationError
)

# Create FastAPI application
app = FastAPI(
    title="Python Jogja Member API",
    version="1.0.0",
    description="API for managing Python Jogjakarta Community members",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Exception handlers
@app.exception_handler(MemberAlreadyExistsError)
async def member_already_exists_handler(request, exc: MemberAlreadyExistsError):
    """Handle member already exists errors (409 Conflict)."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": exc.detail,
            "field": exc.field,
            "error_type": "conflict"
        }
    )


@app.exception_handler(MemberNotFoundError)
async def member_not_found_handler(request, exc: MemberNotFoundError):
    """Handle member not found errors (404 Not Found)."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": exc.detail,
            "error_type": "not_found"
        }
    )


@app.exception_handler(InvalidMemberDataError)
async def invalid_member_data_handler(request, exc: InvalidMemberDataError):
    """Handle invalid member data errors (400 Bad Request)."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.detail,
            "field": exc.field,
            "error_type": "validation_error"
        }
    )


@app.exception_handler(DatabaseOperationError)
async def database_operation_handler(request, exc: DatabaseOperationError):
    """Handle database operation errors (500 Internal Server Error)."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": exc.detail,
            "error_type": "internal_error"
        }
    )


@app.exception_handler(MemberAPIException)
async def generic_api_exception_handler(request, exc: MemberAPIException):
    """Handle any other member API exceptions (500 Internal Server Error)."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred while processing your request",
            "error_type": "internal_error"
        }
    )


# Startup event
@app.on_event("startup")
def on_startup():
    """Initialize database tables on application startup."""
    create_db_and_tables()


# API Endpoints

@app.post(
    "/members/",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new member",
    description="Add a new member to the Python Jogja community database",
    responses={
        201: {"description": "Member created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "Member with this email or phone already exists"},
        500: {"description": "Internal server error"}
    }
)
async def create_member(
    member_data: MemberCreate,
    session: Session = Depends(get_session)
) -> MemberResponse:
    """
    Create a new member in the Python Jogja community.
    
    This endpoint follows the exact business logic sequence from requirements.md:
    1. Validate input data (handled by Pydantic + business logic)
    2. Check email uniqueness
    3. Check phone uniqueness (if provided)
    4. Create and return the new member
    
    Args:
        member_data: Member creation data (name, email, phone)
        session: Database session (injected dependency)
        
    Returns:
        MemberResponse: Created member with generated ID
        
    Raises:
        HTTPException: Various HTTP errors based on business logic
    """
    try:
        # Create member using CRUD function
        new_member = crud.create_member(session, member_data)
        
        # Return the created member
        return MemberResponse.from_orm(new_member)
        
    except (
        MemberAlreadyExistsError,
        MemberNotFoundError,
        InvalidMemberDataError,
        DatabaseOperationError
    ):
        # These exceptions are handled by exception handlers above
        raise
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the member"
        )


@app.get(
    "/members/",
    response_model=List[MemberResponse],
    summary="List all members",
    description="Retrieve all members with optional pagination",
    responses={
        200: {"description": "List of members retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def list_members(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
) -> List[MemberResponse]:
    """
    Retrieve all members with pagination.
    
    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        session: Database session (injected dependency)
        
    Returns:
        List[MemberResponse]: List of members
    """
    try:
        # Limit the maximum number of records to prevent performance issues
        limit = min(limit, 100)
        
        members = crud.get_all_members(session, skip=skip, limit=limit)
        
        return [MemberResponse.from_orm(member) for member in members]
        
    except DatabaseOperationError:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving members"
        )


@app.get(
    "/members/{member_id}",
    response_model=MemberResponse,
    summary="Get member by ID",
    description="Retrieve a specific member by their ID",
    responses={
        200: {"description": "Member retrieved successfully"},
        404: {"description": "Member not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_member(
    member_id: int,
    session: Session = Depends(get_session)
) -> MemberResponse:
    """
    Retrieve a member by their ID.
    
    Args:
        member_id: Unique member identifier
        session: Database session (injected dependency)
        
    Returns:
        MemberResponse: Member data
        
    Raises:
        HTTPException: 404 if member not found, 500 for other errors
    """
    try:
        member = crud.get_member_by_id(session, member_id)
        
        if not member:
            raise MemberNotFoundError("id", str(member_id))
        
        return MemberResponse.from_orm(member)
        
    except (MemberNotFoundError, DatabaseOperationError):
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the member"
        )


@app.put(
    "/members/{member_id}",
    response_model=MemberResponse,
    summary="Update member",
    description="Update an existing member's information",
    responses={
        200: {"description": "Member updated successfully"},
        400: {"description": "Invalid input data"},
        404: {"description": "Member not found"},
        409: {"description": "Email or phone already exists"},
        500: {"description": "Internal server error"}
    }
)
async def update_member(
    member_id: int,
    member_data: MemberUpdate,
    session: Session = Depends(get_session)
) -> MemberResponse:
    """
    Update an existing member's information.
    
    Args:
        member_id: Unique member identifier
        member_data: Partial member update data
        session: Database session (injected dependency)
        
    Returns:
        MemberResponse: Updated member data
    """
    try:
        updated_member = crud.update_member(session, member_id, member_data)
        
        return MemberResponse.from_orm(updated_member)
        
    except (
        MemberNotFoundError,
        InvalidMemberDataError,
        MemberAlreadyExistsError,
        DatabaseOperationError
    ):
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the member"
        )


@app.delete(
    "/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete member",
    description="Delete a member from the database",
    responses={
        204: {"description": "Member deleted successfully"},
        404: {"description": "Member not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_member(
    member_id: int,
    session: Session = Depends(get_session)
):
    """
    Delete a member from the database.
    
    Args:
        member_id: Unique member identifier
        session: Database session (injected dependency)
        
    Returns:
        None: 204 No Content on successful deletion
    """
    try:
        crud.delete_member(session, member_id)
        
        # Return 204 No Content (no response body)
        return None
        
    except (MemberNotFoundError, DatabaseOperationError):
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the member"
        )


@app.get(
    "/health",
    summary="Health check",
    description="Simple health check endpoint",
    responses={
        200: {"description": "Service is healthy"}
    }
)
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "Python Jogja Member API"}


# Root endpoint
@app.get(
    "/",
    summary="API information",
    description="Get basic API information"
)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Python Jogja Member API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    } 