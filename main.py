from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Union
from enum import Enum
app = FastAPI()

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

### Add mock data to test:
mock_user = User(id=1, first_name="John", last_name="Doe", email="example@gmail.com", password="example", username="example")
mock_game = Games(id=1, game_type=GameTypes.color_game)
mock_user_game = UserGames(id=1, user_id=1, game_id=1, score=100, date="2021-09-01")
 
### Define API endpoints:
@app.get("/")
def read_root():
    return {"CogniBackendApp"}

@app.get("/users/{user_id}")
def read_user(user_id: int) -> User:
    return {"user_id": user_id}

@app.get("/users")

@app.get("/users/{user_id}/games")
def read_user_games(user_id: int) -> List[UserGames]:
    return {"user_id": user_id}

@app.get("/users/{user_id}/games/{game_id}")
def read_user_game(user_id: int, game_id: int) -> UserGames:
    return {"user_id": user_id, "game_id": game_id}

