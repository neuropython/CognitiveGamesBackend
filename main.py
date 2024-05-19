from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Union
from enum import Enum
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from bson import ObjectId
from fastapi.exceptions import HTTPException
from urllib.parse import quote_plus
from datetime import datetime
from passlib.context import CryptContext


## Security
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

app = FastAPI(debug=True)
load_dotenv()
_password = quote_plus(str(os.getenv("MONGO_PASSWORD")))
_username = quote_plus(str(os.getenv("MONGO_USERNAME")))
MONGO_URI = f"mongodb+srv://{_username}:{_password}@cognitivedatabase.ivg4g6i.mongodb.net/?retryWrites=true&w=majority&appName=CognitiveDatabase"
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
    password: str 
    username: str

class UserInDB(User):
    hashed_password: str

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
    check_user_exists(id)

    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password

    users_collection.insert_one(user.dict())
    return user

async def check_user_exists(id: str) -> None:
    """Check if a user exists in the database"""
    user = users_collection.find_one({"id": id})
    if user is not None:
        raise HTTPException(status_code=400, detail="User already exists")

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