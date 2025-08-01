from pydantic import BaseModel
from typing import Optional

class UserInDB(BaseModel):
    id: int
    name: str
    email: str
    password: str
    security_question: str
    security_answer: str
    role: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    security_question: str
    security_answer: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class PasswordReset(BaseModel):
    email: str
    security_answer: str
    new_password: str

class User(BaseModel):
    email: str
    password: str
    role: str = "user" 
