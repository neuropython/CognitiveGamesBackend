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

class Games(BaseModel):
    id: int
    game_type: GameTypes

class UserGames(BaseModel):
    id: int
    user_id: int
    game_id: int
    score: int
    date: str

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

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int) -> Union[User, HTTPException]:
    user = users_collection.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users")
def read_users() -> List[User]:
    return {"users": "all"}

@app.get("/users/{user_id}/games")
def read_user_games(user_id: int) -> List[UserGames]:
    return {"user_id": user_id}

@app.get("/users/{user_id}/games/{game_id}")
def read_user_game(user_id: int, game_id: int) -> UserGames:
    return {"user_id": user_id, "game_id": game_id}

@app.post("/users")
def create_user(user: User) -> User:
    id = user.id
    check_user_exists(id)
    users_collection.insert_one(user.dict())
    return user

def check_user_exists(id: str):
    user = users_collection.find_one({"_id": id})
    if user is not None:
        raise HTTPException(status_code=400, detail="User already exists")
