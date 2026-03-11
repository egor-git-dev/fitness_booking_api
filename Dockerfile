# 1. Берем официальный Python
FROM python:3.12-slim

# 2. Устанавливаем рабочую директорию
WORKDIR /app

# 3. Копируем файлы зависимостей
COPY requirements.txt .

# 4. Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем код приложения
COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic

# 6. Открываем порт для FastAPI
EXPOSE 8000

# 7. Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
