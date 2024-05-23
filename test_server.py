import requests
from datetime import datetime

# Test the server
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzE2NDk0MzI2fQ.5Vt2pL8lG9AuyLpogj9Dhyi0bjMvM2jgIbIwsdQSDyY"}
refresh_token_header = {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzE5MDY2MTM2fQ.5d_eMPiimrpWmGyMLC_CSy-qx-NO5NBrTFHpOoAGINc"}
### Test the server
print(requests.get('http://127.0.0.1:8000', headers=headers).text)

#################### USER ######################3

# get single user
print(requests.get('http://127.0.0.1:8000/users/1', headers=headers).text)

# get all users
# print(requests.get('http://127.0.0.1:8000/users'))

# create user
# response = requests.post("http://127.0.0.1:8000/users", json={
#     "first_name": "Johnathan",
#     "last_name": "Doepe",
#     "email": "johndoepe@example.com",
#     "password": "secret1",
#     "username": "johndoepe"
# })
# print(response.text)

### Test game endpoints ###

# get all game scores related to a user
# response = requests.get("http://127.0.0.1:8000/users/games/2",  headers=headers)
# print(response.text)

# get all games
# response = requests.get("http://127.0.0.1:8000/games",  headers=headers)
# print(response.text)

# create game - for backend ####### BACKEND
# response = requests.post('http://127.0.0.1:8000/games', json={
#         "id": 1,
#         "game_type": "memory_game"
#         })
# print(response.text)

# print(requests.get('http://127.0.0.1:8000/games').text)

### Test user games endpoints ###


# login = requests.post('http://127.0.0.1:8000/login', data={"username": "johndoe", "password": "secret"})
# print(login.text)    

# response_me = requests.get('http://127.0.0.1:8000/me', headers=headers)
# print(response_me.text)

# login = requests.post('http://127.0.0.1:8000/refresh_token', params=refresh_token_header)
# print(login.text)  

# response = requests.get('http://127.0.0.1:8000/all_scores/1')
# print(response.text)

# response = requests.post('http://127.0.0.1:8000/add_new_score/number_game', headers=headers, json={
#       "score_list": [
#         {"correctAnswer": [1], "userAnswer": [1], "time": 1},
#     ]
# })
# print(response.text)

# response = requests.post('http://127.0.0.1:8000/add_new_score/color_game', headers=headers, json={
#       "score_list": [
#           {"correctAnswer": "red", "userAnswer": "red", "time": 1},
#     ]
# })
# print(response.text)

# response = requests.post('http://127.0.0.1:8000/add_new_score/memory_game', headers=headers, json={
#       "score_list": [
#           {"wrongMatches": 20, "time": 1},
#           {"wrongMatches": 20, "time": 1},
#     ]
# })
# print(response.text)