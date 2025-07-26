"""
Unit tests for Python Jogja Member API.

This module tests the CRUD operations and business logic using unittest
framework with in-memory SQLite databases for complete isolation.

Following testing.md guidelines:
- unittest framework for simplicity
- Fresh in-memory SQLite database per test
- Given-When-Then structure
- Focus on business logic testing
"""

import unittest
from sqlmodel import create_engine, Session, SQLModel
from typing import Optional

from app.models import Member, MemberCreate, MemberUpdate
from app import crud
from app.exceptions import (
    MemberAlreadyExistsError,
    MemberNotFoundError,
    InvalidMemberDataError,
    DatabaseOperationError
)
from app.validation import validate_name, validate_email, validate_phone, validate_member_data


class TestMemberValidation(unittest.TestCase):
    """Test validation functions."""
    
    def test_validate_name_successfully(self):
        """Test successful name validation."""
        # Given
        valid_name = "John Doe"
        
        # When
        result = validate_name(valid_name)
        
        # Then
        self.assertEqual(result, "John Doe")
    
    def test_validate_name_trims_whitespace(self):
        """Test name validation trims whitespace."""
        # Given
        name_with_whitespace = "  Jane Smith  "
        
        # When
        result = validate_name(name_with_whitespace)
        
        # Then
        self.assertEqual(result, "Jane Smith")
    
    def test_validate_name_rejects_empty(self):
        """Test name validation rejects empty names."""
        # Given
        empty_name = ""
        
        # When/Then
        with self.assertRaises(InvalidMemberDataError) as context:
            validate_name(empty_name)
        
        self.assertEqual(context.exception.field, "name")
    
    def test_validate_name_rejects_too_short(self):
        """Test name validation rejects names that are too short."""
        # Given
        short_name = "A"
        
        # When/Then
        with self.assertRaises(InvalidMemberDataError) as context:
            validate_name(short_name)
        
        self.assertEqual(context.exception.field, "name")
    
    def test_validate_email_successfully(self):
        """Test successful email validation."""
        # Given
        valid_email = "john.doe@example.com"
        
        # When
        result = validate_email(valid_email)
        
        # Then
        self.assertEqual(result, "john.doe@example.com")
    
    def test_validate_email_converts_to_lowercase(self):
        """Test email validation converts to lowercase."""
        # Given
        uppercase_email = "JOHN.DOE@EXAMPLE.COM"
        
        # When
        result = validate_email(uppercase_email)
        
        # Then
        self.assertEqual(result, "john.doe@example.com")
    
    def test_validate_email_rejects_invalid_format(self):
        """Test email validation rejects invalid formats."""
        # Given
        invalid_email = "not-an-email"
        
        # When/Then
        with self.assertRaises(InvalidMemberDataError) as context:
            validate_email(invalid_email)
        
        self.assertEqual(context.exception.field, "email")
    
    def test_validate_phone_successfully(self):
        """Test successful phone validation."""
        # Given
        valid_phone = "+1-234-567-8901"
        
        # When
        result = validate_phone(valid_phone)
        
        # Then
        self.assertEqual(result, "+1-234-567-8901")
    
    def test_validate_phone_handles_none(self):
        """Test phone validation handles None values."""
        # Given
        none_phone = None
        
        # When
        result = validate_phone(none_phone)
        
        # Then
        self.assertIsNone(result)
    
    def test_validate_phone_rejects_invalid_characters(self):
        """Test phone validation rejects invalid characters."""
        # Given
        invalid_phone = "123-abc-7890"
        
        # When/Then
        with self.assertRaises(InvalidMemberDataError) as context:
            validate_phone(invalid_phone)
        
        self.assertEqual(context.exception.field, "phone")


