"""
Примеры использования LLM модуля
"""

import sys
import os

# Если запускаешь локально, добавь путь до модуля
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_module import LLMClient, Config


def example_basic_generation():
    """Пример 1: Базовая генерация текста"""
    print("\n" + "="*60)
    print("ПРИМЕР 1: Базовая генерация текста")
    print("="*60)
    
    client = LLMClient()
    
    response = client.generate(
        prompt="Напиши короткое стихотворение про программирование",
        max_tokens=300,
        temperature=0.8
    )
    
    print(f"Ответ:\n{response}\n")


def example_chat():
    """Пример 2: Chat с историей"""
    print("\n" + "="*60)
    print("ПРИМЕР 2: Chat с историей сообщений")
    print("="*60)
    
    client = LLMClient()
    
    messages = [
        {"role": "user", "content": "Привет! Кто ты?"},
    ]
    
    print(f"User: {messages[0]['content']}")
    
    response1 = client.chat(messages=messages, max_tokens=100)
    print(f"Assistant: {response1}\n")
    
    messages.append({"role": "assistant", "content": response1})
    messages.append({"role": "user", "content": "Какие языки программирования ты знаешь?"})
    
    print(f"User: {messages[-1]['content']}")
    
    response2 = client.chat(messages=messages, max_tokens=200)
    print(f"Assistant: {response2}\n")


def example_system_prompt():
    """Пример 3: Использование system prompt"""
    print("\n" + "="*60)
    print("ПРИМЕР 3: System prompt (инструкции для модели)")
    print("="*60)
    
    client = LLMClient()
    
    response = client.generate(
        prompt="Какой язык программирования лучший?",
        system_prompt="Ты эксперт в Python. Отвечай как истинный Pythonista, с юмором.",
        max_tokens=200,
        temperature=0.7
    )
    
    print(f"Ответ:\n{response}\n")


def example_text_classification():
    """Пример 4: Классификация текста"""
    print("\n" + "="*60)
    print("ПРИМЕР 4: Классификация тональности текста")
    print("="*60)
    
    client = LLMClient()
    
    texts = [
        "Мне очень нравится этот продукт!!!",
        "Ужасно, вообще не работает",
        "Новая версия вышла на продажу",
    ]
    
    for text in texts:
        response = client.generate(
            prompt=f"Классифицируй тональность: '{text}' (позитив/негатив/нейтраль)",
            system_prompt="Ты эксперт анализа тональности. Отвечай одним словом на русском.",
            max_tokens=10,
            temperature=0.1
        )
        print(f"Текст: {text}")
        print(f"Тональность: {response}\n")


def example_code_generation():
    """Пример 5: Генерация кода"""
    print("\n" + "="*60)
    print("ПРИМЕР 5: Генерация кода")
    print("="*60)
    
    client = LLMClient()
    
    response = client.generate(
        prompt="Напиши функцию для вычисления чисел Фибоначчи на Python",
        system_prompt="Ты опытный Python разработчик. Пиши чистый, оптимизированный код с комментариями.",
        max_tokens=400,
        temperature=0.3
    )
    
    print(f"Код:\n{response}\n")


def example_config_info():
    """Пример 6: Информация о конфигурации"""
    print("\n" + "="*60)
    print("ПРИМЕР 6: Информация о конфигурации")
    print("="*60)
    
    config = Config()
    print(f"\nТекущая конфигурация:")
    print(f"  Режим: {config.mode}")
    
    if config.mode == 'local':
        print(f"  Модель Ollama: {config.ollama_model}")
        print(f"  Ollama URL: {config.ollama_base_url}")
    else:
        print(f"  Модель OpenAI: {config.openai_model}")
        print(f"  Base URL: {config.custom_base_url}")
        print(f"  API Key: {'***' if config.openai_api_key else 'не установлен'}")
    
    # Проверяем здоровье сервиса
    client = LLMClient(config)
    is_healthy = client.health_check()
    print(f"  Статус сервиса: {'✓ Здоров' if is_healthy else '✗ Недоступен'}\n")


def example_interactive_chat():
    """Пример 7: Интерактивный чат"""
    print("\n" + "="*60)
    print("ПРИМЕР 7: Интерактивный чат")
    print("="*60)
    print("\nВведи 'exit' для выхода, 'clear' для очистки истории\n")
    
    client = LLMClient()
    messages = []
    
    system_message = "Ты дружелюбный и полезный AI ассистент. Отвечай по-русски."
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'exit':
            print("До встречи!")
            break
        
        if user_input.lower() == 'clear':
            messages = []
            print("История очищена\n")
            continue
        
        if not user_input:
            continue
        
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat(
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            messages.append({"role": "assistant", "content": response})
            print(f"Assistant: {response}\n")
            
        except Exception as e:
            print(f"Ошибка: {str(e)}\n")
            messages.pop()  # Удаляем последний user message если ошибка


def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("LLM Module - Примеры использования")
    print("="*60)
    
    examples = {
        '1': ('Базовая генерация', example_basic_generation),
        '2': ('Chat с историей', example_chat),
        '3': ('System prompt', example_system_prompt),
        '4': ('Классификация текста', example_text_classification),
        '5': ('Генерация кода', example_code_generation),
        '6': ('Информация о конфиге', example_config_info),
        '7': ('Интерактивный чат', example_interactive_chat),
        '0': ('Все примеры', None),
    }
    
    print("\nДоступные примеры:")
    for key, (name, _) in examples.items():
        print(f"  {key} - {name}")
    
    choice = input("\nВыбери номер примера (1-7, 0 для всех): ").strip()
    
    try:
        if choice == '0':
            # Запускаем все примеры кроме интерактивного
            for key in ['1', '2', '3', '4', '5', '6']:
                examples[key][1]()
        elif choice in examples and choice != '0':
            name, func = examples[choice]
            if func:
                func()
            else:
                print("Ошибка выбора")
        else:
            print("Неверный выбор")
    
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\nОшибка: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
