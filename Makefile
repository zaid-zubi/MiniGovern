install:
	poetry install

activate:
	poerty env activate

defaultAdmin:
	python -m seed.seed_admin

db-up:
	docker compose up -d

db-down:
	docker compose down

migrate:
	poetry run alembic upgrade head

revision:
	poetry run alembic revision --autogenerate -m "$(msg)"

lint:
	ruff check .

format:
	ruff format .

test:
	pytest

run:
	uvicorn app.main:app --reload

worker:
	@echo "Using FastAPI BackgroundTasks - no separate worker required"