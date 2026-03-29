#!/bin/bash
# Скрипт для быстрого старта проекта

set -e

echo "=========================================="
echo "MTS Hack LLM Service - Setup"
echo "=========================================="

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "✗ Docker не установлен"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "✗ Docker Compose не установлен"
    exit 1
fi

echo "✓ Docker установлен"

# Копируем .env если не существует
if [ ! -f .env ]; then
    echo "📋 Копирую .env.example в .env"
    cp .env.example .env
    echo "   Отредактируй .env если нужны свои параметры"
else
    echo "✓ .env уже существует"
fi

# Выбираем режим запуска
echo ""
echo "Выбери режим запуска:"
echo "  1 - Локальный режим (Ollama + Qwen 8B)"
echo "  2 - Удаленный режим (OpenAI API)"
read -p "Выбор [1/2]: " mode_choice

case $mode_choice in
    1)
        echo "🚀 Запускаю в локальном режиме..."
        # Обновляем .env
        sed -i '' 's/^MODE=.*/MODE=local/' .env || sed -i 's/^MODE=.*/MODE=local/' .env
        docker-compose --profile local up -d
        ;;
    2)
        echo "🚀 Запускаю в удаленном режиме..."
        echo "⚠️  Убедись что в .env установлен OPENAI_API_KEY"
        # Обновляем .env
        sed -i '' 's/^MODE=.*/MODE=remote/' .env || sed -i 's/^MODE=.*/MODE=remote/' .env
        docker-compose up -d
        ;;
    *)
        echo "✗ Неверный выбор"
        exit 1
        ;;
esac

echo ""
echo "⏳ Жду инициализацию сервиса..."
sleep 5

# Проверяем здоровье сервиса
echo ""
echo "Проверяю здоровье сервиса..."

for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Сервис готов к работе!"
        echo ""
        echo "=========================================="
        echo "API доступен на: http://localhost:8000"
        echo "=========================================="
        echo ""
        echo "Полезные команды:"
        echo "  Проверка статуса:   curl http://localhost:8000/health"
        echo "  Тест генерации:     curl -X POST http://localhost:8000/api/generate -H 'Content-Type: application/json' -d '{\"prompt\": \"Hello!\"}'"
        echo "  Логи:               docker-compose logs -f"
        echo "  Остановка:          docker-compose down"
        echo ""
        echo "Примеры использования давай в examples.py"
        exit 0
    fi
    echo "  Попытка $i/30..."
    sleep 1
done

echo "✗ Сервис не ответил. Проверь логи:"
echo "  docker-compose logs"
exit 1
