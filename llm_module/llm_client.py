"""
LLM Client - унифицированный клиент для работы с Ollama и OpenAI API
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI, AzureOpenAI
import time

from .config import Config

logger = logging.getLogger(__name__)


class LLMClient:
    """Клиент для взаимодействия с LLM (Ollama или OpenAI API)"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Инициализация LLM клиента
        
        Args:
            config: Объект конфигурации. Если не передан, создается новый
        """
        self.config = config or Config()
        self.mode = self.config.mode
        
        if self.mode == 'local':
            self.client = None  # Используем requests для Ollama
            self.base_url = self.config.ollama_base_url
        else:
            # Инициализируем OpenAI клиент
            self.client = OpenAI(
                api_key=self.config.openai_api_key,
                base_url=self.config.custom_base_url
            )
        
        logger.info(f"LLMClient инициализирован в режиме: {self.mode}")
    
    # ========================= Основные методы =========================
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.9,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Генерирует ответ на основе промпта
        
        Args:
            prompt: Основной промпт
            max_tokens: Максимальное количество токенов в ответе
            temperature: Температура (креативность) ответа
            top_p: Top-P параметр
            system_prompt: Системный промпт (инструкции для модели)
        
        Returns:
            Сгенерированный текст
        """
        if self.mode == 'local':
            return self._generate_ollama(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                system_prompt=system_prompt
            )
        else:
            return self._generate_openai(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                system_prompt=system_prompt
            )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Chat режим с поддержкой истории сообщений
        
        Args:
            messages: Список сообщений с format [{"role": "user"/"assistant", "content": "..."}]
            max_tokens: Максимальное количество токенов
            temperature: Температура ответа
            top_p: Top-P параметр
        
        Returns:
            Ответ модели
        """
        if self.mode == 'local':
            return self._chat_ollama(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
        else:
            return self._chat_openai(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
    
    # ========================= Ollama методы =========================
    
    def _generate_ollama(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Генерация с использованием Ollama"""
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.config.ollama_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": max_tokens,
                    }
                },
                timeout=self.config.request_timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при генерации с Ollama: {str(e)}")
            raise
    
    def _chat_ollama(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        top_p: float,
    ) -> str:
        """Chat с использованием Ollama"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.config.ollama_model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": max_tokens,
                    }
                },
                timeout=self.config.request_timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('message', {}).get('content', '').strip()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при чате с Ollama: {str(e)}")
            raise
    
    def check_ollama_health(self) -> bool:
        """Проверяет помощь Ollama сервиса"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            logger.info("✓ Ollama сервис здоров")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Ollama недоступен: {str(e)}")
            return False
    
    def ensure_model_exists(self) -> bool:
        """Скачивает модель если она еще не установлена"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            models = response.json().get('models', [])
            
            model_names = [m.get('name', '') for m in models]
            
            if self.config.ollama_model in model_names:
                logger.info(f"✓ Модель {self.config.ollama_model} уже установлена")
                return True
            
            logger.info(f"Скачиваю модель {self.config.ollama_model}...")
            
            pull_response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.config.ollama_model},
                stream=False,
                timeout=600
            )
            pull_response.raise_for_status()
            
            logger.info(f"✓ Модель {self.config.ollama_model} успешно скачана")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при скачивании модели: {str(e)}")
            raise
    
    def list_models(self) -> List[str]:
        """Получить список доступных моделей Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            models = response.json().get('models', [])
            return [m.get('name', '') for m in models]
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении списка моделей: {str(e)}")
            return []
    
    # ========================= OpenAI методы =========================
    
    def _generate_openai(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Генерация с использованием OpenAI API"""
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при генерации с OpenAI: {str(e)}")
            raise
    
    def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        top_p: float,
    ) -> str:
        """Chat с использованием OpenAI API"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при чате с OpenAI: {str(e)}")
            raise
    
    # ========================= Утилиты =========================
    
    def health_check(self) -> bool:
        """Проверяет здоровье сервиса"""
        try:
            if self.mode == 'local':
                return self.check_ollama_health()
            else:
                # Для OpenAI делаем простой тест
                response = self.client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=10,
                )
                return response.choices[0].message.content is not None
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Получить информацию о конфигурации"""
        return {
            'mode': self.mode,
            'config': self.config.to_dict()
        }
