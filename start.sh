#!/bin/bash
set -e

# Получаем порт из переменной окружения или используем 80 по умолчанию
PORT=${PORT:-80}

echo "Starting backend on port 8080..."
# Запускаем backend в фоне
uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 &

echo "Starting nginx on port $PORT..."
# Обновляем конфигурацию nginx с правильным портом
sed -i "s/listen 80;/listen $PORT;/" /etc/nginx/sites-available/default

# Запускаем nginx на переднем плане
exec nginx -g "daemon off;"
