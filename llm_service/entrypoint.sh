#!/bin/bash

# Entrypoint скрипт для LLM Service

set -e

MODE="${MODE:-local}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen:8b}"

echo "=========================================="
echo "LLM Service Initialization"
echo "Mode: $MODE"
echo "=========================================="

# Если локальный режим, ждем Ollama
if [ "$MODE" = "local" ]; then
    echo "Ожидаю доступность Ollama на $OLLAMA_BASE_URL..."
    
    # Функция для проверки доступности Ollama
    wait_for_ollama() {
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -f "$OLLAMA_BASE_URL/api/tags" 2>/dev/null; then
                echo "✓ Ollama доступен!"
                return 0
            fi
            
            echo "Попытка $attempt/$max_attempts: Ollama недоступен, жду..."
            sleep 2
            attempt=$((attempt + 1))
        done
        
        echo "✗ Ollama так и не стал доступен после $max_attempts попыток"
        return 1
    }
    
    if ! wait_for_ollama; then
        echo "Ошибка: Ollama недоступен. Завершаю работу."
        exit 1
    fi
    
    # Скачиваем модель если она еще не скачана
    echo "Проверяю модель $OLLAMA_MODEL..."
    python3 << 'PYTHON'
import os
import requests
import json

base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
model = os.environ.get('OLLAMA_MODEL', 'qwen:8b')

try:
    # Получаем список моделей
    response = requests.get(f'{base_url}/api/tags', timeout=5)
    models = response.json().get('models', [])
    
    model_names = [m.get('name', '').split(':')[0] for m in models]
    
    if model in [m.get('name', '') for m in models]:
        print(f"✓ Модель {model} уже установлена")
    else:
        print(f"Скачиваю модель {model}...")
        pull_response = requests.post(
            f'{base_url}/api/pull',
            json={'name': model},
            stream=True,
            timeout=600
        )
        
        for line in pull_response.iter_lines():
            if line:
                data = json.loads(line)
                if 'status' in data:
                    print(f"  {data['status']}")
        
        print(f"✓ Модель {model} успешно скачана")
        
except Exception as e:
    print(f"✗ Ошибка при работе с моделями: {str(e)}")
    exit(1)
PYTHON

fi

echo "=========================================="
echo "Запускаю LLM API сервис..."
echo "=========================================="

# Запускаем Flask приложение
exec gunicorn --bind 0.0.0.0:8000 --workers 4 --worker-class sync --timeout 120 app:app
