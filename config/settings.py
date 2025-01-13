import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent

# Cloudflare Configuration
CLOUDFLARE = {
    'TUNNEL_HOST': os.getenv('CLOUDFLARE_TUNNEL_HOST', 'your-tunnel-host.cloudflare.com'),
    'WORKER_URL': os.getenv('CLOUDFLARE_WORKER_URL', 'https://your-worker.your-domain.workers.dev'),
    'API_KEY': os.getenv('CLOUDFLARE_API_KEY', 'your-cloudflare-api-key')
}

# Gemini API Configuration
GEMINI = {
    'API_ENDPOINT': os.getenv('GEMINI_API_ENDPOINT', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'),
    'API_KEY': os.getenv('GEMINI_API_KEY', 'your-gemini-api-key'),
    'MAX_TOKENS': 1000,
    'TEMPERATURE': 0.7
}

# Speech Recognition Configuration
SPEECH_RECOGNITION = {
    'MODEL_PATH': str(BASE_DIR / 'models/vosk-model-small-en-us-0.15'),
    'SAMPLE_RATE': 16000,
    'BUFFER_SIZE': 4000
}

# Text-to-Speech Configuration
TEXT_TO_SPEECH = {
    'VOICE': 'en-us',
    'SPEED': 160,
    'PITCH': 50,
    'VOLUME': 1.0
}

# Local Cache Configuration
CACHE = {
    'DATABASE_PATH': str(BASE_DIR / 'data/cache.db'),
    'MAX_ENTRIES': 1000,
    'CACHE_TTL': 3600  # 1 hour
}

# Logging Configuration
LOGGING = {
    'LEVEL': 'INFO',
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'FILE': str(BASE_DIR / 'logs/app.log')
}
