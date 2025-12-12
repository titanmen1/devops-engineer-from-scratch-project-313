run:
	uvicorn main:app --reload --port 8080

lint:
	ruff check

lint-fix:
	ruff check --fix

test:
	pytest .
