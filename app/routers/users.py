from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, selectinload
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.models import UserDB, RegistrationDB
from app.schemas import UserCreate, UserOut, UserLogin, Token
from app.database import get_db
from app.services.auth_service import get_current_user


router = APIRouter(prefix="/users", tags=["Пользователи"])

# ------------------ Пользователи ------------------

@router.post('/', summary='Добавить пользователя')
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='Пользователь с таким email уже существует')

    # Хэшируем
    hashed = hash_password(user.password)

    # Создаём пользователя
    new_user = UserDB(name=user.name, email=user.email, password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {'message': f'Пользователь {user.name} успешно зарегистрирован'}

@router.get('/', summary='Все пользователи')
def list_users(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
    ):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return db.query(UserDB).all()

@router.delete('/{user_id}', summary='Удалить пользователя')
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
    ):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f'Пользователь с id {user_id} не найден')
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    db.delete(user)
    db.commit()
    return {'message': f'Пользователь {user.name} успешно удалён'}

@router.get('/{user_id}', response_model=UserOut, summary='Информация о пользователе')
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
    ):
    user = (
        db.query(UserDB)
        .options(selectinload(UserDB.trainings).selectinload(RegistrationDB.training))
        .filter(UserDB.id == user_id)
        .first()
    )
    
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail='Доступ запрещён')
    # Список тренировок, на которые записан пользователь
    trainings = [r.training.title for r in user.trainings]
    
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        trainings=trainings
    )

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
