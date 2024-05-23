from typing import Union, Annotated
from fastapi import FastAPI, Depends
from pydantic import BaseModel, EmailStr, SecretStr
from typing import List, Union, Tuple
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
from dependencies import get_password_hash, verify_password
from scipy.stats import pearsonr

app = FastAPI(debug=True)
load_dotenv()
_password = quote_plus(str(os.getenv("MONGO_PASSWORD")))
_username = quote_plus(str(os.getenv("MONGO_USERNAME")))
MONGO_URI = f"mongodb+srv://{_username}:{_password}@cognitivedatabase.ivg4g6i.mongodb.net/?retryWrites=true&w=majority&appName=CognitiveDatabase"

################################# EXCEPTIONS #################################
credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
################################# SECURITY #################################
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

################################# JWT #################################
JWT_SECRET = os.getenv("JWT_SECRET")
EXPIRATION_TIME = os.getenv("EXPIRATION_TIME")

### Authentication ###
def authenticate_user(username: str, password: str):
    """
    Authenticate the user
    
    Args:
        username (str): The username
        password (str): The password
        
    Returns:
        dict: The user if the user is authenticated, False otherwise
    """
    user = users_collection.find_one({"username": username})
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

################################# MODELS #################################
"""
Models classes are not going to be covered in documentation 
since they are not endpoints but rather classes that are used
to define the structure of the data that is being passed around
in the application.
"""

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    user_id: int | None = None

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create an access token
    
    Args:
        data (dict): The data to encode
        expires_delta (timedelta): The expiration time
    
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """
    Create a refresh token
    
    Args:
        data (dict): The data to encode
    
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    # Refresh tokens usually have long validity
    expire = datetime.now() + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt
    
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """
    Get the current user
    
    Args:
        token (str): The token
    
    Returns:
        dict: The user
    
    Raises:
        credentials_exception: If the credentials are invalid
    """
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
################################# MODELS #################################

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
    id: str
    user_id: int
    game_id: int
    score: float
    date: datetime

class ColorGameInput(BaseModel):
    score_list: List[Tuple[List[int], List[int], int]]

class CardsGameInput(BaseModel):
    score_list: List[Tuple[List[int], int]]

class NumberGameInput(BaseModel):
    score_list: List[Tuple[List[int], List[int], int]]
################################# SERIALIZERS #################################
def hide_password_serializer(user):
    """
    Hide the password
    
    Args:
        user (User): The user
    
    Returns:
        dict: The user with the password hidden
    """
    user_dict = user.dict()
    user_dict["password"] = "********"
    return user_dict

################################# DATABASE #################################
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

################################# ROUTES #################################
@app.get("/")
def read_root():
    """
    # Get the root

    This endpoint returns the root of the API.

    ## Returns

    - `dict`: The root

    ## Comments

    This is the root of the API.
    Api is protected by JWT token.

    ## Common headers

    - "Authorization" : "Bearer 'your_valid_token'"
    """
    return {"CogniBackendApp"}

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, token: str = Depends(oauth2_scheme)) -> Union[User, HTTPException]:
    """
    # Read a user

    This endpoint reads a user based on the provided user ID.

    ## Parameters

    - `user_id` (int): The user ID (inside the URL)
    - `token` (str): The token (header)

    ## Returns

    - `Union[User, HTTPException]`: The user or an HTTPException

    ## Raises

    - `HTTPException`: If the user is not found
    - `HTTPException`: If the user is unauthorized

    ## Authorization

    - Bearer Token (header)
    """
    user = users_collection.find_one({"id": user_id})
    current_user = await get_current_user(token)
    if current_user["id"] != user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users")
async def read_users() -> List[User]:
    """
    # Read users
    
    This endpoint reads all users.
    
    ## Returns
    
    - `List[User]`: The list of users
    
    ## Comments
    
    unauthorized access
    
    """
    users = users_collection.find()
    return list(users)

@app.get("/users/{user_id}/games")
async def read_user_games(user_id: int,token: str = Depends(oauth2_scheme)) -> List[UserGames]:
    """
    # Read user games
    
    This endpoint reads all games related to a user.
    
    ## Parameters
    
    - `user_id` (int): The user ID (inside the URL)
    - `token` (str): The token (header)
    
    ## Returns
    
    - `List[UserGames]`: The list of games
    
    ## Raises
    
    - `HTTPException`: If the user is not found
    - `HTTPException`: If the user is unauthorized
    """
    user = users_collection.find_one({"id": user_id})
    curret_user = await get_current_user(token)
    if curret_user["id"] != user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_games = user_games_collection.find({"user_id": user_id})
    return list(user_games)

@app.get("/games")
async def read_games() -> List[Games]:
    """
    # Read games

    This endpoint reads all games.

    ## Returns

    - `List[Games]`: The list of games

    ## Comments

    unauthorized access
    you can ge games id from that endpoint

    """
    games = games_collection.find()
    return list(games)

@app.post("/users")
async def create_user(user: User) -> User:
    """
    # Create a user
    
    This endpoint creates a new user.
    
    ## Parameters
    
    - `user` (User): The user
    
    ## Returns
    
    - `User`: The user
    """
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
    """
    
    # Create a game
    
    This endpoint creates a new game.
    
    ## Parameters
    
    - `game` (Games): The game
    
    ## Returns
    
    - `Games`: The game

    ## Comments

    This endpoint is for backend use only.
    
    """
    games_collection.insert_one(game.dict())
    return game

@app.post("/add_new_score/color_game")
async def create_user_game_color(score: ColorGameInput, token: str = Depends(oauth2_scheme)) -> UserGames:
    """
    Create a new user game score.

    This endpoint allows you to create a new user game score for the color game. 
    It calculates the score based on the user's answers and the correct answers, 
    and then stores the score in the database.

    Args:
    score (ColorGameInput): The user's answers and the correct answers for the game.
    token (str, optional): The user's authentication token. Defaults to Depends(oauth2_scheme).

    Returns:
    UserGames: The created user game score.
    """
    user = await get_current_user(token)
    game_id = 3
    score_to_compute = score.score_list
    scores = []
    for one_game in score_to_compute:
        correct_answers = one_game[0]
        user_answers = one_game[1]
        _correct = sum(c == u for c, u in zip(correct_answers, user_answers))
        correlation = _correct / len(correct_answers)
        _score = correlation * 0.8 +  (-one_game[2]) *0.2
        scores.append(_score)
        final_score = sum(scores) + 100
        print(final_score)
        inserted_document = user_games_collection.insert_one({
        "user_id": user["id"],
        "game_id": game_id,
        "score": final_score,
        "date": datetime.now()
    })
    return {
        "id": str(inserted_document.inserted_id),  
        "user_id": user["id"], 
        "game_id": game_id, 
        "score": final_score, 
        "date": datetime.now()
    }

@app.post("/add_new_score/")
async def create_user_game_color(score: ColorGameInput, token: str = Depends(oauth2_scheme)) -> UserGames:
    """
    Create a new user game score.

    This endpoint allows you to create a new user game score for the color game. 
    It calculates the score based on the user's answers and the correct answers, 
    and then stores the score in the database.

    Args:
    score (ColorGameInput): The user's answers and the correct answers for the game.
    token (str, optional): The user's authentication token. Defaults to Depends(oauth2_scheme).

    Returns:
    UserGames: The created user game score.
    """
    user = await get_current_user(token)
    game_id = 2 
    score_to_compute = score.score_list
    scores = []
    for one_game in score_to_compute:
        correct_answers = one_game[0]
        user_answers = one_game[1]
        _correct = sum(c == u for c, u in zip(correct_answers, user_answers))
        correlation = _correct / len(correct_answers)
        _score = correlation * 0.8 +  (-one_game[2]) *0.2
        scores.append(_score)
        final_score = sum(scores) + 100
        print(final_score)
        inserted_document = user_games_collection.insert_one({
        "user_id": user["id"],
        "game_id": game_id,
        "score": final_score,
        "date": datetime.now()
    })
    return {
        "id": str(inserted_document.inserted_id),  
        "user_id": user["id"], 
        "game_id": game_id, 
        "score": final_score, 
        "date": datetime.now()
    }
    
@app.post("/add_new_score/number_game")
async def create_user_game_number(score: NumberGameInput, token: str = Depends(oauth2_scheme)) -> UserGames:
    """
    Create a new user game score.

    This endpoint allows you to create a new user game score for the number game. 
    It calculates the score based on the user's answers and the correct answers, 
    and then stores the score in the database.

    Args:
    score (NumberGameInput): The user's answers and the correct answers for the game.
    token (str, optional): The user's authentication token. Defaults to Depends(oauth2_scheme).

    Returns:
    UserGames: The created user game score.
    """
    user = await get_current_user(token)
    game_id = 2 
    score_to_compute = score.score_list
    scores = []
    for one_game in score_to_compute:
        correct_answers = one_game[0]
        user_answers = one_game[1]
        _correct = sum(c == u for c, u in zip(correct_answers, user_answers))
        correlation = _correct / len(correct_answers)
        _score = correlation * 0.8 +  (-one_game[2]) *0.2
        scores.append(_score)
        final_score = sum(scores) + 100
        print(final_score)
        inserted_document = user_games_collection.insert_one({
        "user_id": user["id"],
        "game_id": game_id,
        "score": final_score,
        "date": datetime.now()
    })
    return {
        "id": str(inserted_document.inserted_id),  
        "user_id": user["id"], 
        "game_id": game_id, 
        "score": final_score, 
        "date": datetime.now()
    }
    
@app.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    # Login
    
    This endpoint logs in the user and returns an access token.
    
    ## Parameters
    
    - `form_data` (OAuth2PasswordRequestForm): The form data
        - Example: `data={"username": "johndoe", "password": "secret"}`
    
    ## Returns
    
    - `Token`: The token
    
    ## Raises

    - `HTTPException`: If the username or password is incorrect
    """
    print(form_data)
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user["username"]}
    )
    return {"access_token": access_token, "refresh_token": refresh_token} 

