import requests
from datetime import datetime

# Test the server
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lcGUiLCJleHAiOjE3MTY1MDQ0NjB9.17ul-SRwJq6sjkczObfhtyHpcFG072ZYWscK9CmWX80"}
refresh_token = {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzE5MDY2MTM2fQ.5d_eMPiimrpWmGyMLC_CSy-qx-NO5NBrTFHpOoAGINc"}
### Test the server
print(requests.get('http://127.0.0.1:8000', headers=headers).text)

#################### USER ######################

# get single user
# print(requests.get('http://127.0.0.1:8000/users/1', headers=headers).text)

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
# response = requests.get("http://127.0.0.1:8000/users/games/1",  headers=headers)
# print(response.text)

# get all games
# response = requests.get("http://127.0.0.1:8000/games",  headers=headers)
# print(response.text)

### Test user games endpoints ###

login = requests.post('http://127.0.0.1:8000/login', data={"username": "johndoepe", "password": "secret1"})
print(login.text)    

# response_me = requests.get('http://127.0.0.1:8000/me', headers=headers)
# print(response_me.text)

# login = requests.post('http://127.0.0.1:8000/refresh_token', params=refresh_token)
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

# response = requests.get('http://127.0.0.1:8000/do_i_score_below_average/3', headers=headers)
# print(response.text)