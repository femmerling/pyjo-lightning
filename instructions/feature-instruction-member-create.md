# Feature Implementation Guide: Member Creation API

**Target Audience**: Future LLMs working on this codebase  
**Feature**: POST /members/ endpoint and related member management functionality  
**Last Updated**: 2024

---

## 🎯 **Overview**

This document explains the implementation patterns and architectural decisions for the Python Jogja Member API, specifically focusing on the member creation feature. Follow these patterns when extending or modifying the codebase.

---

## 🏗️ **Architecture Pattern**

### **Core Principle: Layered Validation Architecture**

This project uses a **layered validation approach** to avoid SQLModel/Pydantic conflicts:

```
1. Pydantic Models (Basic Type/Length Validation)
   ↓
2. Business Logic Layer (Complex Validation)
   ↓  
3. Database Layer (Constraints & Persistence)
```

**Why This Pattern?**
- Avoids SQLModel/Pydantic validator conflicts that cause mapping errors
- Provides better separation of concerns
- Enables more detailed error handling
- Allows for complex business rules without framework limitations

---

## 📁 **File Organization Pattern**

### **Strict Module Separation**
```
app/
├── models.py          # ONLY data structures, NO validation logic
├── validation.py      # ALL business logic validation functions
├── exceptions.py      # Custom exception hierarchy
├── crud.py           # Database operations + business logic
├── main.py           # FastAPI app + endpoints + exception handlers
└── database.py       # Database configuration + dependency injection
```

**Critical Rule**: Never mix concerns between files. Each file has ONE responsibility.

---

## 🔄 **Implementation Sequence Pattern**

### **For Any CRUD Operation, Follow This Exact Sequence:**

#### **1. Define Data Models (models.py)**
```python
# ✅ KEEP SIMPLE - Only basic Field constraints
class MemberBase(SQLModel):
    name: str = Field(max_length=100)  # NO min_length, NO complex validators
    email: str = Field(max_length=254)
    phone: Optional[str] = Field(default=None, max_length=20)

class Member(MemberBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)  # Database constraints only
    phone: Optional[str] = Field(default=None, unique=True, index=True)

class MemberCreate(MemberBase):
    pass  # Input validation model

class MemberResponse(MemberBase):
    id: int
    class Config:
        from_attributes = True
```

#### **2. Create Custom Exceptions (exceptions.py)**
```python
# ✅ SPECIFIC exceptions for each business rule violation
class MemberAlreadyExistsError(MemberAPIException):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        # Generic message for production security
        detail = f"A member with this {field} is already registered"
        super().__init__(message, detail)
```

#### **3. Implement Validation Functions (validation.py)**
```python
# ✅ PURE functions that validate and normalize
def validate_email(email: str) -> str:
    # 1. Type/null checks
    # 2. Normalize (strip, lowercase)
    # 3. Business rules validation
    # 4. Return normalized value
    # 5. Raise InvalidMemberDataError on failure
```

#### **4. Create CRUD Operations (crud.py)**
```python
# ✅ FOLLOW exact sequence from requirements.md
def create_member(session: Session, member_data: MemberCreate) -> Member:
    try:
        # Step 1: Validate input data
        validated_name, validated_email, validated_phone = validate_member_data(...)
        
        # Step 2: Check email uniqueness
        existing_member_by_email = get_member_by_email(session, validated_email)
        if existing_member_by_email:
            raise MemberAlreadyExistsError("email", validated_email)
        
        # Step 3: Check phone uniqueness (if provided)
        if validated_phone:
            existing_member_by_phone = get_member_by_phone(session, validated_phone)
            if existing_member_by_phone:
                raise MemberAlreadyExistsError("phone", validated_phone)
        
        # Step 4: Create and save
        new_member = Member(name=validated_name, email=validated_email, phone=validated_phone)
        session.add(new_member)
        session.commit()
        session.refresh(new_member)
        return new_member
        
    except (InvalidMemberDataError, MemberAlreadyExistsError):
        session.rollback()
        raise  # Re-raise business logic exceptions
    except IntegrityError as e:
        session.rollback()
        # Convert database errors to business logic exceptions
        if "email" in str(e).lower():
            raise MemberAlreadyExistsError("email", validated_email)
    except Exception as e:
        session.rollback()
        raise DatabaseOperationError("create_member", str(e))
```

#### **5. Create API Endpoints (main.py)**
```python
# ✅ THIN controllers - delegate to CRUD layer
@app.post("/members/", response_model=MemberResponse, status_code=201)
async def create_member(
    member_data: MemberCreate,
    session: Session = Depends(get_session)
) -> MemberResponse:
    try:
        new_member = crud.create_member(session, member_data)
        return MemberResponse.from_orm(new_member)
    except (MemberAlreadyExistsError, InvalidMemberDataError, DatabaseOperationError):
        raise  # Let exception handlers convert to HTTP responses
```

