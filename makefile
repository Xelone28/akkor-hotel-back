PORT=8000
HOST=127.0.0.1

install:
	poetry install

run:
	poetry run uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

test:
	docker compose up -d && cd app && poetry run pytest && docker compose down -v

	