from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import UserDB, TrainingDB, RegistrationDB
from sqlalchemy.exc import SQLAlchemyError

def register_user_to_training(
    db: Session,
    training_id: int,
    user_email: str
):

    training = db.query(TrainingDB).filter(
        TrainingDB.id == training_id
    ).first()

    if not training:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")

    user = db.query(UserDB).filter(
        UserDB.email == user_email
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверка на повторную запись
    existing = db.query(RegistrationDB).filter(
        RegistrationDB.user_id == user.id,
        RegistrationDB.training_id == training_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Вы уже записаны")

    # Проверка вместимости
    count = db.query(RegistrationDB).filter(
        RegistrationDB.training_id == training_id
    ).count()

    if count >= training.capacity:
        raise HTTPException(status_code=400, detail="Мест нет")

    try:
        registration = RegistrationDB(user_id=user.id, training_id=training.id)
        db.add(registration)
        db.commit()
        db.refresh(registration)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка сервера при регистрации")

    return registration
