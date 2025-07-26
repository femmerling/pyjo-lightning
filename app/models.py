"""
Data models for Python Jogja Member API.

This module defines:
- Member SQLModel for database representation
- MemberCreate for API input validation
- MemberResponse for API output serialization

Following guardrails.md, we keep models simple without complex validators
and handle business logic validation in the CRUD layer.
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel


class MemberBase(SQLModel):
    """Base model with common Member fields."""
    name: str = Field(description="Member's full name", max_length=100)
    email: str = Field(description="Member's email address", max_length=254)
    phone: Optional[str] = Field(default=None, description="Member's phone number", max_length=20)


class Member(MemberBase, table=True):
    """
    Member database model.
    
    Represents a Python Jogja community member with basic contact information.
    Enforces uniqueness constraints on email and phone at the database level.
    """
    __tablename__ = "members"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="Unique member identifier")
    email: str = Field(unique=True, index=True, description="Unique email address")
    phone: Optional[str] = Field(default=None, unique=True, index=True, description="Unique phone number")


class MemberCreate(MemberBase):
    """
    Model for creating new members via API.
    
    Used for request validation when adding new members.
    Does not include the 'id' field as it's auto-generated.
    """
    pass


class MemberResponse(MemberBase):
    """
    Model for member API responses.
    
    Used for serializing member data in API responses.
    Includes the auto-generated 'id' field.
    """
    id: int = Field(description="Unique member identifier")
    
    class Config:
        from_attributes = True  # Enables ORM mode for SQLModel compatibility


class MemberUpdate(BaseModel):
    """
    Model for updating existing members.
    
    All fields are optional to support partial updates.
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, min_length=1, max_length=254)
    phone: Optional[str] = Field(default=None, max_length=20) 