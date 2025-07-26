# Requirements: Python Jogja Member Management API - Add New Member

## 1. Feature Description

As a Python Jogja community organizer, I want to add new members to our database, so that we can keep track of our community growth and communicate with them.

## 2. Data Model (`Member`)

The `Member` entity will have the following structure:

* `id`: Primary Key, Integer, Auto-increment (Optional, handled by SQLModel)
* `name`: String, Required
* `email`: String, Required, Unique, Valid Email Format
* `phone`: String, Optional, Unique (if provided)

## 3. Business Logic

When a request to add a new member is received:
* **Uniqueness Check:**
    * If the provided `email` already exists in the database, the request should be rejected.
    * If the provided `phone` (and it's not null) already exists in the database, the request should be rejected.
* **Creation:** If all validations pass, a new `Member` record should be created in the database.

## 4. Validation

* **Client-side:** (Not in scope for API, but assumed basic validation)
* **API (Pydantic):**
    * `name`: Must be a non-empty string.
    * `email`: Must be a valid email format and a non-empty string.
    * `phone`: Must be a string (optional).
* **Database-side (Business Logic):**
    * `email`: Enforce uniqueness.
    * `phone`: Enforce uniqueness (if provided).

## 5. API Endpoint

* **Method:** `POST`
* **Path:** `/members/`
* **Request Body:** JSON object conforming to the `MemberCreate` schema (derived from `Member` model, perhaps excluding `id`).
* **Success Response:** `201 Created` with the newly created `Member` object.
* **Error Responses:**
    * `400 Bad Request`: For invalid input format (Pydantic validation errors).
    * `409 Conflict`: If email or phone already exists.
    * `500 Internal Server Error`: For unexpected server issues.

## 6. Sequence Diagram

```plantuml
@startuml
autonumber
actor Client
participant "FastAPI App" as API
participant "SQLModel/SQLAlchemy" as ORM
participant "Database" as DB

Client -> API: POST /members/ (new_member_data)
activate API

API -> API: Validate input (Pydantic)
alt Input Invalid
    API --x Client: 400 Bad Request (Validation Error)
else Input Valid
    API -> ORM: Query Member by email
    activate ORM
    ORM -> DB: SELECT * FROM member WHERE email = :email
    activate DB
    DB --> ORM: Query Result (existing_member_by_email)
    deactivate DB
    ORM --> API: existing_member_by_email
    deactivate ORM

    alt Email Exists
        API --x Client: 409 Conflict (Email already registered)
    else Email Unique
        API -> ORM: Query Member by phone (if provided)
        activate ORM
        ORM -> DB: SELECT * FROM member WHERE phone = :phone
        activate DB
        DB --> ORM: Query Result (existing_member_by_phone)
        deactivate DB
        ORM --> API: existing_member_by_phone
        deactivate ORM

        alt Phone Exists
            API --x Client: 409 Conflict (Phone already registered)
        else Phone Unique (or not provided)
            API -> ORM: Create new Member object
            API -> ORM: Add Member to session
            activate ORM
            ORM -> DB: INSERT INTO member (name, email, phone) VALUES (...)
            activate DB
            DB --> ORM: New Member ID
            deactivate DB
            ORM --> API: Created Member object
            deactivate ORM
            API --> Client: 201 Created (new_member_data_with_id)
        end
    end
end
deactivate API
@enduml
```
