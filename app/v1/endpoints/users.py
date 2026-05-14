from fastapi import APIRouter, HTTPException
from typing import List
from app.crud import crud_user
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[User])
def read_users():
    return crud_user.get_users()

@router.post("/", response_model=User, status_code=201)
def create_user(user_in: UserCreate):
    new_id = max(user.id for user in crud_user.get_users()) + 1 if crud_user.get_users() else 1
    user = User(id=new_id, **user_in.dict())
    return crud_user.create_user(user)

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int):
    db_user = crud_user.get_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user_in: UserUpdate):
    db_user = crud_user.update_user(user_id, user_in.dict())
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}", response_model=User)   
def delete_user(user_id: int):
    db_user = crud_user.delete_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user