class TestMemberCRUD(unittest.TestCase):
    """Test CRUD operations for members."""
    
    def setUp(self):
        """Set up each test with a fresh in-memory database."""
        self.engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)
    
    def tearDown(self):
        """Clean up after each test."""
        self.session.close()
    
    def test_create_member_successfully(self):
        """Test successful member creation."""
        # Given
        member_data = MemberCreate(
            name="John Doe",
            email="john.doe@example.com",
            phone="+1234567890"
        )
        
        # When
        created_member = crud.create_member(self.session, member_data)
        
        # Then
        self.assertIsNotNone(created_member.id)
        self.assertEqual(created_member.name, "John Doe")
        self.assertEqual(created_member.email, "john.doe@example.com")
        self.assertEqual(created_member.phone, "+1234567890")
    
    def test_create_member_without_phone(self):
        """Test creating member without phone number."""
        # Given
        member_data = MemberCreate(
            name="Jane Smith",
            email="jane.smith@example.com"
        )
        
        # When
        created_member = crud.create_member(self.session, member_data)
        
        # Then
        self.assertIsNotNone(created_member.id)
        self.assertEqual(created_member.name, "Jane Smith")
        self.assertEqual(created_member.email, "jane.smith@example.com")
        self.assertIsNone(created_member.phone)
    
    def test_create_member_email_already_exists(self):
        """Test creating member with existing email raises error."""
        # Given
        first_member = MemberCreate(
            name="John Doe",
            email="john.doe@example.com"
        )
        crud.create_member(self.session, first_member)
        
        second_member = MemberCreate(
            name="Jane Doe",
            email="john.doe@example.com"  # Same email
        )
        
        # When/Then
        with self.assertRaises(MemberAlreadyExistsError) as context:
            crud.create_member(self.session, second_member)
        
        self.assertEqual(context.exception.field, "email")
        self.assertEqual(context.exception.value, "john.doe@example.com")
    
    def test_create_member_phone_already_exists(self):
        """Test creating member with existing phone raises error."""
        # Given
        first_member = MemberCreate(
            name="John Doe",
            email="john.doe@example.com",
            phone="+1234567890"
        )
        crud.create_member(self.session, first_member)
        
        second_member = MemberCreate(
            name="Jane Smith",
            email="jane.smith@example.com",
            phone="+1234567890"  # Same phone
        )
        
        # When/Then
        with self.assertRaises(MemberAlreadyExistsError) as context:
            crud.create_member(self.session, second_member)
        
        self.assertEqual(context.exception.field, "phone")
        self.assertEqual(context.exception.value, "+1234567890")
    
    def test_create_member_invalid_name(self):
        """Test creating member with invalid name raises error."""
        # Given
        member_data = MemberCreate(
            name="",  # Invalid empty name
            email="john.doe@example.com"
        )
        
        # When/Then
        with self.assertRaises(InvalidMemberDataError) as context:
            crud.create_member(self.session, member_data)
        
        self.assertEqual(context.exception.field, "name")
    
    def test_create_member_invalid_email(self):
        """Test creating member with invalid email raises error."""
        # Given
        member_data = MemberCreate(
            name="John Doe",
            email="not-an-email"  # Invalid email format
        )
        
        # When/Then
        with self.assertRaises(InvalidMemberDataError) as context:
            crud.create_member(self.session, member_data)
        
        self.assertEqual(context.exception.field, "email")
    
    def test_get_member_by_id_successfully(self):
        """Test successful member retrieval by ID."""
        # Given
        member_data = MemberCreate(
            name="John Doe",
            email="john.doe@example.com"
        )
        created_member = crud.create_member(self.session, member_data)
        
        # When
        retrieved_member = crud.get_member_by_id(self.session, created_member.id)
        
        # Then
        self.assertIsNotNone(retrieved_member)
        self.assertEqual(retrieved_member.id, created_member.id)
        self.assertEqual(retrieved_member.name, "John Doe")
        self.assertEqual(retrieved_member.email, "john.doe@example.com")
    
    def test_get_member_by_id_not_found(self):
        """Test member retrieval with non-existent ID returns None."""
        # Given
        non_existent_id = 999
        
        # When
        result = crud.get_member_by_id(self.session, non_existent_id)
        
        # Then
        self.assertIsNone(result)
    
    def test_get_member_by_email_successfully(self):
        """Test successful member retrieval by email."""
        # Given
        member_data = MemberCreate(
            name="John Doe",
            email="john.doe@example.com"
        )
        created_member = crud.create_member(self.session, member_data)
        
        # When
        retrieved_member = crud.get_member_by_email(self.session, "john.doe@example.com")
        
        # Then
        self.assertIsNotNone(retrieved_member)
        self.assertEqual(retrieved_member.id, created_member.id)
        self.assertEqual(retrieved_member.email, "john.doe@example.com")
    
    def test_get_member_by_email_case_insensitive(self):
        """Test member retrieval by email is case insensitive."""
        # Given
        member_data = MemberCreate(
            name="John Doe",
            email="john.doe@example.com"
        )
        created_member = crud.create_member(self.session, member_data)
        
        # When
        retrieved_member = crud.get_member_by_email(self.session, "JOHN.DOE@EXAMPLE.COM")
        
        # Then
        self.assertIsNotNone(retrieved_member)
        self.assertEqual(retrieved_member.id, created_member.id)
    
    def test_get_member_by_phone_successfully(self):
        """Test successful member retrieval by phone."""
        # Given
        member_data = MemberCreate(
            name="John Doe",
            email="john.doe@example.com",
            phone="+1234567890"
        )
        created_member = crud.create_member(self.session, member_data)
        
        # When
        retrieved_member = crud.get_member_by_phone(self.session, "+1234567890")
        
        # Then
        self.assertIsNotNone(retrieved_member)
        self.assertEqual(retrieved_member.id, created_member.id)
        self.assertEqual(retrieved_member.phone, "+1234567890")
    
    def test_get_all_members_successfully(self):
        """Test successful retrieval of all members."""
        # Given
        member1 = MemberCreate(name="John Doe", email="john@example.com")
        member2 = MemberCreate(name="Jane Smith", email="jane@example.com")
        
        crud.create_member(self.session, member1)
        crud.create_member(self.session, member2)
        
        # When
        all_members = crud.get_all_members(self.session)
        
        # Then
        self.assertEqual(len(all_members), 2)
        emails = [member.email for member in all_members]
        self.assertIn("john@example.com", emails)
        self.assertIn("jane@example.com", emails)
    
    def test_get_all_members_with_pagination(self):
        """Test member retrieval with pagination."""
        # Given
        for i in range(5):
            member_data = MemberCreate(
                name=f"Member {i}",
                email=f"member{i}@example.com"
            )
            crud.create_member(self.session, member_data)
        
        # When
        paginated_members = crud.get_all_members(self.session, skip=2, limit=2)
        
        # Then
        self.assertEqual(len(paginated_members), 2)
    
    def test_update_member_successfully(self):
        """Test successful member update."""
        # Given
        member_data = MemberCreate(
            name="John Doe",
            email="john.doe@example.com"
        )
        created_member = crud.create_member(self.session, member_data)
        
        update_data = MemberUpdate(name="John Smith")
        
        # When
        updated_member = crud.update_member(self.session, created_member.id, update_data)
        
        # Then
        self.assertEqual(updated_member.id, created_member.id)
        self.assertEqual(updated_member.name, "John Smith")
        self.assertEqual(updated_member.email, "john.doe@example.com")  # Unchanged
    
    def test_update_member_not_found(self):
        """Test updating non-existent member raises error."""
        # Given
        non_existent_id = 999
        update_data = MemberUpdate(name="John Smith")
        
        # When/Then
        with self.assertRaises(MemberNotFoundError) as context:
            crud.update_member(self.session, non_existent_id, update_data)
        
        self.assertEqual(context.exception.identifier, "id")
        self.assertEqual(context.exception.value, "999")
    
    def test_delete_member_successfully(self):
        """Test successful member deletion."""
        # Given
        member_data = MemberCreate(
            name="John Doe",
            email="john.doe@example.com"
        )
        created_member = crud.create_member(self.session, member_data)
        
        # When
        result = crud.delete_member(self.session, created_member.id)
        
        # Then
        self.assertTrue(result)
        
        # Verify member is deleted
        deleted_member = crud.get_member_by_id(self.session, created_member.id)
        self.assertIsNone(deleted_member)
    
    def test_delete_member_not_found(self):
        """Test deleting non-existent member raises error."""
        # Given
        non_existent_id = 999
        
        # When/Then
        with self.assertRaises(MemberNotFoundError) as context:
            crud.delete_member(self.session, non_existent_id)
        
        self.assertEqual(context.exception.identifier, "id")
        self.assertEqual(context.exception.value, "999")


