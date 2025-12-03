import requests

def test_login():
    url = "http://localhost:8000/api/login/access-token"
    data = {
        "username": "admin",
        "password": "password"
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            token = response.json()
            print("Login successful!")
            print(f"Token type: {token['token_type']}")
            print(f"Access token: {token['access_token'][:20]}...")
        else:
            print(f"Login failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
