run:
	uv run uvicorn app.main:app --reload --port 8080 --host 0.0.0.0

run-frontend:
	npx start-hexlet-devops-deploy-crud-frontend

dev:
	npx concurrently "make run" "make run-frontend"

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

test:
	uv run pytest .
