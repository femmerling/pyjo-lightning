"""
Database configuration and session management for Python Jogja Member API.

This module provides:
- SQLite database engine configuration
- Session management with dependency injection
- Database initialization utilities
"""

from typing import Generator
from sqlmodel import SQLModel, Session, create_engine
from functools import lru_cache
import os


@lru_cache()
def get_database_url() -> str:
    """
    Get database URL from environment or use default SQLite.
    
    Returns:
        str: Database URL for SQLAlchemy engine
    """
    return os.getenv("DATABASE_URL", "sqlite:///./pyjo_members.db")


@lru_cache()
def get_engine():
    """
    Create and cache SQLAlchemy engine.
    
    Returns:
        Engine: SQLAlchemy engine instance
    """
    database_url = get_database_url()
    
    # For SQLite, we need to enable foreign key constraints
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    
    engine = create_engine(
        database_url,
        connect_args=connect_args,
        echo=False  # Set to True for SQL logging in development
    )
    
    return engine


def create_db_and_tables() -> None:
    """
    Create database tables from SQLModel models.
    Should be called once at application startup.
    """
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides database sessions.
    
    Yields:
        Session: SQLModel session instance
        
    This dependency will:
    - Create a new session for each request
    - Automatically close the session after the request
    - Handle session rollback on exceptions
    """
    engine = get_engine()
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close() 