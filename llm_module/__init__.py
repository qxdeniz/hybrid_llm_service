"""
LLM Module - унифицированный интерфейс для работы с LLM
Поддерживает локальный режим (Ollama) и удаленный (OpenAI API)
"""

from .llm_client import LLMClient
from .config import Config

__version__ = "1.0.0"
__author__ = "MTS Hack Team"

__all__ = ['LLMClient', 'Config']
