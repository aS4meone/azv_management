from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    role: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True
