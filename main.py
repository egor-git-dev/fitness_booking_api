from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import List

app = FastAPI()


class User(BaseModel):
    name: str
    email: EmailStr
    password: str


users_db: List[User] = []


class Training(BaseModel):
    id: int
    title: str
    description: str
    capacity: int               # Сколько людей может записаться
    attendees: list[str] = []   # Список email зарегистрированных пользователей


trainings_db: List[Training] = []


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


@app.post('/trainings')
def create_training(training: Training):
    for t in trainings_db:
        if t.id == training.id:
            return {"error": "Тренировка с таким id уже существует"}
    trainings_db.append(training)
    return {'message': f'Тренировка "{training.title}" создана'}


@app.get('/trainings')
def list_trainings():
    return trainings_db


@app.post('/trainings/{training_id}/register')
def register_training(training_id: int, user_email: EmailStr):
    # Ищем тренировку
    for training in trainings_db:
        if training.id == training_id:
            # Проверяем есть ли место
            if len(training.attendees) >= training.capacity:
                return {'error': 'Мест нет'}
            # Проверяем что пользователь зарегистрирован
            for user in users_db:
                if user.email == user_email:
                    if user_email in training.attendees:
                        return {'error': 'Вы уже записаны на эту тренировку'}
                    training.attendees.append(user_email)
                    return {'message': f'{user_email} успешно записан на {training.title}'}
            return {'error': 'Пользователь не найден'}
    return {'error': 'Тренировка не найдена'}


@app.get('/users')
def list_users():
    return users_db
