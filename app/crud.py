"""
CRUD operations for Python Jogja Member API.

This module implements Create, Read, Update, Delete operations for members
with proper business logic validation and error handling.

Following guardrails.md, all validation is handled here in the business logic layer
rather than in Pydantic models to avoid SQLModel conflicts.
"""

from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.models import Member, MemberCreate, MemberUpdate
from app.validation import validate_member_data
from app.exceptions import (
    MemberAlreadyExistsError,
    MemberNotFoundError,
    DatabaseOperationError,
    InvalidMemberDataError
)


def get_member_by_email(session: Session, email: str) -> Optional[Member]:
    """
    Retrieve a member by email address.
    
    Args:
        session: Database session
        email: Member's email address
        
    Returns:
        Optional[Member]: Member if found, None otherwise
    """
    try:
        statement = select(Member).where(Member.email == email.lower())
        return session.exec(statement).first()
    except Exception as e:
        raise DatabaseOperationError("get_member_by_email", str(e))


def get_member_by_phone(session: Session, phone: str) -> Optional[Member]:
    """
    Retrieve a member by phone number.
    
    Args:
        session: Database session
        phone: Member's phone number
        
    Returns:
        Optional[Member]: Member if found, None otherwise
    """
    try:
        statement = select(Member).where(Member.phone == phone)
        return session.exec(statement).first()
    except Exception as e:
        raise DatabaseOperationError("get_member_by_phone", str(e))


def get_member_by_id(session: Session, member_id: int) -> Optional[Member]:
    """
    Retrieve a member by ID.
    
    Args:
        session: Database session
        member_id: Member's unique ID
        
    Returns:
        Optional[Member]: Member if found, None otherwise
    """
    try:
        return session.get(Member, member_id)
    except Exception as e:
        raise DatabaseOperationError("get_member_by_id", str(e))


def get_all_members(session: Session, skip: int = 0, limit: int = 100) -> List[Member]:
    """
    Retrieve all members with pagination.
    
    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[Member]: List of members
    """
    try:
        statement = select(Member).offset(skip).limit(limit)
        return list(session.exec(statement).all())
    except Exception as e:
        raise DatabaseOperationError("get_all_members", str(e))


def create_member(session: Session, member_data: MemberCreate) -> Member:
    """
    Create a new member following the business logic sequence from requirements.md.
    
    Sequence:
    1. Validate input data
    2. Check email uniqueness
    3. Check phone uniqueness (if provided)
    4. Create and save member
    
    Args:
        session: Database session
        member_data: Member creation data
        
    Returns:
        Member: Newly created member with ID
        
    Raises:
        InvalidMemberDataError: If validation fails
        MemberAlreadyExistsError: If email or phone already exists
        DatabaseOperationError: If database operation fails
    """
    try:
        # Step 1: Validate input data
        validated_name, validated_email, validated_phone = validate_member_data(
            member_data.name,
            member_data.email,
            member_data.phone
        )
        
        # Step 2: Check email uniqueness
        existing_member_by_email = get_member_by_email(session, validated_email)
        if existing_member_by_email:
            raise MemberAlreadyExistsError("email", validated_email)
        
        # Step 3: Check phone uniqueness (if provided)
        if validated_phone:
            existing_member_by_phone = get_member_by_phone(session, validated_phone)
            if existing_member_by_phone:
                raise MemberAlreadyExistsError("phone", validated_phone)
        
        # Step 4: Create new member with validated data
        new_member = Member(
            name=validated_name,
            email=validated_email,
            phone=validated_phone
        )
        
        # Add to session and commit
        session.add(new_member)
        session.commit()
        session.refresh(new_member)
        
        return new_member
        
    except (InvalidMemberDataError, MemberAlreadyExistsError):
        # Re-raise business logic exceptions as-is
        session.rollback()
        raise
    except IntegrityError as e:
        # Handle database constraint violations
        session.rollback()
        if "email" in str(e).lower():
            raise MemberAlreadyExistsError("email", validated_email)
        elif "phone" in str(e).lower():
            raise MemberAlreadyExistsError("phone", validated_phone or "")
        else:
            raise DatabaseOperationError("create_member", "Constraint violation")
    except Exception as e:
        # Handle unexpected database errors
        session.rollback()
        raise DatabaseOperationError("create_member", str(e))


def update_member(session: Session, member_id: int, member_data: MemberUpdate) -> Member:
    """
    Update an existing member with partial data.
    
    Args:
        session: Database session
        member_id: ID of member to update
        member_data: Partial member update data
        
    Returns:
        Member: Updated member
        
    Raises:
        MemberNotFoundError: If member doesn't exist
        InvalidMemberDataError: If validation fails
        MemberAlreadyExistsError: If email or phone conflicts
        DatabaseOperationError: If database operation fails
    """
    try:
        # Get existing member
        existing_member = get_member_by_id(session, member_id)
        if not existing_member:
            raise MemberNotFoundError("id", str(member_id))
        
        # Validate and update fields that are provided
        update_data = {}
        
        if member_data.name is not None:
            update_data["name"] = validate_member_data(member_data.name, "dummy@example.com")[0]
        
        if member_data.email is not None:
            validated_email = validate_member_data("Dummy", member_data.email)[1]
            # Check email uniqueness (exclude current member)
            existing_email_member = get_member_by_email(session, validated_email)
            if existing_email_member and existing_email_member.id != member_id:
                raise MemberAlreadyExistsError("email", validated_email)
            update_data["email"] = validated_email
        
        if member_data.phone is not None:
            validated_phone = validate_member_data("Dummy", "dummy@example.com", member_data.phone)[2]
            if validated_phone:
                # Check phone uniqueness (exclude current member)
                existing_phone_member = get_member_by_phone(session, validated_phone)
                if existing_phone_member and existing_phone_member.id != member_id:
                    raise MemberAlreadyExistsError("phone", validated_phone)
            update_data["phone"] = validated_phone
        
        # Apply updates
        for field, value in update_data.items():
            setattr(existing_member, field, value)
        
        session.add(existing_member)
        session.commit()
        session.refresh(existing_member)
        
        return existing_member
        
    except (InvalidMemberDataError, MemberAlreadyExistsError, MemberNotFoundError):
        session.rollback()
        raise
    except IntegrityError as e:
        session.rollback()
        if "email" in str(e).lower():
            raise MemberAlreadyExistsError("email", update_data.get("email", ""))
        elif "phone" in str(e).lower():
            raise MemberAlreadyExistsError("phone", update_data.get("phone", ""))
        else:
            raise DatabaseOperationError("update_member", "Constraint violation")
    except Exception as e:
        session.rollback()
        raise DatabaseOperationError("update_member", str(e))


def delete_member(session: Session, member_id: int) -> bool:
    """
    Delete a member by ID.
    
    Args:
        session: Database session
        member_id: ID of member to delete
        
    Returns:
        bool: True if deleted successfully
        
    Raises:
        MemberNotFoundError: If member doesn't exist
        DatabaseOperationError: If database operation fails
    """
    try:
        existing_member = get_member_by_id(session, member_id)
        if not existing_member:
            raise MemberNotFoundError("id", str(member_id))
        
        session.delete(existing_member)
        session.commit()
        
        return True
        
    except MemberNotFoundError:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise DatabaseOperationError("delete_member", str(e)) 