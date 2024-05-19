import requests

# Test the server
print(requests.get('http://127.0.0.1:8000').text)