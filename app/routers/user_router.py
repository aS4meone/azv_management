from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud
from app.core.security.tokens import create_access_token
from app.crud import change_password
from app.dependencies.database.database import get_db
from app.dependencies.get_current_user import get_current_user
from app.schemas.password_schema import PasswordChange
from app.schemas.user_schemas import User, UserCreate, UserLogin

router = APIRouter(tags=['auth'])


@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@router.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me/")
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password/")
async def change_password(password_change: PasswordChange, current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=current_user.username)
    if not db_user or db_user.password != password_change.old_password:
        raise HTTPException(status_code=400, detail="Incorrect password")
    crud.change_password(db=db, user_id=db_user.id, new_password=password_change.new_password)
    return {"message": "Password updated successfully"}
