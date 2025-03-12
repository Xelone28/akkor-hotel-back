PORT=8000
HOST=127.0.0.1

install:
	poetry install

run:
	docker-compose up --build -d

testing:
	docker-compose down -v
	docker-compose up --build -d
	echo "⏳ Attente du démarrage de FastAPI..."
	sleep 5
	cd app && poetry run pytest
	docker-compose down -v