"""
LLM Service API
Поддерживает как локальный режим (Ollama) так и удаленный (OpenAI API)
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

# Добавляем llm_module в path
sys.path.insert(0, '/app')

from llm_module import LLMClient
from llm_module.config import Config

# Инициализация логирования
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Инициализация конфигурации и клиента
config = Config()
llm_client = None

def initialize_client():
    """Инициализирует LLM клиент с нужным режимом"""
    global llm_client
    try:
        logger.info(f"Инициализирую LLM в режиме: {config.mode}")
        llm_client = LLMClient(config)
        
        if config.mode == 'local':
            # Для локального режима проверяем доступность Ollama
            logger.info("Проверяю доступность Ollama...")
            llm_client.check_ollama_health()
            
            # Скачиваем модель если не있는
            logger.info(f"Проверяю наличие модели {config.ollama_model}...")
            llm_client.ensure_model_exists()
            
        else:
            # Для удаленного режима проверяем API ключ
            if not config.openai_api_key:
                raise ValueError("OPENAI_API_KEY не установлен")
            logger.info("OpenAI API клиент инициализирован")
        
        logger.info("✓ LLM клиент успешно инициализирован")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка инициализации LLM клиента: {str(e)}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья API"""
    try:
        if llm_client is None:
            return jsonify({'status': 'initializing', 'mode': config.mode}), 202
        
        is_healthy = llm_client.health_check()
        if is_healthy:
            return jsonify({
                'status': 'healthy',
                'mode': config.mode,
                'model': config.ollama_model if config.mode == 'local' else config.openai_model
            }), 200
        else:
            return jsonify({'status': 'unhealthy', 'mode': config.mode}), 503
            
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    """
    Генерирует ответ от LLM
    
    Request JSON:
    {
        "prompt": "Ваше сообщение",
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.9
    }
    """
    try:
        if llm_client is None:
            return jsonify({'error': 'LLM client not initialized'}), 503
        
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing "prompt" in request'}), 400
        
        prompt = data['prompt']
        max_tokens = data.get('max_tokens', 500)
        temperature = data.get('temperature', 0.7)
        top_p = data.get('top_p', 0.9)
        
        logger.info(f"Генерирую ответ на промпт: {prompt[:50]}...")
        
        response = llm_client.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        
        return jsonify({
            'success': True,
            'response': response,
            'mode': config.mode,
            'model': config.ollama_model if config.mode == 'local' else config.openai_model
        }), 200
        
    except Exception as e:
        logger.error(f"Generate error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint với history поддержкой
    
    Request JSON:
    {
        "messages": [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi!"}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    """
    try:
        if llm_client is None:
            return jsonify({'error': 'LLM client not initialized'}), 503
        
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({'error': 'Missing "messages" in request'}), 400
        
        messages = data['messages']
        max_tokens = data.get('max_tokens', 500)
        temperature = data.get('temperature', 0.7)
        
        logger.info(f"Chat отправлен с {len(messages)} сообщениями")
        
        response = llm_client.chat(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return jsonify({
            'success': True,
            'response': response,
            'mode': config.mode
        }), 200
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """Получить список доступных моделей"""
    try:
        if config.mode == 'local':
            models = llm_client.list_models()
            return jsonify({
                'models': models,
                'mode': 'local'
            }), 200
        else:
            return jsonify({
                'models': [config.openai_model],
                'mode': 'remote'
            }), 200
            
    except Exception as e:
        logger.error(f"List models error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Получить текущую конфигурацию"""
    return jsonify({
        'mode': config.mode,
        'model': config.ollama_model if config.mode == 'local' else config.openai_model,
        'base_url': config.ollama_base_url if config.mode == 'local' else config.custom_base_url
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        initialize_client()
        logger.info("Запускаю Flask сервер...")
        app.run(host='0.0.0.0', port=8000, debug=False)
    except Exception as e:
        logger.error(f"Ошибка при запуске: {str(e)}")
        exit(1)
