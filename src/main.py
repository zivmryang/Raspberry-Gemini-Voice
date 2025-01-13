"""
树莓派语音助手主应用模块

本模块协调语音识别、API通信和文本转语音组件，提供流畅的语音交互体验。

应用程序遵循以下关键原则：
- 模块化设计，职责清晰分离
- 全面的错误处理和日志记录
- 配置驱动行为
- 优雅的关闭处理

使用示例：
    assistant = VoiceAssistant()
    if assistant.initialize():
        assistant.run()
"""

import logging
import signal
import sys
from typing import Optional
from raspberry_gemini_voice.src.speech_recognition.recognizer import SpeechRecognizer
from raspberry_gemini_voice.src.api_client.client import GeminiClient
from raspberry_gemini_voice.src.text_to_speech.synthesizer import TextToSpeech
from config import settings
from .exceptions import (
    VoiceAssistantError,
    ConfigurationError,
    InitializationError,
    SpeechRecognitionError,
    APIError,
    TTSError,
    ValidationError,
    TimeoutError,
    ResourceError
)

# Configure logging
logger = logging.getLogger(__name__)

class VoiceAssistant:
    """主语音助手类，协调所有组件
    
    本类管理语音助手应用程序的生命周期，
    包括初始化、主执行循环和优雅关闭。
    
    属性：
        running: 布尔标志，指示助手是否处于活动状态
        recognizer: 语音识别组件
        api_client: API通信组件
        tts: 文本转语音合成组件
    """
    
    def __init__(self):
        """使用所有必需组件初始化语音助手
        
        初始化语音识别、API客户端和文本转语音组件。
        设置信号处理程序以实现优雅关闭。
        """
        self.running = False
        self.recognizer = SpeechRecognizer()
        self.api_client = GeminiClient()
        self.tts = TextToSpeech()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def initialize(self) -> bool:
        """
        Initialize all components of the voice assistant.
        
        Returns:
            bool: True if all components initialized successfully, False otherwise
            
        Raises:
            ConfigurationError: If required configuration is missing or invalid
            InitializationError: If any component fails to initialize
        """
        try:
            # Initialize components with timeout
            init_results = []
            for component, init_func in [
                ('Speech Recognizer', self.recognizer.initialize),
                ('API Client', self.api_client.initialize),
                ('Text-to-Speech', self.tts.initialize)
            ]:
                try:
                    result = init_func()
                    if not result:
                        logger.error(f"{component} failed to initialize")
                    init_results.append(result)
                except Exception as e:
                    logger.error(f"{component} initialization error: {str(e)}")
                    init_results.append(False)

            if not all(init_results):
                raise InitializationError("One or more components failed to initialize")
            
            # Validate configuration
            if not self._validate_config():
                raise ConfigurationError("Invalid configuration detected")
            
            logger.info("All components initialized successfully")
            return True
            
        except ConfigurationError as e:
            logger.error(f"Configuration error: {str(e)}")
            return False
        except InitializationError as e:
            logger.error(f"Initialization error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected initialization error: {str(e)}", exc_info=True)
            return False

    def _validate_config(self) -> bool:
        """
        Validate the application configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
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
                return False
        return True

    def _get_nested_config(self, path: str) -> Optional[str]:
        """
        Get nested configuration value using dot notation.
        
        Args:
            path: Configuration path in dot notation (e.g., 'CLOUDFLARE.WORKER_URL')
            
        Returns:
            Optional[str]: Configuration value if found, None otherwise
        """
        keys = path.split('.')
        value = settings
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, AttributeError):
            return None

    def run(self) -> None:
        """
        Main application loop that handles voice interaction.
        
        This method continuously listens for user input, processes it through the API,
        and provides voice responses until shutdown is requested.
        """
        self.running = True
        logger.info("Starting voice assistant...")
        
        try:
            while self.running:
                # Listen for user input
                logger.info("Listening for speech...")
                text = self.recognizer.recognize_speech()
                
                if not text:
                    logger.debug("No speech detected")
                    continue
                    
                logger.info(f"Recognized text: {text}")
                
                # Get response from API
                response = self.api_client.get_response(text)
                if not response:
                    response = "Sorry, I couldn't process that request."
                    logger.warning("Empty response from API")
                    
                # Speak the response
                self.tts.speak(response)
                
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}", exc_info=True)
        finally:
            self.shutdown()

    def _handle_signal(self, signum: int, frame) -> None:
        """
        Handle termination signals for graceful shutdown.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def shutdown(self) -> None:
        """
        Clean up resources and perform graceful shutdown.
        
        This method ensures all components are properly closed and resources
        are released before exiting.
        """
        logger.info("Shutting down voice assistant...")
        try:
            self.recognizer.close()
            self.api_client.close()
            self.tts.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
        finally:
            logger.info("Shutdown complete")

