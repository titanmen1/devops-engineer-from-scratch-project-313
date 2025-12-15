#!/bin/bash
set -e

# Получаем порт из переменной окружения или используем 80 по умолчанию
PORT=${PORT:-80}

echo "Starting backend on port 8081..."
# Запускаем backend в фоне на порту 8081 (чтобы освободить 8080 для nginx)
uv run uvicorn app.main:app --host 127.0.0.1 --port 8081 &

echo "Starting nginx on ports $PORT and 8080..."
# Обновляем конфигурацию nginx с правильным портом
sed -i "s/listen 80;/listen $PORT;/" /etc/nginx/sites-available/default

# Запускаем nginx на переднем плане
exec nginx -g "daemon off;"
