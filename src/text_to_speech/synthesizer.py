import logging
import subprocess
import threading
from config import settings

logger = logging.getLogger(__name__)

class TextToSpeech:
    def __init__(self):
        self.process = None
        self.lock = threading.Lock()
        self.voice = settings.TTS['VOICE']
        self.speed = settings.TTS['SPEED']
        self.pitch = settings.TTS['PITCH']

    def initialize(self):
        """Initialize the text-to-speech system"""
        try:
            # Test if espeak is installed
            subprocess.run(['espeak', '--version'], check=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info("Text-to-speech initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize text-to-speech: {str(e)}")
            return False

    def speak(self, text: str):
        """Convert text to speech and play it"""
        if not text:
            return

        try:
            # Stop any existing speech
            self.stop()

            # Build espeak command
            command = [
                'espeak',
                '-v', self.voice,
                '-s', str(self.speed),
                '-p', str(self.pitch),
                '--stdout'
            ]

            # Start the speech process
            with self.lock:
                self.process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )
                
                # Pipe the text to espeak
                self.process.stdin.write(text.encode('utf-8'))
                self.process.stdin.close()

                # Play the audio using aplay
                aplay = subprocess.Popen(
                    ['aplay'],
                    stdin=self.process.stdout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Wait for completion
                aplay.communicate()
                self.process = None

            logger.info(f"Spoke text: {text[:50]}...")  # Log first 50 chars

        except Exception as e:
            logger.error(f"Error during text-to-speech: {str(e)}")
            self.stop()

    def stop(self):
        """Stop any ongoing speech"""
        with self.lock:
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=1)
                except:
                    self.process.kill()
                finally:
                    self.process = None
                    logger.info("Stopped ongoing speech")

    def set_voice(self, voice: str):
        """Set the TTS voice"""
        self.voice = voice
        logger.info(f"Changed TTS voice to: {voice}")

    def set_speed(self, speed: int):
        """Set the speech speed (words per minute)"""
        self.speed = speed
        logger.info(f"Changed TTS speed to: {speed} wpm")

    def set_pitch(self, pitch: int):
        """Set the speech pitch (0-99)"""
        self.pitch = pitch
        logger.info(f"Changed TTS pitch to: {pitch}")

    def close(self):
        """Clean up resources"""
        self.stop()
        logger.info("Text-to-speech system closed")
