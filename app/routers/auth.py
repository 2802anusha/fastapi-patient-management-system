from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse

# Create a router for authentication-related endpoints
router = APIRouter()


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')


@router.post('/signup', response_model=UserResponse, status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='Username already exists')

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail='Email already registered')

    # Hash the password before storing
    hashed_password = hash_password(user.password)

    # Create new user with hashed password
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # refresh to get the auto-generated id

    return new_user
