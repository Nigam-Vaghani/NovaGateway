.PHONY: dev test build lint migrate

dev:
	docker-compose up --build

prod:
	docker-compose -f docker-compose.prod.yml up -d --build

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check .

migrate:
	cd backend && alembic upgrade head

down:
	docker-compose down