if __name__ == "__main__":
    # Configure logging
    # Configure logging with rotation (10MB per file, keep 5 backups)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(
                'voice_assistant.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    try:
        assistant = VoiceAssistant()
        if assistant.initialize():
            assistant.run()
        else:
            logger.error("Failed to initialize voice assistant")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
"""
Main application module for Raspberry Pi Voice Assistant.

This module orchestrates the speech recognition, API communication, and text-to-speech
components to provide a seamless voice interaction experience.

The application follows these key principles:
- Modular design with clear separation of concerns
- Comprehensive error handling and logging
- Configuration-driven behavior
- Graceful shutdown handling

Example usage:
    assistant = VoiceAssistant()
    if assistant.initialize():
        assistant.run()
"""

import logging
import signal
import sys
from typing import Optional, List, Dict, Any
from raspberry_gemini_voice.src.speech_recognition.recognizer import SpeechRecognizer
from raspberry_gemini_voice.src.api_client.client import GeminiClient
from raspberry_gemini_voice.src.text_to_speech.synthesizer import TextToSpeech
from config import settings

# Configure logging with consistent format
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            'voice_assistant.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
    ]
)

class VoiceAssistant:
    """Main voice assistant class that coordinates all components."""
    
    def __init__(self):
        """Initialize the voice assistant with all required components."""
        self.running = False
        self.recognizer = SpeechRecognizer()
        self.api_client = GeminiClient()
        self.tts = TextToSpeech()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def initialize(self) -> bool:
        """
        Initialize all components of the voice assistant.
        
        Initializes each component in sequence and validates configuration.
        If any component fails to initialize, the entire initialization fails.
        
        Returns:
            bool: True if all components initialized successfully, False otherwise
            
        Raises:
            ConfigurationError: If required configuration is missing or invalid
            InitializationError: If any component fails to initialize
        """
        try:
            if not all([
                self.recognizer.initialize(),
                self.api_client.initialize(),
                self.tts.initialize()
            ]):
                logger.error("Failed to initialize one or more components")
                return False
            
            # Validate configuration
            if not self._validate_config():
                logger.error("Invalid configuration detected")
                return False
            
            logger.info("All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}", exc_info=True)
            return False

    def _validate_config(self) -> bool:
        """
        Validate the application configuration.
        
        Checks for required configuration values and ensures they are properly
        formatted. Logs any missing or invalid configuration.
        
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
                return False
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

    def run(self) -> None:
        """
        Main application loop that handles voice interaction.
        
        This method continuously:
        1. Listens for user speech input
        2. Processes the input through the API
        3. Provides voice responses
        4. Repeats until shutdown is requested
        
        Raises:
            KeyboardInterrupt: When user requests shutdown
            APIError: If API communication fails
            SpeechRecognitionError: If speech recognition fails
            TTSError: If text-to-speech synthesis fails
        """
        self.running = True
        logger.info("Starting voice assistant...")
        
        try:
            while self.running:
                # Listen for user input
                logger.info("Listening for speech...")
                text = self.recognizer.recognize_speech()
                
                if not text:
                    logger.debug("No speech detected")
                    continue
                    
                logger.info(f"Recognized text: {text}")
                
                # Get response from API
                response = self.api_client.get_response(text)
                if not response:
                    response = "Sorry, I couldn't process that request."
                    logger.warning("Empty response from API")
                    
                # Speak the response
                self.tts.speak(response)
                
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}", exc_info=True)
        finally:
            self.shutdown()

    def _handle_signal(self, signum: int, frame) -> None:
        """
        Handle termination signals for graceful shutdown.
        
        Args:
            signum: Signal number
            frame: Current stack frame
            
        Note:
            This method is registered as a signal handler for SIGINT and SIGTERM.
            It sets the running flag to False to initiate graceful shutdown.
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def shutdown(self) -> None:
        """
        Clean up resources and perform graceful shutdown.
        
        This method:
        1. Closes all active components
        2. Releases system resources
        3. Ensures clean application exit
        
        Note:
            This method is called both during normal shutdown and error conditions.
            It should be idempotent and safe to call multiple times.
        """
        logger.info("Shutting down voice assistant...")
        try:
            self.recognizer.close()
            self.api_client.close()
            self.tts.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
        finally:
            logger.info("Shutdown complete")