@app.post("/refresh_token", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    # Refresh token
    
    This endpoint refreshes the token.
    
    ## Parameters
    
    - `token` (str): The token (header)
    
    ## Returns
    
    - `Token`: The token
    
    ## Raises
    
    - `HTTPException`: If the token is invalid
    
    ## Authorization
    
    - Bearer Token (header)
    
    ## Comments
    
    This endpoint is used to refresh the token. But it is only valid for 15 minutes.
    It is because refresh token doesnt exist in this project. Only access token is used.
    """
    payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = users_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    # Read current user
    
    This endpoint reads the current user.
    
    ## Parameters
    
    - `current_user` (dict): The current user
    
    ## Returns
    
    - `dict`: The user
    
    ## Comments
    
    This endpoint is used to get the current user. You can get id of the user from here.
    it may be used in other endpoints.
    """
    user_without_id = {k: v for k, v in current_user.items() if k != '_id' and k != 'password'}
    return {"user": user_without_id, "message": "You are authorized"}

@app.get("/all_scores/{game_id}")
async def read_all_scores(game_id: int) -> List[UserGames]:
    """
    # Read all scores
    
    This endpoint reads all scores.
    
    ## Returns
    
    - `List[UserGames]`: The list of scores
    
    ## Comments
    
    unauthorized access
    
    """
    game = games_collection.find_one({"id": game_id})
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    scores = user_games_collection.find({"game_id": game_id})
    return list(scores)

    