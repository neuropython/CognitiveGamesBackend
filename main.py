from typing import Union, Annotated
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field, EmailStr, SecretStr
from typing import List, Optional, Union
from enum import Enum
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException

app = FastAPI(debug=True)
load_dotenv()
_password = quote_plus(str(os.getenv("MONGO_PASSWORD")))
_username = quote_plus(str(os.getenv("MONGO_USERNAME")))
MONGO_URI = f"mongodb+srv://{_username}:{_password}@cognitivedatabase.ivg4g6i.mongodb.net/?retryWrites=true&w=majority&appName=CognitiveDatabase"

## Security
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Hashing functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

# JWT 
JWT_SECRET = os.getenv("JWT_SECRET")
EXPIRATION_TIME = os.getenv("EXPIRATION_TIME")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    user_id: int | None = None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    data_dict = data.get()
    to_encode = data_dict.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = users_collection.find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    return user
## Define database_models:

class GameTypes(Enum):
    color_game = "color_game"
    memory_game = "memory_game"
    number_game = "number_game"

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: SecretStr

class Games(BaseModel):
    id: int
    game_type: GameTypes

    class Config:
        use_enum_values = True

class UserGames(BaseModel):
    id: int
    user_id: int
    game_id: int
    score: int
    date: datetime
### serializers:
def hide_password_serializer(user):
    user_dict = user.dict()
    user_dict["password"] = "********"
    return user_dict

### Connect to MongoDB:
client = MongoClient(MONGO_URI)
db = client["Data"]

users_collection = db["Users"]
games_collection = db["Games"]
user_games_collection = db["UserGames"]

try:
    client.admin.command('ismaster')
    print("Connected to MongoDB")
except Exception as e:
    print("Cannot connect to MongoDB: ", e)

### Define API endpoints:
@app.get("/")
def read_root():
    return {"CogniBackendApp"}

@app.post("login")
async def login(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int) -> Union[User, HTTPException]:
    """Get a user by ID"""
    user = users_collection.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users")
async def read_users() -> List[User]:
    """Get all users"""
    users = users_collection.find()
    return list(users)

@app.get("/users/{user_id}/games")
async def read_user_games(user_id: int) -> List[UserGames]:
    """Get all games for a user by ID"""
    user = users_collection.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_games = user_games_collection.find({"user_id": user_id})
    return list(user_games)

@app.get("/games")
async def read_games() -> List[Games]:
    """Get all games"""
    games = games_collection.find()
    return list(games)

@app.post("/users")
async def create_user(user: User) -> User:
    """Create a new user"""
    id = user.id
    user_check = check_user_exists(id)
    if user_check == 1:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = pwd_context.hash(user.password.get_secret_value())
    user.password = hashed_password
    users_collection.insert_one(user.model_dump())
    return hide_password_serializer(user)

def check_user_exists(id: str) -> None:
    """Check if a user exists in the database"""
    user = users_collection.find_one({"id": id})
    if user is not None:
        return 1

@app.post("/games")
async def create_game(game: Games) -> Games:
    """Create a new game"""
    games_collection.insert_one(game.dict())
    return game

@app.post("/users/{user_id}/games/{game_id}")
async def create_user_game(user_id: int, game_id: int, game: UserGames) -> UserGames:
    """Create a new user game"""
    user = users_collection.find_one({"id": user_id})
    games = games_collection.find_one({"id":game_id})
    if user is None :
        raise HTTPException(status_code=404, detail="User not found")
    if games is None:
        raise HTTPException(status_code=404, detail="Game not found")
    user_games_collection.insert_one(game.dict())
    return game

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    print(form_data)
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"} 

@app.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user), response_model=User):
    user_without_id = {k: v for k, v in current_user.items() if k != '_id' and k != 'password'}
    return {"user": user_without_id, "message": "You are authorized"}