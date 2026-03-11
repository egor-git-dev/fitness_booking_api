from pydantic import BaseModel, EmailStr


# ------------------- SCHEMAS -------------------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class TrainingCreate(BaseModel):
    title: str
    description: str
    capacity: int

class TrainingRegister(BaseModel):
    user_email: EmailStr

class TrainingOut(BaseModel):
    id: int
    title: str
    description: str | None
    capacity: int
    attendees: list[str]

    class Config:
        orm_mode = True
        
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    trainings: list[str]
    
    class Config:
        orm_mode = True
