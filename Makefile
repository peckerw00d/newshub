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