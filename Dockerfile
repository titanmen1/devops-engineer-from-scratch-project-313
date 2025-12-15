
FROM python:3.14-slim

WORKDIR /app

# Установка nginx
RUN apt-get update && \
    apt-get install -y nginx

# Установка uv для Python
RUN pip install uv

# Копирование и установка Python зависимостей
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

# Копирование backend кода
COPY app ./app

# Копирование фронтенда
COPY ./frontend/dist /usr/share/nginx/html

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Копирование скрипта запуска
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
