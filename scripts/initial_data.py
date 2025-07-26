#!/usr/bin/env python3
"""
Initial data script for Python Jogja Member API.

This script populates the database with sample member data for development
and demonstration purposes. It can be run standalone or imported as a module.

Usage:
    python scripts/initial_data.py
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path so we can import app modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session
from app.database import get_engine, create_db_and_tables
from app.models import MemberCreate
from app import crud
from app.exceptions import MemberAlreadyExistsError


# Sample member data for development
SAMPLE_MEMBERS = [
    {
        "name": "Andi Pratama",
        "email": "andi.pratama@jogja.dev",
        "phone": "+62812345671"
    },
    {
        "name": "Siti Nurhaliza",
        "email": "siti.nurhaliza@python-jogja.org",
        "phone": "+62812345672"
    },
    {
        "name": "Budi Santoso",
        "email": "budi.santoso@gmail.com",
        "phone": "+62812345673"
    },
    {
        "name": "Maya Sari",
        "email": "maya.sari@yahoo.com",
        "phone": None  # Member without phone
    },
    {
        "name": "Rizki Ramadhan",
        "email": "rizki.ramadhan@outlook.com",
        "phone": "+62812345674"
    },
    {
        "name": "Indira Kusuma",
        "email": "indira.kusuma@python.id",
        "phone": None  # Another member without phone
    },
    {
        "name": "Fajar Nugroho",
        "email": "fajar.nugroho@dev.co.id",
        "phone": "+62812345675"
    },
    {
        "name": "Dewi Lestari",
        "email": "dewi.lestari@jogja.ac.id",
        "phone": "+62812345676"
    },
    {
        "name": "Agus Wijaya",
        "email": "agus.wijaya@tech.com",
        "phone": "+62812345677"
    },
    {
        "name": "Rina Amelia",
        "email": "rina.amelia@startup.id",
        "phone": None  # Third member without phone
    }
]


def create_sample_members(session: Session) -> None:
    """
    Create sample members in the database.
    
    Args:
        session: Database session
    """
    created_count = 0
    skipped_count = 0
    
    print("Creating sample members...")
    print("-" * 50)
    
    for member_data in SAMPLE_MEMBERS:
        try:
            member_create = MemberCreate(**member_data)
            created_member = crud.create_member(session, member_create)
            
            print(f"✅ Created: {created_member.name} ({created_member.email})")
            created_count += 1
            
        except MemberAlreadyExistsError as e:
            print(f"⚠️  Skipped: {member_data['name']} - {e.detail}")
            skipped_count += 1
            
        except Exception as e:
            print(f"❌ Error creating {member_data['name']}: {str(e)}")
    
    print("-" * 50)
    print(f"Summary: {created_count} created, {skipped_count} skipped")


def list_all_members(session: Session) -> None:
    """
    List all members in the database.
    
    Args:
        session: Database session
    """
    try:
        members = crud.get_all_members(session)
        
        print(f"\nCurrent members in database ({len(members)} total):")
        print("-" * 70)
        print(f"{'ID':<3} | {'Name':<20} | {'Email':<30} | {'Phone':<15}")
        print("-" * 70)
        
        for member in members:
            phone_display = member.phone or "N/A"
            print(f"{member.id:<3} | {member.name:<20} | {member.email:<30} | {phone_display:<15}")
        
        print("-" * 70)
        
    except Exception as e:
        print(f"Error listing members: {str(e)}")


def clear_all_members(session: Session) -> None:
    """
    Clear all members from the database (for testing purposes).
    
    Args:
        session: Database session
    """
    try:
        members = crud.get_all_members(session)
        deleted_count = 0
        
        print("Clearing all members...")
        for member in members:
            crud.delete_member(session, member.id)
            deleted_count += 1
        
        print(f"✅ Deleted {deleted_count} members")
        
    except Exception as e:
        print(f"Error clearing members: {str(e)}")


def main():
    """Main function to run the initial data script."""
    print("Python Jogja Member API - Initial Data Script")
    print("=" * 50)
    
    # Initialize database
    try:
        create_db_and_tables()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        return 1
    
    # Create database session
    engine = get_engine()
    
    with Session(engine) as session:
        # Check if we should clear existing data
        if len(sys.argv) > 1 and sys.argv[1] == "--clear":
            clear_all_members(session)
            print()
        
        # Create sample members
        create_sample_members(session)
        
        # List all members
        list_all_members(session)
    
    print("\n✅ Initial data script completed!")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1) 