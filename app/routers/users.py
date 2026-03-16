from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.models import UserDB, RegistrationDB
from app.schemas import UserCreate, UserOut
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Пользователи"])

# ------------------ Пользователи ------------------

@router.post('/', summary='Добавить пользователя')
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='Пользователь с таким email уже существует')

    new_user = UserDB(name=user.name, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {'message': f'Пользователь {user.name} успешно зарегистрирован'}

@router.get('/', summary='Все пользователи')
def list_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()

@router.delete('/{user_id}', summary='Удалить пользователя')
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f'Пользователь с id {user_id} не найден')
    db.delete(user)
    db.commit()
    return {'message': f'Пользователь {user.name} успешно удалён'}

@router.get('/{user_id}', response_model=UserOut, summary='Информация о пользователе')
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
