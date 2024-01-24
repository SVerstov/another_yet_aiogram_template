.PHONY: init migrate migrations downgrade


init:
	poetry install --no-root
	poetry shell


migrate:
	poetry run alembic upgrade head


migrations:
	poetry run alembic revision --autogenerate --message "$(word 2,$(MAKECMDGOALS))"

downgrade:
	poetry run alembic downgrade -1
