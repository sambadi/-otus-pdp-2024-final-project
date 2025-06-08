install:  # установка зависимостей
	uv sync

lint: # проверка кода с помощью pre-commit
	uv run pre-commit run --all-files


test: # тестирование проекта
	uv run pytest --cov=tech_seeker
