from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
from ..models.schemas import (
    LoginRequest, RegisterRequest, LoginResponse, 
    User, APIResponse, UserPreferences
)
from ..models.database import db
from ..core.security import verify_password, get_password_hash, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = db.get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return user without password
    return User(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        preferences=user.preferences
    )


@router.post("/register", response_model=APIResponse)
async def register(request: RegisterRequest):
    # Check if user already exists
    if db.get_user_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(request.password)
    user = db.create_user(
        email=request.email,
        password=hashed_password,
        name=request.name
    )
    
    # Generate token
    token = create_access_token({"user_id": user.id})
    
    # Return user without password
    user_response = User(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        preferences=user.preferences
    )
    
    return APIResponse(
        success=True,
        data={
            "user": user_response.model_dump(),
            "token": token
        }
    )


@router.post("/login", response_model=APIResponse)
async def login(request: LoginRequest):
    # Find user
    user = db.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate token
    token = create_access_token({"user_id": user.id})
    
    # Return user without password
    user_response = User(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        preferences=user.preferences
    )
    
    return APIResponse(
        success=True,
        data={
            "user": user_response.model_dump(),
            "token": token
        }
    )


@router.get("/profile", response_model=APIResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return APIResponse(
        success=True,
        data={"user": current_user.model_dump()}
    )


@router.put("/profile", response_model=APIResponse)
async def update_profile(
    name: str = None,
    preferences: UserPreferences = None,
    current_user: User = Depends(get_current_user)
):
    updates = {}
    if name:
        updates["name"] = name
    if preferences:
        updates["preferences"] = preferences
    
    updated_user = db.update_user(current_user.id, **updates)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return without password
    user_response = User(
        id=updated_user.id,
        email=updated_user.email,
        name=updated_user.name,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        preferences=updated_user.preferences
    )
    
    return APIResponse(
        success=True,
        data={"user": user_response.model_dump()}
    )