#### **6. Add Exception Handlers (main.py)**
```python
# ✅ CONVERT business exceptions to HTTP responses
@app.exception_handler(MemberAlreadyExistsError)
async def member_already_exists_handler(request, exc: MemberAlreadyExistsError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.detail, "field": exc.field, "error_type": "conflict"}
    )
```

---

## ✅ **Testing Pattern**

### **Use unittest + In-Memory SQLite**
```python
class TestMemberCRUD(unittest.TestCase):
    def setUp(self):
        # ✅ FRESH database per test
        self.engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)
    
    def tearDown(self):
        self.session.close()
    
    def test_create_member_successfully(self):
        # ✅ GIVEN-WHEN-THEN structure
        # Given
        member_data = MemberCreate(name="John Doe", email="john@example.com")
        
        # When
        created_member = crud.create_member(self.session, member_data)
        
        # Then
        self.assertIsNotNone(created_member.id)
        self.assertEqual(created_member.email, "john@example.com")
```

### **Test Categories to Always Include**
1. **Validation Tests** - Test each validation function independently
2. **CRUD Tests** - Test database operations with fresh data
3. **Business Logic Tests** - Test edge cases and complex scenarios
4. **Error Handling Tests** - Test all exception paths

---

## 🚨 **Critical Guardrails**

### **❌ NEVER Do These Things**

1. **Don't use complex Pydantic validators in SQLModel classes**
   ```python
   # ❌ BAD - Causes SQLModel mapping errors
   class Member(SQLModel, table=True):
       email: str = Field(..., validator=complex_email_validator)
   ```

2. **Don't put business logic in models**
   ```python
   # ❌ BAD - Models should be data structures only
   class Member(SQLModel, table=True):
       def validate_email(self):  # Business logic doesn't belong here
   ```

3. **Don't use raw SQL**
   ```python
   # ❌ BAD - Security risk, breaks ORM
   session.execute("SELECT * FROM members WHERE email = ?", email)
   ```

4. **Don't expose internal errors in production**
   ```python
   # ❌ BAD - Exposes internal details
   raise HTTPException(500, detail=str(database_exception))
   ```

### **✅ ALWAYS Do These Things**

1. **Validate in business logic layer**
2. **Use specific exception types**
3. **Normalize data (lowercase emails, trim whitespace)**
4. **Handle database rollbacks on errors**
5. **Use dependency injection for database sessions**
6. **Write comprehensive tests with fresh databases**

---

## 🔧 **Extension Patterns**

### **Adding New Validation Rules**
1. Add validation function to `validation.py`
2. Update `validate_member_data()` to call it
3. Add specific exception to `exceptions.py` if needed
4. Write tests for the new validation

### **Adding New Endpoints**
1. Create new Pydantic models in `models.py` if needed
2. Add CRUD function to `crud.py`
3. Add endpoint to `main.py`
4. Add exception handlers if new exceptions
5. Write comprehensive tests

### **Adding New Business Rules**
1. Create validation function in `validation.py`
2. Update CRUD operations to use it
3. Add appropriate exception handling
4. Update tests to cover new scenarios

---

## 📋 **Validation Implementation Checklist**

When implementing any new validation:

- [ ] ✅ Function is pure (no side effects)
- [ ] ✅ Handles null/empty inputs appropriately
- [ ] ✅ Normalizes data (trim, lowercase, etc.)
- [ ] ✅ Uses specific exception types
- [ ] ✅ Has comprehensive error messages
- [ ] ✅ Follows consistent parameter patterns
- [ ] ✅ Returns normalized data
- [ ] ✅ Has corresponding unit tests
- [ ] ✅ Documented with clear docstrings

---

## 🎯 **Key Success Factors**

1. **Separation of Concerns**: Each layer has ONE responsibility
2. **Consistent Error Handling**: Always use custom exceptions → HTTP responses
3. **Data Normalization**: Always normalize input data consistently
4. **Database Safety**: Always handle rollbacks and constraints
5. **Type Safety**: Use type hints everywhere
6. **Test Coverage**: Test all paths, especially error conditions

---

## 📚 **Reference Implementation**

For the complete implementation example, see:
- `app/crud.py:create_member()` - Perfect CRUD pattern
- `app/validation.py:validate_email()` - Perfect validation pattern
- `tests/test_members.py:TestMemberCRUD` - Perfect testing pattern

**Follow these patterns exactly for consistency and reliability.**

---

*This guide ensures future development maintains the same high-quality patterns and architectural consistency established in the initial implementation.* 