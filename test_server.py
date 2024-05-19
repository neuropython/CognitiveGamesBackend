import requests

# Test the server
print(requests.get('http://127.0.0.1:8000').text)

print(requests.get('http://127.0.0.1:8000/users/1').text)

response = requests.post("http://127.0.0.1:8000/users", json={
    "id": 2,
    "first_name": "John",
    "last_name": "Doe",
    "email": "johndoe@example.com",
    "password": "secret",
    "username": "johndoe"
})