def configure_logging() -> None:
    """Configure application logging with rotation and formatting.
    
    Sets up logging with:
    - INFO level by default
    - Timestamped format
    - Console output
    - Rotating file handler (10MB per file, 5 backups)
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(
                'voice_assistant.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )

if __name__ == "__main__":
    # TODO: Add integration tests for main execution flow
    # TODO: Add unit tests for configuration validation
    # TODO: Add performance benchmarks for speech recognition
    
    configure_logging()
    
    try:
        assistant = VoiceAssistant()
        if assistant.initialize():
            assistant.run()
        else:
            logger.error("Failed to initialize voice assistant")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
"""
Main application module for Raspberry Pi Voice Assistant.

This module orchestrates the speech recognition, API communication, and text-to-speech
components to provide a seamless voice interaction experience.
"""

import logging
import signal
import sys
from typing import Optional
from raspberry_gemini_voice.src.speech_recognition.recognizer import SpeechRecognizer
from raspberry_gemini_voice.src.api_client.client import GeminiClient
from raspberry_gemini_voice.src.text_to_speech.synthesizer import TextToSpeech
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

class VoiceAssistant:
    """Main voice assistant class that coordinates all components."""
    
    def __init__(self):
        """Initialize the voice assistant with all required components."""
        self.running = False
        self.recognizer = SpeechRecognizer()
        self.api_client = GeminiClient()
        self.tts = TextToSpeech()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def initialize(self) -> bool:
        """
        初始化语音助手的所有组件
        
        返回：
            bool: 如果所有组件初始化成功返回True，否则返回False
            
        抛出：
            ConfigurationError: 如果缺少或配置无效
            InitializationError: 如果任何组件初始化失败
            ResourceError: 如果无法分配系统资源
        """
        try:
            # 使用超时机制初始化组件
            init_results = []
            for component, init_func in [
                ('Speech Recognizer', self.recognizer.initialize),
                ('API Client', self.api_client.initialize),
                ('Text-to-Speech', self.tts.initialize)
            ]:
                try:
                    result = init_func()
                    if not result:
                        logger.error(f"{component} failed to initialize")
                    init_results.append(result)
                except Exception as e:
                    logger.error(f"{component} initialization error: {str(e)}")
                    init_results.append(False)

            if not all(init_results):
                raise InitializationError("One or more components failed to initialize")
            
            # 验证配置
            if not self._validate_config():
                raise ConfigurationError("Invalid configuration detected")
            
            logger.info("All components initialized successfully")
            return True
            
        except ConfigurationError as e:
            logger.error(f"Configuration error: {str(e)}")
            return False
        except InitializationError as e:
            logger.error(f"Initialization error: {str(e)}")
            return False
        except ResourceError as e:
            logger.error(f"Resource allocation error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected initialization error: {str(e)}", exc_info=True)
            return False

    def _validate_config(self) -> bool:
        """
        验证应用程序配置
        
        返回：
            bool: 如果配置有效返回True，否则返回False
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
                return False
        return True

    def _get_nested_config(self, path: str) -> Optional[str]:
        """
        使用点符号获取嵌套配置值
        
        参数：
            path: 点符号表示的配置路径（例如'CLOUDFLARE.WORKER_URL'）
            
        返回：
            Optional[str]: 如果找到返回配置值，否则返回None
        """
        keys = path.split('.')
        value = settings
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, AttributeError):
            return None

    def run(self) -> None:
        """
        处理语音交互的主应用程序循环
        
        本方法持续：
        1. 监听用户语音输入
        2. 通过API处理输入
        3. 提供语音响应
        4. 重复直到请求关闭
        
        抛出：
            KeyboardInterrupt: 当用户请求关闭时
            APIError: 如果API通信失败
            SpeechRecognitionError: 如果语音识别失败
            TTSError: 如果文本转语音合成失败
        """
        self.running = True
        logger.info("Starting voice assistant...")
        
        try:
            while self.running:
                try:
                    # Listen for user input
                    logger.info("Listening for speech...")
                    text = self.recognizer.recognize_speech()
                    
                    if not text:
                        logger.debug("No speech detected")
                        continue
                        
                    logger.info(f"Recognized text: {text}")
                    
                    # Get response from API
                    try:
                        response = self.api_client.get_response(text)
                        if not response:
                            response = "Sorry, I couldn't process that request."
                            logger.warning("Empty response from API")
                            
                        # Speak the response
                        try:
                            self.tts.speak(response)
                        except TTSError as e:
                            logger.error(f"Text-to-speech error: {str(e)}")
                            continue
                            
                    except APIError as e:
                        logger.error(f"API communication error: {str(e)}")
                        self.tts.speak("Sorry, I'm having trouble connecting to the service.")
                        continue
                        
                except SpeechRecognitionError as e:
                    logger.error(f"Speech recognition error: {str(e)}")
                    self.tts.speak("Sorry, I didn't catch that. Please try again.")
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {str(e)}", exc_info=True)
        finally:
            self.shutdown()

    def _handle_signal(self, signum: int, frame) -> None:
        """
        Handle termination signals for graceful shutdown.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def shutdown(self) -> None:
        """
        Clean up resources and perform graceful shutdown.
        
        This method ensures all components are properly closed and resources
        are released before exiting.
        """
        logger.info("Shutting down voice assistant...")
        try:
            self.recognizer.close()
            self.api_client.close()
            self.tts.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
        finally:
            logger.info("Shutdown complete")

if __name__ == "__main__":
    # Configure logging with rotation (10MB per file, keep 5 backups)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(
                'voice_assistant.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    try:
        assistant = VoiceAssistant()
        if assistant.initialize():
            assistant.run()
        else:
            logger.error("Failed to initialize voice assistant")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
"""
Main application module for Raspberry Pi Voice Assistant.

