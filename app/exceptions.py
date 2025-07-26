"""
Custom exceptions for Python Jogja Member API.

This module defines business logic exceptions that will be caught
and converted to appropriate HTTP responses by FastAPI exception handlers.

Following guardrails.md, we use specific exceptions for business rule violations
rather than generic errors, and provide generic error messages for production.
"""

from typing import Optional


class MemberAPIException(Exception):
    """Base exception for all Member API business logic errors."""
    
    def __init__(self, message: str, detail: Optional[str] = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class MemberAlreadyExistsError(MemberAPIException):
    """
    Raised when attempting to create a member with an email or phone
    that already exists in the database.
    
    This exception should be caught and converted to HTTP 409 Conflict.
    """
    
    def __init__(self, field: str, value: str):
        self.field = field  # 'email' or 'phone'
        self.value = value
        message = f"Member with {field} '{value}' already exists"
        detail = f"A member with this {field} is already registered"
        super().__init__(message, detail)


class MemberNotFoundError(MemberAPIException):
    """
    Raised when attempting to access a member that doesn't exist.
    
    This exception should be caught and converted to HTTP 404 Not Found.
    """
    
    def __init__(self, identifier: str, value: str):
        self.identifier = identifier  # 'id', 'email', etc.
        self.value = value
        message = f"Member with {identifier} '{value}' not found"
        detail = "The requested member does not exist"
        super().__init__(message, detail)


class InvalidMemberDataError(MemberAPIException):
    """
    Raised when member data fails business logic validation.
    
    This exception should be caught and converted to HTTP 400 Bad Request.
    """
    
    def __init__(self, field: str, value: str, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        message = f"Invalid {field}: {reason}"
        detail = f"The provided {field} is not valid"
        super().__init__(message, detail)


class DatabaseOperationError(MemberAPIException):
    """
    Raised when a database operation fails unexpectedly.
    
    This exception should be caught and converted to HTTP 500 Internal Server Error.
    """
    
    def __init__(self, operation: str, details: Optional[str] = None):
        self.operation = operation
        message = f"Database operation failed: {operation}"
        detail = "An internal error occurred while processing your request"
        super().__init__(message, detail) 