run:
	uv run uvicorn main:app --reload --port 8080

lint:
	uv run ruff check

lint-fix:
	uv run ruff check --fix

test:
	uv run pytest .
