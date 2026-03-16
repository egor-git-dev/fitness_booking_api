from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from app.models import UserDB, RegistrationDB, TrainingDB
from app.schemas import TrainingCreate, TrainingOut, TrainingRegister
from app.database import get_db
from app.services.registration_service import register_user_to_training


router = APIRouter(prefix="/trainings", tags=["Тренировки"])


# --------------------- Тренировки ---------------------

@router.post('/', summary='Создать тренировку')
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

@router.get('/', response_model=list[TrainingOut], summary='Все тренировки')
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

@router.post("/{training_id}/register", summary='Записать пользователя на тренировку')
def register(training_id: int, request: TrainingRegister, db: Session = Depends(get_db)):
    registration = register_user_to_training(db=db, training_id=training_id, user_email=request.user_email)
    
    # register_user_to_training(db=db, training_id=training_id, user_email=request.user_email)
    return {'message': f'Пользователь "{registration.user.name}" успешно записан на тренировку {registration.training.title}'}


@router.get('/{training_id}', response_model=TrainingOut, summary='Информация о тренировке')
def get_training(training_id: int, db: Session = Depends(get_db)):
    training = (
        db.query(TrainingDB)
        .options(selectinload(TrainingDB.registrations).selectinload(RegistrationDB.user))
        .filter(TrainingDB.id == training_id)
        .first()
    )
    if not training:
        raise HTTPException(status_code=404, detail='Тренировка не найдена')
    
    attendees = [r.user.email for r in training.registrations]
    
    return TrainingOut(
        id=training.id,
        title=training.title,
        description=training.description,
        capacity=training.capacity,
        attendees=attendees
    )


@router.delete('/{training_id}', summary='Удалить тренировку')
def delete_training(training_id: int, db: Session = Depends(get_db)):
    training = db.query(TrainingDB).filter(TrainingDB.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail='Тренировка не найдена')
    db.delete(training)
    db.commit()
    
    return {'message': f'Тренировка "{training.title}" успешно удалена'}
