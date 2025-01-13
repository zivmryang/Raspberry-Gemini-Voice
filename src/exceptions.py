"""Custom exceptions for the voice assistant application."""

class VoiceAssistantError(Exception):
    """Base class for all voice assistant exceptions."""
    pass

class ConfigurationError(VoiceAssistantError):
    """Raised when there are issues with application configuration."""
    pass

class InitializationError(VoiceAssistantError):
    """Raised when a component fails to initialize."""
    pass

class SpeechRecognitionError(VoiceAssistantError):
    """Raised when speech recognition fails."""
    pass

class APIError(VoiceAssistantError):
    """Raised when API communication fails."""
    pass

class TTSError(VoiceAssistantError):
    """Raised when text-to-speech synthesis fails."""
    pass

class ValidationError(VoiceAssistantError):
    """Raised when input validation fails."""
    pass

class TimeoutError(VoiceAssistantError):
    """Raised when an operation times out."""
    pass

class ResourceError(VoiceAssistantError):
    """Raised when resource allocation fails."""
    pass
