.PHONY: help build up down logs stop restart test client clean

help:
	@echo "MTS Hack LLM Service - Commands"
	@echo ""
	@echo "Setup & Deploy:"
	@echo "  make setup          - Начальная настройка"
	@echo "  make build          - Построить образы"
	@echo "  make up-local       - Запустить локальный режим (Ollama)"
	@echo "  make up-remote      - Запустить удаленный режим (OpenAI)"
	@echo "  make up             - Запустить (режим из .env)"
	@echo "  make down           - Остановить все контейнеры"
	@echo "  make stop           - Остановить без удаления"
	@echo "  make restart        - Перезагрузить"
	@echo ""
	@echo "Development:"
	@echo "  make logs           - Просмотр логов"
	@echo "  make logs-api       - Логи LLM API"
	@echo "  make logs-ollama    - Логи Ollama"
	@echo "  make test           - Тест генерации"
	@echo "  make test-api       - Тест REST API"
	@echo "  make health         - Проверка здоровья"
	@echo "  make models         - Список моделей"
	@echo "  make pull           - Скачать модель"
	@echo ""
	@echo "Utils:"
	@echo "  make shell          - Shell в LLM контейнер"
	@echo "  make shell-ollama   - Shell в Ollama контейнер"
	@echo "  make ps             - Статус контейнеров"
	@echo "  make clean          - Очистить образы"
	@echo "  make example        - Запустить примеры"
	@echo ""

setup:
	@chmod +x setup.sh llm_cli.py
	@./setup.sh

build:
	docker-compose build

up-local:
	@sed -i '' 's/^MODE=.*/MODE=local/' .env || sed -i 's/^MODE=.*/MODE=local/' .env
	docker-compose --profile local up -d
	@make health

up-remote:
	@sed -i '' 's/^MODE=.*/MODE=remote/' .env || sed -i 's/^MODE=.*/MODE=remote/' .env
	docker-compose up -d
	@make health

up:
	docker-compose up -d
	@make health

down:
	docker-compose down -v

stop:
	docker-compose stop

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f llm-api

logs-ollama:
	docker-compose logs -f ollama

health:
	@python3 llm_cli.py health

config:
	@python3 llm_cli.py config

models:
	@python3 llm_cli.py models

test:
	@python3 llm_cli.py test --prompt "Что такое Python?"

test-api:
	@python3 llm_cli.py rest

pull:
	@python3 llm_cli.py pull

ps:
	docker-compose ps

shell:
	docker-compose exec llm-api /bin/bash

shell-ollama:
	docker-compose exec ollama /bin/bash

clean:
	docker-compose down -v
	docker system prune -f

example:
	@python3 examples.py
