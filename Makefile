run:
	uv run uvicorn app.main:app --reload --port 8080 --host 0.0.0.0

install-frontend:
	npm ci

run-frontend:
	npx start-hexlet-devops-deploy-crud-frontend

dev:
	npx concurrently "make run" "make run-frontend"

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

db-up:
	docker compose up -d db

db-down:
	docker compose down

test:
	uv run pytest .
