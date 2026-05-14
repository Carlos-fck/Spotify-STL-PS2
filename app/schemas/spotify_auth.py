import requests
import base64

def get_spotify_access_token(client_id: str, client_secret: str) -> str:
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials"},
        timeout=10,
    )

    response.raise_for_status()
    return response.json()["access_token"]