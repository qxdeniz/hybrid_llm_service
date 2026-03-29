#Hybrid LLM Service

Полнофункциональный Docker сервис для локальной и удаленной работы с языковыми моделями.

## Возможности

- 🚀 **Два режима работы:**
  - `local` - Ollama с моделью Qwen 8B (автоматическое скачивание)
  - `remote` - OpenAI API или другие совместимые API

- 🐳 **Docker Compose** - полная оркестрация сервисов
- 🐍 **Python модуль** - готов к импорту в ваш проект
- 🔄 **REST API** - для интеграции с любыми приложениями
- 💪 **Поддержка потоковой обработки** - работа с длинными текстами
- ⚙️ **Гибкая конфигурация** - через переменные окружения

## Быстрый старт

### Предварительные требования

- Docker & Docker Compose
- Python 3.8+ (для использования модуля локально)

### 1. Подготовка

```bash
cp .env.example .env
```

### 2. Локальный режим (Ollama)

```bash
# Запуск с локальной моделью
docker-compose --profile local up -d

# Проверка статуса
curl http://localhost:8000/health

# Проверка доступных моделей
curl http://localhost:8000/api/models
```

### 3. Удаленный режим (OpenAI)

Отредактируйте `.env`:

```env
MODE=remote
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo
CUSTOM_BASE_URL=https://api.openai.com/v1
```

Запуск:
```bash
docker-compose up -d
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Generate (простая генерация)
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Привет, как дела?",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### Chat (с историей)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Привет!"},
      {"role": "assistant", "content": "Привет! Как дела?"},
      {"role": "user", "content": "Хорошо, спасибо!"}
    ],
    "max_tokens": 100
  }'
```

### Список моделей
```bash
curl http://localhost:8000/api/models
```

### Конфигурация
```bash
curl http://localhost:8000/api/config
```

## Python модуль

### Установка

```python
# Добавьте путь до проекта
import sys
sys.path.insert(0, '/path/to/mts-hack')

from llm_module import LLMClient, Config
```

### Использование

#### Базовая генерация

```python
from llm_module import LLMClient

client = LLMClient()

# Простой промпт
response = client.generate(
    prompt="Напиши стихотворение про программирование",
    max_tokens=300,
    temperature=0.8
)

print(response)
```

#### Chat режим

```python
from llm_module import LLMClient

client = LLMClient()

messages = [
    {"role": "user", "content": "Привет!"},
]

response = client.chat(
    messages=messages,
    max_tokens=200
)

print(response)

# Продолжаем диалог
messages.append({"role": "assistant", "content": response})
messages.append({"role": "user", "content": "Расскажи о себе"})

response2 = client.chat(
    messages=messages,
    max_tokens=200
)

print(response2)
```

#### Кастомная конфигурация

```python
from llm_module import Config, LLMClient

# Создаем кастомную конфиг
config = Config()

# Проверяем режим
print(f"Текущий режим: {config.mode}")
print(f"Модель: {config.ollama_model if config.mode == 'local' else config.openai_model}")

# Создаем клиент с конфигом
client = LLMClient(config)

# Проверяем здоровье
is_healthy = client.health_check()
print(f"Сервис здоров: {is_healthy}")

# Список доступных моделей (для локального режима)
if config.mode == 'local':
    models = client.list_models()
    print(f"Доступные модели: {models}")
```

#### System prompt

```python
from llm_module import LLMClient

client = LLMClient()

response = client.generate(
    prompt="Какой язык программирования лучший?",
    system_prompt="Ты эксперт в Python. Отвечай кратко и по делу.",
    max_tokens=200,
    temperature=0.5
)

print(response)
```

## Переменные окружения

```env
# Основная конфигурация
MODE=local                                          # 'local' или 'remote'

# Локальный режим (Ollama)
OLLAMA_MODEL=qwen:8b                              # Модель для использования
OLLAMA_BASE_URL=http://localhost:11434            # URL Ollama сервиса

# Удаленный режим (OpenAI API)
OPENAI_API_KEY=your_key_here                      # API ключ
OPENAI_MODEL=gpt-4-turbo                          # Модель OpenAI
CUSTOM_BASE_URL=https://api.openai.com/v1         # Кастомный URL API

# Остальное
LLM_SERVICE_PORT=8000                             # Порт сервиса
LOG_LEVEL=INFO                                     # Уровень логирования
REQUEST_TIMEOUT=30                                 # Timeout запросов (сек)
MAX_RETRIES=3                                      # Максимум повторов
```

## Структура проекта

```
mts-hack/
├── docker-compose.yml           # Оркестрация контейнеров
├── .env.example                 # Пример конфигурации
├── .gitignore
├── README.md
│
├── llm_service/                 # API сервис
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                   # Flask приложение
│   └── entrypoint.sh            # Инициализация
│
└── llm_module/                  # Python модуль для импорта
    ├── __init__.py
    ├── config.py                # Конфигурация
    └── llm_client.py            # Основной клиент
```

## Примеры использования

### Пример 1: Классификация текста

```python
from llm_module import LLMClient

client = LLMClient()

text = "Мне очень нравится этот продукт!"

response = client.generate(
    prompt=f"Классифицируй тональность текста (позитив/негатив/нейтраль): '{text}'",
    system_prompt="Ты эксперт в анализе тональности текста. Отвечай одним словом.",
    max_tokens=10,
    temperature=0.3
)

print(f"Тональность: {response}")
```

### Пример 2: Генерация кода

```python
from llm_module import LLMClient

client = LLMClient()

response = client.generate(
    prompt="Напиши функцию для вычисления факториала на Python",
    system_prompt="Ты опытный Python разработчик. Пиши качественный код.",
    max_tokens=500,
    temperature=0.3
)

print(response)
```

### Пример 3: Interactive Chat Bot

```python
from llm_module import LLMClient

client = LLMClient()
messages = []

print("Chat Bot (введи 'exit' для выхода)")
print("=" * 50)

while True:
    user_input = input("You: ").strip()
    
    if user_input.lower() == 'exit':
        break
    
    if not user_input:
        continue
    
    messages.append({"role": "user", "content": user_input})
    
    response = client.chat(
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )
    
    messages.append({"role": "assistant", "content": response})
    
    print(f"Bot: {response}\n")
```

## Производительность

- **Ollama (qwen:8b)**: ~200-500ms на запрос (зависит от железа)
- **OpenAI API**: ~1-3s на запрос (зависит от модели и нагрузки)

Рекомендуемые ресурсы для Ollama:
- CPU: 4+ ядра
- RAM: 16+ GB
- GPU: NVIDIA с 6+ GB VRAM (опционально)

## Решение проблем

### Ollama не запускается

```bash
# Проверь логи
docker-compose logs ollama

# Убедись что образ скачалась
docker images | grep ollama
```

### API недоступен

```bash
# Проверь что контейнер запущен
docker-compose ps

# Проверь логи LLM сервиса
docker-compose logs llm-api

# Проверь порт
curl -v http://localhost:8000/health
```

### Модель не скачивается

```bash
# Проверь интернет соединение
# Проверь место на диске 
# Модель qwen:8b занимает ~5GB

# Попытайся скачать вручную
docker-compose exec ollama ollama pull qwen:8b
```
