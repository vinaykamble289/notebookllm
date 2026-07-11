from fastapi import APIRouter, HTTPException, status, Depends, Header
from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt
from typing import Optional

from app.models.schemas import UserLogin, UserRegister, Token, UserResponse, CurrentUser, Role
from app.models.database import db
from app.core.config import settings

router = APIRouter()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(authorization: Optional[str] = Header(None)) -> CurrentUser:
    """Get current user from JWT token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(token)
    user_id = payload.get("user_id")
    username = payload.get("username")
    role = payload.get("role", "student")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.get_user_by_id(user_id)
    if user is None:
        # For demo purposes, return the data from the token
        return CurrentUser(
            id=user_id,
            username=username,
            email=f"{username}@example.com",
            role=Role(role) if role in ["student", "admin"] else Role.STUDENT
        )
    
    return CurrentUser(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        role=Role(user.get("role", "student"))
    )


async def get_current_active_user(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Get current active user"""
    return current_user


def require_role(required_role: Role):
    """Dependency factory for role-based access control"""
    async def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role != required_role.value and current_user.role != Role.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires {required_role.value} role."
            )
        return current_user
    return role_checker


@router.post("/login/json", response_model=Token)
async def login(credentials: UserLogin):
    """Login endpoint"""
    user = db.get_user_by_username(credentials.username)
    
    # Debug: log user info
    print(f"Login attempt for: {credentials.username}")
    print(f"User found: {user}")
    
    # Check if user exists and has password
    if not user:
        print("User not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if "password_hash" not in user:
        print("No password_hash in user")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        print("Password verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Include role in JWT token
    access_token = create_access_token({
        "sub": user["username"], 
        "user_id": user["id"],
        "username": user["username"],
        "role": user.get("role", "student")
    })
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """Register new user"""
    # Check if user exists
    if db.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user with specified role (defaults to student)
    password_hash = hash_password(user_data.password)
    
    # Get role value
    role_value = user_data.role.value if user_data.role else "student"
    
    user_id = db.add_user({
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": password_hash,
        "role": role_value
    })
    
    return {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email
    }


@router.get("/me", response_model=CurrentUser)
async def get_current_user_info(current_user: CurrentUser = Depends(get_current_user)):
    """Get current user info"""
    return current_user


@router.post("/logout")
async def logout():
    """Logout endpoint"""
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Change password"""
    user = db.get_user_by_id(current_user.id)
    
    if not user or not verify_password(current_password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    new_hash = hash_password(new_password)
    db.update_user_password(current_user.id, new_hash)
    
    return {"message": "Password changed successfully"}


@router.get("/users", response_model=list[UserResponse])
async def list_users(current_user: CurrentUser = Depends(require_role(Role.ADMIN))):
    """List all users (admin only)"""
    users = db.list_users()
    return [
        {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
        for user in users
    ]


@router.post("/users/{user_id}/change-role")
async def change_user_role(
    user_id: str,
    new_role: Role,
    current_user: CurrentUser = Depends(require_role(Role.ADMIN))
):
    """Change user role (admin only)"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.update_user_role(user_id, new_role.value)
    
    return {"message": f"User role changed to {new_role.value}", "user_id": user_id}
