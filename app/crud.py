from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schemas import UserCreate


def create_user(db: Session, user: UserCreate):
    hashed_password = user.password
    db_user = User(username=user.username, password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def change_password(db: Session, user_id: int, new_password: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    db.query(User).filter(User.id == user_id).update({"password": new_password})
    db.commit()
    return db_user

