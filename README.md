# Sound Chain

A template for a FastAPI project with a Jinja2 fronted.

## Setup

1.  Install Python dependencies: `pip install -r requirements.txt`
2.  Run the backend: `uvicorn app.main:app --host "0.0.0.0" --port "8000" --reload `

## Docker

1.  Build the image: `docker-compose build`
2.  Run the container: `docker-compose up`

## API Examples

### Users

*   **GET /api/v1/users/**: Get all users.
*   **POST /api/v1/users/**: Create a new user.
    *   Body: `{"name": "John Doe", "email": "john.doe@example.com"}`
*   **GET /api/v1/users/{user_id}**: Get a specific user.
*   **PUT /api/v1/users/{user_id}**: Update a user.
    *   Body: `{"name": "John Doe", "email": "john.doe@newdomain.com"}`
*   **DELETE /api/v1/users/{user_id}**: Delete a user.

### Items

*   **GET /api/v1/items/**: Get all items.
*   **GET /api/v1/items/protected**: Get protected items. Requires `X-Token` header.
    *   Header: `X-Token: fake-super-secret-token`


Limpar cache 

Get-ChildItem -Path . -Name __pycache__ -Recurse -Force | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Name "*.pyc" -Recurse -Force | Remove-Item -Force
pip cache purge