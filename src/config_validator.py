import logging
from typing import Optional
from config import settings
from src.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class ConfigValidator:
    """
    Validates the application configuration.
    """

    def validate_config(self) -> bool:
        """
        Validate the application configuration.

        Checks for required configuration values and ensures they are present.
        Logs any missing configuration.

        Returns:
            bool: True if configuration is valid, False otherwise

        Raises:
            ConfigurationError: If required configuration is missing or invalid
        """
        required_config = [
            'CLOUDFLARE.WORKER_URL',
            'GEMINI.API_KEY',
            'TTS.VOICE',
            'CACHE.MAX_ENTRIES'
        ]

        for config_path in required_config:
            if not self._get_nested_config(config_path):
                logger.error(f"Missing required configuration: {config_path}")
                raise ConfigurationError(f"Missing required configuration: {config_path}")
        return True

    def _get_nested_config(self, path: str) -> Optional[str]:
        """
        Get nested configuration value using dot notation.

        Args:
            path: Configuration path in dot notation (e.g., 'CLOUDFLARE.WORKER_URL')

        Returns:
            Optional[str]: Configuration value if found, None otherwise

        Raises:
            KeyError: If configuration path is invalid
            AttributeError: If configuration structure is invalid
        """
        keys = path.split('.')
        value = settings
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, AttributeError):
            return None