This module orchestrates the speech recognition, API communication, and text-to-speech
components to provide a seamless voice interaction experience.
"""

import logging
import signal
import sys
from typing import Optional
from raspberry_gemini_voice.src.speech_recognition.recognizer import SpeechRecognizer
from raspberry_gemini_voice.src.api_client.client import GeminiClient
from raspberry_gemini_voice.src.text_to_speech.synthesizer import TextToSpeech
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

class VoiceAssistant:
    """Main voice assistant class that coordinates all components."""
    
    def __init__(self):
        """Initialize the voice assistant with all required components."""
        self.running = False
        self.recognizer = SpeechRecognizer()
        self.api_client = GeminiClient()
        self.tts = TextToSpeech()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def initialize(self) -> bool:
        """
        Initialize all components of the voice assistant.
        
        Returns:
            bool: True if all components initialized successfully, False otherwise
        """
        try:
            if not all([
                self.recognizer.initialize(),
                self.api_client.initialize(),
                self.tts.initialize()
            ]):
                logger.error("Failed to initialize one or more components")
                return False
            
            # Validate configuration
            if not self._validate_config():
                logger.error("Invalid configuration detected")
                return False
            
            logger.info("All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}", exc_info=True)
            return False

    def _validate_config(self) -> bool:
        """
        Validate the application configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
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
                return False
        return True

    def _get_nested_config(self, path: str) -> Optional[str]:
        """
        Get nested configuration value using dot notation.
        
        Args:
            path: Configuration path in dot notation (e.g., 'CLOUDFLARE.WORKER_URL')
            
        Returns:
            Optional[str]: Configuration value if found, None otherwise
        """
        keys = path.split('.')
        value = settings
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, AttributeError):
            return None

    def run(self) -> None:
        """
        Main application loop that handles voice interaction.
        
        This method continuously listens for user input, processes it through the API,
        and provides voice responses until shutdown is requested.
        """
        self.running = True
        logger.info("Starting voice assistant...")
        
        try:
            while self.running:
                # 监听用户输入
                logger.info("正在监听语音...")
                text = self.recognizer.recognize_speech()
                
                if not text:
                    logger.debug("未检测到语音")
                    continue
                    
                logger.info(f"识别到的文本: {text}")
                
                # 从API获取响应
                response = self.api_client.get_response(text)
                if not response:
                    response = "抱歉，我无法处理该请求。"
                    logger.warning("API返回空响应")
                    
                # 语音输出响应
                self.tts.speak(response)
                
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}", exc_info=True)
        finally:
            self.shutdown()

    def _handle_signal(self, signum: int, frame) -> None:
        """
        处理终止信号以实现优雅关闭
        
        参数：
            signum: 信号编号
            frame: 当前堆栈帧
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def shutdown(self) -> None:
        """
        清理资源并执行优雅关闭
        
        本方法确保所有组件正确关闭并在退出前释放资源。
        """
        logger.info("正在关闭语音助手...")
        try:
            self.recognizer.close()
            self.api_client.close()
            self.tts.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
        finally:
            logger.info("关闭完成")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('voice_assistant.log')
        ]
    )
    
    try:
        assistant = VoiceAssistant()
        if assistant.initialize():
            assistant.run()
        else:
            logger.error("Failed to initialize voice assistant")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
"""
Main application module for Raspberry Pi Voice Assistant.

