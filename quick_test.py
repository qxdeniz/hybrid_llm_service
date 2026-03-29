"""
Скрипт для быстрого тестирования функциональности
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_module import LLMClient, Config


def test_basic():
    """Базовый тест"""
    print("\n" + "="*60)
    print("БАЗОВЫЙ ТЕСТ")
    print("="*60)
    
    try:
        config = Config()
        print(f"\n✓ Конфиг загружен: {config}")
        
        client = LLMClient(config)
        print(f"✓ Клиент создан")
        
        # Получаем информацию
        info = client.get_info()
        print(f"✓ Информация о клиенте: {info['mode']}")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def test_health():
    """Тест здоровья"""
    print("\n" + "="*60)
    print("ТЕСТ ЗДОРОВЬЯ")
    print("="*60)
    
    try:
        config = Config()
        client = LLMClient(config)
        
        health = client.health_check()
        if health:
            print(f"\n✓ Сервис здоров")
        else:
            print(f"\n⚠  Сервис недоступен")
        
        return health
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        return False


def test_generate():
    """Тест генерации"""
    print("\n" + "="*60)
    print("ТЕСТ ГЕНЕРАЦИИ")
    print("="*60)
    
    try:
        config = Config()
        client = LLMClient(config)
        
        print(f"\n⏳ Генерирую текст...")
        response = client.generate(
            prompt="Привет! Как дела?",
            max_tokens=50,
            temperature=0.5
        )
        
        print(f"\n✓ Ответ получен:")
        print(f"   {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        return False


def test_chat():
    """Тест чата"""
    print("\n" + "="*60)
    print("ТЕСТ ЧАТА")
    print("="*60)
    
    try:
        config = Config()
        client = LLMClient(config)
        
        messages = [
            {"role": "user", "content": "Привет!"}
        ]
        
        print(f"\n⏳ Отправляю сообщение...")
        response = client.chat(
            messages=messages,
            max_tokens=50,
            temperature=0.5
        )
        
        print(f"\n✓ Ответ получен:")
        print(f"   {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        return False


if __name__ == '__main__':
    results = []
    
    results.append(("Конфиг", test_basic()))
    
    if results[0][1]:  # Если конфиг работает
        results.append(("Здоровье", test_health()))
        
        # Если здоров, тестируем функциональность
        if results[1][1]:
            results.append(("Генерация", test_generate()))
            results.append(("Чат", test_chat()))
    
    # Отчет
    print("\n" + "="*60)
    print("ОТЧЕТ")
    print("="*60)
    
    for name, result in results:
        status = "✓ OK" if result else "✗ FAIL"
        print(f"  {name}: {status}")
    
    all_pass = all(result for _, result in results)
    
    if all_pass:
        print("\n✓ Все тесты прошли успешно!")
        sys.exit(0)
    else:
        print("\n✗ Некоторые тесты не прошли")
        sys.exit(1)
