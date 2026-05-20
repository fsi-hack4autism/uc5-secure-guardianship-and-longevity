"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from database import get_db
from models import User
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SignUpRequest(BaseModel):
    """Sign up request"""
    email: EmailStr
    password: str
    user_type: str  # 'beneficiary', 'guardian', 'advisor'
    full_name: str


class SignInRequest(BaseModel):
    """Sign in request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    user_type: str


def hash_password(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, user_type: str, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiration_hours)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": str(user_id),
        "user_type": user_type,
        "exp": expire,
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    """User registration"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate user type
    if request.user_type not in ["beneficiary", "guardian", "advisor"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user type"
        )
    
    # Create new user
    new_user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        user_type=request.user_type,
        is_active=True,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.user_id} ({request.user_type})")
    
    # Generate token
    access_token = create_access_token(new_user.user_id, new_user.user_type)
    
    return TokenResponse(
        access_token=access_token,
        user_id=str(new_user.user_id),
        user_type=new_user.user_type,
    )


@router.post("/signin", response_model=TokenResponse)
async def signin(request: SignInRequest, db: Session = Depends(get_db)):
    """User login"""
    
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    logger.info(f"User signed in: {user.user_id}")
    
    # Generate token
    access_token = create_access_token(user.user_id, user.user_type)
    
    return TokenResponse(
        access_token=access_token,
        user_id=str(user.user_id),
        user_type=user.user_type,
    )


@router.post("/refresh")
async def refresh_token(current_user_id: str = Depends(get_current_user)):
    """Refresh access token"""
    user = db.query(User).filter(User.user_id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    access_token = create_access_token(user.user_id, user.user_type)
    return TokenResponse(access_token=access_token)


def get_current_user(token: str = None) -> str:
    """Get current user from JWT token"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
