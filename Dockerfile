# Загрузка собранного фронтенда из npm-пакета
FROM node:22-alpine AS frontend

WORKDIR /frontend

COPY package.json package-lock.json ./
RUN npm ci --omit=dev


FROM python:3.14-slim

WORKDIR /app

# Установка nginx
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx && \
    rm -rf /var/lib/apt/lists/*

# Установка uv для Python
RUN pip install uv

# Копирование и установка Python зависимостей
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

# Копирование backend кода
COPY app ./app

# Копирование фронтенда
COPY --from=frontend \
    /frontend/node_modules/@hexlet/project-devops-deploy-crud-frontend/dist \
    /usr/share/nginx/html

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Копирование скрипта запуска
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
