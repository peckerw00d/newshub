up:
	docker compose up -d

down:
	docker compose down

stop:
	docker compose stop

run:
	PYTHONPATH=$PYTHONPATH:. poetry run python3 src/app/main.py

run_unit_tests:
	PYTHONPATH=$PYTHONPATH:. poetry run pytest tests/unit/

migrations:
	alembic revision --autogenerate
	alembic upgrade head

worker:
	PYTHONPATH=$PYTHONPATH:. poetry run taskiq worker src.app.main:broker

scheduler:
	PYTHONPATH=$PYTHONPATH:. poetry run taskiq scheduler src.app.main:scheduler