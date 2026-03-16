from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, Mapped, mapped_column, relationship, selectinload

Base = declarative_base()


# ------------------- МОДЕЛИ -------------------

class UserDB(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    trainings: Mapped[list["RegistrationDB"]] = relationship(
        back_populates="user",
        cascade='all, delete-orphan'
    )


class TrainingDB(Base):
    __tablename__ = 'trainings'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str | None]
    capacity: Mapped[int]

    registrations: Mapped[list["RegistrationDB"]] = relationship(
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
