from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = 'postgresql://egor:1234@localhost:5432/fitness_db'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ------------------- DB SESSION -------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
