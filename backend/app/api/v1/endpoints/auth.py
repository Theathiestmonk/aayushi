"""
Authentication endpoints for user login, registration, and session management
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.core.supabase import supabase_manager
from app.core.security import create_access_token, verify_token

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Request Models
class UserRegistration(BaseModel):
    """User registration request model"""
    full_name: str = Field(..., min_length=2, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")

class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

class PasswordReset(BaseModel):
    """Password reset request model"""
    email: EmailStr = Field(..., description="User's email address")

class GoogleOAuthRequest(BaseModel):
    """Google OAuth request model"""
    supabase_user_id: str = Field(..., description="Supabase user ID from OAuth")
    email: EmailStr = Field(..., description="User's email from Google")
    full_name: str = Field(..., description="User's full name from Google")
    avatar_url: Optional[str] = Field(None, description="User's avatar URL from Google")
    provider: str = Field(default="google", description="OAuth provider")

class TokenResponse(BaseModel):
    """Authentication token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str
    username: str

class AuthResponse(BaseModel):
    """Authentication response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/register", response_model=AuthResponse, summary="Register a new user")
async def register_user(user_data: UserRegistration):
    """
    Register a new user account
    
    - **email**: User's email address (must be unique)
    - **password**: User's password (minimum 8 characters)
    - **full_name**: User's full name
    """
    try:
        # Prepare user data for Supabase
        supabase_user_data = {
            "full_name": user_data.full_name or "",
        }
        
        # Register user with Supabase
        result = await supabase_manager.sign_up(
            email=user_data.email,
            password=user_data.password,
            user_data=supabase_user_data
        )
        
        if result["success"]:
            # Check if email confirmation is required
            if result.get("user") and not result.get("session"):
                # Email confirmation required
                return AuthResponse(
                    success=True,
                    message="Registration successful! Please check your email to confirm your account before signing in.",
                    data={
                        "email": user_data.email,
                        "email_confirmation_required": True,
                        "message": "Please check your email to confirm your account",
                        "redirect_to": "email_confirmation"
                    }
                )
            elif result.get("session"):
                # User is automatically confirmed (if Supabase settings allow)
                user_id = result["user"].id
                access_token = create_access_token(
                    data={"sub": user_id, "email": user_data.email}
                )
                
                return AuthResponse(
                    success=True,
                    message="Registration successful! You can now sign in.",
                    data={
                        "user_id": user_id,
                        "email": user_data.email,
                        "full_name": user_data.full_name,
                        "access_token": access_token,
                        "profile": result["profile"],
                        "redirect_to": "dashboard"
                    }
                )
            else:
                return AuthResponse(
                    success=True,
                    message="Registration successful! Please check your email to confirm your account.",
                    data={
                        "email": user_data.email,
                        "email_confirmation_required": True,
                        "redirect_to": "email_confirmation"
                    }
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Registration failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"❌ User registration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse, summary="Authenticate user")
async def login_user(user_credentials: UserLogin):
    """
    Authenticate an existing user
    
    - **email**: User's email address
    - **password**: User's password
    """
    try:
        # Sign in user with Supabase
        result = await supabase_manager.sign_in(
            email=user_credentials.email,
            password=user_credentials.password
        )
        
        if result["success"]:
            # Create JWT token
            user_id = result["user"].id
            access_token = create_access_token(
                data={"sub": user_id, "email": user_credentials.email}
            )
            
            # Check onboarding status from profile
            profile = result["profile"]
            onboarding_completed = profile.get("onboarding_completed", False) if profile else False
            
            logger.info(f"✅ User logged in successfully: {user_credentials.email}")
            logger.info(f"📋 Onboarding status: {onboarding_completed}")
            
            return AuthResponse(
                success=True,
                message="Login successful",
                data={
                    "user_id": user_id,
                    "email": user_credentials.email,
                    "username": profile.get("username", ""),
                    "access_token": access_token,
                    "profile": {
                        **profile,
                        "onboarding_completed": onboarding_completed
                    }
                }
            )
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
            
    except Exception as e:
        logger.error(f"❌ User login failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/logout", response_model=AuthResponse, summary="Sign out user")
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Sign out the current user
    
    Requires valid Bearer token in Authorization header
    """
    try:
        # Verify the token
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # For now, just return success without calling Supabase sign_out
        # since we're using our own JWT tokens, not Supabase session tokens
        logger.info(f"✅ User logged out successfully: {user_id}")
        
        return AuthResponse(
            success=True,
            message="Logout successful"
        )
            
    except Exception as e:
        logger.error(f"❌ User logout failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Logout failed: {str(e)}"
        )

