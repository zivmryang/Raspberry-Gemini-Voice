import json
import logging
import requests
from datetime import datetime
from typing import Optional, Dict
from config import settings
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Database setup for caching
Base = declarative_base()

class ApiCache(Base):
    __tablename__ = 'api_cache'
    query_hash = Column(String(64), primary_key=True)
    response = Column(Text)
    timestamp = Column(String)

# Initialize database
engine = create_engine(f'sqlite:///{settings.CACHE["DATABASE_PATH"]}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class GeminiClient:
    def __init__(self) -> None:
        """Initialize the Gemini API client with default settings.
        
        Sets up:
        - HTTP session with authentication headers
        - Default timeout (10 seconds)
        - Retry mechanism (3 attempts)
        - Database connection for caching
        """
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.CLOUDFLARE["API_KEY"]}'
        })
        # Set default timeout for all requests (10 seconds)
        self.timeout: int = 10
        self.max_retries: int = 3
        self.cache_session = Session()

    def initialize(self) -> bool:
        """Initialize the API client by testing the connection.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Example:
            >>> client = GeminiClient()
            >>> if not client.initialize():
            ...     print("Failed to initialize API client")
        """
        try:
            # Test connection to Cloudflare Worker
            response = self.session.get(
                settings.CLOUDFLARE['WORKER_URL'],
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info("API client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize API client: {str(e)}")
            return False

    def get_response(self, text: str) -> Optional[str]:
        """Get response from Gemini API through Cloudflare Worker"""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(text)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return cached_response

            # Prepare request payload
            payload = {
                "contents": [{
                    "parts": [{"text": text}]
                }],
                "generationConfig": {
                    "maxOutputTokens": settings.GEMINI['MAX_TOKENS'],
                    "temperature": settings.GEMINI['TEMPERATURE']
                }
            }

            # Make API request with retry logic
            last_error = None
            for attempt in range(self.max_retries):
                try:
                    response = self.session.post(
                        settings.CLOUDFLARE['WORKER_URL'],
                        data=json.dumps(payload),
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    break
                except requests.exceptions.Timeout as e:
                    last_error = e
                    logger.warning(f"API request timed out (attempt {attempt + 1}/{self.max_retries})")
                    if attempt == self.max_retries - 1:
                        raise
                except requests.exceptions.RequestException as e:
                    last_error = e
                    logger.error(f"API request failed: {str(e)}")
                    raise

            if last_error:
                raise last_error

            # Parse response
            response_data = response.json()
            generated_text = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')

            if generated_text:
                # Cache the response
                self._cache_response(cache_key, generated_text)
                return generated_text
            else:
                raise ValueError("No valid response from API")

        except requests.exceptions.Timeout:
            logger.error("API request timed out after maximum retries")
            return "Sorry, the request timed out. Please try again."
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            return "Sorry, there was an error processing your request."

    def _generate_cache_key(self, text: str) -> str:
        """Generate a unique cache key for the query"""
        return str(hash(text))

    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if available"""
        cached = self.cache_session.query(ApiCache).filter_by(query_hash=cache_key).first()
        if cached:
            return cached.response
        return None

    def _cache_response(self, cache_key: str, response: str) -> None:
        """Cache the API response with automatic cleanup.
        
        Args:
            cache_key: Unique hash key for the query
            response: API response text to cache
            
        Raises:
            DatabaseError: If caching operation fails
            
        Note:
            Implements LRU (Least Recently Used) cache eviction policy
            when cache reaches maximum capacity.
        """
        try:
            # Check if cache is full
            cache_count = self.cache_session.query(ApiCache).count()
            if cache_count >= settings.CACHE['MAX_ENTRIES']:
                # Remove 10% oldest entries when cache is full
                delete_count = max(1, int(settings.CACHE['MAX_ENTRIES'] * 0.1))
                oldest_entries = self.cache_session.query(ApiCache)\
                    .order_by(ApiCache.timestamp)\
                    .limit(delete_count)\
                    .all()
                for entry in oldest_entries:
                    self.cache_session.delete(entry)

            # Add new entry
            new_cache = ApiCache(
                query_hash=cache_key,
                response=response,
                timestamp=str(datetime.now())
            )
            self.cache_session.add(new_cache)
            self.cache_session.commit()
        except Exception as e:
            logger.error(f"Failed to cache response: {str(e)}")
            self.cache_session.rollback()
            raise

    def close(self):
        """Clean up resources"""
        self.cache_session.close()
        self.session.close()
        logger.info("API client closed")
