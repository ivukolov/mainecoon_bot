FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

python.exe -m pip install --upgrade pip
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app .

CMD ["python", "main.py"]