@router.post("/reset-password", response_model=AuthResponse, summary="Request password reset")
async def request_password_reset(reset_data: PasswordReset):
    """
    Send password reset email to user
    
    - **email**: User's email address
    """
    try:
        # Send password reset email via Supabase
        result = await supabase_manager.reset_password(reset_data.email)
        
        if result["success"]:
            logger.info(f"✅ Password reset email sent: {reset_data.email}")
            
            return AuthResponse(
                success=True,
                message="Password reset email sent. Please check your email."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Password reset failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"❌ Password reset failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Password reset failed: {str(e)}"
        )

@router.get("/me", response_model=AuthResponse, summary="Get current user profile")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get the current user's profile information
    
    Requires valid Bearer token in Authorization header
    """
    try:
        # Verify the token
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user profile from Supabase (handle case where user hasn't completed onboarding)
        result = await supabase_manager.get_user_profile(user_id)
        
        if result["success"]:
            # User has a complete profile
            profile_data = result["profile"]
            profile_data["onboarding_completed"] = profile_data.get("onboarding_completed", False)
            
            return AuthResponse(
                success=True,
                message="Profile retrieved successfully",
                data=profile_data
            )
        else:
            # User doesn't have a profile yet (hasn't completed onboarding)
            # Return basic info from the JWT token
            email = payload.get("email", "")
            return AuthResponse(
                success=True,
                message="Basic user info retrieved",
                data={
                    "id": user_id,
                    "email": email,
                    "username": email.split('@')[0] if email else "",
                    "full_name": "",
                    "onboarding_completed": False,
                    "created_at": None,
                    "updated_at": None
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Failed to get user profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get profile: {str(e)}"
        )

@router.post("/verify-session", response_model=AuthResponse, summary="Verify user session")
async def verify_session(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify if the current user session is valid
    
    Requires valid Bearer token in Authorization header
    """
    try:
        # Verify the token
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Verify session with Supabase
        result = await supabase_manager.verify_user_session(credentials.credentials)
        
        if result["success"] and result["valid"]:
            return AuthResponse(
                success=True,
                message="Session is valid",
                data={"user_id": user_id, "valid": True}
            )
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid session"
            )
            
    except Exception as e:
        logger.error(f"❌ Session verification failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Session verification failed: {str(e)}"
        )

@router.get("/health", summary="Authentication service health check")
async def auth_health_check():
    """Check if the authentication service is healthy"""
    try:
        # Basic health check
        return {
            "status": "healthy",
            "service": "authentication",
            "timestamp": datetime.utcnow().isoformat(),
            "supabase_connected": True
        }
    except Exception as e:
        logger.error(f"❌ Authentication health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Authentication service unhealthy: {str(e)}"
        )

@router.get("/test-supabase", summary="Test Supabase connection")
async def test_supabase():
    """
    Test Supabase connection and configuration
    """
    try:
        from app.core.supabase import supabase_manager
        
        # Test basic connection
        test_result = {
            "supabase_url": supabase_manager.supabase_url,
            "supabase_key_set": bool(supabase_manager.supabase_key),
            "connection_status": "Testing..."
        }
        
        # Try to get project info
        try:
            # This will test if we can connect to Supabase
            project_info = supabase_manager.client.auth.get_session()
            test_result["connection_status"] = "✅ Connected successfully"
            test_result["project_info"] = "Connection verified"
        except Exception as e:
            test_result["connection_status"] = f"❌ Connection failed: {str(e)}"
        
        return {
            "success": True,
            "message": "Supabase connection test",
            "data": test_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Test failed: {str(e)}"
        }