This module orchestrates the speech recognition, API communication, and text-to-speech
components to provide a seamless voice interaction experience.
"""

import logging
import signal
import sys
from typing import Optional
from raspberry_gemini_voice.src.speech_recognition.recognizer import SpeechRecognizer
from raspberry_gemini_voice.src.api_client.client import GeminiClient
from raspberry_gemini_voice.src.text_to_speech.synthesizer import TextToSpeech
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

class VoiceAssistant:
    """Main voice assistant class that coordinates all components."""
    
    def __init__(self):
        """Initialize the voice assistant with all required components."""
        self.running = False
        self.recognizer = SpeechRecognizer()
        self.api_client = GeminiClient()
        self.tts = TextToSpeech()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def initialize(self) -> bool:
        """
        Initialize all components of the voice assistant.
        
        Returns:
            bool: True if all components initialized successfully, False otherwise
        """
        try:
            if not all([
                self.recognizer.initialize(),
                self.api_client.initialize(),
                self.tts.initialize()
            ]):
                logger.error("Failed to initialize one or more components")
                return False
            
            # Validate configuration
            if not self._validate_config():
                logger.error("Invalid configuration detected")
                return False
            
            logger.info("All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}", exc_info=True)
            return False

    def _validate_config(self) -> bool:
        """
        Validate the application configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
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
                return False
        return True

    def _get_nested_config(self, path: str) -> Optional[str]:
        """
        Get nested configuration value using dot notation.
        
        Args:
            path: Configuration path in dot notation (e.g., 'CLOUDFLARE.WORKER_URL')
            
        Returns:
            Optional[str]: Configuration value if found, None otherwise
        """
        keys = path.split('.')
        value = settings
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, AttributeError):
            return None

    def run(self) -> None:
        """
        Main application loop that handles voice interaction.
        
        This method continuously listens for user input, processes it through the API,
        and provides voice responses until shutdown is requested.
        """
        self.running = True
        logger.info("Starting voice assistant...")
        
        try:
            while self.running:
                # Listen for user input
                logger.info("Listening for speech...")
                text = self.recognizer.recognize_speech()
                
                if not text:
                    logger.debug("No speech detected")
                    continue
                    
                logger.info(f"Recognized text: {text}")
                
                # Get response from API
                response = self.api_client.get_response(text)
                if not response:
                    response = "Sorry, I couldn't process that request."
                    logger.warning("Empty response from API")
                    
                # Speak the response
                self.tts.speak(response)
                
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}", exc_info=True)
        finally:
            self.shutdown()

    def _handle_signal(self, signum: int, frame) -> None:
        """
        Handle termination signals for graceful shutdown.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def shutdown(self) -> None:
        """
        Clean up resources and perform graceful shutdown.
        
        This method ensures all components are properly closed and resources
        are released before exiting.
        """
        logger.info("Shutting down voice assistant...")
        try:
            self.recognizer.close()
            self.api_client.close()
            self.tts.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
        finally:
            logger.info("Shutdown complete")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('voice_assistant.log')
        ]
    )
    
    try:
        assistant = VoiceAssistant()
        if assistant.initialize():
            assistant.run()
        else:
            logger.error("Failed to initialize voice assistant")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
"""
Main application module for Raspberry Pi Voice Assistant.

