from fastapi import FastAPI
from pydantic import BaseModel, EmailStr


app = FastAPI()


users_db = []


class User(BaseModel):
    name: str
    email: EmailStr
    password: str


@app.get('/')
def read_root():
    return {'message': 'Привет! Fitness API работает'}


@app.post('/users')
def create_user(user: User):
    for u in users_db:
        if u.email == user.email:
            return {'error': 'Пользователь с таким email уже существует'}

    users_db.append(user)
    return {'message': f'Пользователь {user.name} успешно зарегистрирован'}