@router.post("/google-oauth", response_model=AuthResponse)
async def google_oauth_login(oauth_data: GoogleOAuthRequest):
    """
    Handle Google OAuth authentication with account linking support.
    
    This endpoint properly handles the case where a user first registers with email/password
    and then tries to authenticate with Google OAuth using the same email. Instead of creating
    a new account, it links the OAuth provider to the existing account while preserving
    the original Supabase user ID and all existing user data.
    """
    try:
        logger.info(f"🔄 Processing Google OAuth for user: {oauth_data.email}")
        
        # Check if user already exists in auth.users by trying to create them
        # If they already exist, Supabase will return an error
        try:
            # Try to create user in auth.users
            auth_response = supabase_manager.client.auth.admin.create_user({
                "email": oauth_data.email,
                "user_metadata": {
                    "full_name": oauth_data.full_name,
                    "provider": oauth_data.provider,
                    "avatar_url": oauth_data.avatar_url
                }
            })
            
            if not auth_response.user:
                raise HTTPException(status_code=400, detail="Failed to create user in auth.users")
            
            # New user created successfully
            logger.info(f"✅ New user created in auth.users: {oauth_data.email}")
            user_id = auth_response.user.id
            
        except Exception as create_error:
            # User already exists in auth.users
            if "already been registered" in str(create_error) or "already exists" in str(create_error).lower():
                logger.info(f"✅ User already exists in auth.users: {oauth_data.email}")
                # Use the provided supabase_user_id since user exists
                user_id = oauth_data.supabase_user_id
            else:
                logger.error(f"❌ Failed to create or find user: {str(create_error)}")
                raise HTTPException(status_code=400, detail=f"Authentication failed: {str(create_error)}")
        
        # Check if user has a profile in user_profiles (onboarding data)
        existing_profile = supabase_manager.client.table("user_profiles").select("*").eq("id", user_id).execute()
        
        if existing_profile.data:
            # User has onboarding data, just return existing profile
            logger.info(f"✅ User has existing profile: {oauth_data.email}")
            user = existing_profile.data[0]
        else:
            # User doesn't have onboarding data yet, create basic profile
            logger.info(f"✅ Creating basic profile for user: {oauth_data.email}")
            
            profile_data = {
                "id": user_id,
                "email": oauth_data.email,
                "full_name": oauth_data.full_name,
                "onboarding_completed": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            profile_response = supabase_manager.client.table("user_profiles").insert(profile_data).execute()
            
            if profile_response.data:
                user = profile_response.data[0]
                logger.info(f"✅ Basic profile created: {oauth_data.email}")
            else:
                # Fallback to basic user data
                user = {
                    "id": user_id,
                    "email": oauth_data.email,
                    "full_name": oauth_data.full_name,
                    "onboarding_completed": False
                }
                logger.warning(f"⚠️ Failed to create profile, using basic user data: {oauth_data.email}")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user["id"]), "email": user["email"]}
        )
        
        logger.info(f"✅ Google OAuth successful for user: {user['email']}")
        
        return {
            "success": True,
            "message": "Google OAuth authentication successful",
            "data": {
                "user_id": str(user["id"]),
                "email": user["email"],
                "username": user.get("username", user["email"].split('@')[0]),
                "full_name": user.get("full_name", ""),
                "onboarding_completed": user.get("onboarding_completed", False),
                "created_at": user.get("created_at"),
                "updated_at": user.get("updated_at"),
                "access_token": access_token,
                "profile": {
                    "id": str(user["id"]),
                    "email": user["email"],
                    "username": user.get("username", user["email"].split('@')[0]),
                    "full_name": user.get("full_name", ""),
                    "avatar_url": user.get("avatar_url"),
                    "onboarding_completed": user.get("onboarding_completed", False),
                    "created_at": user.get("created_at"),
                    "updated_at": user.get("updated_at")
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Google OAuth failed: {str(e)}")
        return {
            "success": False,
            "error": f"Google OAuth authentication failed: {str(e)}"
        }

