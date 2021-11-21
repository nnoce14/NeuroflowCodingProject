import requests

BASE_URL = 'http://127.0.0.1:5000/api'
MOOD = '/mood'

def test_base_endpoint():
    response = requests.get(BASE_URL+MOOD)
    print(response)
    print(response.json())

if __name__ == "__main__":

    test_base_endpoint()
