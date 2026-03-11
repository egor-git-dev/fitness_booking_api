from fastapi import FastAPI, Depends, HTTPException
from app import models, schemas, deps
from app.models import UserDB, TrainingDB, RegistrationDB
from app.schemas import UserCreate, UserOut,TrainingOut, TrainingCreate, TrainingRegister
from app.deps import get_db
from sqlalchemy.orm import sessionmaker, Session, Mapped, mapped_column, relationship, selectinload

app = FastAPI()


# ------------------- ENDPOINTS -------------------

@app.get('/')
def read_root():
    return {'message': 'Привет! Fitness API работает'}

# ------------------ Пользователи ------------------

@app.post('/users', summary='Добавить пользователя')
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='Пользователь с таким email уже существует')

    new_user = UserDB(name=user.name, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {'message': f'Пользователь {user.name} успешно зарегистрирован'}

@app.get('/users', summary='Все пользователи')
def list_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()

@app.delete('/users/{user_id}', summary='Удалить пользователя')
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f'Пользователь с id {user_id} не найден')
    db.delete(user)
    db.commit()
    return {'message': f'Пользователь {user.name} успешно удалён'}

@app.get('/users/{user_id}', response_model=UserOut, summary='Информация о пользователе')
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = (
        db.query(UserDB)
        .options(selectinload(UserDB.trainings).selectinload(RegistrationDB.training))
        .filter(UserDB.id == user_id)
        .first()
    )
    
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    # Список тренировок, на которые записан пользователь
    trainings = [r.training.title for r in user.trainings]
    
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        trainings=trainings
    )

# --------------------- Тренировки ---------------------

@app.post('/trainings', summary='Создать тренировку')
def create_training(training: TrainingCreate, db: Session = Depends(get_db)):
    new_training = TrainingDB(
        title=training.title,
        description=training.description,
        capacity=training.capacity
    )
    db.add(new_training)
    db.commit()
    db.refresh(new_training)
    return {'message': f'Тренировка "{training.title}" создана'}

@app.get('/trainings', response_model=list[TrainingOut], summary='Все тренировки')
def list_trainings(db: Session = Depends(get_db)):
    trainings = (
        db.query(TrainingDB)
        .options(selectinload(TrainingDB.registrations).selectinload(RegistrationDB.user))
        .all()
    )

    result = []
    for t in trainings:
        attendees = [r.user.email for r in t.registrations]
        result.append(
            TrainingOut(
                id=t.id,
                title=t.title,
                description=t.description,
                capacity=t.capacity,
                attendees=attendees
            )
        )
    return result

@app.post("/trainings/{training_id}/register", summary='Записать пользователя на тренировку')
def register(training_id: int, request: TrainingRegister, db: Session = Depends(get_db)):

    training = db.query(TrainingDB).filter(TrainingDB.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")

    user = db.query(UserDB).filter(UserDB.email == request.user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверка на уже зарегистрированных
    existing = db.query(RegistrationDB).filter(
        RegistrationDB.user_id == user.id,
        RegistrationDB.training_id == training_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail='Вы уже записаны на эту тренировку')

    # Проверка вместимости
    count = db.query(RegistrationDB).filter(RegistrationDB.training_id == training_id).count()
    if count >= training.capacity:
        raise HTTPException(status_code=400, detail="Мест нет")

    registration = RegistrationDB(user_id=user.id, training_id=training_id)
    db.add(registration)
    db.commit()
    db.refresh(registration)

    return {"message": f"Пользователь {user.name} успешно записан на тренировку {training.title}"}


@app.get('/trainings/{training_id}', response_model=TrainingOut, summary='Информация о тренировке')
def get_training(training_id: int, db: Session = Depends(get_db)):
    training = (
        db.query(TrainingDB)
        .options(selectinload(TrainingDB.registrations).selectinload(RegistrationDB.user))
        .filter(TrainingDB.id == training_id)
        .first()
    )
    if not training:
        raise HTTPException(status_code=404, detail='Тренировка не найдена')
    
    ateendees = [r.user.email for r in training.registrations]
    
    return TrainingOut(
        id=training.id,
        title=training.title,
        description=training.description,
        capacity=training.capacity,
        attendees=ateendees
    )


@app.delete('/trainings/{training_id}', summary='Удалить тренировку')
def delete_training(training_id: int, db: Session = Depends(get_db)):
    training = db.query(TrainingDB).filter(TrainingDB.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail='Тренировка не найдена')
    db.delete(training)
    db.commit()
    
    return {'message': f'Тренировка c id {training_id} успешно удалена'}
