# Fitness Booking API

Простой API для фитнес-клуба на FastAPI с PostgreSQL.

Позволяет:
- Управлять пользователями (создание, удаление, просмотр)
- Управлять тренировками (создание,удаление, просмотр)
- Регистрацию пользователей на тренировки через email

## Технологии

- Python 3.12
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Uvicorn

## Установка

1. Клонируем репозиторий:

git clone <адрес_твоего_репозитория>
cd Fitness_Booking_API

2. Создаём и активируем виртуальное окружение:

python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

3. Устанавливаем зависимости:

pip install -r requirements.txt

4. Создаём базу данных PostgreSQL:

CREATE DATABASE fitness_db;

5. Запускаем сервер:

uvicorn main:app --reload

После запуска API будет доступен на: http://127.0.0.1:8000

Swagger документация: http://127.0.0.1:8000/docs

ReDoc документация: http://127.0.0.1:8000/redoc

## Эндпоинты API

### Пользователи

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /users | Создать пользователя |
| GET | /users | Список всех пользователей |
| GET | /users/{id} | Получить пользователя по ID и список его тренировок |
| DELETE | /users/{id} | Удалить пользователя |

#### Пример POST /users
{
  "name": "Егор",
  "email": "egor@example.com",
  "password": "1234"
}

### Тренировки

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /trainings | Создать тренировку |
| GET | /trainings | Список всех тренировок с участниками |
| GET | /trainings/{id} | Получить тренировку по ID с участниками |
| POST | /trainings/{id}/register | Записать пользователя на тренировку через email |
| DELETE | /trainings/{id} | Удалить тренировку |

#### Пример POST /trainings
{
  "title": "Йога для начинающих",
  "description": "Расслабляющая йога",
  "capacity": 10
}

#### Пример POST /trainings/{id}/register
{
  "user_email": "egor@example.com"
}

### Примеры GET ответов

#### GET /users/{id}
{
  "id": 1,
  "name": "Егор",
  "email": "egor@example.com",
  "trainings": ["Йога для начинающих", "Силовая тренировка"]
}

#### GET /trainings
[
  {
    "id": 1,
    "title": "Йога для начинающих",
    "description": "Расслабляющая йога",
    "capacity": 10,
    "attendees": ["egor@example.com"]
  },
  {
    "id": 2,
    "title": "Силовая тренировка",
    "description": "Фитнес для всех уровней",
    "capacity": 8,
    "attendees": ["egor@example.com", "anna@example.com"]
  }
]

## Postman

В проекте есть готовая коллекция Postman:

postman/Fitness_API.postman_collection.json

Импортируйте её в Postman:

Import → Upload Files → выберите файл Fitness_API.postman_collection.json

### Environment

Коллекция использует переменную:

base_url

Создайте Environment в Postman и добавьте переменную:

base_url = http://127.0.0.1:8000

После этого все запросы будут работать автоматически.

Пример запросов в коллекции:

{{base_url}}/users  
{{base_url}}/trainings  
{{base_url}}/trainings/{id}

## Автор

Егор Милехин