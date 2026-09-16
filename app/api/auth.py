import re
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.database.db import db_manager

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

class LoginRequest(BaseModel):
    email: str = Field(..., example="cibinjool08@gmail.com")
    password: str = Field(..., example="password123")

class RegisterRequest(BaseModel):
    email: str = Field(..., example="cibinjool08@gmail.com")
    password: str = Field(..., example="password123")
    full_name: Optional[str] = Field(None, example="cibinjool08")
    role: Optional[str] = Field("Senior Analyst", example="Senior Analyst")
    organization: Optional[str] = Field("TerraScope Intelligence Lab", example="TerraScope Intelligence Lab")

def validate_email_format(email: str):
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

@router.post("/login")
def login_endpoint(payload: LoginRequest):
    email = payload.email.strip() if payload.email else ""
    password = payload.password if payload.password else ""

    if not email or not validate_email_format(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid email address."
        )

    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required."
        )

    user = db_manager.authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    session_token = f"ts_session_{uuid.uuid4().hex}"
    return {
        "success": True,
        "message": "Authentication successful.",
        "user": user,
        "token": session_token
    }

@router.post("/register")
def register_endpoint(payload: RegisterRequest):
    email = payload.email.strip() if payload.email else ""
    password = payload.password if payload.password else ""
    full_name = payload.full_name.strip() if payload.full_name else ""

    if not email or not validate_email_format(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid email address."
        )

    if not password or len(password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 4 characters long."
        )

    if not full_name:
        full_name = email.split('@')[0]

    existing_user = db_manager.get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please sign in instead."
        )

    created_user = db_manager.create_user(
        email=email,
        password=password,
        full_name=full_name,
        role=payload.role or "Senior Analyst",
        organization=payload.organization or "TerraScope Intelligence Lab"
    )

    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user account. Please try again."
        )

    created_user["name"] = created_user["full_name"]
    session_token = f"ts_session_{uuid.uuid4().hex}"
    return {
        "success": True,
        "message": "Account created successfully.",
        "user": created_user,
        "token": session_token
    }

@router.get("/me")
def current_user_endpoint():
    return {
        "status": "AUTH_ACTIVE",
        "service": "TerraScope AI SQLite Auth Engine"
    }
