from typing import List, Optional
from app.models.user import User

# In-memory "database"
db: List[User] = [
    User(id=1, name="Alice", email="alice@example.com"),
    User(id=2, name="Bob", email="bob@example.com"),
]

def get_user(user_id: int) -> Optional[User]:
    return next((user for user in db if user.id == user_id), None)

def get_users() -> List[User]:
    return db

def create_user(user_in: User) -> User:
    db.append(user_in)
    return user_in

def update_user(user_id: int, user_in: dict) -> Optional[User]:
    user = get_user(user_id)
    if user:
        for key, value in user_in.items():
            if value is not None:
                setattr(user, key, value)
        return user
    return None

def delete_user(user_id: int) -> Optional[User]:
    user = get_user(user_id)
    if user:
        db.remove(user)
        return user
    return None