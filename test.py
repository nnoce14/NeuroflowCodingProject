import requests
from requests.auth import HTTPBasicAuth

BASE_URL = 'http://127.0.0.1:5000/api'
MOOD = '/mood'
USERS = '/users'

def test_mood_endpoint_for_user(username, password):
    response = requests.get(BASE_URL+MOOD, auth=HTTPBasicAuth(username, password))
    print(response)
    print(response.json())

def test_users_endpoint_for_user(userID, username, password):
    response = requests.get(BASE_URL+USERS+'/'+str(userID), auth=HTTPBasicAuth(username, password))
    print(response)
    print(response.json())

if __name__ == "__main__":
    test_mood_endpoint_for_user("guest", "password")
    print("")
    test_users_endpoint_for_user(1, "guest", "password")