This module orchestrates the speech recognition, API communication, and text-to-speech
components to provide a seamless voice interaction experience.
"""

import logging
import signal
import sys
from typing import Optional
from raspberry_gemini_voice.src.speech_recognition.recognizer import SpeechRecognizer
from raspberry_gemini_voice.src.api_client.client import GeminiClient
from raspberry_gemini_voice.src.text_to_speech.synthesizer import TextToSpeech
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

class VoiceAssistant:
    """Main voice assistant class that coordinates all components."""
    
    def __init__(self):
        """Initialize the voice assistant with all required components."""
        self.running = False
        self.recognizer = SpeechRecognizer()
        self.api_client = GeminiClient()
        self.tts = TextToSpeech()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def initialize(self) -> bool:
        """
        Initialize all components of the voice assistant.
        
        Returns:
            bool: True if all components initialized successfully, False otherwise
        """
        try:
            if not all([
                self.recognizer.initialize(),
                self.api_client.initialize(),
                self.tts.initialize()
            ]):
                logger.error("Failed to initialize one or more components")
                return False
            
            # Validate configuration
            if not self._validate_config():
                logger.error("Invalid configuration detected")
                return False
            
            logger.info("All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}", exc_info=True)
            return False

    def _validate_config(self) -> bool:
        """
        Validate the application configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
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
                return False
        return True

    def _get_nested_config(self, path: str) -> Optional[str]:
        """
        Get nested configuration value using dot notation.
        
        Args:
            path: Configuration path in dot notation (e.g., 'CLOUDFLARE.WORKER_URL')
            
        Returns:
            Optional[str]: Configuration value if found, None otherwise
        """
        keys = path.split('.')
        value = settings
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, AttributeError):
            return None

    def run(self) -> None:
        """
        Main application loop that handles voice interaction.
        
        This method continuously listens for user input, processes it through the API,
        and provides voice responses until shutdown is requested.
        """
        self.running = True
        logger.info("Starting voice assistant...")
        
        try:
            while self.running:
                # Listen for user input
                logger.info("Listening for speech...")
                text = self.recognizer.recognize_speech()
                
                if not text:
                    logger.debug("No speech detected")
                    continue
                    
                logger.info(f"Recognized text: {text}")
                
                # Get response from API
                response = self.api_client.get_response(text)
                if not response:
                    response = "Sorry, I couldn't process that request."
                    logger.warning("Empty response from API")
                    
                # Speak the response
                self.tts.speak(response)
                
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}", exc_info=True)
        finally:
            self.shutdown()

    def _handle_signal(self, signum: int, frame) -> None:
        """
        Handle termination signals for graceful shutdown.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def shutdown(self) -> None:
        """
        Clean up resources and perform graceful shutdown.
        
        This method ensures all components are properly closed and resources
        are released before exiting.
        """
        logger.info("Shutting down voice assistant...")
        try:
            self.recognizer.close()
            self.api_client.close()
            self.tts.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
        finally:
            logger.info("Shutdown complete")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('voice_assistant.log')
        ]
    )
    
    try:
        assistant = VoiceAssistant()
        if assistant.initialize():
            assistant.run()
        else:
            logger.error("Failed to initialize voice assistant")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
"""
Main application module for Raspberry Pi Voice Assistant.

