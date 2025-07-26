"""
Business logic validation functions for Python Jogja Member API.

This module implements validation functions that are called from the CRUD layer.
Following guardrails.md, we handle validation in the business logic layer
rather than using complex Pydantic validators to avoid SQLModel conflicts.
"""

import re
from typing import Optional
from app.exceptions import InvalidMemberDataError


def validate_name(name: str) -> str:
    """
    Validate and normalize member name.
    
    Args:
        name: Raw name input from user
        
    Returns:
        str: Validated and normalized name
        
    Raises:
        InvalidMemberDataError: If name is invalid
    """
    if not name or not isinstance(name, str):
        raise InvalidMemberDataError("name", str(name), "Name is required")
    
    # Strip whitespace and normalize
    normalized_name = name.strip()
    
    if not normalized_name:
        raise InvalidMemberDataError("name", name, "Name cannot be empty or only whitespace")
    
    if len(normalized_name) < 2:
        raise InvalidMemberDataError("name", name, "Name must be at least 2 characters long")
    
    if len(normalized_name) > 100:
        raise InvalidMemberDataError("name", name, "Name cannot exceed 100 characters")
    
    # Check for invalid characters (letters, numbers, spaces, hyphens, apostrophes, dots)
    if not re.match(r"^[a-zA-Z0-9\s\-'\.]+$", normalized_name):
        raise InvalidMemberDataError("name", name, "Name contains invalid characters")
    
    return normalized_name


def validate_email(email: str) -> str:
    """
    Validate and normalize email address.
    
    Args:
        email: Raw email input from user
        
    Returns:
        str: Validated and normalized email (lowercase)
        
    Raises:
        InvalidMemberDataError: If email format is invalid
    """
    if not email or not isinstance(email, str):
        raise InvalidMemberDataError("email", str(email), "Email is required")
    
    # Strip whitespace and convert to lowercase
    normalized_email = email.strip().lower()
    
    if not normalized_email:
        raise InvalidMemberDataError("email", email, "Email cannot be empty")
    
    if len(normalized_email) > 254:  # RFC 5321 limit
        raise InvalidMemberDataError("email", email, "Email address is too long")
    
    # Basic email regex pattern (RFC 5322 compliant)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, normalized_email):
        raise InvalidMemberDataError("email", email, "Invalid email format")
    
    # Additional checks for common issues
    if '..' in normalized_email:
        raise InvalidMemberDataError("email", email, "Email cannot contain consecutive dots")
    
    if normalized_email.startswith('.') or normalized_email.endswith('.'):
        raise InvalidMemberDataError("email", email, "Email cannot start or end with a dot")
    
    return normalized_email


def validate_phone(phone: Optional[str]) -> Optional[str]:
    """
    Validate and normalize phone number.
    
    Args:
        phone: Raw phone input from user (optional)
        
    Returns:
        Optional[str]: Validated and normalized phone number or None
        
    Raises:
        InvalidMemberDataError: If phone format is invalid
    """
    if phone is None:
        return None
    
    if not isinstance(phone, str):
        raise InvalidMemberDataError("phone", str(phone), "Phone must be a string")
    
    # Strip whitespace
    normalized_phone = phone.strip()
    
    if not normalized_phone:
        return None  # Empty phone is allowed
    
    if len(normalized_phone) > 20:
        raise InvalidMemberDataError("phone", phone, "Phone number is too long")
    
    # Remove common formatting characters for validation
    clean_phone = re.sub(r'[\s\-\(\)\+\.]', '', normalized_phone)
    
    # Check if it contains only digits after cleaning
    if not clean_phone.isdigit():
        raise InvalidMemberDataError("phone", phone, "Phone number contains invalid characters")
    
    if len(clean_phone) < 8:
        raise InvalidMemberDataError("phone", phone, "Phone number is too short")
    
    if len(clean_phone) > 15:  # ITU-T E.164 standard
        raise InvalidMemberDataError("phone", phone, "Phone number is too long")
    
    # Return the original formatted version (preserve user formatting)
    return normalized_phone


def validate_member_data(name: str, email: str, phone: Optional[str] = None) -> tuple[str, str, Optional[str]]:
    """
    Validate all member data fields together.
    
    Args:
        name: Member's name
        email: Member's email
        phone: Member's phone (optional)
        
    Returns:
        tuple: (validated_name, validated_email, validated_phone)
        
    Raises:
        InvalidMemberDataError: If any field is invalid
    """
    validated_name = validate_name(name)
    validated_email = validate_email(email)
    validated_phone = validate_phone(phone)
    
    return validated_name, validated_email, validated_phone 