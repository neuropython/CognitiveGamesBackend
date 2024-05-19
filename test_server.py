import requests
from datetime import datetime

# Test the server
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzE2MTUxNzE5fQ.AMVUVQDiHv6NrAkdl4LU29Lioo0GtPk79pl32ZzZYCM"}

### Test the server
print(requests.get('http://127.0.0.1:8000', headers=headers).text)

### Test user endpoints ###

print(requests.get('http://127.0.0.1:8000/users/1', headers=headers).text)

# response = requests.post("http://127.0.0.1:8000/users", json={
#     "id": 1,
#     "first_name": "John",
#     "last_name": "Doe",
#     "email": "johndoe@example.com",
#     "password": "secret",
#     "username": "johndoe"
# })
# print(response.text)

# print(requests.get('http://127.0.0.1:8000/users').text)

### Test game endpoints ###

# response = requests.post('http://127.0.0.1:8000/games', json={
#         "id": 3,
#         "game_type": "number_game"
#         })
# print(response.text)

# print(requests.get('http://127.0.0.1:8000/games').text)

### Test user games endpoints ###

# response = requests.post('http://127.0.0.1:8000/users/1/games/2', json={
#     "id": 1,
#     "user_id": 1,
#     "game_id": 3,
#     "score": 100,
#     "date": datetime.now().isoformat()
# })

# print(response.text)

# response = requests.get('http://127.0.0.1:8000/users/1/games')
# print(response.text)

login = requests.post('http://127.0.0.1:8000/token', data={"username": "johndoe", "password": "secret"})
print(login.text)    

# response_me = requests.get('http://127.0.0.1:8000/me', headers=headers)
# print(response_me.text)