This module orchestrates the speech recognition, API communication, and text-to-speech
components to provide a seamless voice interaction experience.
"""

import logging
import signal
import sys
from typing import Optional
from raspberry_gemini_voice.src.speech_recognition.recognizer import SpeechRecognizer
from raspberry_gemini_voice.src.api_client.client import GeminiClient
from raspberry_gemini_voice.src.text_to_speech.synthesizer import TextToSpeech
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

class VoiceAssistant:
    """Main voice assistant class that coordinates all components."""
    
    def __init__(self):
        """Initialize the voice assistant with all required components."""
        self.running = False
        self.recognizer = SpeechRecognizer()
        self.api_client = GeminiClient()
        self.tts = TextToSpeech()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def initialize(self) -> bool:
        """
        Initialize all components of the voice assistant.
        
        Returns:
            bool: True if all components initialized successfully, False otherwise
        """
        try:
            if not all([
                self.recognizer.initialize(),
                self.api_client.initialize(),
                self.tts.initialize()
            ]):
                logger.error("Failed to initialize one or more components")
                return False
            
            # Validate configuration
            if not self._validate_config():
                logger.error("Invalid configuration detected")
                return False
            
            logger.info("All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}", exc_info=True)
            return False

    def _validate_config(self) -> bool:
        """
        Validate the application configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
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
                return False
        return True

    def _get_nested_config(self, path: str) -> Optional[str]:
        """
        Get nested configuration value using dot notation.
        
        Args:
            path: Configuration path in dot notation (e.g., 'CLOUDFLARE.WORKER_URL')
            
        Returns:
            Optional[str]: Configuration value if found, None otherwise
        """
        keys = path.split('.')
        value = settings
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, AttributeError):
            return None

    def run(self) -> None:
        """
        Main application loop that handles voice interaction.
        
        This method continuously listens for user input, processes it through the API,
        and provides voice responses until shutdown is requested.
        """
        self.running = True
        logger.info("Starting voice assistant...")
        
        try:
            while self.running:
                # Listen for user input
                logger.info("Listening for speech...")
                text = self.recognizer.recognize_speech()
                
                if not text:
                    logger.debug("No speech detected")
                    continue
                    
                logger.info(f"Recognized text: {text}")
                
                # Get response from API
                response = self.api_client.get_response(text)
                if not response:
                    response = "Sorry, I couldn't process that request."
                    logger.warning("Empty response from API")
                    
                # Speak the response
                self.tts.speak(response)
                
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}", exc_info=True)
        finally:
            self.shutdown()

    def _handle_signal(self, signum: int, frame) -> None:
        """
        Handle termination signals for graceful shutdown.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def shutdown(self) -> None:
        """
        Clean up resources and perform graceful shutdown.
        
        This method ensures all components are properly closed and resources
        are released before exiting.
        """
        logger.info("Shutting down voice assistant...")
        try:
            self.recognizer.close()
            self.api_client.close()
            self.tts.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
        finally:
            logger.info("Shutdown complete")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('voice_assistant.log')
        ]
    )
    
    try:
        assistant = VoiceAssistant()
        if assistant.initialize():
            assistant.run()
        else:
            logger.error("Failed to initialize voice assistant")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
import logging
import signal
import sys
from raspberry_gemini_voice.src.speech_recognition.recognizer import SpeechRecognizer
from raspberry_gemini_voice.src.api_client.client import GeminiClient
from raspberry_gemini_voice.src.text_to_speech.synthesizer import TextToSpeech
from config import settings

logger = logging.getLogger(__name__)

class VoiceAssistant:
    def __init__(self):
        self.running = False
        self.recognizer = SpeechRecognizer()
        self.api_client = GeminiClient()
        self.tts = TextToSpeech()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def initialize(self):
        """Initialize all components"""
        try:
            if not all([
                self.recognizer.initialize(),
                self.api_client.initialize(),
                self.tts.initialize()
            ]):
                logger.error("Failed to initialize one or more components")
                return False
            
            logger.info("All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            return False

    def run(self):
        """Main application loop"""
        self.running = True
        logger.info("Starting voice assistant...")
        
        try:
            while self.running:
                # Listen for user input
                logger.info("Listening for speech...")
                text = self.recognizer.recognize_speech()
                
                if not text:
                    continue
                    
                logger.info(f"Recognized text: {text}")
                
                # Get response from API
                response = self.api_client.get_response(text)
                if not response:
                    response = "Sorry, I couldn't process that request."
                    
                # Speak the response
                self.tts.speak(response)
                
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
        finally:
            self.shutdown()

    def _handle_signal(self, signum, frame):
        """Handle termination signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def shutdown(self):
        """Clean up resources"""
        logger.info("Shutting down voice assistant...")
        self.recognizer.close()
        self.api_client.close()
        self.tts.close()
        logger.info("Shutdown complete")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    assistant = VoiceAssistant()
    if assistant.initialize():
        assistant.run()
    else:
        logger.error("Failed to initialize voice assistant")
        sys.exit(1)
