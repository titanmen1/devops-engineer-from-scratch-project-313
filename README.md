### Hexlet tests and linter status:
[![Actions Status](https://github.com/titanmen1/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/titanmen1/devops-engineer-from-scratch-project-313/actions)
[![CI](https://github.com/titanmen1/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/titanmen1/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml)


### Демо
Приложение развернуто и доступно по адресу: https://devops-engineer-from-scratch-project-313-7vsm.onrender.com

### Установка зависимостей

- Установите пакетный менеджер UV

Выполните команды
```bash
uv sync
make install-frontend
```


### Запуск проекта

Бэкенд:
```bash
make run
```

Фронтенд (dev-сервер с проксированием запросов на бэкенд):
```bash
make run-frontend
```

Сборка фронтенда в `frontend/dist` (в репозитории не хранится, собирается при билде):
```bash
make build-frontend
```


### Тесты

Тесты работают с реальной базой данных: каждый тест выполняется внутри
транзакции, которая откатывается после его завершения.

Поднимите базу для тестов и запустите тесты:
```bash
make db-up
make test
```

Адрес базы задаётся переменной `TEST_DATABASE_URL`, по умолчанию —
`postgresql+psycopg://postgres:postgres@localhost:5432/urlshortener_test`.
Если порт 5432 занят, укажите свой: `POSTGRES_PORT=5433 make db-up`.
