PORT=8000
HOST=127.0.0.1

install:
	poetry install

run:
	poetry run uvicorn main:app --host $(HOST) --port $(PORT) --reload

test:
	cd app && poetry run pytest