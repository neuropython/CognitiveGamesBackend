import requests
from datetime import datetime

# Test the server
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzE2MTUxNzE5fQ.AMVUVQDiHv6NrAkdl4LU29Lioo0GtPk79pl32ZzZYCM"}
refresh_token_header = {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzE5MDY2MTM2fQ.5d_eMPiimrpWmGyMLC_CSy-qx-NO5NBrTFHpOoAGINc"}
### Test the server
print(requests.get('http://127.0.0.1:8000', headers=headers).text)

#################### USER ######################3

# get single user
# print(requests.get('http://127.0.0.1:8000/users/1', headers=headers).text)

# get all users
# print(requests.get('http://127.0.0.1:8000/users'))

# create user
# response = requests.post("http://127.0.0.1:8000/users", json={
#     "id": 2,
#     "first_name": "John",
#     "last_name": "Doe",
#     "email": "johndoe@example.com",
#     "password": "secret",
#     "username": "johndoe"
# })
# print(response.text)

### Test game endpoints ###

# get all game scores related to a user
# response = requests.get("http://127.0.0.1:8000/users/1/games",  headers=headers)
# print(response.text)

# get all games
# response = requests.get("http://127.0.0.1:8000/games",  headers=headers)
# print(response.text)

# create game - for backend
# response = requests.post('http://127.0.0.1:8000/games', json={
#         "id": 1,
#         "game_type": "memory_game"
#         })
# print(response.text)

# print(requests.get('http://127.0.0.1:8000/games').text)

### Test user games endpoints ###

# response = requests.post('http://127.0.0.1:8000/add_new_score', headers=headers, json={
#     "id": 1,
#     "user_id": 1,
#     "game_id": 3,
#     "score": 100,
#     "date": datetime.now().isoformat()
# })

# print(response.text)

# login = requests.post('http://127.0.0.1:8000/login', data={"username": "johndoe", "password": "secret"})
# print(login.text)    

# response_me = requests.get('http://127.0.0.1:8000/me', headers=headers)
# print(response_me.text)

login = requests.post('http://127.0.0.1:8000/refresh_token', params=refresh_token_header)
print(login.text)  

# response = requests.get('http://127.0.0.1:8000/all_scores/3')
# print(response.text)