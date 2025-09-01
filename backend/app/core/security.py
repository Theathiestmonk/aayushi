"""
Security utilities for authentication and authorization
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"❌ Password verification failed: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a plain password
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"❌ Password hashing failed: {str(e)}")
        raise ValueError(f"Failed to hash password: {str(e)}")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        The encoded JWT token
    """
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"✅ Access token created successfully for user: {data.get('sub', 'unknown')}")
        
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"❌ Failed to create access token: {str(e)}")
        raise ValueError(f"Failed to create access token: {str(e)}")

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token
    
    Args:
        token: The JWT token to verify
        
    Returns:
        The decoded token payload
        
    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp is None:
            raise ValueError("Token has no expiration")
        
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            raise ValueError("Token has expired")
        
        # Check if token has required fields
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Token missing user ID")
        
        logger.info(f"✅ Token verified successfully for user: {user_id}")
        return payload
        
    except JWTError as e:
        logger.error(f"❌ JWT token verification failed: {str(e)}")
        raise ValueError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Token verification failed: {str(e)}")
        raise ValueError(f"Token verification failed: {str(e)}")

def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get the expiration time of a JWT token
    
    Args:
        token: The JWT token to check
        
    Returns:
        The expiration datetime or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        
        if exp:
            return datetime.fromtimestamp(exp)
        return None
        
    except Exception as e:
        logger.error(f"❌ Failed to get token expiration: {str(e)}")
        return None

def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token has expired
    
    Args:
        token: The JWT token to check
        
    Returns:
        True if expired, False otherwise
    """
    try:
        expiration = get_token_expiration(token)
        if expiration:
            return datetime.utcnow() > expiration
        return True  # Consider invalid tokens as expired
        
    except Exception as e:
        logger.error(f"❌ Failed to check token expiration: {str(e)}")
        return True

def refresh_token(token: str) -> Optional[str]:
    """
    Refresh a JWT token if it's close to expiring
    
    Args:
        token: The current JWT token
        
    Returns:
        New token if refresh needed, None otherwise
    """
    try:
        payload = verify_token(token)
        
        # Check if token expires within 5 minutes
        exp = payload.get("exp")
        if exp:
            expiration_time = datetime.fromtimestamp(exp)
            refresh_threshold = datetime.utcnow() + timedelta(minutes=5)
            
            if expiration_time < refresh_threshold:
                # Create new token with same data
                new_token = create_access_token({
                    "sub": payload.get("sub"),
                    "email": payload.get("email")
                })
                
                logger.info(f"✅ Token refreshed for user: {payload.get('sub')}")
                return new_token
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Failed to refresh token: {str(e)}")
        return None

def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token
    
    Args:
        email: The user's email address
        
    Returns:
        A JWT token for password reset
    """
    try:
        # Create token that expires in 1 hour
        expire = datetime.utcnow() + timedelta(hours=1)
        
        to_encode = {
            "email": email,
            "type": "password_reset",
            "exp": expire
        }
        
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"✅ Password reset token created for: {email}")
        
        return token
        
    except Exception as e:
        logger.error(f"❌ Failed to create password reset token: {str(e)}")
        raise ValueError(f"Failed to create password reset token: {str(e)}")

def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return the email
    
    Args:
        token: The password reset token
        
    Returns:
        The email address if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if it's a password reset token
        if payload.get("type") != "password_reset":
            return None
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        email = payload.get("email")
        if email:
            logger.info(f"✅ Password reset token verified for: {email}")
            return email
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Password reset token verification failed: {str(e)}")
        return None

def create_user_session_token(user_id: str, email: str, additional_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a session token for user authentication
    
    Args:
        user_id: The user's unique identifier
        email: The user's email address
        additional_data: Optional additional data to include
        
    Returns:
        The session JWT token
    """
    try:
        to_encode = {
            "sub": user_id,
            "email": email,
            "type": "session",
            "iat": datetime.utcnow()
        }
        
        if additional_data:
            to_encode.update(additional_data)
        
        # Session tokens last longer (24 hours)
        expire = datetime.utcnow() + timedelta(hours=24)
        to_encode.update({"exp": expire})
        
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"✅ Session token created for user: {user_id}")
        
        return token
        
    except Exception as e:
        logger.error(f"❌ Failed to create session token: {str(e)}")
        raise ValueError(f"Failed to create session token: {str(e)}")

def verify_session_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a session token
    
    Args:
        token: The session token to verify
        
    Returns:
        The decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if it's a session token
        if payload.get("type") != "session":
            return None
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        logger.info(f"✅ Session token verified for user: {payload.get('sub')}")
        return payload
        
    except Exception as e:
        logger.error(f"❌ Session token verification failed: {str(e)}")
        return None

