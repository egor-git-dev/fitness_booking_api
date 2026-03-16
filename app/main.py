from fastapi import FastAPI

from app.routers import users
from app.routers import trainings

app = FastAPI()


app.include_router(users.router)
app.include_router(trainings.router)


@app.get('/')
def read_root():
    return {'message': 'Привет! Fitness API работает'}
