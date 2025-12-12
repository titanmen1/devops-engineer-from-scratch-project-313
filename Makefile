run:
	uv run uvicorn app.main:app --reload --port 8080

lint:
	uv run ruff check .

lint-fix:
	uv run ruff format .

test:
	uv run pytest .
