"""
Конфигурация для LLM модуля
"""

import os
from typing import Literal
from dotenv import load_dotenv

# Загружаем .env файл если он есть
load_dotenv()

class Config:
    """Конфигурация для LLM сервиса"""
    
    def __init__(self):
        # Основной параметр - режим работы
        self.mode: Literal['local', 'remote'] = os.getenv('MODE', 'local').lower()
        
        if self.mode not in ['local', 'remote']:
            raise ValueError(f"MODE должен быть 'local' или 'remote', получено: {self.mode}")
        
        # Параметры для локального режима (Ollama)
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'qwen:8b')
        
        # Параметры для удаленного режима (OpenAI API)
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')
        self.custom_base_url = os.getenv('CUSTOM_BASE_URL', 'https://api.openai.com/v1')
        
        # Общие параметры
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
    
    def __repr__(self):
        return f"Config(mode='{self.mode}', model='{self.ollama_model if self.mode == 'local' else self.openai_model}')"
    
    def to_dict(self):
        """Преобразует конфиг в словарь"""
        return {
            'mode': self.mode,
            'ollama_base_url': self.ollama_base_url,
            'ollama_model': self.ollama_model,
            'openai_api_key': '***' if self.openai_api_key else '',
            'openai_model': self.openai_model,
            'custom_base_url': self.custom_base_url,
        }
