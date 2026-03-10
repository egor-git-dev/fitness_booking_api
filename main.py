from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, Mapped, mapped_column, relationship, selectinload

app = FastAPI()

DATABASE_URL = 'postgresql://egor:1234@localhost:5432/fitness_db'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ------------------- МОДЕЛИ -------------------

class UserDB(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    trainings: Mapped[List["RegistrationDB"]] = relationship(
        back_populates="user",
        cascade='all, delete-orphan'
    )


class TrainingDB(Base):
    __tablename__ = 'trainings'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str | None]
    capacity: Mapped[int]

    registrations: Mapped[List["RegistrationDB"]] = relationship(
        back_populates="training",
        cascade='all, delete-orphan'
    )


class RegistrationDB(Base):
    __tablename__ = 'registrations'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    training_id: Mapped[int] = mapped_column(ForeignKey('trainings.id'))

    user: Mapped[UserDB] = relationship("UserDB", back_populates="trainings")
    training: Mapped[TrainingDB] = relationship("TrainingDB", back_populates="registrations")

Base.metadata.create_all(bind=engine)

# ------------------- DB SESSION -------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    description: Optional[str]
    capacity: int
    attendees: List[str]

    class Config:
        orm_mode = True

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
    return {'message': f'Пользователь c id {user_id} успешно удалён'}

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

@app.get('/trainings', response_model=List[TrainingOut], summary='Все тренировки')
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
        raise HTTPException(status_code=400, detail="Вы уже записаны на эту тренировку")

    # Проверка вместимости
    count = db.query(RegistrationDB).filter(RegistrationDB.training_id == training_id).count()
    if count >= training.capacity:
        raise HTTPException(status_code=400, detail="Мест нет")

    registration = RegistrationDB(user_id=user.id, training_id=training_id)
    db.add(registration)
    db.commit()
    db.refresh(registration)

    return {"message": f"Пользователь {user.name} успешно записан на тренировку {training.title}"}


@app.get('/trainings/{training_id}', response_model=TrainingOut, summary="Информация о тренировке")
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