class TestMemberBusinessLogic(unittest.TestCase):
    """Test business logic scenarios and edge cases."""
    
    def setUp(self):
        """Set up each test with a fresh in-memory database."""
        self.engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)
    
    def tearDown(self):
        """Clean up after each test."""
        self.session.close()
    
    def test_email_normalization_prevents_duplicates(self):
        """Test email normalization prevents case-sensitive duplicates."""
        # Given
        member1 = MemberCreate(name="John Doe", email="john@example.com")
        crud.create_member(self.session, member1)
        
        member2 = MemberCreate(name="Jane Doe", email="JOHN@EXAMPLE.COM")
        
        # When/Then
        with self.assertRaises(MemberAlreadyExistsError):
            crud.create_member(self.session, member2)
    
    def test_phone_uniqueness_only_when_provided(self):
        """Test phone uniqueness is only enforced when phone is provided."""
        # Given
        member1 = MemberCreate(name="John Doe", email="john@example.com")  # No phone
        member2 = MemberCreate(name="Jane Smith", email="jane@example.com")  # No phone
        
        # When
        created_member1 = crud.create_member(self.session, member1)
        created_member2 = crud.create_member(self.session, member2)
        
        # Then
        self.assertIsNotNone(created_member1.id)
        self.assertIsNotNone(created_member2.id)
        self.assertIsNone(created_member1.phone)
        self.assertIsNone(created_member2.phone)
    
    def test_data_trimming_and_normalization(self):
        """Test data is properly trimmed and normalized."""
        # Given
        member_data = MemberCreate(
            name="  John Doe  ",
            email="  JOHN.DOE@EXAMPLE.COM  ",
            phone="  +1234567890  "
        )
        
        # When
        created_member = crud.create_member(self.session, member_data)
        
        # Then
        self.assertEqual(created_member.name, "John Doe")
        self.assertEqual(created_member.email, "john.doe@example.com")
        self.assertEqual(created_member.phone, "+1234567890")


if __name__ == "__main__":
    unittest.main() 