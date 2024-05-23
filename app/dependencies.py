from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient

### Authentication ###

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
JWT_SECRET = os.getenv("JWT_SECRET")
EXPIRATION_TIME = os.getenv("EXPIRATION_TIME")

# Hashing functions

def verify_password(plain_password, hashed_password):
    """
    Verify the password
    
    Args:
        plain_password (str): The plain password
        hashed_password (str): The hashed password
    
    Returns:
        bool: True if the password is verified, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Get the password hash
    
    Args:
        password (str): The password
    
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)
